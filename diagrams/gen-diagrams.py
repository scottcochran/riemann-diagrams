#!/usr/bin/env python3
"""Generate the riemann diagrams (SVG, adaptive light/dark).

Each diagram is a module diagrams/src/d_<id>_<slug>.py exposing ID, SLUG and build() -> Canvas. It reads the
riemann-blueprint, its lean-facts.json and the mirror's Main.lean and Statements.lean at build time, and fails if
they disagree with what the diagram draws. Output: diagrams/<ID>-<slug>-<DATE>.svg. Run with no arguments for all,
or with ids (R1 R2). With --map, the map mode: nothing of the blueprint or the proof is quoted, and the output
goes to diagrams/map/. Standard library only. Use Python 3.12 or later: sum() over floats changed in 3.12, and with it
the coordinates.

    uv run python diagrams/gen-diagrams.py
"""
import importlib
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "src"))
MAP = "--map" in sys.argv
if MAP:
    os.environ["RIEMANN_MAP"] = "1"          # read by bp.py when it loads, below

import lib  # noqa: E402
from lib import DATE  # noqa: E402


def main(argv):
    if sys.version_info < (3, 12):
        sys.exit("gen-diagrams: Python 3.12 or later, so that the output is reproducible")
    want = {a.upper() for a in argv if not a.startswith("--")}
    out_dir = HERE / "map" if MAP else HERE
    out_dir.mkdir(exist_ok=True)
    manifest_path = out_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    failed = 0
    for name in sorted(p.stem for p in (HERE / "src").glob("d_*.py")):
        if want and name.split("_")[1].upper() not in want:
            continue
        lib.TEXT_BOXES.clear()          # a diagram that failed must not leave its text in the next one's check
        try:
            m = importlib.import_module(name)
            canvas = m.build()
            svg = canvas.svg()
        except Exception as e:  # report and carry on, so one broken module cannot block the rest
            print(f"ERROR {name}: {e!r}")
            failed += 1
            continue
        out = out_dir / f"{m.ID}-{m.SLUG}-{DATE}.svg"
        out.write_text(svg, encoding="utf-8")
        print(out.relative_to(HERE.parent))
        manifest[m.ID] = {"file": out.name, "title": canvas.title, **canvas.stats()}
        for w in canvas.warnings:
            print("  WARNING", w)
            failed += 1
    if not failed:
        manifest = {k: manifest[k] for k in sorted(manifest, key=lambda k: (k[0], int(k[1:])))}
        manifest_path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
