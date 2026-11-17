"""The libraries a map page loads, pinned in one place: each version and file with its sha256. sync fetches
them once from jsDelivr into a cache and copies them into the project's vendor/, so the page draws from a
file with no network, and check holds vendor/ to these hashes."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

NPM = "https://cdn.jsdelivr.net/npm"
REGION = re.compile(r"<!-- data-map:vendor((?: \S+)*) -->\n(.*?)<!-- /data-map:vendor -->", re.S)
CARRIER = re.compile(r"\A// [^\n]*\n\(self\.dmVendor \?\?= \{\}\)\[(\"[^\"]+\")\] = (\".*\");\n\Z", re.S)


class VendorError(Exception):
    pass


@dataclass(frozen=True)
class File:
    """A file of a pinned package. `load` says how the page takes it: "text" carries it as a string, for an ES
    module or a worker's script, which Chrome won't load from a file; "script" and "style" are tags in the
    page's head; a "license" only travels with the code."""
    path: str
    sha256: str
    load: str

    @property
    def key(self) -> str:
        return re.sub(r"\.m?js$", "", Path(self.path).name)

    @property
    def target(self) -> str:
        return f"{self.key}.text.js" if self.load == "text" else Path(self.path).name


@dataclass(frozen=True)
class Lib:
    name: str
    version: str
    files: tuple[File, ...]

    @property
    def folder(self) -> str:
        return f"{self.name.lstrip('@').replace('/', '-')}@{self.version}"


LIBS = {lib.name: lib for lib in (
    Lib("maplibre-gl", "6.18.0", (
        File("dist/maplibre-gl.mjs", "1e0a68844041aec6621a10d4725c9970c3b19cf7e1605d98b01dbc993e1058b2", "text"),
        File("dist/maplibre-gl-worker.mjs", "c8998a2616612ebc7afc3a6f83e31ad1c5f6187550a018b4fd0561779c33015b", "text"),
        File("dist/maplibre-gl.css", "a90798a1953017790e590f7e1bd35ff103a8a4263972cb47290b78adf86f8c20", "style"),
        File("LICENSE.txt", "ee5fc05a0677eaf69601d2c7db0d9ecd6cc27c3abc1d0733bc9ed34707cf8ef2", "license"))),
    Lib("proj4", "2.22.0", (
        File("dist/proj4.js", "af7df653d91ea591f33d26fb958990bbd3071b2db644a4edaba441cc9861a474", "text"),
        File("LICENSE.md", "d514fd8b286fc00a5c97a29f8a99b73f1a4053bbdd00c400aee5f24a1b6b301e", "license"))),
    Lib("deck.gl", "9.4.1", (
        File("dist.min.js", "08857e84bc2e5478a62ce1dc59b9b5fae9ae0a21104c78503dece316d69a1ca6", "script"),
        File("LICENSE", "e499a2c2ba3b9faabe91fdfddf43e329439263264b7148e5548d0ec605cce9f2", "license"))),
    Lib("pmtiles", "4.5.0", (
        File("dist/pmtiles.js", "caf981bc46f6327ee7e65d5dc964d89d38a69f60edca2bd4c5c890c21b554c6c", "script"),)),
    Lib("@protomaps/basemaps", "5.7.2", (
        File("dist/basemaps.js", "551864f01da1bfe3005e99987197f22f56d0c35f9a10fa1727a889e2434af16d", "script"),)),
)}
PINS = {name: lib.version for name, lib in LIBS.items()}
# Each project path sync writes, mapped to its library and file.
TARGETS = {f"vendor/{lib.folder}/{f.target}": (lib, f) for lib in LIBS.values() for f in lib.files}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cache_dir() -> Path:
    if env := os.environ.get("DM_CACHE"):
        return Path(env)
    return Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "data-map"


def needs(spec: dict, asked: list[str]) -> list[Lib]:
    """The libraries a page draws with: MapLibre for any map, proj4 under a CRS, pmtiles and the Protomaps
    basemaps for a .pmtiles basemap, and whatever the template's vendor marker asks for, such as deck.gl."""
    proj = spec.get("projection") or {}
    want = set(asked)
    if proj:
        want.add("maplibre-gl")
    if proj.get("type") == "crs":
        want.add("proj4")
    if any(re.search(r"\.pmtiles$", str(t.get("url") or "")) for t in spec.get("tiles") or []):
        want |= {"pmtiles", "@protomaps/basemaps"}
    unknown = sorted(want - LIBS.keys())
    if unknown:
        raise VendorError(f"no pinned library named {', '.join(unknown)}; the pins are {', '.join(LIBS)}")
    return [lib for name, lib in LIBS.items() if name in want]


