"""F8 — Where the proof's assumptions enter, and where they are discharged.

The five theorems of Main.lean are closed propositions, so every assumption the formal proof takes is discharged
inside it. Reads src/lean-hypotheses.json (bp.read_hypotheses), written from Sutherland's export of the proof: the
structures behind the blueprint arrows that are borne out only as hypotheses, with their fields, the statements
that take them and the declarations that build them; and, for every statement whose Lean states a `Prop`, the
theorems that conclude it. The build fails if the structures, the counts by class or the export's axioms differ
from what is recorded here, or if the axioms are not the ones the mirror's comparator.json permits."""
import collections

import bp
from bp import names
from chapter import band
from lib import Canvas

ID, SLUG = "F8", "assumptions"

W = 3400
G = 64
S = 13.5
NCOLS = 4
SHORT = {
    "main-theorems": "Main theorems", "architecture": "Outline", "chap-zero-free": "Zero-free",
    "chap-families": "Families", "chap-theta": "Theta", "chap-heights": "Heights", "chap-sha": "Sha",
    "chap-galois": "Galois", "chap-literature": "Literature",
}
# The structures, by their Lean names.
PACKAGES = [
    "GlobalTheory.HeightCounting.Up.PublishedInputsThirdLayerAlt",
    "GlobalTheory.Mem.LiteralAutomorphy.LitLocAlt",
    "GlobalTheory.Mem.LiteralAutomorphy.LiteratureAutomorphyHypothesis",
    "GlobalTheory.Mem.LiteralAutomorphy.LiteratureCMHypothesis",
    "GlobalTheory.Mem.LiteralAutomorphy.LiteratureRankNHypothesis",
    "GlobalTheory.Mem.Top.Bl.MultiplicityCoverHypotheses",
    "GlobalTheory.NRows.ThetaLocalInputsAlt",
    "GlobalTheory.PrimIn.PublishedThetaConditionTheorems",
]
# The Props by class.
CLASSES = {"outright": 275, "conditional": 6, "never": 7, "absent": 1}
WORDS = {"outright": "concluded outright", "conditional": "concluded only under assumptions",
         "never": "never concluded under this name", "absent": "not in the proof"}


