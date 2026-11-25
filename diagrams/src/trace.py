"""A trace poster: one chain of reductions from a theorem of Main.lean down to one statement, as cards.

The chain is a shortest path in the blueprint's `uses` graph from the three theorems nothing else uses to the
target, found breadth-first; its cards run in reading order from the target, the deepest statement, to the
Main.lean theorem, so that the poster reads as a proof: nothing is used before it is proved. Each module records
the chain it expects (EXPECTED), and the build fails if the blueprint now gives another. The cards and the arrows
are those of the chapter posters. Each link is drawn by its verdict against the formal proof (src/lean-edges.json),
which must be the module's VERDICTS (every link `direct` but those named)."""
import collections

import bp
from bp import PROV_ACCENT, abridge, names, node, paragraphs, rich
from lib import Canvas

W = 3400
G = 64
VG = 110
S = 13.5
NCOLS = 5


def band(c, x, y, title, sub=None):
    c.text(x, y + 22, title, 22, "ink", bold=True)
    if sub:
        return y + 40 + c.para(x, y + 36, c.x1 - x, sub, 14.5, "muted") + 14
    return y + 54


def chain_to(g, target):
    """The shortest chain from the roots to `target`, as the Graphviz trace_proof.py finds it."""
    depth, parent = g.depths(g.roots())
    if target not in depth:
        raise ValueError(f"{target} is not reachable from the main theorems")
    path = []
    while target is not None:
        path.append(target)
        target = parent[target]
    return list(reversed(path))


