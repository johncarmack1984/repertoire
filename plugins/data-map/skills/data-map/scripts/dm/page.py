"""new and sync: start a map project from a stack's template, and inline the page library and the data
so the page opens from file:// with nothing else beside it."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

from . import FAIL, PASS, VERSION, WARN, crs, report

TEMPLATES = Path(__file__).resolve().parents[2] / "assets" / "templates"
LIB = {"css": ("style", "datamap.css"), "js": ("script", "datamap.js")}
LIB_REGION = re.compile(r"<!-- data-map:lib (css|js)(?: (\S+) sha256:([0-9a-f]{64}))? -->\n(?:<(?:style|script)>\n(.*?)</(?:style|script)>\n)?<!-- /data-map:lib \1 -->", re.S)
DATA_REGION = re.compile(r"<!-- data-map:data -->\n(.*?)<!-- /data-map:data -->", re.S)
DATA_FILE = re.compile(r'<!-- data-map:file (\S+) sha256:([0-9a-f]{64}) -->\n<script type="application/json" id="dm-data-([^"]+)">(.*?)</script>\n', re.S)
SPEC = re.compile(r'(<script type="application/json" id="dm-spec">\n?)(.*?)(\n?</script>)', re.S)

EQUAL_EARTH = {"type": "crs", "name": "custom:equal-earth", "definition": crs.equal_earth(crs.WORLD_LON0), "property": "equal-area"}
PRESETS = {
    "equal-earth": {"projection": EQUAL_EARTH},
    "globe": {"projection": {"type": "globe"}},
    "mercator": {"projection": {"type": "mercator"}},
    "chart": {"projection": None, "idiom": ["no-map"], "extent": None, "zoom": None, "omit": [], "legend": None},
}
STACK_PRESETS = {"maplibre": ("equal-earth", "globe", "mercator", "chart"), "deck-gl": ("globe", "mercator")}


class UsageError(Exception):
    pass


def stacks() -> list[str]:
    return sorted(d.name for d in TEMPLATES.iterdir() if d.is_dir() and d.name != "lib")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def lib_block(name: str) -> str:
    tag, fname = LIB[name]
    body = (TEMPLATES / "lib" / fname).read_text(encoding="utf-8")
    if f"</{tag}" in body:
        raise UsageError(f"lib/{fname} contains </{tag}, which would end the inlined region early")
    if not body.endswith("\n"):
        body += "\n"
    return f"<!-- data-map:lib {name} {VERSION} sha256:{sha(body.encode())} -->\n<{tag}>\n{body}</{tag}>\n<!-- /data-map:lib {name} -->"


def data_files(out: Path) -> list[Path]:
    """Every JSON and GeoJSON file in OUT/data, legend.json first, then by name."""
    folder = out / "data"
    files = sorted(p for p in folder.glob("*") if p.suffix in (".json", ".geojson") and p.is_file()) if folder.is_dir() else []
    return sorted(files, key=lambda p: (p.name != "legend.json", p.name))


def data_block(path: Path) -> str:
    raw = path.read_bytes()
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as err:
        raise UsageError(f"{path} is not JSON: {err}") from None
    # "<" only occurs inside JSON strings, so escaping it keeps the JSON valid and the script element closed.
    text = json.dumps(obj, separators=(",", ":"), ensure_ascii=False).replace("<", "\\u003c")
    return f'<!-- data-map:file data/{path.name} sha256:{sha(raw)} -->\n<script type="application/json" id="dm-data-{path.stem}">{text}</script>\n'


def synced(text: str, out: Path, page: Path) -> str:
    found = {m[1] for m in LIB_REGION.finditer(text)}
    for name in LIB:
        if name not in found:
            raise UsageError(f"{page} has no data-map:lib {name} region with intact markers; start from `datamap.py new`")
    text = LIB_REGION.sub(lambda m: lib_block(m[1]), text)
    if not DATA_REGION.search(text):
        raise UsageError(f"{page} has no <!-- data-map:data --> region; start from `datamap.py new`")
    blocks = "".join(data_block(p) for p in data_files(out))
    return DATA_REGION.sub(lambda m: f"<!-- data-map:data -->\n{blocks}<!-- /data-map:data -->", text, count=1)


def drift(text: str, out: Path) -> list[str]:
    """What sync would change in the page, in words."""
    said = []
    for m in LIB_REGION.finditer(text):
        body = (TEMPLATES / "lib" / LIB[m[1]][1]).read_text(encoding="utf-8")
        if not body.endswith("\n"):
            body += "\n"
        if not m[3]:
            said.append(f"the {m[1]} library region is empty")
        elif m[4] is None or sha(m[4].encode()) != m[3]:
            said.append(f"the {m[1]} library region was edited by hand")
        elif m[3] != sha(body.encode()) or m[2] != VERSION:
            said.append(f"the {m[1]} library region is {m[2]}, older than assets/templates/lib")
    if not (out / "data").is_dir():
        return said
    region = DATA_REGION.search(text)
    inlined = {m[1]: m[2] for m in DATA_FILE.finditer(region[1])} if region else {}
    on_disk = {f"data/{p.name}": sha(p.read_bytes()) for p in data_files(out)}
    for name in sorted(on_disk.keys() - inlined.keys()):
        said.append(f"{name} is not inlined")
    for name in sorted(inlined.keys() - on_disk.keys()):
        said.append(f"{name} is inlined but no longer in data/")
    for name in sorted(on_disk.keys() & inlined.keys()):
        if on_disk[name] != inlined[name]:
            said.append(f"{name} changed since the last sync")
    return said


RESERVED = {"test", "std", "core", "alloc", "proc_macro", "proc-macro", "self", "super", "crate", "build"}


def package_slug(folder: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", folder.lower()).strip("-") or "map"
    if slug[0].isdigit():
        slug = "map-" + slug
    return slug + "-map" if slug in RESERVED else slug


def rename_package(out: Path) -> str:
    """Name the Cargo package after OUT's folder, in Cargo.toml and its own entry in Cargo.lock."""
    toml = out / "Cargo.toml"
    text = toml.read_text(encoding="utf-8")
    m = re.search(r'(\[package\][^\[]*?\nname\s*=\s*")([^"]+)(")', text)
    if not m:
        raise UsageError(f"{toml} has no [package] name to rename")
    new = package_slug(out.resolve().name)
    toml.write_text(text[:m.start(2)] + new + text[m.end(2):], encoding="utf-8")
    lock = out / "Cargo.lock"
    if lock.is_file():
        old = re.escape(m[2])
        lock.write_text(re.sub(rf'(\[\[package\]\]\nname = "){old}("\nversion = "[^"]*"\ndependencies)', rf"\g<1>{new}\g<2>",
                               lock.read_text(encoding="utf-8"), count=1), encoding="utf-8")
    return new


