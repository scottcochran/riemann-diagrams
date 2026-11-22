"""R1 — Main.lean, theorem by theorem: the five theorems, the statements they are made of, and the chain of
reductions that proves them.

Every node is read from the files at build time (bp.py): the Lean panel is the declaration's signature from the
blueprint's lean-facts.json, the italic line is the blueprint's statement, the bullets are its proof, and the
Stated with / Proof uses / Used by lines are the blueprint's `uses` edges. The arrows are the proof uses between the
drawn statements, and the build fails if they are not exactly the ones listed in EXPECTED."""
import re

import bp
from bp import PROV_ACCENT, PROV_SHORT, abridge, code, names, node, paragraphs, rich
from lib import Canvas

ID, SLUG = "R1", "main-theorems"

W = 3400
G = 64             # the gutter between columns, where arrows run
VG = 96            # the gap between rows
S = 13.5

# Where each statement sits: id -> (row, column, columns spanned). Used statements sit above their users.
PLACE = {
    "def-riemann-hypothesis": (0, 0, 1), "def-nonvanishing-half-plane": (0, 1, 1), "def-zeros-on-line": (0, 2, 1),
    "def-sha-bound": (1, 0, 1), "def-galois-reps-polarized": (1, 1, 1), "def-local-parameters": (1, 2, 1),
    "thm-galois-reps-polarized": (2, 0, 1), "thm-sha-bound": (2, 1, 1), "thm-local-parameters-exist": (2, 2, 1),
    "thm-auxiliary-fields": (2, 3, 1), "thm-families-connected": (2, 4, 1),
    "thm-family-data-exists": (3, 0, 1), "thm-zero-free-from-connected": (3, 1, 1), "thm-primitive-suffice": (3, 2, 1),
    "thm-zero-free-from-families": (4, 0, 1), "thm-grh-from-theta-integrals": (4, 1, 1),
    "thm-grh-from-sha-bound": (4, 2, 1), "thm-grh-from-galois": (4, 3, 1),
    "lem-zeta-nonvanishing": (5, 0, 1), "thm-half-plane": (5, 1, 1), "thm-riemann-hypothesis": (5, 2, 1),
    "thm-critical-line": (5, 3, 1), "thm-critical-line-primitive": (5, 4, 1),
}
BANDS = {0: "1 · What is claimed, and the statements the proof passes between its stages",
         2: "2 · What the chapters deliver",
         4: "3 · The chain of reductions",
         5: "4 · Main.lean: the five theorems"}
BAND_SUB = {
    0: "Three definitions state the claims (row 1) and three state what the stages hand to each other (row 2). "
       "Definitions are joined to the statements that use them by the **Stated with** lines, not by arrows.",
    2: "Each chapter of the blueprint proves one of these. Their proofs are drawn in diagram R2; here they are the "
       "inputs of the chain below.",
    4: "Read right to left: each theorem reduces the half-plane claim to the one on its left, and `GRH from Galois "
       "representations` gathers the whole chain. An arrow from A to B says that the proof of B uses A.",
    5: "The five theorems of `Main.lean`, with the one hard statement among them, `GRH, half-plane form`. The other "
       "four follow from it by the functional equation.",
}
# The proof-use edges among the drawn statements, (used, user). The build fails if the blueprint has others.
EXPECTED = [
    ("def-local-parameters", "thm-sha-bound"),
    ("thm-galois-reps-polarized", "thm-half-plane"), ("thm-galois-reps-polarized", "thm-sha-bound"),
    ("thm-local-parameters-exist", "thm-sha-bound"), ("thm-local-parameters-exist", "thm-family-data-exists"),
    ("thm-sha-bound", "thm-grh-from-galois"), ("thm-local-parameters-exist", "thm-grh-from-galois"),
    ("thm-auxiliary-fields", "thm-zero-free-from-families"), ("thm-families-connected", "thm-zero-free-from-families"),
    ("thm-family-data-exists", "thm-grh-from-theta-integrals"), ("thm-family-data-exists", "thm-grh-from-galois"),
    ("thm-zero-free-from-connected", "thm-zero-free-from-families"),
    ("thm-zero-free-from-connected", "thm-grh-from-galois"),
    ("thm-primitive-suffice", "thm-zero-free-from-families"),
    ("thm-zero-free-from-families", "thm-grh-from-theta-integrals"),
    ("thm-zero-free-from-families", "thm-grh-from-galois"),
    ("thm-grh-from-theta-integrals", "thm-grh-from-sha-bound"), ("thm-grh-from-theta-integrals", "thm-grh-from-galois"),
    ("thm-grh-from-sha-bound", "thm-grh-from-galois"),
    ("thm-grh-from-galois", "thm-half-plane"),
    ("thm-half-plane", "thm-riemann-hypothesis"), ("thm-half-plane", "thm-critical-line"),
    ("thm-half-plane", "thm-critical-line-primitive"), ("lem-zeta-nonvanishing", "thm-riemann-hypothesis"),
]


