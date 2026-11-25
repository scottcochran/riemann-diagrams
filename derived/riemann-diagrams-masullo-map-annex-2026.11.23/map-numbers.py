#!/usr/bin/env python3
"""Print the numbers the write-up cites from the RiemannMasullo progress map.

    python3 -I map-numbers.py PAGE.html

PAGE.html is the map's page as fetched (it is not kept here: it is 4.8 MB and another project's work). The page
holds its whole data model as one JSON object, `const DATA = {...}`, written by that project's
`scripts/progress/build.py`; this script reads that object and nothing else. Standard library only.
"""
import collections
import hashlib
import json
import sys

raw = open(sys.argv[1], "rb").read()
page = raw.decode("utf-8", errors="replace")
D, _ = json.JSONDecoder().raw_decode(page, page.index("const DATA = ") + len("const DATA = "))
groups, decls, errata = D["groups"], D["decls"], D["errata"]
KIND, STATE, FLAGS, STMT, PROOF = 1, 2, 10, 12, 13      # columns of a declaration row, as template.html names them

print("page sha256 ", hashlib.sha256(raw).hexdigest())
print("generated   ", D["meta"]["generated"])
print("commit      ", D["meta"]["commit"])
print("totals      ", json.dumps(D["totals"]))
print("sections    ", dict(collections.Counter(g["state"] for g in groups)))
print("needs edges ", sum(len(g["needs"]) for g in groups))
print("paper items ", sum(len(g["items"]) for g in groups))
print("declarations", len(decls), dict(collections.Counter(d[KIND] + ":" + d[STATE] for d in decls)))
print("edges       ", sum(len(d[STMT]) for d in decls), "in statements,", sum(len(d[PROOF]) for d in decls), "in proofs only")
printed = [d for d in decls if d[0].startswith("Printed.")]
print("Printed.*   ", len(printed), "declarations,", sum(d[KIND] == "t" for d in printed), "of them theorems")
print("history     ", len(D["history"]), "runs,", D["history"][0]["time"], "to", D["history"][-1]["time"])
print("merged      ", len(D["merged"]), "pull requests by", len({m[0] for m in D["merged"]}), "accounts other than the owner")

entries, gaps = errata["entries"], errata["gaps"]
print("\nerrata      ", len(entries), dict(collections.Counter(e[1] for e in entries)))
print("by check    ", dict(collections.Counter(e[1] + ":" + e[2] for e in entries)))
print("no repair   ", len(gaps), "rows naming", sum(e[8] for e in entries), "entries")
print("linked      ", sum(bool(e[7]) for e in entries), "entries name a Printed.* declaration the map found")

chapter_of = lambda i: groups[i]["chapter"] if i >= 0 else "-"
by_kind = collections.Counter((chapter_of(e[6]), e[1]) for e in entries)
by_gap = collections.Counter(chapter_of(g["group"]) for g in gaps)
print("\nchapter      sections  defs  thms proved  solid |   F    I    M    R | no repair")
keys = [(c["key"], c["label"]) for c in D["chapters"]] + [(None, "support"), ("-", "unplaced")]
for key, label in keys:
    gs = [g for g in groups if g["chapter"] == key]
    col = lambda f: sum(g[f] for g in gs)
    print(f"{label:12s} {len(gs):8d} {col('defs'):5d} {col('thms'):5d} {col('proved'):6d} {col('solid'):6d} | "
          + " ".join(f"{by_kind[(key, k)]:4d}" for k in "FIMR") + f" | {by_gap[key]:4d}")

print("\nsupport groups:")
for g in groups:
    if g["chapter"] is None:
        print(f"  {g['num']}: {g['title']}, {g['thms']} theorems")

print("\nwhere no repair is known:")
for g in gaps:
    print(f"  {chapter_of(g['group']):5s} {' '.join(g['ids']):45s} {g['item']}")

print("\nnotes the generator printed:")
for n in D["notes"]:
    print("  -", n)
