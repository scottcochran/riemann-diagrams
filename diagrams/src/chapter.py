"""A chapter poster: every statement of one blueprint chapter as a card, laid out from the chapter's own
dependency graph, with the chapter's theorem at the foot.

The layout is computed: a statement's row is one above the highest row of the statements that use it, so nothing
is used before it is proved; rows wider than the grid are split; a card's column follows the cards that use it.
Statements that nothing in the chapter uses in a proof get a shorter card. The arrows are the chapter's proof
uses, and the build fails if they are not exactly the module's EXPECTED. Dashed arrows are results a proof names
in its text without listing them as uses, checked the same way against HYPOTHESES; one that would point upward is
listed instead of drawn. R3 is the hand-laid-out original of this form."""
import collections
import re

import bp
from bp import PROV_ACCENT, abridge, names, node, paragraphs, rich
from lib import Canvas

W = 3400
G = 64
S = 13.5
NCOLS = 5


def band(c, x, y, title, sub=None):
    c.text(x, y + 22, title, 22, "ink", bold=True)
    if sub:
        return y + 40 + c.para(x, y + 36, c.x1 - x, sub, 14.5, "muted") + 14
    return y + 54


def hypotheses(g, stmts):
    """(a, b): the proof text of b names a, a result of the chapter, which the uses of b do not list."""
    inside = set(stmts)
    out = []
    for b in stmts:
        pf = bp.proof(g, b) or ""
        for a in sorted(set(re.findall(r"\[([a-z0-9-]+)\]", pf))):
            if a in inside and a != b and a not in g.uses(b) and g.nodes[a]["kind"] != "definition":
                out.append((a, b))
    return out


def layout(stmts, edges, dashed, path_of, section_of):
    """-> rows: list of lists of (id, column); drawn_dashed: the dashed edges that point downward."""
    users = {k: set() for k in stmts}
    for a, b in edges:
        users[a].add(b)

    def reaches(x, y):
        seen, stack = set(), [x]
        while stack:
            v = stack.pop()
            if v == y:
                return True
            if v in seen:
                continue
            seen.add(v)
            stack.extend(users[v])
        return False

    drawn_dashed = []
    for a, b in dashed:                     # a dashed edge joins the order only if it keeps it acyclic
        if not reaches(b, a):
            users[a].add(b)
            drawn_dashed.append((a, b))
    memo = {}

    def d(k):                               # distance to the foot: longest chain of users below k
        if k not in memo:
            memo[k] = 0 if not users[k] else 1 + max(d(b) for b in users[k])
        return memo[k]

    D = max(d(k) for k in stmts)
    uses_of = {k: {a for a in stmts if k in users[a]} for k in stmts}
    rowno = {}
    for k in stmts:
        if not users[k] and not uses_of[k]:
            rowno[k] = -1                   # unconnected: a row of their own at the top
        else:
            rowno[k] = D - d(k)             # as low as its users allow
    # pack: a row wider than the grid sends the cards with the most slack up into the nearest row with room,
    # never above the cards they use
    count = collections.Counter(rowno.values())
    for r in sorted(set(rowno.values()), reverse=True):
        if r < 0:
            continue
        while count[r] > NCOLS:
            movable = []
            for k in stmts:
                if rowno[k] != r:
                    continue
                lo = max([rowno[a] for a in uses_of[k]] + [0]) + 1 if uses_of[k] else 0
                dest = [q for q in range(r - 1, lo - 1, -1) if count[q] < NCOLS]
                if dest:
                    movable.append((r - lo, k, dest[0]))
            if not movable:
                break
            movable.sort(key=lambda t: (-t[0], t[1]))
            _, k, q = movable[0]
            count[r] -= 1
            count[q] += 1
            rowno[k] = q
    logical = collections.defaultdict(list)
    for k, r in rowno.items():
        logical[r].append(k)
    rows, col = [], {}
    for r in sorted(logical, reverse=True):          # from the foot up, so users are placed first
        ks = logical[r]

        def bary(k):
            us = [col[b] for b in users[k] if b in col]
            return sum(us) / len(us) if us else (NCOLS - 1) / 2

        ks.sort(key=lambda k: (section_of(k), bary(k), path_of(k)))
        chunks = [ks[i:i + NCOLS] for i in range(0, len(ks), NCOLS)]
        placed = []
        for chunk in reversed(chunks):               # the chunk nearest the users goes lowest
            chunk.sort(key=lambda k: (bary(k), path_of(k)))
            taken, row = set(), []
            for k in chunk:
                want = max(0, min(NCOLS - 1, round(bary(k))))
                cands = [want + i for i in range(NCOLS)] + [want - i for i in range(1, NCOLS)]
                c_ = next(c for c in cands if 0 <= c < NCOLS and c not in taken)
                taken.add(c_)
                col[k] = c_
                row.append((k, c_))
            placed.append(sorted(row, key=lambda t: t[1]))
        rows = list(reversed(placed)) + rows
    return rows, drawn_dashed


