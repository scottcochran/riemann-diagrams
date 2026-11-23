"""F9 — Where the formal work is: the declarations under each statement's Lean, and their size.

Reads src/lean-weight.json (bp.read_weight), written from Sutherland's export of the proof: for each statement, the
Lean declarations it names and the helper declarations that only its Lean reaches, each counted and sized by the
number of distinct expression nodes in their terms; and one statement, R3's chapter theorem, opened to its
helpers by namespace, with the statement that has the most. Laid out by chapter, by provenance, the heaviest statements against the length of their
proofs in the blueprint, and the opened statement. The build fails if the totals or the heaviest statements
differ from what is recorded here."""
import collections

import bp
from bp import PROV_ACCENT, PROV_SHORT, paragraphs
from chapter import band
from lib import Canvas

ID, SLUG = "F9", "weight"

W = 3400
G = 64
S = 13.5
SHORT = {
    "main-theorems": "Main theorems", "architecture": "Outline", "chap-zero-free": "Zero-free",
    "chap-families": "Families", "chap-theta": "Theta", "chap-heights": "Heights", "chap-sha": "Sha",
    "chap-galois": "Galois", "chap-literature": "Literature",
}
# The statements opened to their helpers, each with why: R3's chapter theorem, as the plan named it, and the
# statement with the most formal work of its own.
OPENED = [("thm-zero-free-from-connected", "R3's chapter theorem"),
          ("thm-family-membership-admissible-data", "the most formal work of its own")]
# The file's totals, as recorded when this poster was written.
TOTALS = {"declarations": 1484733, "project": 1269850, "named": 1229, "helpers": 1268621, "helpers_by_reach": {"none": 4928, "one": 502612, "two": 179332, "more": 581749}, "size_project": 2503334210, "size_unreached": 5886290}
# The three statements with the largest helpers only they reach, by size.
HEAVIEST = ["thm-family-membership-admissible-data", "thm-sha-bound", "thm-good-towers-from-arakelov-inputs"]
TOP_N = 16


def fmt(n):
    return f"{n:,}"