def build(ID, TARGET, EXPECTED, title, why, VERDICTS=None):
    g = bp.load()
    mirror = bp.read_mirror()
    path = chain_to(g, TARGET) if TARGET else g.deepest_trace(g.roots())
    if path != list(EXPECTED):
        raise ValueError(f"{ID}: the chain differs from the recorded one: {path}")
    rev = g.used_by()
    depth, _ = g.depths(g.roots())
    main_names = {t["name"] for t in mirror["theorems"]}
    order = list(reversed(path))                     # reading order: the deepest statement first
    steps = list(zip(order, order[1:]))              # (used, user): each card is used by the next
    dashed = [(a, b) for a, b in steps if a not in g.proof_uses(b)]
    for a, b in steps:
        if a not in g.uses(b):
            raise ValueError(f"{ID}: {b} does not use {a}")
    lean = bp.read_edges(g)
    VERDICTS = VERDICTS or {}
    verd = {(a, b): lean.verdict(b, a) for a, b in steps}
    diff = sorted((e, v) for e, v in verd.items() if v != VERDICTS.get(e, "direct"))
    if diff or set(VERDICTS) - set(verd):
        raise ValueError(f"{ID}: verdicts differ from VERDICTS (link, verdict now): {diff or sorted(VERDICTS)}")
    borne = {"direct", "hypothesis", "through"}
    holds = all(v in borne for v in verd.values())
    chapters = []
    for k in order:
        ch = g.nodes[k]["_chapter"]
        if not chapters or chapters[-1] != ch:
            chapters.append(ch)
    drawn = set(order)

    c = Canvas(ID, title,
               f"One chain through the proof: {len(order)} statements, each used by the proof of the next, from "
               f"`{order[0]}` at depth {depth[order[0]]} up to `{order[-1]}` of `Main.lean`. It is a shortest "
               "chain in the blueprint's `uses` graph, found breadth-first from the three theorems nothing else "
               "uses, so every statement on it is as far from the main theorems as it can be. **Read it as a "
               "proof**, left to right and top to bottom: nothing is used before it is proved. Each card is one "
               "blueprint statement, as in the chapter posters; an arrow from A to B says that the proof of B "
               "uses A. Each link is checked against the formal proof's references: see the card **The chain**. "
               + why + (" **Map mode**: nothing of the blueprint's text or the proof's source is "
               "quoted." if bp.MAP else "") + " **No Lean was built**: see diagram R1, band 5.",
               W, f"`riemann-blueprint` at {g.bp_commit} (the front matter, statement and proof of every statement "
               "on the chain; `lean-facts.json` for the signatures, files and lines); "
               f"`leanprover-community/riemann-hypothesis` at {mirror['commit']} (`src/Main.lean`); "
               "`diagrams/src/lean-edges.json`, the verdicts on the blueprint's arrows from Sutherland's export of "
               f"the proof at {g.mirror_pin} (sha256 {lean.export_sha256[:12]}…). The chain is computed; the "
               "abridgements are the diagram's own, as marked.",
               state=f"State drawn: riemann-blueprint at {g.bp_commit}, which pins the mirror at {g.mirror_pin}; "
                     f"Main.lean from the mirror at {mirror['commit']}")
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    CW = (WW - 4 * G) / 5

    def colx(i):
        return X0 + i * (CW + G)

    def span(n):
        return n * CW + (n - 1) * G

    y = c.y
    y = band(c, X0, y, "1 · Reading the poster")
    y += c.legend(X0, y, [("box", "green", "new in Alpöge's proof"), ("box", "amber", "modified from the literature"),
                          ("box", "blue", "published"),
                          ("arrow", "muted", "A → B: the proof of B uses A (the arrow takes A's colour)"),
                          ("arrow", "amber", "A ⇢ B: B is stated with A (dashed)", "7 5")]
                  + bp.verdict_legend(set(verd.values())), title="Legend") + 26
    key = [
        "**Title and pill.** The title is the blueprint's; the pill gives the step on the chain, the kind and the "
        "provenance: **new** in Alpöge's proof, **modified** from a published result, or **published** as it "
        "stands. `Main.lean` marks the theorem the chain ends in.",
        "**The Lean panel** is the signature of the first declaration the blueprint lists for the statement, as "
        "`lean-facts.json` records it, wrapped and cut at nine lines. The footer gives its file and line in the "
        "mirror and the other declarations.",
        "**The line in italics** is the blueprint's statement, and **the bullets** are its proof, paragraph by "
        "paragraph, abridged where marked with …; links appear as `ids` and maths is rewritten in plain Unicode.",
        "**Proof uses** and **Used by** list every edge, not only the one the chain takes: the chain is one path "
        "through a tree, and the footers show where the other branches go.",
    ]
    if bp.MAP:
        key = bp.MAP_KEY
    route = []
    for i, k in enumerate(order):
        n = g.nodes[k]
        route.append(f"{i + 1}. `{k}` ({g.nodes[n['_chapter']]['title']}, depth {depth[k]})")
    chain_body = [
        "**The chain**, in reading order: " + "; ".join(route) + ".",
        "**The chapters it crosses**, in order: " + " → ".join(f"`{ch}`" for ch in chapters) + ".",
        f"**Depth** counts `uses` edges from the main theorems: `{order[0]}` is at depth {depth[order[0]]}, "
        f"the deepest statement on the chain. The blueprint's deepest statement of all is at depth "
        f"{max(depth.values())}.",
    ]
    cnt = collections.Counter(verd.values())
    odd = [f"`{a}` → `{b}` {'only by way of other statements' if v == 'through' else v}"
           for (a, b), v in verd.items() if v != "direct"]
    chain_body.append(
        ("**The chain holds in the formal proof.** " if holds else "**The chain breaks in the formal proof.** ")
        + f"Of its {len(steps)} links, {cnt['direct']} are borne out directly"
        + (": " + "; ".join(odd) if odd else "") + ". "
        + f"The Lean of `{order[-1]}` " + ("reaches" if lean.reaches(order[-1], order[0]) else "does not reach")
        + f" `{order[0]}`. Read from Sutherland's export of the published proof, with no Lean built; "
        "`diagrams/EDGES.md` gives the method.")
    hk = max(c.card(0, 0, span(2), "How to read a node", key, draw=False, size=S),
             c.card(0, 0, span(3), "The chain", chain_body, draw=False, size=S))
    c.card(colx(0), y, span(2), "How to read a node", key, "grey", h=hk, size=S, tint=False)
    c.card(colx(2), y, span(3), "The chain", chain_body, "grey", h=hk, size=S, tint=False)
    y += hk + 50

    y = band(c, X0, y, "2 · The chain, as a proof",
             "Left to right, then the next row. The last card is the theorem of `Main.lean` the chain reaches.")
    rows = [order[i:i + NCOLS] for i in range(0, len(order), NCOLS)]
    pos, rowof = {}, {}
    for r, row in enumerate(rows):
        items = []
        for i, k in enumerate(row):
            kw = bp.statement_card(g, k, CW, drawn, rev, depth, main_names, ID)
            kw["pill"] = f"step {order.index(k) + 1} · " + kw["pill"]
            items.append((k, i, kw))
        hh = max(node(c, 0, 0, CW, draw=False, **kw) for _, _, kw in items)
        for k, i, kw in items:
            node(c, colx(i), y, CW, h=hh, **kw)
            pos[k] = (colx(i), y, CW, hh)
            rowof[k] = r
        y += hh + VG
    y -= VG
    bp.arrows(c, pos, rowof, steps, lambda a: PROV_ACCENT[g.nodes[a].get("provenance")], VG, G, X0, X1, NCOLS,
              colx, dashed=dashed, verdicts=verd)
    return c
