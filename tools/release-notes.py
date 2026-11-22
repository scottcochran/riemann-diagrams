#!/usr/bin/env python3
"""Write the notes of a release from the tag, the pins and the manifests.

    python3 tools/release-notes.py TAG pins.json diagrams/manifest.json diagrams/map/manifest.json > notes.md

The notes carry what a reader needs to check a citation of a poster (PLAN.md, Phase 5): the tag message, which
opens with the kind of move; the three pins, with links to the commits they resolve to; one row per poster with
its card and arrow counts, so that what moved between releases can be read without opening the SVGs; and the
workflow run that regenerated and checked the posters at the tag. Standard library only.
"""
import json
import subprocess
import sys


def main(tag, pins_path, *manifests):
    pins = json.load(open(pins_path, encoding="utf-8"))
    message = subprocess.run(["git", "tag", "-l", "--format=%(contents)", tag], capture_output=True,
                             text=True, check=True).stdout.strip()
    out = [message, ""]
    out.append("## The sources")
    out.append("")
    out.append("| Pin | Value | Commit |")
    out.append("|---|---|---|")
    bp = pins["blueprint"]
    mi = pins["mirror"]
    out.append(f"| The blueprint (`BP_COMMIT`) | `{bp['pin']}` | [{bp['commit'][:10]}]({bp['url']}) |")
    out.append(f"| The mirror the blueprint pins (`MIRROR_PIN`) | `{pins['mirror_pin']}` | the blueprint's `lakefile.toml` |")
    out.append(f"| The mirror `Main.lean` is read from (`MIRROR_COMMIT`) | `{mi['pin']}` | [{mi['commit'][:10]}]({mi['url']}) |")
    out.append(f"| riemann-diagrams | `{tag}` | [{pins['generator']['commit'][:10]}]({pins['generator']['url']}) |")
    out.append("")
    out.append(f"Regenerated with Python {pins['python']}; the generator uses the standard library only.")
    out.append("")
    for path in manifests:
        m = json.load(open(path, encoding="utf-8"))
        kind = "The map set (nothing quoted)" if "/map/" in path else "The reader set"
        out.append(f"## {kind}")
        out.append("")
        out.append("| Id | Poster | Cards | Arrows | File |")
        out.append("|---|---|---:|---:|---|")
        for k, v in m.items():
            title = v["title"].replace("|", "\\|")
            out.append(f"| {k} | {title} | {v['cards']} | {v['arrows']} | `{v['file']}` |")
        out.append("")
    out.append("## Checking a citation")
    out.append("")
    out.append("`SHA256SUMS` covers every asset. A poster's state line, at its foot, names the same pins as the table "
               "above. The posters are SVG only: every browser renders them, and a render to PNG at a legible width "
               "runs to many megabytes a poster, so none is shipped.")
    out.append("")
    out.append(f"The posters were regenerated from the pinned sources and compared byte for byte with the tagged "
               f"commit in workflow run [{pins['run']['id']}]({pins['run']['url']}), which passed before this release "
               "was created.")
    out.append("")
    out.append("No licence has been granted for the text the reader posters quote; see `NOTICE`. The reader set is "
               "for readers of this repository, and the map set is the form that may be passed on.")
    print("\n".join(out))


if __name__ == "__main__":
    main(*sys.argv[1:])