def band(c, x, y, title, sub=None):
    c.text(x, y + 22, title, 22, "ink", bold=True)
    if sub:
        return y + 40 + c.para(x, y + 36, c.x1 - x, sub, 14.5, "muted") + 14
    return y + 54


def build():
    g = bp.load()
    mirror = bp.read_mirror()
    drawn = set(PLACE)
    for k in drawn:
        if k not in g.statements:
            raise ValueError(f"R1 draws {k}, which the blueprint does not have")
    edges = [(a, b) for b in sorted(drawn) for a in g.proof_uses(b) if a in drawn]
    if set(edges) != set(EXPECTED):
        raise ValueError(f"R1: arrows and proof uses differ: {sorted(set(edges) ^ set(EXPECTED))}")
    main_names = {t["name"] for t in mirror["theorems"]}
    carried = {x for k in sorted(drawn) for x in g.nodes[k].get("lean", [])}
    if not main_names <= carried:
        raise ValueError(f"R1: Main.lean theorems carried by no drawn node: {sorted(main_names - carried)}")
    rev = g.used_by()
    depth, _ = g.depths(g.roots())

    c = Canvas(ID, "`Main.lean`, theorem by theorem: the five theorems, the statements they are made of, and the "
               "chain of reductions that proves them",
               "The formal proof is 164,464 Lean files with no comments; the blueprint reads it as 416 statements "
               "and the edges between them. This diagram draws the five theorems of `Main.lean`, the definitions "
               "they are stated with, and the chain of reductions by which the hard one, `GRH, half-plane form`, "
               "reaches the theorems that the chapters prove. Each node is one blueprint statement: the Lean "
               "declaration it stands for, as the blueprint's facts file records its signature, the statement in "
               "words, how its proof goes, and what it uses and is used by. **Read it from the foot up**: the five "
               "theorems are at the bottom, and everything above is what their proofs use. **No Lean was built** "
               "for the blueprint or for this diagram: the edges were resolved from the source text and some are "
               "wrong, and whether the formal proof is correct is a question for the kernel checks of band 5.",
               W, f"`riemann-blueprint` at {g.bp_commit} (the front matter, statement and proof of every drawn node; "
               "`lean-facts.json` for every signature, file and line; the `architecture` chapter's introduction); "
               f"`leanprover-community/riemann-hypothesis` at {mirror['commit']} (`src/Main.lean`, "
               "`src/Statements.lean`, `comparator.json`, `verification/NOTES.md`). The depth table and the "
               "abridgements are the diagram's own, computed or cut as marked.",
               state=f"State drawn: riemann-blueprint at {g.bp_commit}, which pins the mirror at {g.mirror_pin}; "
                     f"Main.lean, Statements.lean and the verification notes from the mirror at {mirror['commit']}")
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    CW = (WW - 4 * G) / 5

    def colx(i):
        return X0 + i * (CW + G)

    def span(n):
        return n * CW + (n - 1) * G

    # ---------------------------------------------------------------------------------- node content
    def stmt_node(k, w):
        n = g.nodes[k]
        prov = n.get("provenance")
        lean = n.get("lean", [])
        if not lean:
            raise ValueError(f"R1: {k} has no Lean declaration to draw")
        first = lean[0]
        fact = g.lean_facts.get(first)
        if not fact or not fact.get("signature"):
            raise ValueError(f"R1: lean-facts.json has no signature for {first}")
        is_main = any(x in main_names for x in lean)
        pill = ("Main.lean · " if is_main else "") + f"{n['kind']} · {PROV_SHORT[prov]}"
        say = abridge(rich(" ".join(paragraphs(bp.body(g, k))[:2])), 620)
        pf = bp.proof(g, k)
        bullets = []
        if pf is not None:
            paras = paragraphs(pf)
            for p in paras[:4]:
                bullets.append(abridge(rich(p), 330))
            if len(paras) > 4:
                bullets.append(f"… and {len(paras) - 4} more paragraphs in the blueprint's proof.")
        elif n["kind"] != "definition":
            bullets.append("The blueprint gives no proof for this statement.")
        su, pu, ub = g.statement_uses(k), g.proof_uses(k), rev[k]
        foot = ["**Stated with** " + (names(su) if su else "no other statement")]
        if n["kind"] != "definition":
            hidden = [u for u in pu if u not in drawn]
            foot.append("**Proof uses** " + (names(pu) if pu else "nothing the blueprint names")
                        + (f" · {len(hidden)} of these are not drawn here" if hidden else ""))
        foot.append("**Used by** " + (names(ub) if ub else "no other statement: it is one of the five theorems"))
        where = g.lean_location(first)
        more = f" · and {len(lean) - 1} more: " + names(lean[1:4]) + (" …" if len(lean) > 4 else "") if len(lean) > 1 else ""
        foot.append(f"**Lean** {code(first)} at {code(where)}{more}")
        chap = g.nodes[n["_chapter"]]["title"]
        foot.append(f"Blueprint `{n['_path']}` ({chap}) · depth {depth.get(k, '—')} from the main theorems")
        return dict(name=n["title"], accent=PROV_ACCENT[prov], pill=pill,
                    formula=bp.lean_block(fact["signature"], bp.columns(w)), say=say, bullets=bullets, foot=foot,
                    dash="6 4" if n["kind"] == "definition" else None)

    pos, rowof = {}, {}

    def row(y, items, h=None):
        """items: (key, column, columns spanned, node kwargs). Equal height over the row. Returns the height."""
        hh = max([node(c, 0, 0, span(n), draw=False, **kw) for _, _, n, kw in items] + [h or 0])
        for key, i, n, kw in items:
            node(c, colx(i), y, span(n), h=hh, **kw)
            pos[key] = (colx(i), y, span(n), hh)
        return hh

    rows = {}
    for k, (r, i, n) in PLACE.items():
        rows.setdefault(r, []).append((k, i, n))
        rowof[k] = r

    # ---------------------------------------------------------------------------------- extra cards
    key_body = [
        "**Title and pill.** The title is the blueprint's; the pill gives the kind and the provenance: **new** "
        "in Alpöge's proof, **modified** from a published result, or **published** as it stands. "
        "`Main.lean` marks the theorems the Comparator config names.",
        "**The Lean panel** is the signature of the first declaration the blueprint lists for the statement, as "
        "`lean-facts.json` records it, wrapped and cut at nine lines. The footer gives the file and line in the "
        "mirror and the other declarations.",
        "**The line in italics** is the blueprint's statement, and **the bullets** are the blueprint's proof, "
        "paragraph by paragraph. Both are abridged where marked with …; links appear as `ids` and maths is "
        "rewritten in plain Unicode.",
        "**Stated with** lists the statements this one is written in terms of; **Proof uses** what its proof "
        "cites; **Used by** what cites it. **An arrow from A to B**: the proof of B uses A, and the arrow takes "
        "A's colour. Statement uses are not drawn.",
    ]
    stm = mirror["theorems"]
    props = mirror["props"]
    lean_lines = [t["src"] for t in stm] + [""]
    for p in props.values():
        lean_lines += p["lines"] + [""]
    stm_bullets = [
        "**The claims.** `Main.lean` states the five theorems the Comparator config names, each as a Prop that "
        "`Statements.lean` defines from Mathlib's `riemannZeta` and `DirichletCharacter.LFunction`; "
        "`riemannHypothesis` is Mathlib's own `RiemannHypothesis`.",
        "**The proof terms** `rhOfAll`, `allChi`, `claimAll` and `critAll` are where the five theorems enter the "
        "164,464 files of the proof. Everything above them in this diagram is what those terms unfold to.",
        "**The permitted axioms** are " + ", ".join(f"`{a}`" for a in mirror["axioms"]) + ": a proof using any "
        "other is rejected before a kernel runs.",
    ]
    stm_node = dict(name="Main.lean and Statements.lean", accent="grey", pill="the claims, as the mirror states them",
                    formula=bp.lean_lines(lean_lines, bp.columns(span(2)), 22), say=None, bullets=stm_bullets,
                    foot=[f"`src/Main.lean` (every theorem) and `src/Statements.lean` (every definition) at "
                          f"{mirror['commit']} · the axioms from `comparator.json`"])
    arch = [rich(p) for p in paragraphs(bp.body(g, "architecture"))]
    stages = [p for p in arch if re.match(r"(Galois|The Tate|Families|Slope|Landau)", p)]
    if len(stages) != 5:
        raise ValueError(f"R1: the architecture chapter's introduction does not list five stages: {len(stages)}")

    # ---------------------------------------------------------------------------------- the rows
    y = c.y
    y = band(c, X0, y, BANDS[0], BAND_SUB[0])
    y += c.legend(X0, y, [("box", "green", "new in Alpöge's proof"), ("box", "amber", "modified from the literature"),
                          ("box", "blue", "published"), ("box", "grey", "from the mirror, not the blueprint"),
                          ("arrow", "muted", "A → B: the proof of B uses A (the arrow takes A's colour)")],
                  title="Legend") + 26
    for r in sorted(rows):
        if r in BANDS and r != 0:
            y += 20
            y = band(c, X0, y, BANDS[r], BAND_SUB.get(r))
        items = [(k, i, n, stmt_node(k, span(n))) for k, i, n in rows[r]]
        extra = None
        if r == 0:
            extra = ("key", 3, 2, "How to read a node", key_body, "grey")
        elif r == 3:
            extra = ("stages", 3, 2, "The five stages of the proof (the architecture chapter's own list)",
                     [abridge(s, 420) for s in stages], "grey")
        hh = max(node(c, 0, 0, span(n), draw=False, **kw) for _, _, n, kw in items)
        if r == 1:
            hh = max(hh, node(c, 0, 0, span(2), draw=False, **stm_node))
        if extra:
            hh = max(hh, c.card(0, 0, span(extra[2]), extra[3], extra[4], draw=False, size=S))
        for k, i, n, kw in items:
            node(c, colx(i), y, span(n), h=hh, **kw)
            pos[k] = (colx(i), y, span(n), hh)
        if r == 1:
            node(c, colx(3), y, span(2), h=hh, **stm_node)
        if extra:
            c.card(colx(extra[1]), y, span(extra[2]), extra[3], extra[4], extra[5], h=hh, size=S, tint=False)
        y += hh + VG
    y -= VG

    bp.arrows(c, pos, rowof, edges, lambda a: PROV_ACCENT[g.nodes[a].get("provenance")], VG, G, X0, X1, 5, colx)

    # ---------------------------------------------------------------------------------- band 5: reference
    y += 60
    y = band(c, X0, y, "5 · Reference: the five theorems, the depth of the proof, and what has been checked")
    tw = [330, 330, 300, 230, 330]
    c.text(X0, y + 15, "The theorems of Main.lean, and the blueprint node that carries each", 15, "muted", bold=True)
    trows = []
    for t in stm:
        oid = bp.MAIN_LEAN_THEOREMS[t["name"]]
        trows.append([t["name"], t["prop"], t["proof"], oid, g.nodes[oid]["title"]])
    ht = c.table(X0, y + 30, [("Theorem", tw[0], {"mono": True}), ("Stated as", tw[1], {"mono": True}),
                              ("Proof term", tw[2], {"mono": True}), ("Blueprint node", tw[3], {"mono": True}),
                              ("Title", tw[4])], trows, size=S)
    by = {}
    for oid, d in depth.items():
        r = by.setdefault(d, {"n": 0, "published": 0, "modified": 0, "new": 0})
        r["n"] += 1
        p = g.nodes[oid].get("provenance")
        if p in r:
            r[p] += 1
    drows = [[str(d), str(r["n"]), str(r["published"]), str(r["modified"]), str(r["new"])] for d, r in sorted(by.items())]
    drows.append({"cells": ["Total", str(sum(r["n"] for r in by.values())), str(sum(r["published"] for r in by.values())),
                            str(sum(r["modified"] for r in by.values())), str(sum(r["new"] for r in by.values()))],
                  "accent": "grey"})
    dx = X0 + sum(tw) + 70
    dw = [130, 150, 150, 150, 130]
    c.text(dx, y + 15, "Statements by depth from the main theorems (the diagram's own count)", 15, "muted", bold=True)
    hd = c.table(dx, y + 30, [("Depth", dw[0]), ("Statements", dw[1]), ("Published", dw[2]), ("Modified", dw[3]),
                              ("New", dw[4])], drows, size=S)
    unreached = len(g.statements) - sum(r["n"] for r in by.values())
    c.card(dx, y + 30 + hd + 24, sum(dw), "Reading the table", [
        "A statement's depth is the fewest `uses` edges from one of the three theorems nothing else uses "
        "(`The Riemann Hypothesis` and the two critical-line forms) down to it. The five theorems of `Main.lean` "
        "sit at depths 0 and 1.",
        f"{unreached} of the blueprint's {len(g.statements)} statements are reached by no edge from the main "
        "theorems: the blueprint's remarks and a few results whose users it did not resolve.",
        "Published results sit mostly at depths 4 and 5: the new argument is the top of the tree and rests on "
        "the literature below it.",
    ], "grey", size=S, tint=False)
    rx = dx + sum(dw) + 70
    rw = X1 - rx
    c.text(rx, y + 15, "Checked and proved: what is known about the formal proof", 15, "muted", bold=True)
    ry = y + 30
    ry += c.card(rx, ry, rw, "Built: Lean's own kernel", [
        "`lake build Main` compiles every file of the submission; a successful build is a check by the kernel of "
        "Lean v4.33.1, the version the project pins. The mirror's notes list independent complete builds, and "
        "compare their compiled files with the checksums the author published: in the complete one, "
        "`Main.olean` is identical.",
    ], "teal", size=S) + 20
    ry += c.card(rx, ry, rw, "Judged: Comparator, not yet", [
        "`lake comparator` exports the five theorems and replays them in kernels independent of Lean's own, "
        "Lean paranoid and nanoda, allowing only the three axioms of `comparator.json`. The notes say its output "
        "will be added when the run finishes. **At the state drawn, no result is recorded.**",
    ], "amber", size=S) + 20
    c.card(rx, ry, rw, "Read: this blueprint and diagram", [
        "No Lean was built for the blueprint. Its `uses` edges were resolved from identifiers in the source text, "
        "and its README says some are wrong and that every proof status reads *absent*. This diagram inherits "
        "both limits. A node here says what a statement is, not that it is proved.",
    ], "red", size=S)
    return c
