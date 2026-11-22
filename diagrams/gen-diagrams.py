#!/usr/bin/env python3
"""Generate the riemann diagrams (SVG, adaptive light/dark).

Each diagram is a module diagrams/src/d_<id>_<slug>.py exposing ID, SLUG and build() -> Canvas. It reads the
riemann-blueprint, its lean-facts.json and the mirror's Main.lean and Statements.lean at build time, and fails if
they disagree with what the diagram draws. Output: diagrams/<ID>-<slug>-<DATE>.svg. Run with no arguments for all,
or with ids (R1 R2). With --map, the map mode: nothing of the blueprint or the proof is quoted, and the output
goes to diagrams/map/ as map-<ID>-<slug>-<DATE>.svg, so that a map poster has the same name in the tree, on the
Pages site and among a release's flat assets. The set's manifest.json is the registry of the links between
posters: it lists every poster's anchors, and an id with no card on a poster links to the poster that draws it.
When a run moves a poster's anchors it updates the manifest and exits 1, asking for a second run so that the
links of every poster follow. Standard library only. Use Python 3.12 or later: sum() over floats changed in 3.12, and with it
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
    lib.load_registry(manifest)     # the links between posters resolve against the committed manifest
    before = {k: v.get("anchors") for k, v in manifest.items()}
    failed, moved = 0, []
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
        out = out_dir / f"{'map-' if MAP else ''}{m.ID}-{m.SLUG}-{DATE}.svg"
        out.write_text(svg, encoding="utf-8")
        print(out.relative_to(HERE.parent))
        manifest[m.ID] = {"file": out.name, "title": canvas.title, **canvas.stats(), "anchors": sorted(canvas.anchors),
                          "links": canvas.links, "links_out": canvas.links_out, "links_ext": canvas.links_ext}
        if sorted(canvas.anchors) != before.get(m.ID):
            moved.append(m.ID)
        for w in canvas.warnings:
            print("  WARNING", w)
            failed += 1
    if not failed:
        manifest = {k: manifest[k] for k in sorted(manifest, key=lambda k: (k[0], int(k[1:])))}
        manifest_path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        if moved:
            print(f"NOTE the anchors of {', '.join(moved)} moved: the links of every poster were resolved against the "
                  f"previous {manifest_path.relative_to(HERE.parent)}, now updated. Run again so that they follow.")
            return 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
