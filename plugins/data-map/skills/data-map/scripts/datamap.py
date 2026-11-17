#!/usr/bin/env python3
"""data-map: the levers that do a map's arithmetic, and the page and check commands."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dm import VERSION, commands  # noqa: E402

MODULES = [commands]
for name in ("page", "check"):
    try:
        MODULES.append(__import__(f"dm.{name}", fromlist=["register"]))
    except ImportError:
        pass


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(prog="datamap.py", description=__doc__)
    parser.add_argument("--version", action="version", version=f"data-map {VERSION}")
    sub = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")
    for module in MODULES:
        module.register(sub)
    args = parser.parse_args(argv)
    try:
        return args.run(args)
    except commands.InputError as err:
        print(f"datamap.py {args.command}: {err}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
