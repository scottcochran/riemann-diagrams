"""F1 — What the stages pass to each other: the definitions of the blueprint, how they are built from one another,
and which chapters use each.

Every other poster follows the theorems. This one follows the definitions: the objects one chapter makes and
another consumes. Each card is one definition, laid out so that a definition stands above the definitions stated
in terms of it; the arrows are those `uses` edges, and the build fails if they are not exactly EXPECTED. The table
at the foot counts, for each definition, the statements of each chapter that use it, with the chapter that makes it
marked. The three definitions the blueprint's outline names as the interfaces between stages are checked against
INTERFACES."""
import collections

import bp
from bp import PROV_ACCENT, abridge, names, node, paragraphs, rich
from chapter import band, layout
from lib import Canvas

ID, SLUG = "F1", "definitions"

W = 3400
G = 64
S = 13.5
NCOLS = 5
N_DEFS = 24
# The three definitions the outline's section "What the stages pass to each other" holds.
INTERFACES = ["def-local-parameters", "def-galois-reps-polarized", "def-sha-bound"]
# The `uses` edges between definitions, (used, user). The build fails if the blueprint has others.
EXPECTED = [
    ("def-local-parameters", "def-galois-reps-polarized"),
    ("def-auxiliary-field-data", "def-family-ranks"),
    ("def-family-ranks", "def-harish-chandra-parameters"),
    ("def-auxiliary-field-data", "def-family-hermitian-spaces"), ("def-family-ranks", "def-family-hermitian-spaces"),
    ("def-auxiliary-field-data", "def-family-member"), ("def-family-ranks", "def-family-member"),
    ("def-harish-chandra-parameters", "def-family-member"), ("def-family-hermitian-spaces", "def-family-member"),
    ("def-family-member", "def-family-scale"), ("def-harish-chandra-parameters", "def-family-scale"),
    ("def-family-member", "def-family"), ("def-family-scale", "def-family"),
    ("def-sha-error-term", "def-family-data"), ("def-family", "def-family-data"),
    ("def-family-member", "def-congruence-data"), ("def-auxiliary-field-data", "def-congruence-data"),
    ("def-slope-data", "def-connected-families"),
]
SHORT = {
    "main-theorems": "Main theorems", "architecture": "Outline", "chap-zero-free": "Zero-free",
    "chap-families": "Families", "chap-theta": "Theta", "chap-heights": "Heights", "chap-sha": "Sha",
    "chap-galois": "Galois", "chap-literature": "Literature",
}


def pack(g, defs, edges, home, chapters):
    """Rows of (id, column): the definitions joined by an edge laid out by chapter.layout, so that a definition
    stands above the definitions stated in terms of it; the rest fill the free columns, the emptiest row first,
    in the blueprint's chapter order, and rows of their own above the grid if those run out."""
    joined = sorted({x for e in edges for x in e})
    rows, _ = layout(joined, edges, [], lambda k: g.nodes[k]["_path"], lambda k: chapters.index(home[k]))
    alone = sorted((k for k in defs if k not in joined),
                   key=lambda k: (chapters.index(home[k]), g.nodes[k].get("order", 0), k))
    extra = []
    while alone:                            # the emptiest row first, the topmost of equals, the leftmost free column
        free = [(NCOLS - len(row), -r) for r, row in enumerate(rows)]
        if not free or max(free)[0] <= 0:
            extra.append([alone.pop(0) for _ in range(min(NCOLS, len(alone)))])
            continue
        r = -max(free)[1]
        taken = {i for _, i in rows[r]}
        i = next(i for i in range(NCOLS) if i not in taken)
        rows[r].append((alone.pop(0), i))
        rows[r].sort(key=lambda t: t[1])
    return [[(k, i) for i, k in enumerate(chunk)] for chunk in extra] + rows