def build(ID, CH, EXPECTED, HYPOTHESES):
    g = bp.load()
    mirror = bp.read_mirror()
    stmts = sorted(k for k in g.statements if g.nodes[k]["_chapter"] == CH)
    drawn = set(stmts)
    edges = [(a, b) for b in stmts for a in g.proof_uses(b) if a in drawn]
    if set(edges) != set(EXPECTED):
        raise ValueError(f"{ID}: arrows and proof uses differ: {sorted(set(edges) ^ set(EXPECTED))}")
    hyp = hypotheses(g, stmts)
    if set(hyp) != set(HYPOTHESES):
        raise ValueError(f"{ID}: hypotheses named in proofs differ: {sorted(set(hyp) ^ set(HYPOTHESES))}")
    rev = g.used_by()
    depth, _ = g.depths(g.roots())
    main_names = {t["name"] for t in mirror["theorems"]}
    sections = sorted((k for k, v in g.nodes.items() if v["kind"] == "section" and v["_chapter"] == CH),
                      key=lambda k: g.nodes[k].get("order", 0))
    sec_dir = {s: g.nodes[s]["_path"].rsplit("/", 1)[0] + "/" for s in sections}

    def section_of(k):
        p = g.nodes[k]["_path"]
        for i, s in enumerate(sections):
            if p.startswith(sec_dir[s]):
                return i
        return len(sections)

    def under(sec):
        return sorted(k for k in stmts if g.nodes[k]["_path"].startswith(sec_dir[sec]))

    ch = g.nodes[CH]
    rows, drawn_dashed = layout(stmts, edges, hyp, lambda k: g.nodes[k]["_path"], section_of)
    not_drawn = [e for e in hyp if e not in drawn_dashed]
    is_head = {k for k in stmts if g.nodes[k]["_path"].endswith("_section.md") or g.nodes[k]["_path"].count("/") == 1}
    compact = {k for k in stmts if k not in is_head}
    roots = [k for k in stmts if g.nodes[k]["kind"] != "definition" and g.nodes[k]["_path"].count("/") <= (
        2 if g.nodes[k]["_path"].endswith("_section.md") else 1)]
    main = sorted(roots, key=lambda k: (g.nodes[k].get("order", 0), k))[0]

    imports, exports = collections.Counter(), collections.Counter()
    by_chapter = collections.Counter()
    for k in stmts:
        for u in g.uses(k):
            if u not in drawn:
                imports[u] += 1
                by_chapter[g.nodes[u]["_chapter"]] += 1
        for u in rev[k]:
            if u not in drawn:
                exports[k] += 1
    n_edges_lane = collections.Counter()
    rowof_tmp = {k: i for i, row in enumerate(rows) for k, _ in row}
    for a, b in edges + drawn_dashed:
        n_edges_lane[rowof_tmp[a]] += 1
        n_edges_lane[rowof_tmp[b] - 1] += 1
    VG = max(96, 12 * max(n_edges_lane.values(), default=0) + 24)

    intro = rich(paragraphs(bp.body(g, CH))[0])
    c = Canvas(ID, f"{ch['title']}: every statement of the chapter, and what each one rests on",
               f"The blueprint's chapter {ch.get('order')} in one poster: its {len(stmts)} statements as cards, "
               "each with the Lean declaration it stands for, the statement in words, how its proof goes, and "
               "what it uses and is used by. **Read it from the foot up**: the chapter's theorem, "
               f"`{main}`, is at the bottom, and every card stands above the cards whose proofs use it. An arrow "
               "from A to B says that the proof of B uses A; a dashed arrow says that the proof of B names A "
               "without listing it as a use. The statements that head a section or a group of results have "
               "full cards; the others are drawn shorter. "
               "The chapter's own introduction: " + abridge(intro, 700) + " **No Lean was built**: see diagram "
               "R1, band 5.",
               W, f"`riemann-blueprint` at {g.bp_commit} (`{ch['_path'].rsplit('/', 1)[0]}/`: the chapter's and "
               "every section's `_section.md`, every statement's front matter, body and proof; `lean-facts.json` "
               "for the signatures, files and lines); `leanprover-community/riemann-hypothesis` at "
               f"{mirror['commit']} (`src/Main.lean`). The layout is computed from the chapter's own edges; the "
               "dashed arrows, the abridgements and the import counts are the diagram's own, as marked.",
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
    y += c.legend(X0, y, [("box", "green", "new in Alpöge's proof"), ("box", "amber", "modified from the literature"),
                          ("box", "blue", "published"),
                          ("arrow", "muted", "A → B: the proof of B uses A (the arrow takes A's colour)"),
                          ("arrow", "amber", "A ⇢ B: the proof of B names A without listing it as a use (dashed)", "7 5")],
                  title="Legend") + 26
    key = [
        "**Title and pill.** The title is the blueprint's; the pill gives the kind and the provenance: **new** in "
        "Alpöge's proof, **modified** from a published result, or **published** as it stands.",
        "**The Lean panel** is the signature of the first declaration the blueprint lists for the statement, as "
        "`lean-facts.json` records it, wrapped and cut at nine lines (four on a short card). The footer gives its "
        "file and line in the mirror and the other declarations.",
        "**The line in italics** is the blueprint's statement, and **the bullets** are its proof, paragraph by "
        "paragraph, abridged where marked with …; links appear as `ids` and maths is rewritten in plain Unicode.",
        "**Stated with**, **Proof uses** and **Used by** are the blueprint's edges. A proof use outside the "
        "chapter is counted, not drawn. **Rows**: a card's row is one above the highest card whose proof uses it, "
        "or higher where that makes room; a card sits under the cards that use it where it can. A short card "
        "shows four lines of the signature and one paragraph of the proof.",
    ]
    imp = [f"The chapter's proofs and statements use {sum(imports.values())} results outside it, "
           + ", ".join(f"{n} from `{ch_}`" for ch_, n in by_chapter.most_common()) + "."]
    if imports:
        imp.append("**Used most** " + ", ".join(f"`{u}` ({n})" for u, n in imports.most_common(8)) + ".")
    if exports:
        imp.append("**Used by other chapters** " + ", ".join(f"`{k}` ({n})" for k, n in exports.most_common(8)) + ".")
    else:
        imp.append("No statement of the chapter is used outside it.")
    hyp_body = []
    if hyp:
        hyp_body.append("The proof texts of these statements name a result of the chapter that their `uses` lists "
                        "leave out. Either the Lean theorem takes it as a hypothesis, or the blueprint's edge "
                        "resolution missed it; the diagram cannot tell which.")
        hyp_body.append("**Drawn dashed** " + (", ".join(f"`{a}` ⇢ `{b}`" for a, b in drawn_dashed) or "none") + ".")
        if not_drawn:
            hyp_body.append("**Named, not drawn** (it would point upward): "
                            + ", ".join(f"`{a}` in the proof of `{b}`" for a, b in not_drawn) + ".")
    else:
        hyp_body.append("Every result a proof in this chapter names in its text is also in its `uses` list. There "
                        "are no dashed arrows.")
    hk = max(c.card(0, 0, span(2), "How to read a node", key, draw=False, size=S),
             c.card(0, 0, span(2), "What the chapter uses from outside, and what uses it", imp, draw=False, size=S),
             c.card(0, 0, span(1), "Named in a proof, not listed as a use", hyp_body, draw=False, size=S))
    c.card(colx(0), y, span(2), "How to read a node", key, "grey", h=hk, size=S, tint=False)
    c.card(colx(2), y, span(2), "What the chapter uses from outside, and what uses it", imp, "grey", h=hk, size=S,
           tint=False)
    c.card(colx(4), y, span(1), "Named in a proof, not listed as a use", hyp_body, "amber", h=hk, size=S,
           tint=bool(hyp))
    y += hk + 50

    # ---------------------------------------------------------------------------------- the grid
    y = band(c, X0, y, "2 · The chapter, from its leaves down to its theorem",
             f"{len(rows)} rows. Section by section the chapter runs: "
             + "; ".join(f"{g.nodes[s].get('order')}. {g.nodes[s]['title']} ({len(under(s))})" for s in sections)
             + ". The cards keep that order within a row where the arrows allow.")
    pos, rowof = {}, {}
    for r, row in enumerate(rows):
        items = [(k, i, bp.statement_card(g, k, CW, drawn, rev, depth, main_names, ID, compact=k in compact))
                 for k, i in row]
        hh = max(node(c, 0, 0, CW, draw=False, **kw) for _, _, kw in items)
        for k, i, kw in items:
            node(c, colx(i), y, CW, h=hh, **kw)
            pos[k] = (colx(i), y, CW, hh)
            rowof[k] = r
        y += hh + VG
    y -= VG
    bp.arrows(c, pos, rowof, edges + drawn_dashed, lambda a: PROV_ACCENT[g.nodes[a].get("provenance")], VG, G,
              X0, X1, NCOLS, colx, dashed=drawn_dashed)

    # ---------------------------------------------------------------------------------- the chapter's own account
    y += 60
    y = band(c, X0, y, "3 · The argument in the chapter's own words, section by section",
             "The first paragraph of each section's introduction in the blueprint, in the chapter's order, with "
             "the statements each section holds. Abridged where marked with ….")
    cards = []
    for sec in sections:
        n = g.nodes[sec]
        body_ = bp.body(g, sec)
        paras = paragraphs(body_)
        intro_s = abridge(rich(paras[0]), 900) if paras else "The blueprint gives this section no introduction."
        cards.append((f"{n.get('order')}. {n['title']}", [intro_s, "**Holds** " + names(under(sec), 8)]))
    for i in range(0, len(cards), NCOLS):
        chunk = cards[i:i + NCOLS]
        hh = max(c.card(0, 0, CW, t, b, draw=False, size=S) for t, b in chunk)
        for j, (t, b) in enumerate(chunk):
            c.card(colx(j), y, CW, t, b, "teal", h=hh, size=S, tint=False)
        y += hh + 30
    held_all = sum(len(under(s)) for s in sections)
    at_root = [k for k in stmts if g.nodes[k]["_path"].count("/") == 1 or (
        g.nodes[k]["_path"].endswith("_section.md") and g.nodes[k]["_path"].count("/") == 2)]
    c.text(X0, y + 15, f"{held_all} statements in the {len(sections)} sections, and {len(at_root)} at the chapter's "
           "root: " + names(at_root) + ".", 13.5, "muted")
    return c
