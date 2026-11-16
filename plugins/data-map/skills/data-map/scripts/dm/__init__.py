"""data-map's levers, pages, and check."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass

VERSION = "0.1.0"


@dataclass(frozen=True)
class Finding:
    status: str
    check: str
    message: str
    fix: str = ""
    pitfall: int | None = None

    def line(self) -> str:
        cite = f" [P{self.pitfall}]" if self.pitfall else ""
        fix = f" Fix: {_stop(self.fix)}" if self.fix else ""
        return f"{self.status} {self.check}{cite}: {_stop(self.message)}{fix}"


def _stop(text: str) -> str:
    return text if text.endswith((".", "?", "!")) else text + "."


def PASS(check: str, message: str, pitfall: int | None = None) -> Finding:
    return Finding("PASS", check, message, "", pitfall)


def WARN(check: str, message: str, fix: str, pitfall: int | None = None) -> Finding:
    return Finding("WARN", check, message, fix, pitfall)


def FAIL(check: str, message: str, fix: str, pitfall: int | None = None) -> Finding:
    return Finding("FAIL", check, message, fix, pitfall)


def report(findings: list, as_json: bool = False, extra: dict | None = None) -> int:
    """Prints the findings as lines, or as one JSON object, and returns the exit code."""
    ok = not any(f.status == "FAIL" for f in findings)
    if as_json:
        out = {"ok": ok, "findings": [asdict(f) for f in findings]}
        out.update(extra or {})
        print(json.dumps(out, indent=1, ensure_ascii=False))
    else:
        for f in findings:
            print(f.line())
    return 0 if ok else 1