def region(libs: list[Lib]) -> str:
    """The tags in the page's head that load LIBS from vendor/, styles first."""
    tags = []
    for load, tag in (("style", '<link rel="stylesheet" href="{}">'), ("text", '<script src="{}"></script>'), ("script", '<script src="{}"></script>')):
        tags += [tag.format(f"vendor/{lib.folder}/{f.target}") for lib in libs for f in lib.files if f.load == load]
    return "".join(t + "\n" for t in tags)


def fetch(lib: Lib, f: File) -> bytes:
    """The file's bytes from the cache, or from jsDelivr into the cache, checked against the pin."""
    cached = cache_dir() / lib.folder / f.path
    if cached.is_file():
        data = cached.read_bytes()
        if sha(data) == f.sha256:
            return data
    url = f"{os.environ.get('DM_NPM', NPM)}/{lib.name}@{lib.version}/{f.path}"
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            data = r.read()
    except (urllib.error.URLError, OSError) as err:
        raise VendorError(f"can't fetch {url} ({getattr(err, 'reason', err)}), and the cache at {cache_dir()} doesn't hold it; "
                          f"run sync once with a network, or copy {cache_dir()} from a machine that has it") from None
    if sha(data) != f.sha256:
        raise VendorError(f"{url} came back with sha256 {sha(data)}, not the pinned {f.sha256}")
    cached.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=cached.parent, delete=False) as tmp:
        tmp.write(data)
    os.replace(tmp.name, cached)
    return data


def body(lib: Lib, f: File, data: bytes) -> bytes:
    """What vendor/ holds for the file: the file itself, or for "text" a classic script that carries it as a string."""
    if f.load != "text":
        return data
    head = f"// {lib.name} {lib.version}, {f.path} from npm, carried as text: the page runs it from a blob URL, which works from a file with no network.\n"
    return (head + f"(self.dmVendor ??= {{}})[{json.dumps(f.key)}] = {json.dumps(data.decode('utf-8'))};\n").encode("ascii")


def original_sha(path: Path, f: File) -> str | None:
    """The sha256 of the pinned file a vendor/ file holds or carries, or None when it isn't one."""
    data = path.read_bytes()
    if f.load != "text":
        return sha(data)
    m = CARRIER.fullmatch(data.decode("ascii", errors="replace"))
    return sha(json.loads(m[2]).encode("utf-8")) if m and json.loads(m[1]) == f.key else None


def install(out: Path, libs: list[Lib]) -> list[str]:
    """Make OUT/vendor hold exactly LIBS: copy in what's missing or changed, and remove pinned folders no longer
    used. Returns the paths written or removed."""
    vendor, done = out / "vendor", []
    want = {f"vendor/{lib.folder}/{f.target}": (lib, f) for lib in libs for f in lib.files}
    for rel, (lib, f) in want.items():
        path = out / rel
        if path.is_file() and original_sha(path, f) == f.sha256:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body(lib, f, fetch(lib, f)))
        done.append(rel)
    keep = {lib.folder for lib in libs}
    pinned = re.compile(r"(?:[\w.-]+)@\d[\w.-]*")
    for d in sorted(vendor.iterdir()) if vendor.is_dir() else []:
        if d.is_dir() and pinned.fullmatch(d.name) and d.name not in keep:
            shutil.rmtree(d)
            done.append(f"vendor/{d.name}/")
    if vendor.is_dir() and not any(vendor.iterdir()):
        vendor.rmdir()
    return done


def problems(out: Path, libs: list[Lib]) -> list[str]:
    """What install would change, in words."""
    said = []
    for lib in libs:
        for f in lib.files:
            rel = f"vendor/{lib.folder}/{f.target}"
            if not (out / rel).is_file():
                said.append(f"{rel} is missing")
            elif original_sha(out / rel, f) != f.sha256:
                said.append(f"{rel} is not the pinned {lib.name} {lib.version}")
    return said
