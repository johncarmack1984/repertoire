"""Headless Chrome over the DevTools protocol on --remote-debugging-pipe, and a local server that
answers HTTP Range requests, so a map page renders exactly as a reader's browser draws it."""
from __future__ import annotations

import base64
import fcntl
import functools
import json
import os
import queue
import re
import shutil
import subprocess
import tempfile
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

GL_FLAGS = {
    "default": [],
    "swiftshader": ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
}

READY_JS = """(async (ms) => {
  const until = performance.now() + ms, grace = performance.now() + 5000;
  while (!window.dataMap) {
    if (performance.now() > grace) throw new Error('window.dataMap was not defined 5 s after the load event');
    await new Promise(r => setTimeout(r, 50));
  }
  const late = new Promise((_, no) => setTimeout(() => no(new Error(`dataMap.ready did not resolve within ${ms / 1000} s`)), until - performance.now()));
  await Promise.race([window.dataMap.ready, late]);
  await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  return true;
})(%d)"""

PROBE_JS = """(() => {
  const gl = document.createElement('canvas').getContext('webgl2');
  const info = gl && gl.getExtension('WEBGL_debug_renderer_info');
  const candidates = [...document.querySelectorAll('canvas, svg, #map, .maplibregl-map, .leaflet-container, .mapboxgl-map')]
    .map(e => e.getBoundingClientRect()).filter(r => r.width > 0 && r.height > 0)
    .map(r => [Math.max(r.left, 0), Math.max(r.top, 0), Math.min(r.right, innerWidth) - Math.max(r.left, 0), Math.min(r.bottom, innerHeight) - Math.max(r.top, 0)]);
  const area = candidates.sort((a, b) => b[2] * b[3] - a[2] * a[3])[0] || [0, 0, innerWidth, innerHeight];
  return {renderer: gl ? gl.getParameter(info ? info.UNMASKED_RENDERER_WEBGL : gl.RENDERER) : null,
          w: innerWidth, h: innerHeight, dpr: devicePixelRatio, area,
          hook: typeof window.dataMap === 'object' && window.dataMap !== null};
})()"""

# Every host name fails to resolve, so nothing loads from the network; file:// and data: URLs still work.
NO_NETWORK = "--host-resolver-rules=MAP * ~NOTFOUND , EXCLUDE 127.0.0.1"

HOOK_JS = "typeof window.dataMap === 'object' && window.dataMap !== null"

REPORT_JS = "(async () => typeof window.dataMap?.report === 'function' ? {value: await window.dataMap.report()} : null)()"

# Failures that mean the machine has no route to the internet, not that the page asked for a bad URL.
OFFLINE = re.compile(r"ERR_(INTERNET_DISCONNECTED|NAME_NOT_RESOLVED|NAME_RESOLUTION_FAILED|ADDRESS_UNREACHABLE|NETWORK_ACCESS_DENIED"
                     r"|PROXY_CONNECTION_FAILED|TUNNEL_CONNECTION_FAILED|CONNECTION_(REFUSED|TIMED_OUT|RESET|CLOSED|FAILED)|TIMED_OUT)")


def find_browser() -> str | None:
    if env := os.environ.get("DM_BROWSER"):
        return env if Path(env).exists() else shutil.which(env)
    for base in (Path("/Applications"), Path.home() / "Applications"):
        for app in ("Google Chrome", "Chromium", "Microsoft Edge", "Brave Browser"):
            exe = base / f"{app}.app" / "Contents" / "MacOS" / app
            if exe.exists():
                return str(exe)
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "brave-browser"):
        if found := shutil.which(name):
            return found
    names = {"Chromium", "Google Chrome for Testing", "chrome", "chrome-headless-shell", "headless_shell"}
    for cache in (Path.home() / "Library/Caches/ms-playwright", Path.home() / ".cache/ms-playwright"):
        dirs = sorted(cache.glob("chromium*"), key=lambda d: ("headless" not in d.name, -int(re.sub(r"\D", "", d.name) or 0)))
        for d in dirs:
            for exe in sorted(d.rglob("*")):
                if exe.name in names and exe.is_file() and os.access(exe, os.X_OK):
                    return str(exe)
    return None