def run_new(args) -> int:
    out = Path(args.out)
    known = stacks()
    if args.stack not in known:
        raise UsageError(f"no template for stack {args.stack!r}; the stacks are {', '.join(known)}")
    if out.exists() and any(out.iterdir()) and not args.force:
        raise UsageError(f"{out} exists and is not empty; pass --force to write over it")
    src = TEMPLATES / args.stack
    page = src / "index.html"
    preset = args.preset
    if page.exists():
        allowed = STACK_PRESETS.get(args.stack, tuple(PRESETS))
        preset = preset or allowed[0]
        if preset not in allowed:
            raise UsageError(f"{args.stack} draws {', '.join(allowed)}; {preset} needs another stack")
    elif preset:
        raise UsageError(f"{args.stack} sets its projection in its own files; drop --preset")
    # shutil.copy keeps no timestamps: a copy carrying the template's old mtimes looks built already to cargo.
    shutil.copytree(src, out, dirs_exist_ok=True, copy_function=shutil.copy)
    (out / "data").mkdir(exist_ok=True)
    findings = []
    if (out / "Cargo.toml").is_file():
        name = rename_package(out)
        findings.append(PASS("package", f"Cargo package and binary named {name}, so projects that share a CARGO_TARGET_DIR build separate binaries"))
    if page.exists():
        target = out / "index.html"
        text = synced(target.read_text(encoding="utf-8"), out, target)
        m = SPEC.search(text)
        spec = json.loads(m[2])
        spec.update(json.loads(json.dumps(PRESETS[preset])))
        text = text[:m.start(2)] + json.dumps(spec, indent=1, ensure_ascii=False) + text[m.end(2):]
        target.write_text(text, encoding="utf-8")
        findings.append(PASS("new", f"wrote {out.resolve()} from the {args.stack} template, preset {preset}"))
    else:
        findings.append(PASS("new", f"wrote {out.resolve()} from the {args.stack} template"))
    then = f"run datamap.py sync {out}" if page.exists() else "cargo run --release -- --snapshot out.png, then datamap.py check --png out.png"
    findings.append(PASS("next", f"fill brief.md, write the layers with --out-dir {out / 'data'}, then {then}"))
    return report(findings, args.json)