def build():
    g = bp.load()
    mirror = bp.read_mirror()
    wt = bp.read_weight(g)
    t, st = wt["totals"], wt["statements"]
    if t != TOTALS:
        raise ValueError(f"F9: the totals are {t}, written for {TOTALS}")
    heavy = sorted(st, key=lambda k: (-st[k]["helpers_size"], k))
    if heavy[:3] != HEAVIEST:
        raise ValueError(f"F9: the heaviest statements are {heavy[:3]}, written for {HEAVIEST}")
    if sorted(wt["opened"]) != sorted(o for o, _ in OPENED):
        raise ValueError(f"F9: lean-weight.json opens {sorted(wt['opened'])}, written for {OPENED}")
    if OPENED[1][0] != heavy[0]:
        raise ValueError(f"F9: the statement with the most formal work is {heavy[0]}, not {OPENED[1][0]}")

    def chap(k):
        return g.nodes[k]["_chapter"]

    def prov(k):
        return g.nodes[k].get("provenance")

    excl_size = sum(v["helpers_size"] for v in st.values())
    own_size = sum(v["own_size"] for v in st.values())
    br = t["helpers_by_reach"]

    c = Canvas(ID, "Where the formal work is: the declarations under each statement's Lean, and their size",
               "Each statement of the blueprint names a few Lean declarations, but its proof in Lean rests on many "
               "more: helper lemmas, auxiliary definitions, the pieces the compiler splits a proof into. This "
               f"poster counts them. The published proof holds {fmt(t['project'])} declarations of the project "
               f"itself, beside the library's; {fmt(t['named'])} are named by statements, and the other "
               f"{fmt(t['helpers'])} are helpers. A helper that only one statement's Lean reaches, before reaching "
               "another statement's, is that statement's own work; the rest are shared. **Size** is the number of "
               "distinct expression nodes in a declaration's terms, its proof included: a measure of how much the "
               "compiler wrote, not of difficulty. Everything here is read from Andrew Sutherland's export of the "
               "proof; `diagrams/EDGES.md` gives the method. **No Lean was built**: see diagram R1, band 5."
               + (" **Map mode**: this poster quotes nothing in either form." if bp.MAP else ""),
               W, f"`riemann-blueprint` at {g.bp_commit} (every statement's chapter, provenance, `lean` list and "
               "proof, for its paragraph count); `diagrams/src/lean-weight.json`, read from Sutherland's export of "
               f"the proof at {g.mirror_pin} (sha256 {wt['proof']['export_sha256'][:12]}…), with the project's "
               f"declarations told from the library's by the cache run at {wt['project_names']['mirror'][:10]}; "
               f"`leanprover-community/riemann-hypothesis` at {mirror['commit']} (`src/Main.lean`). Every count is "
               "the diagram's own.",
               state=f"State drawn: riemann-blueprint at {g.bp_commit}, which pins the mirror at {g.mirror_pin}; "
                     f"Main.lean from the mirror at {mirror['commit']}")
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    CW = (WW - 4 * G) / 5

    def colx(i):
        return X0 + i * (CW + G)

    def span(n):
        return n * CW + (n - 1) * G

    # ---------------------------------------------------------------------------------- reading the poster
    y = c.y
    y = band(c, X0, y, "1 · Reading the poster")
    key = [
        "**Own declarations** are those a statement's `lean` list names. **Own helpers** are the project's "
        "declarations its Lean reaches, through declarations no statement names, that no other statement's Lean "
        "reaches: the formal work under that statement alone. A helper two or more statements reach is "
        "**shared**, and counted under none of them.",
        "**The project's declarations** are told from the library's (Mathlib, core) by name: those the build "
        "cache of the mirror at a later commit compiles as the project's, and others under the same "
        "namespaces. A project lemma the later tree dropped from a library namespace is counted as the "
        "library's.",
        "**Size** counts the distinct expression nodes in a declaration's type and value. Two declarations that "
        "share a subterm each count it. It measures the terms the compiler wrote, which a tactic proof can make "
        "large for a short argument.",
    ]
    nums = [
        f"**{fmt(t['project'])} project declarations** of the {fmt(t['declarations'])} in the export: "
        f"{fmt(t['named'])} named by statements, {fmt(t['helpers'])} helpers.",
        f"**Helpers by how many statements reach them**: {fmt(br['one'])} by one, {fmt(br['two'])} by two, "
        f"{fmt(br['more'])} by three or more, {fmt(br['none'])} by none.",
        f"**Size**: {fmt(t['size_project'])} nodes in all; {fmt(own_size)} in the named declarations, "
        f"{fmt(excl_size)} in helpers only one statement reaches.",
    ]
    hk = max(c.card(0, 0, span(3), "How to read the poster", key, draw=False, size=S),
             c.card(0, 0, span(2), "The formal work in numbers", nums, draw=False, size=S))
    c.card(colx(0), y, span(3), "How to read the poster", key, "grey", h=hk, size=S, tint=False)
    c.card(colx(3), y, span(2), "The formal work in numbers", nums, "teal", h=hk, size=S, tint=False)
    y += hk + 50

    # ---------------------------------------------------------------------------------- by chapter, by provenance
    y = band(c, X0, y, "2 · By chapter, and by provenance",
             "Left: each chapter's statements, their own declarations and the helpers only they reach, with "
             "the chapter's share of all such helpers by size. Right: the same by the blueprint's provenance: "
             "new in Alpöge's proof, modified from the literature, or published.")
    chapters = sorted(g.chapters, key=lambda ch: (g.nodes[ch].get("order", 0), ch))
    agg = collections.defaultdict(collections.Counter)
    for k, v in st.items():
        a = agg[chap(k)]
        a["n"] += 1
        for f in ("own", "own_size", "helpers", "helpers_size"):
            a[f] += v[f]
    lw = WW * 0.58
    ccols = [("Chapter", 220), ("Statements", 140), ("Own decls", 140), ("Own size", 170), ("Own helpers", 160),
             ("Helpers' size", 190), ("Share", lw - 220 - 140 - 140 - 170 - 160 - 190)]
    crows = [[f"**{SHORT[ch]}**", str(agg[ch]["n"]), fmt(agg[ch]["own"]), fmt(agg[ch]["own_size"]),
              fmt(agg[ch]["helpers"]), fmt(agg[ch]["helpers_size"]),
              f"{agg[ch]['helpers_size'] * 100 // excl_size}%"] for ch in chapters]
    crows.append(["**All**", str(len(st)), fmt(sum(a["own"] for a in agg.values())), fmt(own_size),
                  fmt(sum(a["helpers"] for a in agg.values())), fmt(excl_size), "100%"])
    ch_h = c.table(X0, y, ccols, crows, size=S)
    pagg = collections.defaultdict(collections.Counter)
    for k, v in st.items():
        a = pagg[prov(k)]
        a["n"] += 1
        a["helpers"] += v["helpers"]
        a["helpers_size"] += v["helpers_size"]
    px = X0 + lw + G
    pw = X1 - px
    pcols = [("Provenance", 200), ("Statements", 140), ("Own helpers", 160), ("Helpers' size", 190),
             ("Share", pw - 200 - 140 - 160 - 190)]
    prows = [{"cells": [PROV_SHORT[p], str(pagg[p]["n"]), fmt(pagg[p]["helpers"]), fmt(pagg[p]["helpers_size"]),
                        f"{pagg[p]['helpers_size'] * 100 // excl_size}%"], "accent": PROV_ACCENT[p]}
             for p in ("new", "modified", "published", None) if pagg[p]["n"]]
    ph = c.table(px, y, pcols, prows, size=S)
    y += max(ch_h, ph) + 50

    # ---------------------------------------------------------------------------------- the heaviest statements
    y = band(c, X0, y, "3 · The statements with the most formal work of their own",
             f"The {TOP_N} statements whose own helpers are largest, with the length of their proofs in the "
             "blueprint in paragraphs. A statement with much formal work and a short blueprint proof is one "
             "where the prose summarises a great deal.")
    hrows = []
    for k in heavy[:TOP_N]:
        v = st[k]
        pf = bp.proof(g, k)
        npar = len(paragraphs(pf)) if pf else 0
        hrows.append({"cells": [k, SHORT[chap(k)], PROV_SHORT[prov(k)], str(v["own"]), fmt(v["helpers"]),
                                fmt(v["helpers_size"]), fmt(v["shared"]), str(npar) if pf else "no proof"],
                      "accent": PROV_ACCENT[prov(k)]})
    hcols = [("Statement", 560, {"mono": True}), ("Chapter", 180), ("Provenance", 170), ("Own decls", 140),
             ("Own helpers", 170), ("Helpers' size", 200), ("Shared helpers", 200),
             ("Blueprint proof, paragraphs", WW - 560 - 180 - 170 - 140 - 170 - 200 - 200)]
    y += c.table(X0, y, hcols, hrows, size=S) + 50

    # ---------------------------------------------------------------------------------- statements opened
    for i, (o, why) in enumerate(OPENED):
        op, v = wt["opened"][o], st[o]
        y = band(c, X0, y, f"{4 + i} · One statement opened: {o}, {why}",
                 f"Its {v['own']} own declaration{'s' if v['own'] != 1 else ''} and the {fmt(v['helpers'])} helper"
                 f"{'s' if v['helpers'] != 1 else ''} only its Lean reaches, {fmt(v['helpers_size'])} nodes in "
                 f"all; it shares {fmt(v['shared'])} more helpers with other statements. Left: its own helpers by "
                 "namespace. Right: its own declarations and its largest helpers.")
        nsrows = sorted(op["namespaces"].items(), key=lambda t_: (-t_[1]["size"], t_[0]))
        nw = WW * 0.5
        ncols = [("Namespace", nw - 160 - 180, {"mono": True}), ("Helpers", 160), ("Size", 180)]
        nh = c.table(X0, y, ncols, [[k, fmt(x["helpers"]), fmt(x["size"])] for k, x in nsrows[:TOP_N]]
                     + ([[f"… and {len(nsrows) - TOP_N} more namespaces",
                          fmt(sum(x["helpers"] for _, x in nsrows[TOP_N:])),
                          fmt(sum(x["size"] for _, x in nsrows[TOP_N:]))]] if len(nsrows) > TOP_N else []), size=S)
        rx = X0 + nw + G
        rw = X1 - rx
        lrows = [{"cells": [d["name"], "own", fmt(d["size"])], "accent": "green"} for d in op["own"]]
        lrows += [[d["name"], "helper", fmt(d["size"])] for d in op["largest"]]
        lh = c.table(rx, y, [("Declaration", rw - 140 - 180, {"mono": True}), ("Kind", 140), ("Size", 180)], lrows,
                     size=S)
        y += max(nh, lh) + 50
    return c