class RangeHandler(SimpleHTTPRequestHandler):
    """Static files, plus single-range requests answered with 206 and Content-Range."""

    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".pmtiles": "application/octet-stream",
                      ".mjs": "text/javascript", ".geojson": "application/geo+json"}

    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_head(self):
        spec = self.headers.get("Range")
        path = self.translate_path(self.path)
        if not spec or os.path.isdir(path):
            return super().send_head()
        try:
            f = open(path, "rb")
        except OSError:
            self.send_error(404)
            return None
        with f:
            size = os.fstat(f.fileno()).st_size
            m = re.fullmatch(r"bytes=(\d*)-(\d*)", spec.strip())
            if m and m[1]:
                start, end = int(m[1]), min(int(m[2]) if m[2] else size - 1, size - 1)
            elif m and m[2]:
                start, end = max(size - int(m[2]), 0), size - 1
            else:
                start, end = size, 0
            if start > end:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return None
            f.seek(start)
            body = f.read(end - start + 1)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        return BytesIO(body)

    def log_message(self, *args):
        pass


class CdpError(Exception):
    pass


class Chrome:
    """One headless Chrome spoken to over --remote-debugging-pipe. Chrome reads requests on
    fd 3 and writes replies and events on fd 4, each a JSON object ending in a NUL byte."""

    def __init__(self, browser: str, flags: list[str], size: tuple[int, int]):
        self.profile = tempfile.TemporaryDirectory(prefix="dm-chrome-")
        self.log = open(Path(self.profile.name) / "stderr.log", "w+b")
        to_chrome, self.tx = self._high(os.pipe())
        self.rx, from_chrome = self._high(os.pipe())
        cmd = [browser, "--headless=new", "--remote-debugging-pipe", f"--user-data-dir={self.profile.name}",
               "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--hide-scrollbars",
               "--mute-audio", f"--window-size={size[0]},{size[1]}", *flags, *os.environ.get("DM_CHROME_FLAGS", "").split(), "about:blank"]
        if os.environ.get("CI") or os.geteuid() == 0:
            cmd.insert(1, "--no-sandbox")

        def onto_3_and_4():
            os.dup2(to_chrome, 3)
            os.dup2(from_chrome, 4)

        # The child's ends must sit at fds 3 and 4 exactly, and Popen keeps fds only at their
        # own numbers, so they are moved there after fork; pass_fds keeps the copies open.
        self.proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=self.log, stderr=self.log,
                                     pass_fds=(3, 4), preexec_fn=onto_3_and_4)
        os.close(to_chrome)
        os.close(from_chrome)
        self.inbox: queue.Queue = queue.Queue()
        self.events: list[dict] = []
        self.next_id = 0
        threading.Thread(target=self._read, daemon=True).start()

    @staticmethod
    def _high(fds: tuple[int, int]) -> tuple[int, int]:
        moved = tuple(fcntl.fcntl(fd, fcntl.F_DUPFD_CLOEXEC, 10) for fd in fds)
        for fd in fds:
            os.close(fd)
        return moved

    def _read(self):
        buf = b""
        while chunk := os.read(self.rx, 1 << 20):
            *msgs, buf = (buf + chunk).split(b"\0")
            for m in msgs:
                self.inbox.put(json.loads(m))
        self.inbox.put(None)

    def post(self, method: str, params: dict | None = None, session: str | None = None) -> int:
        self.next_id += 1
        msg = {"id": self.next_id, "method": method, "params": params or {}}
        if session:
            msg["sessionId"] = session
        data = memoryview(json.dumps(msg).encode() + b"\0")
        while data:
            data = data[os.write(self.tx, data):]
        return self.next_id

    def call(self, method: str, params: dict | None = None, session: str | None = None, timeout: float = 30) -> dict:
        want = self.post(method, params, session)
        deadline = time.monotonic() + timeout
        while True:
            m = self._next(deadline, method)
            if m.get("id") == want:
                if "error" in m:
                    raise CdpError(f"{method}: {m['error'].get('message')}")
                return m["result"]

    def wait_for(self, event: str, session: str, timeout: float) -> dict:
        deadline = time.monotonic() + timeout
        while True:
            m = self._next(deadline, event)
            if m.get("method") == event and m.get("sessionId") == session:
                return m["params"]

    def _next(self, deadline: float, waiting_on: str) -> dict:
        m = self._take(max(deadline - time.monotonic(), 0))
        if m is None:
            raise CdpError(f"{waiting_on}: no answer from Chrome in time")
        return m

    def _take(self, timeout: float) -> dict | None:
        try:
            m = self.inbox.get(timeout=timeout)
        except queue.Empty:
            return None
        if m is None:
            raise CdpError(f"Chrome exited ({self.stderr_tail()})")
        if "method" in m:
            self.events.append(m)
            if m["method"] == "Target.attachedToTarget":
                # Web workers report their own console, exceptions and fetches; MapLibre tiles and
                # reprojects GeoJSON in them.
                child = m["params"]["sessionId"]
                for domain in ("Runtime.enable", "Network.enable"):
                    self.post(domain, session=child)
        return m

    def settle(self, quiet: float, extra: float, deadline: float) -> None:
        """For a page with no readiness hook: wait until no request has been in flight for QUIET
        seconds, then EXTRA seconds more for drawing, never past DEADLINE."""
        inflight: set = set()
        last = time.monotonic()

        def track(m: dict) -> bool:
            key = (m.get("sessionId"), m.get("params", {}).get("requestId"))
            if m.get("method") == "Network.requestWillBeSent":
                # Worker scripts from blob: URLs, and data: URLs, never report that they finished.
                if not m["params"]["request"]["url"].startswith(("blob:", "data:")):
                    inflight.add(key)
                return True
            if m.get("method") in ("Network.loadingFinished", "Network.loadingFailed"):
                inflight.discard(key)
                return True
            return False

        for m in self.events:
            track(m)
        while (now := time.monotonic()) < deadline and (inflight or now - last < quiet):
            m = self._take(min(0.1, deadline - now))
            if m is not None and track(m):
                last = time.monotonic()
        end = min(time.monotonic() + extra, deadline)
        while (now := time.monotonic()) < end:
            self._take(end - now)

    def stderr_tail(self) -> str:
        self.log.seek(0)
        lines = self.log.read().decode(errors="replace").strip().splitlines()
        return " | ".join(lines[-3:]) or "no stderr"

    def close(self):
        try:
            self.post("Browser.close")
            self.proc.wait(5)
        except (OSError, subprocess.TimeoutExpired):
            self.proc.kill()
            self.proc.wait()
        for fd in (self.tx, self.rx):
            try:
                os.close(fd)
            except OSError:
                pass
        self.log.close()
        self.profile.cleanup()