def run_sync(args) -> int:
    out = Path(args.out)
    page = out / "index.html"
    if not page.is_file():
        raise UsageError(f"{page} does not exist; sync is for the maplibre and deck-gl stacks")
    old = page.read_text(encoding="utf-8")
    if not (out / "data").is_dir() and (region := DATA_REGION.search(old)) and DATA_FILE.search(region[1]):
        raise UsageError(f"{out / 'data'} does not exist, so sync would drop every data file {page} inlines; restore data/ first")
    new = synced(old, out, page)
    files = [f"data/{p.name}" for p in data_files(out)]
    findings = []
    if args.check:
        said = drift(old, out)
        if new != old:
            findings.append(FAIL("sync", f"{page} is out of date: {'; '.join(said) or 'region layout differs'}", f"run datamap.py sync {out}"))
        else:
            findings.append(PASS("sync", f"{page} holds the current library and {len(files)} data files"))
        return report(findings, args.json)
    if not files:
        findings.append(WARN("sync", f"{out / 'data'} holds no JSON or GeoJSON yet", "write the layers with --out-dir OUT/data first", 9))
    if new != old:
        page.write_text(new, encoding="utf-8")
    size = len(new.encode()) / 1e6
    findings.append(PASS("sync", f"{page} inlines the {VERSION} library and {', '.join(files) or 'no data files'} ({size:.1f} MB)"))
    if size > 20:
        findings.append(WARN("size", f"the page is {size:.0f} MB, slow to open",
                             "cut the data to what the map draws, or serve large layers as PMTiles"))
    return report(findings, args.json)


def run(args) -> int:
    try:
        return {"new": run_new, "sync": run_sync}[args.command](args)
    except UsageError as err:
        print(f"datamap.py {args.command}: {err}")
        return 2


def register(sub) -> None:
    p = sub.add_parser("new", help="start a map project from a stack's template",
                       description="Copies the stack's template into OUT, with brief.md to fill in and an empty data/ folder.")
    p.add_argument("stack", metavar="STACK", help="maplibre, deck-gl, or mln-rs")
    p.add_argument("out", metavar="OUT", help="the project folder to create")
    p.add_argument("--preset", choices=sorted(PRESETS), help="equal-earth (maplibre's default), globe (deck-gl's default), mercator, or chart (a page with no map, for a no-map answer)")
    p.add_argument("--force", action="store_true", help="write into a folder that is not empty")
    p.add_argument("--json", action="store_true", help="print one JSON object instead of lines")
    p.set_defaults(run=run)
    p = sub.add_parser("sync", help="inline the page library and OUT/data into index.html",
                       description="Inlines every JSON and GeoJSON file in OUT/data, so the page opens from file://.")
    p.add_argument("out", metavar="OUT", help="the project folder")
    p.add_argument("--check", action="store_true", help="change nothing; exit 1 if the page is out of date")
    p.add_argument("--json", action="store_true", help="print one JSON object instead of lines")
    p.set_defaults(run=run)