def build():
    g = bp.load()
    mirror = bp.read_mirror()
    h = bp.read_hypotheses(g)
    P = h["packages"]
    if sorted(P) != sorted(PACKAGES):
        raise ValueError(f"F8: the structures are {sorted(P)}, written for {PACKAGES}")
    cls = collections.Counter(v["class"] for v in h["props"].values())
    if dict(cls) != CLASSES:
        raise ValueError(f"F8: the Props by class are {dict(cls)}, written for {CLASSES}")
    if sorted(h["axioms"]) != sorted(mirror["axioms"]):
        raise ValueError(f"F8: the export's axioms are {h['axioms']}, comparator.json permits {mirror['axioms']}")
    if any(not b["statement"] and not b["reached_from"] for v in P.values() for b in v["builders"]):
        raise ValueError("F8: a builder no statement's Lean reaches; the cards say every one is reached")

    def chap(k):
        return g.nodes[k]["_chapter"]

    n_arrows = sum(len(v) for v in h["arrows"].values())
    fields = sorted({f for v in P.values() for f in v["fields"]})
    takers = sorted({t for v in P.values() for t in v["taken_by"]})
    builders = [b for v in P.values() for b in v["builders"]]
    lit = sum(1 for f in fields if chap(f) == "chap-literature")
    props = h["props"]
    n_stmt = len({v["statement"] for v in props.values()})

    c = Canvas(ID, "Where the proof's assumptions enter, and where they are discharged",
               "The five theorems of `Main.lean` are closed propositions: they assume nothing. So every assumption "
               "the formal proof takes along the way is discharged inside it. This poster follows two kinds. "
               f"**Structures of assumptions**: {n_arrows} of the blueprint's arrows are borne out only as "
               "hypotheses, where a statement's Lean takes a structure one of whose fields states the other. "
               f"They pass through {len(P)} structures; each card gives what its fields state, which statements "
               "take it, and which build it, discharging it. **Stated claims**: "
               f"{n_stmt} statements give a `Prop` among their Lean, a claim stated to be proved or assumed; the "
               "tables give, for each, whether some theorem of the proof concludes it, outright or only under "
               "assumptions. Everything here is read from Andrew Sutherland's export of the proof, which holds "
               "exactly what the five main theorems depend on; `diagrams/EDGES.md` gives the method. **No Lean "
               "was built**: see diagram R1, band 5."
               + (" **Map mode**: this poster quotes nothing in either form." if bp.MAP else ""),
               W, f"`riemann-blueprint` at {g.bp_commit} (every statement's chapter and `lean` list; "
               "`lean-facts.json` for which declarations are `Prop` definitions); `diagrams/src/lean-hypotheses.json`, "
               f"read from Sutherland's export of the proof at {g.mirror_pin} (sha256 "
               f"{h['proof']['export_sha256'][:12]}…); `leanprover-community/riemann-hypothesis` at "
               f"{mirror['commit']} (`src/Main.lean`, `comparator.json`). Every count is the diagram's own.",
               state=f"State drawn: riemann-blueprint at {g.bp_commit}, which pins the mirror at {g.mirror_pin}; "
                     f"Main.lean from the mirror at {mirror['commit']}")
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    CW = (WW - (NCOLS - 1) * G) / NCOLS

    def colx(i):
        return X0 + i * (CW + G)

    # ---------------------------------------------------------------------------------- reading the poster
    y = c.y
    y = band(c, X0, y, "1 · Reading the poster")
    key = [
        "**A structure of assumptions** is a Lean structure whose fields are claims. A theorem that takes one "
        "as an argument assumes all its fields at once. A **builder** is a declaration whose type concludes in "
        "the structure: it supplies every field, and so discharges the assumptions. The builders here are "
        "helpers no statement names, so each card gives the statements whose Lean reaches them.",
        "**A stated claim** is a `Prop` definition among a statement's Lean declarations. It is **concluded "
        "outright** when some theorem of the proof has it as its conclusion with no premise typed by another "
        "blueprint `Prop` or a structure above; **only under assumptions** when every such theorem has one; "
        "**never under this name** when no theorem has it as its conclusion, which leaves room for one that "
        "concludes a `Prop` of another name unfolding to the same.",
        "The test reads the types of declarations, not their proofs, and recognises only the premises named "
        "above, so **outright** means no premise this test recognises.",
    ]
    nums = [
        f"**{n_arrows} arrows** borne out only as hypotheses, from {len(takers)} statements to {len(fields)}, "
        f"{lit} of them in the literature chapter, through **{len(P)} structures**.",
        f"**{len(builders)} builders**, all helpers no statement names.",
        f"**{len(props)} stated claims** of {n_stmt} statements: "
        + ", ".join(f"{cls[k]} {WORDS[k]}" for k in CLASSES) + ".",
        f"**The axioms** of everything the main theorems depend on, as the export holds it: "
        + ", ".join(f"`{a}`" for a in h["axioms"]) + ", exactly those `comparator.json` permits, and no "
        "`sorryAx`. This is read from the export, not checked by a kernel.",
    ]
    hk = max(c.card(0, 0, 2 * CW + G, "How to read the poster", key, draw=False, size=S),
             c.card(0, 0, 2 * CW + G, "The assumptions in numbers", nums, draw=False, size=S))
    c.card(colx(0), y, 2 * CW + G, "How to read the poster", key, "grey", h=hk, size=S, tint=False)
    c.card(colx(2), y, 2 * CW + G, "The assumptions in numbers", nums, "teal", h=hk, size=S, tint=False)
    y += hk + 50

    # ---------------------------------------------------------------------------------- the structures
    y = band(c, X0, y, "2 · The structures of assumptions",
             "One card per structure, by the number of claims its fields state. **Fields state**: the statements "
             "its fields are claims of. **Taken by**: the statements whose Lean takes it, so assumes them. **Built "
             "by**: the declarations that supply every field, with the statements whose Lean reaches each.")
    cards = []
    for p in sorted(P, key=lambda p: (-len(P[p]["fields"]), p)):
        v = P[p]
        fl = collections.Counter(SHORT[chap(f)] for f in v["fields"])
        bl = []
        for b in v["builders"]:
            who = [b["statement"]] if b["statement"] else b["reached_from"]
            bl.append(f"`{b['name'].rsplit('.', 1)[-1]}`, reached from " + names(who, 6))
        cards.append(dict(
            name=p.rsplit(".", 1)[-1], title_mono=True, formula=[],
            pill=f"{len(v['fields'])} field claim{'s' if len(v['fields']) != 1 else ''}",
            accent="teal",
            bullets=["**Fields state** " + names(v["fields"], 14)
                     + " (" + ", ".join(f"{n} {ch_}" for ch_, n in sorted(fl.items(), key=lambda t: (-t[1], t[0])))
                     + ")",
                     "**Taken by** " + names(v["taken_by"], 10),
                     "**Built by** " + "; ".join(bl)],
            foot=[f"**Lean** `{p}`"]))
    for i in range(0, len(cards), NCOLS):
        chunk = cards[i:i + NCOLS]
        hh = max(bp.node(c, 0, 0, CW, draw=False, **kw) for kw in chunk)
        for j, kw in enumerate(chunk):
            bp.node(c, colx(j), y, CW, h=hh, **kw)
        y += hh + 30
    y += 20

    # ---------------------------------------------------------------------------------- the stated claims
    y = band(c, X0, y, "3 · The stated claims, and whether the proof concludes them",
             "Left: each chapter's `Prop` definitions by class. Right: every claim not concluded outright, with "
             "the theorems that conclude it and the statements their premises are claims of.")
    by = collections.defaultdict(collections.Counter)
    for v in props.values():
        by[chap(v["statement"])][v["class"]] += 1
    chapters = sorted(g.chapters, key=lambda ch: (g.nodes[ch].get("order", 0), ch))
    lw = WW * 0.4
    tcols = [("Chapter", 220)] + [(WORDS[k].capitalize(), (lw - 220 - 100) / 4) for k in CLASSES] + [("Total", 100)]
    trows = [[f"**{SHORT[ch]}**"] + [str(by[ch][k]) if by[ch][k] else "" for k in CLASSES]
             + [str(sum(by[ch].values()))] for ch in chapters if by[ch]]
    trows.append(["**All**"] + [str(cls[k]) for k in CLASSES] + [str(len(props))])
    th = c.table(X0, y, tcols, trows, size=S)
    rx = X0 + lw + G
    rw = X1 - rx
    rrows = []
    for x, v in sorted(props.items(), key=lambda t: (list(CLASSES).index(t[1]["class"]), t[1]["statement"], t[0])):
        if v["class"] == "outright":
            continue
        pb = v["proved_by"]
        by_ = "; ".join(f"`{q['theorem'].rsplit('.', 1)[-1]}`" + (f" ({q['statement']})" if q["statement"] else "")
                        for q in pb[:2]) + (f" and {len(pb) - 2} more" if len(pb) > 2 else "")
        prem = sorted({p for q in pb for p in q["premises"]} | {k.rsplit(".", 1)[-1] for q in pb
                                                                 for k in q["package_premises"]})
        rrows.append({"cells": [v["statement"], x, WORDS[v["class"]], by_ or "none", ", ".join(prem) or "—"],
                      "accent": "amber" if v["class"] == "conditional" else "red" if v["class"] == "never" else "grey"})
    rcols = [("Statement", 330, {"mono": True}), ("Prop", 400, {"mono": True}), ("Class", 260),
             ("Concluded by", rw - 330 - 400 - 260 - 330), ("Premises", 330, {"mono": True})]
    rh = c.table(rx, y, rcols, rrows, size=S)
    y += max(th, rh) + 30
    outright_lit = sum(1 for v in props.values() if chap(v["statement"]) == "chap-literature" and v["class"] == "outright")
    all_lit = sum(1 for v in props.values() if chap(v["statement"]) == "chap-literature")
    c.text(X0, y + 15, f"Of the literature chapter's {all_lit} stated claims, {outright_lit} are concluded outright.",
           13.5, "muted")
    return c