def capture(browser: str, folder: Path, page: str, out: Path, w: int, h: int, scale: float, timeout: float,
            flags: list[str], url: str | None = None, phone: bool = False, actions: list | None = None) -> dict:
    """Serve FOLDER, open PAGE in it at WxH and device scale SCALE, wait on window.dataMap.ready (or, on a
    page without that hook, for the network to go quiet and the page to settle), and write the
    screenshot to OUT. `launch_error` means Chrome never answered, which is the machine's problem,
    not the page's. With URL, open that instead of serving FOLDER, as a reader opening the file does.
    PHONE lays the page out as a phone with a touch screen does. ACTIONS, each (method, params, seconds),
    are DevTools calls such as Input.dispatchTouchEvent, made once the page is ready and each followed by
    that many seconds for the page to answer, before the report and the screenshot."""
    run = {"png": str(out), "viewport": [w, h, scale], "flags": flags, "seconds": {}}
    t0 = time.monotonic()
    try:
        chrome = Chrome(browser, flags, (w, h))
    except OSError as e:
        run["launch_error"] = str(e)
        return run
    server = None
    if url is None:
        server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(RangeHandler, directory=str(folder)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f"http://127.0.0.1:{server.server_address[1]}/{page}"
    run["url"] = url
    s = None
    try:
        try:
            run["chrome"] = chrome.call("Browser.getVersion", timeout=20)["product"]
        except (CdpError, OSError) as e:
            run["launch_error"] = f"{e} ({chrome.stderr_tail()})"
            raise CdpError(run["launch_error"]) from None
        target = chrome.call("Target.createTarget", {"url": "about:blank"})["targetId"]
        s = chrome.call("Target.attachToTarget", {"targetId": target, "flatten": True})["sessionId"]
        for domain in ("Page.enable", "Runtime.enable", "Network.enable"):
            chrome.call(domain, session=s)
        chrome.call("Target.setAutoAttach", {"autoAttach": True, "waitForDebuggerOnStart": False, "flatten": True}, s)
        chrome.call("Emulation.setDeviceMetricsOverride", {"width": w, "height": h, "deviceScaleFactor": scale, "mobile": phone}, s)
        if phone:
            chrome.call("Emulation.setTouchEmulationEnabled", {"enabled": True, "maxTouchPoints": 5}, s)
        run["seconds"]["launch"] = round(time.monotonic() - t0, 2)
        nav = chrome.call("Page.navigate", {"url": run["url"]}, s)
        if nav.get("errorText"):
            raise CdpError(f"navigation failed: {nav['errorText']}")
        started = time.monotonic()
        chrome.wait_for("Page.loadEventFired", s, timeout)
        run["hook"] = bool(value(chrome.call("Runtime.evaluate", {"expression": HOOK_JS, "returnByValue": True}, s)))
        if run["hook"]:
            ready = chrome.call("Runtime.evaluate", {"expression": READY_JS % int(timeout * 1000), "awaitPromise": True,
                                                     "returnByValue": True}, s, timeout + 10)
            if exc := ready.get("exceptionDetails"):
                run["ready_error"] = thrown(exc)
        else:
            chrome.settle(quiet=2.0, extra=3.0, deadline=started + min(timeout, 30.0))
        run["seconds"]["ready"] = round(time.monotonic() - started, 2)
        for method, params, pause in actions or []:
            chrome.call(method, params, s)
            chrome.settle(quiet=0, extra=pause, deadline=time.monotonic() + pause)
        run["probe"] = value(chrome.call("Runtime.evaluate", {"expression": PROBE_JS, "returnByValue": True}, s))
        if run["hook"]:
            report = chrome.call("Runtime.evaluate", {"expression": REPORT_JS, "awaitPromise": True, "returnByValue": True}, s)
            if exc := report.get("exceptionDetails"):
                run["report_error"] = thrown(exc)
            else:
                run["report"] = (value(report) or {}).get("value")
        shot = chrome.call("Page.captureScreenshot", {"format": "png"}, s, timeout)
        out.write_bytes(base64.b64decode(shot["data"]))
    except (CdpError, OSError) as e:
        run.setdefault("error", f"Chrome stopped answering: {e}" if isinstance(e, OSError) else str(e))
    finally:
        events = chrome.events
        chrome.close()
        if server:
            server.shutdown()
            server.server_close()
    run["problems"] = problems(events, s)
    run["seconds"]["total"] = round(time.monotonic() - t0, 2)
    return run


def value(result: dict):
    return result.get("result", {}).get("value")


def describe(obj: dict) -> str:
    """One line for a CDP RemoteObject: a primitive's value, or an error's message, which a
    minified error class leaves out of its description."""
    if "value" in obj:
        return str(obj["value"])
    props = {p["name"]: p.get("value") for p in obj.get("preview", {}).get("properties", [])}
    text = props.get("message") or obj.get("description") or obj.get("type", "")
    return text.splitlines()[0] if text else ""


def thrown(details: dict) -> str:
    return describe(details["exception"]) if "exception" in details else details.get("text", "")


def problems(events: list[dict], page: str | None) -> list[dict]:
    """Console errors and warnings, uncaught exceptions, and failed requests, each once. A failed
    request to another host that never got an answer is marked offline."""
    urls, out = {}, []
    for e in events:
        p, kind = e["params"], e["method"]
        where = "" if e.get("sessionId") == page else "(worker) "
        if kind == "Network.requestWillBeSent":
            urls[p["requestId"]] = p["request"]["url"]
        elif kind == "Runtime.consoleAPICalled" and p["type"] in ("error", "assert", "warning"):
            text = " ".join(describe(a) for a in p["args"])
            out.append({"kind": "console", "level": "warning" if p["type"] == "warning" else "error", "message": where + text})
        elif kind == "Runtime.exceptionThrown":
            out.append({"kind": "exception", "level": "error", "message": where + thrown(p["exceptionDetails"])})
        elif kind == "Network.responseReceived" and p["response"]["status"] >= 400 and not p["response"]["url"].endswith("/favicon.ico"):
            out.append({"kind": "network", "level": "error", "message": f"{p['response']['status']} {p['response']['url']}"})
        elif kind == "Network.loadingFailed" and not p.get("canceled"):
            url = urls.get(p["requestId"], p["requestId"])
            host = urlparse(url).hostname or ""
            offline = bool(OFFLINE.search(p["errorText"])) and host not in ("127.0.0.1", "localhost")
            out.append({"kind": "network", "level": "error", "message": f"{p['errorText']} {url}", "offline": offline})
    seen, unique = set(), []
    for f in out:
        if (key := (f["kind"], f["message"])) not in seen:
            seen.add(key)
            unique.append(f)
    return unique