def build():
    g = bp.load()
    mirror = bp.read_mirror()
    if set(SHORT) != g.chapters:
        raise ValueError(f"F1: SHORT does not name exactly the blueprint's chapters: {sorted(set(SHORT) ^ g.chapters)}")
    chapters = sorted(g.chapters, key=lambda ch: (g.nodes[ch].get("order", 0), ch))
    defs = sorted(k for k in g.statements if g.nodes[k]["kind"] == "definition")
    if len(defs) != N_DEFS:
        raise ValueError(f"F1: the blueprint has {len(defs)} definitions, the poster is written for {N_DEFS}")
    drawn = set(defs)
    edges = [(a, b) for b in defs for a in g.uses(b) if a in drawn]
    if set(edges) != set(EXPECTED):
        raise ValueError(f"F1: arrows and definition uses differ: {sorted(set(edges) ^ set(EXPECTED))}")
    iface_dir = g.nodes["sec-outline-interfaces"]["_path"].rsplit("/", 1)[0] + "/"
    iface = sorted(k for k in defs if g.nodes[k]["_path"].startswith(iface_dir))
    if iface != sorted(INTERFACES):
        raise ValueError(f"F1: the interfaces section holds {iface}, not {sorted(INTERFACES)}")
    rev = g.used_by()
    depth, _ = g.depths(g.roots())
    main_names = {t["name"] for t in mirror["theorems"]}
    home = {k: g.nodes[k]["_chapter"] for k in defs}
    # consumption: definition -> chapter -> number of statements of that chapter that use it
    use = {k: collections.Counter(g.nodes[u]["_chapter"] for u in rev[k]) for k in defs}
    made = collections.Counter(home.values())
    by_prov = collections.Counter(g.nodes[k].get("provenance") or "unlabelled" for k in defs)
    rows = pack(g, defs, edges, home, chapters)
    n_edges_lane = collections.Counter()
    rowof_tmp = {k: i for i, row in enumerate(rows) for k, _ in row}
    for a, b in edges:
        n_edges_lane[rowof_tmp[a]] += 1
        n_edges_lane[rowof_tmp[b] - 1] += 1
    VG = max(96, 12 * max(n_edges_lane.values(), default=0) + 24)
    iface_users = sum(len(rev[k]) for k in INTERFACES)
    iface_chapters = sorted({g.nodes[u]["_chapter"] for k in INTERFACES for u in rev[k]})
    towers = [k for k in defs if any(a in drawn for a in g.uses(k))]
    succ = collections.defaultdict(list)
    for a, b in edges:
        succ[a].append(b)
    memo = {}

    def tower(k):                            # the longest chain of definitions stated in terms of k, from k
        if k not in memo:
            below = [tower(b) for b in sorted(succ[k])]
            memo[k] = [k] + max(below, key=lambda t: (len(t), t)) if below else [k]
        return memo[k]

    tallest = max((tower(k) for k in defs), key=lambda t: (len(t), t))
    alone = [k for k in defs if k not in {x for e in edges for x in e}]

    c = Canvas(ID, f"What the stages pass to each other: the {len(defs)} definitions of the blueprint, how they are "
               "built from one another, and which chapters use each",
               "Every other poster follows the theorems. This one follows the definitions: the objects one chapter "
               "of the proof makes and another consumes. Each card is one of the blueprint's definitions, with the "
               "Lean declaration it stands for, the definition in words, and the chapter that makes it in its pill. "
               "**Read the grid from the foot up**: a definition stands above the definitions stated in terms of "
               "it, and an arrow from A to B says that B is defined using A. The table at the foot is the flow "
               "between stages: for each definition, how many statements of each chapter use it, with the chapter "
               "that makes it marked. The outline's own section on the interfaces names three definitions as what "
               f"the arithmetic stages pass to the analytic ones; those three are used by {iface_users} statements "
               f"in {len(iface_chapters)} chapters. **No Lean was built**: see diagram R1, band 5."
               + (" **Map mode**: nothing of the blueprint's text or the proof's source is quoted." if bp.MAP else ""),
               W, f"`riemann-blueprint` at {g.bp_commit} (every definition's front matter and body; every "
               "statement's chapter and uses, for the counts; `architecture/sec-outline-interfaces/`; "
               "`lean-facts.json` for the signatures, files and lines); `leanprover-community/riemann-hypothesis` "
               f"at {mirror['commit']} (`src/Main.lean`). The layout is computed from the definitions' own uses; "
               "the counts, the chapter labels and the abridgements are the diagram's own.",
               state=f"State drawn: riemann-blueprint at {g.bp_commit}, which pins the mirror at {g.mirror_pin}; "
                     f"Main.lean from the mirror at {mirror['commit']}")
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    CW = (WW - 4 * G) / 5

    def colx(i):
        return X0 + i * (CW + G)

    def span(n):
        return n * CW + (n - 1) * G

    def consumers(k, limit=9):
        parts = [f"{SHORT[ch]} {n}" for ch, n in sorted(use[k].items(), key=lambda t: (-t[1], chapters.index(t[0])))]
        return ", ".join(parts[:limit]) + (f" … and {len(parts) - limit} more" if len(parts) > limit else "")

    # ---------------------------------------------------------------------------------- reading the poster
    y = c.y
    y = band(c, X0, y, "1 · Reading the poster")
    y += c.legend(X0, y, [("box", "green", "new in Alpöge's proof"), ("box", "amber", "modified from the literature"),
                          ("box", "blue", "published"), ("box", "grey", "unlabelled"),
                          ("arrow", "muted", "A → B: definition B is stated in terms of A (the arrow takes A's colour)")],
                  title="Legend") + 26
    key = [
        "**Title and pill.** The title is the blueprint's; the pill gives the kind, the chapter that makes the "
        "definition, and the provenance: **new** in Alpöge's proof, **modified** from a published definition, or "
        "**published** as it stands. Definitions are drawn with a dashed border on every poster of this set.",
        "**The Lean panel** is the signature of the first declaration the blueprint lists for the definition, as "
        "`lean-facts.json` records it, wrapped and cut at nine lines. The footer gives its file and line in the "
        "mirror and the other declarations.",
        "**The line in italics** is the blueprint's definition, abridged where marked with …; links appear as "
        "`ids` and maths is rewritten in plain Unicode. A definition has no proof, so there are no bullets.",
        "**Stated with** and **Used by** are the blueprint's edges. **Used in** counts the statements of each "
        "chapter that use the definition, in their statement or their proof; it is the row of the table at the "
        "foot. **Rows**: a card stands above the definitions stated in terms of it; cards of one chapter sit "
        "together where the arrows allow.",
    ]
    if bp.MAP:
        key = bp.MAP_KEY + [
            "**Used in** counts the statements of each chapter that use the definition, in their statement or "
            "their proof; it is the row of the table at the foot. The pill names the chapter that makes the "
            "definition."]
    paras = paragraphs(bp.body(g, "sec-outline-interfaces"))
    if not paras:
        raise ValueError("F1: sec-outline-interfaces has no introduction")
    iface_body = [abridge(rich(paras[0]), 1100) if not bp.MAP
                  else f"{len(paras)} paragraph(s) of introduction. " + bp.NOT_QUOTED]
    iface_body.append("**The three** " + ", ".join(
        f"`{k}` (made in {SHORT[home[k]]}, used by {len(rev[k])} statements)" for k in INTERFACES) + ".")
    flow = [
        f"**Made** {len(defs)} definitions: " + ", ".join(
            f"{made[ch]} in {SHORT[ch]}" for ch in chapters if made[ch]) + ". By provenance: " + ", ".join(
            f"{v} {k}" for k, v in sorted(by_prov.items())) + ".",
        f"**Built from one another** {len(towers)} of them are stated in terms of another definition; the "
        f"{len(edges)} arrows of the grid. The tallest tower is {len(tallest)} definitions high, from "
        f"`{tallest[0]}` ({SHORT[home[tallest[0]]]}) to `{tallest[-1]}` ({SHORT[home[tallest[-1]]]}).",
        "**Consumed** " + ", ".join(
            f"{SHORT[ch]} {sum(use[k][ch] for k in defs)}" for ch in chapters if any(use[k][ch] for k in defs))
        + " statements use a definition. **Used most** " + ", ".join(
            f"`{k}` ({len(rev[k])})" for k in sorted(defs, key=lambda k: (-len(rev[k]), k))[:5]) + ".",
    ]
    hk = max(c.card(0, 0, span(2), "How to read a node", key, draw=False, size=S),
             c.card(0, 0, span(2), "The interfaces, in the outline's own words (`sec-outline-interfaces`)", iface_body,
                    draw=False, size=S),
             c.card(0, 0, span(1), "Made, built, consumed", flow, draw=False, size=S))
    c.card(colx(0), y, span(2), "How to read a node", key, "grey", h=hk, size=S, tint=False)
    c.card(colx(2), y, span(2), "The interfaces, in the outline's own words (`sec-outline-interfaces`)", iface_body,
           "teal", h=hk, size=S, tint=False)
    c.card(colx(4), y, span(1), "Made, built, consumed", flow, "grey", h=hk, size=S, tint=False)
    y += hk + 50

    # ---------------------------------------------------------------------------------- the grid
    y = band(c, X0, y, "2 · The definitions, each above the definitions stated in terms of it",
             f"{len(rows)} rows. The {len(defs) - len(alone)} definitions joined by an arrow are laid out from "
             f"their uses, the families chapter's tower from auxiliary field data to family data running down "
             f"the grid; the {len(alone)} that no arrow touches fill the free places, the emptiest rows first, "
             "in the blueprint's chapter order.")
    pos, rowof = {}, {}
    for r, row in enumerate(rows):
        items = []
        for k, i in row:
            kw = bp.statement_card(g, k, CW, drawn, rev, depth, main_names, ID)
            n = g.nodes[k]
            kw["pill"] = f"definition · {SHORT[home[k]]} · {bp.PROV_SHORT[n.get('provenance')]}"
            used_in = (f"**Used in** {len(rev[k])} statements in {len(use[k])} chapters: {consumers(k)}"
                       if rev[k] else "**Used in** no statement")
            at = next(j for j, f in enumerate(kw["foot"]) if f.startswith("**Lean**") or f.startswith("Blueprint"))
            kw["foot"].insert(at, used_in)
            items.append((k, i, kw))
        hh = max(node(c, 0, 0, CW, draw=False, **kw) for _, _, kw in items)
        for k, i, kw in items:
            node(c, colx(i), y, CW, h=hh, **kw)
            pos[k] = (colx(i), y, CW, hh)
            rowof[k] = r
        y += hh + VG
    y -= VG
    bp.arrows(c, pos, rowof, edges, lambda a: PROV_ACCENT[g.nodes[a].get("provenance")], VG, G, X0, X1, NCOLS, colx)

    # ---------------------------------------------------------------------------------- the matrix
    y += 60
    y = band(c, X0, y, "3 · Where each definition is made, and which chapters consume it",
             "One row per definition, grouped by the chapter that makes it, in the blueprint's chapter order. A "
             "cell counts the statements of that chapter whose statement or proof uses the definition; the "
             "chapter that makes it is marked **here**. Counted from the blueprint's `uses` edges over all "
             f"{len(g.statements)} statements.")
    fixed = [("Definition", 330, {"mono": True}), ("Title", 470)]
    tail = [("Statements", 130), ("Lean decls", 110)]
    cw = (WW - sum(w for _, w, *_ in fixed + tail)) / len(chapters)
    cols = fixed + [(SHORT[ch], cw) for ch in chapters] + tail
    trows = []
    for ch in chapters:
        mine = sorted((k for k in defs if home[k] == ch), key=lambda k: (g.nodes[k].get("order", 0), k))
        if not mine:
            continue
        trows.append({"group": f"Made in {SHORT[ch]}: {g.nodes[ch]['title']} ({len(mine)})", "accent": "grey"})
        for k in mine:
            n = g.nodes[k]
            cells = [k, n["title"]]
            for col in chapters:
                v = use[k][col]
                if col == ch:
                    cells.append(f"**here** · {v}" if v else "**here**")
                else:
                    cells.append(str(v) if v else "")
            cells += [str(len(rev[k])), str(len(n.get("lean", [])))]
            trows.append({"cells": cells, "accent": PROV_ACCENT[n.get("provenance")]})
    totals = ["", "**Statements using a definition**"] + [
        str(sum(use[k][col] for k in defs)) for col in chapters] + [str(sum(len(rev[k]) for k in defs)),
                                                                    str(sum(len(g.nodes[k].get("lean", [])) for k in defs))]
    trows.append(totals)
    c.table(X0, y, cols, trows, size=S)
    return c
