"""R2 — The proof, chapter by chapter: the nine chapters of the blueprint, what each proves, and which chapters use
which.

Each chapter is one card: its main theorem's Lean signature, the chapter's own introduction, its sections with
their statement counts, and the chapters it uses and is used by. The arrows are the chapters' `uses` edges, and the
build fails if they are not exactly the ones listed in EXPECTED. The table at the foot lists the published results
the proof cites most, counted from the blueprint's edges."""
import re

import bp
from bp import abridge, code, names, node, paragraphs, rich
from lib import Canvas

ID, SLUG = "R2", "chapters"

W = 3400
G = 64
VG = 96
S = 13.5

# Where each chapter sits: id -> (row, column, columns spanned). Used chapters sit above their users.
PLACE = {
    "chap-literature": (0, 0, 3),
    "chap-theta": (1, 0, 2), "chap-heights": (1, 2, 1), "chap-galois": (1, 3, 2),
    "chap-sha": (2, 2, 3),
    "chap-families": (3, 0, 3),
    "chap-zero-free": (4, 0, 3),
    "architecture": (5, 0, 3), "main-theorems": (5, 3, 2),
}
# What each chapter proves: the first result, by the blueprint's order, among the statements at the chapter's root.
CHAPTER_THEOREM = {
    "chap-zero-free": "thm-zero-free-from-connected", "chap-families": "thm-family-data-exists",
    "chap-theta": "thm-theta-inputs", "chap-heights": "thm-covolume-bound", "chap-sha": "thm-sha-bound",
    "chap-galois": "thm-galois-reps-polarized", "architecture": "thm-grh-from-galois",
    "main-theorems": "thm-half-plane", "chap-literature": None,
}
ACCENT = {"chap-literature": "blue", "main-theorems": "amber", "architecture": "grey"}
# The `uses` edges between chapters, (used, user). The build fails if the blueprint has others.
EXPECTED = [
    ("architecture", "main-theorems"),
    ("chap-zero-free", "architecture"), ("chap-families", "architecture"), ("chap-sha", "architecture"),
    ("chap-galois", "architecture"),
    ("chap-families", "chap-zero-free"), ("chap-literature", "chap-zero-free"),
    ("chap-theta", "chap-families"), ("chap-heights", "chap-families"), ("chap-sha", "chap-families"),
    ("chap-galois", "chap-families"), ("chap-literature", "chap-families"),
    ("chap-galois", "chap-sha"), ("chap-literature", "chap-sha"),
    ("chap-literature", "chap-galois"), ("chap-literature", "chap-heights"), ("chap-literature", "chap-theta"),
]
TOP_N = 12


def band(c, x, y, title, sub=None):
    c.text(x, y + 22, title, 22, "ink", bold=True)
    if sub:
        return y + 40 + c.para(x, y + 36, c.x1 - x, sub, 14.5, "muted") + 14
    return y + 54


def build():
    g = bp.load()
    mirror = bp.read_mirror()
    if set(PLACE) != g.chapters:
        raise ValueError(f"R2 does not draw exactly the blueprint's chapters: {sorted(set(PLACE) ^ g.chapters)}")
    edges = [(u, k) for k in sorted(g.chapters) for u in g.nodes[k].get("uses", []) if u in g.chapters]
    if set(edges) != set(EXPECTED):
        raise ValueError(f"R2: arrows and chapter uses differ: {sorted(set(edges) ^ set(EXPECTED))}")
    rev = g.used_by()
    in_chapter = {ch: sorted(k for k in g.statements if g.nodes[k]["_chapter"] == ch) for ch in g.chapters}
    sections = {ch: sorted([k for k, v in g.nodes.items() if v["kind"] == "section" and v["_chapter"] == ch],
                           key=lambda k: g.nodes[k].get("order", 0)) for ch in g.chapters}

    def under(sec):
        d = g.nodes[sec]["_path"].rsplit("/", 1)[0] + "/"
        return [k for k in g.statements if g.nodes[k]["_path"].startswith(d)]

    for ch, t in CHAPTER_THEOREM.items():
        roots = sorted([k for k in in_chapter[ch] if g.nodes[k]["kind"] in bp.RESULTS
                        and g.nodes[k]["_path"].count("/") <= (2 if g.nodes[k]["_path"].endswith("_section.md") else 1)],
                       key=lambda k: (g.nodes[k].get("order", 0), k))
        if (roots[0] if roots else None) != t:
            raise ValueError(f"R2: the first result at the root of {ch} is {roots[:1]}, not {t}")

    c = Canvas(ID, "The proof, chapter by chapter: what each chapter of the blueprint proves, and which chapters "
               "use which",
               "The blueprint reads Alpöge's formal proof as nine chapters: the main theorems, an outline, five "
               "chapters that each carry out one stage of the argument, and a chapter of published results. Each "
               "card is one chapter: the Lean declaration of the theorem it proves, the chapter's own introduction, "
               "its sections with the number of statements in each, and the chapters it uses. An arrow from A to B "
               "says that chapter B uses chapter A; **read it from the foot up**, as diagram R1. The table at the "
               "foot counts which published results the proof leans on most. **No Lean was built** for the "
               "blueprint; see band 5 of diagram R1 for what is known about the formal proof.",
               W, f"`riemann-blueprint` at {g.bp_commit} (every chapter's `_section.md`: its uses, order and "
               "introduction; every section's title and order; every statement's chapter, provenance, source and "
               "uses; `lean-facts.json` for the signatures); `leanprover-community/riemann-hypothesis` at "
               f"{mirror['commit']} (`src/Main.lean`). The statement counts, the citation counts and the "
               "abridgements are the diagram's own.",
               state=f"State drawn: riemann-blueprint at {g.bp_commit}, which pins the mirror at {g.mirror_pin}; "
                     f"Main.lean from the mirror at {mirror['commit']}")
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    CW = (WW - 4 * G) / 5

    def colx(i):
        return X0 + i * (CW + G)

    def span(n):
        return n * CW + (n - 1) * G

    def chapter_node(ch, w):
        n = g.nodes[ch]
        stmts = in_chapter[ch]
        prov = {}
        for k in stmts:
            p = g.nodes[k].get("provenance") or "unlabelled"
            prov[p] = prov.get(p, 0) + 1
        t = CHAPTER_THEOREM[ch]
        cols = bp.columns(w)
        if t is None:
            refs = len([p for p in (bp.BLUEPRINT / "references").glob("*.md")])
            formula = [(0, f"no theorem of its own: {len(stmts)} statements in {len(sections[ch])} sections, "
                           f"cited from {refs} references", True)]
        elif not g.nodes[t].get("lean"):
            formula = [(0, f"{t} has no Lean declaration: it is the blueprint's own grouping of the chapter's "
                           f"results", True)]
        else:
            first = g.nodes[t]["lean"][0]
            fact = g.lean_facts.get(first)
            if not fact or not fact.get("signature"):
                raise ValueError(f"R2: lean-facts.json has no signature for {first}")
            formula = bp.lean_block(fact["signature"], cols, 8)
        say = abridge(rich(paragraphs(bp.body(g, ch))[0]), 900 if w > span(1) + 1 else 620)
        bullets = []
        for sec in sections[ch]:
            bullets.append(f"**{g.nodes[sec]['title']}** (`{sec}`): {len(under(sec))} statements")
        if not bullets:
            bullets.append("No sections: the chapter is its statements.")
        uses = [u for u in n.get("uses", []) if u in g.chapters]
        users = sorted(k for k in g.chapters if ch in g.nodes[k].get("uses", []))
        foot = ["**Uses** " + (names(uses) if uses else "no other chapter"),
                "**Used by** " + (names(users) if users else "no other chapter: it states the results"),
                f"**Statements** {len(stmts)}: " + ", ".join(f"{v} {k}" for k, v in sorted(prov.items()))]
        if t is not None:
            lean = g.nodes[t].get("lean", [])
            foot.append(f"**Main theorem** `{t}`: {g.nodes[t]['title']}"
                        + (f" · Lean {code(lean[0])} at {code(g.lean_location(lean[0]))}" if lean else ""))
        foot.append(f"Blueprint `{n['_path'].rsplit('/', 1)[0]}/`")
        acc = ACCENT.get(ch, "green")
        return dict(name=f"{n.get('order', '')}. {n['title']}", accent=acc, pill=f"chapter · {len(stmts)} statements",
                    formula=formula, say=say, bullets=bullets, foot=foot)

    key = [
        "**The Lean panel** is the signature of the theorem at the chapter's root, the one the chapter exists to "
        "prove, as `lean-facts.json` records it; cut at eight lines. The footer names it and gives its file and "
        "line in the mirror.",
        "**The line in italics** is the first paragraph of the chapter's own introduction, abridged where marked "
        "with …. **The bullets** are its sections in order, each with the number of statements under it.",
        "**Uses** and **Used by** are the chapter `uses` lines of the blueprint. **An arrow from A to B**: chapter "
        "B uses chapter A, and the arrow takes A's colour.",
        "Colours: the chapters of the new argument are green, the published results blue, the main theorems "
        "amber and the outline grey.",
    ]
    arch = [rich(p) for p in paragraphs(bp.body(g, "architecture"))]
    stages = [p for p in arch if re.match(r"(Galois|The Tate|Families|Slope|Landau)", p)]
    if len(stages) != 5:
        raise ValueError(f"R2: the architecture chapter's introduction does not list five stages: {len(stages)}")
    checks = [abridge(rich(p), 420) for p in paragraphs(bp.body(g, "rem-points-to-check"))]
    if len(checks) < 3:
        raise ValueError("R2: rem-points-to-check has fewer than three paragraphs to list")

    y = c.y
    y = band(c, X0, y, "The chapters, from the literature up to the main theorems",
             "Published results at the top; the five stages of the argument in the middle, each a chapter; the "
             "outline and the main theorems at the foot. Nothing is used before it is proved.")
    y += c.legend(X0, y, [("box", "green", "a stage of the new argument"), ("box", "blue", "published results"),
                          ("box", "amber", "the main theorems"), ("box", "grey", "the outline"),
                          ("arrow", "muted", "A → B: chapter B uses chapter A (the arrow takes A's colour)")],
                  title="Legend") + 26
    rows, rowof, pos = {}, {}, {}
    for k, (r, i, n) in PLACE.items():
        rows.setdefault(r, []).append((k, i, n))
        rowof[k] = r
    # The cards that are not chapters: row -> (column, columns spanned, title, body, accent). They are registered
    # with the arrow router as obstacles, so no arrow is routed through them.
    EXTRA = {0: (3, 2, "How to read a chapter", key, "grey"),
             2: (0, 2, "The five stages of the proof (the architecture chapter's own list)",
                 [abridge(s, 460) for s in stages], "grey"),
             3: (3, 2, "Points to check first (the blueprint's own list, `rem-points-to-check`)", checks[:6], "red")}
    for r in sorted(rows):
        items = [(k, i, n, chapter_node(k, span(n))) for k, i, n in rows[r]]
        hh = max(node(c, 0, 0, span(n), draw=False, **kw) for _, _, n, kw in items)
        ex = EXTRA.get(r)
        if ex:
            hh = max(hh, c.card(0, 0, span(ex[1]), ex[2], ex[3], draw=False, size=S))
        for k, i, n, kw in items:
            node(c, colx(i), y, span(n), h=hh, **kw)
            pos[k] = (colx(i), y, span(n), hh)
        if ex:
            c.card(colx(ex[0]), y, span(ex[1]), ex[2], ex[3], ex[4], h=hh, size=S, tint=ex[4] == "red")
            pos[f"_extra{r}"], rowof[f"_extra{r}"] = (colx(ex[0]), y, span(ex[1]), hh), r
        y += hh + VG
    y -= VG
    bp.arrows(c, pos, rowof, edges, lambda a: ACCENT.get(a, "green"), VG, G, X0, X1, 5, colx)

    # ---------------------------------------------------------------------------------- the literature
    y += 60
    lit = sorted(k for k in g.statements if g.nodes[k]["_chapter"] == "chap-literature")
    y = band(c, X0, y, "What the proof cites from the literature most",
             f"The {TOP_N} published results with the most citing statements, counted from the blueprint's `uses` "
             f"edges over all {len(lit)} statements of the published-results chapter. The source is the "
             "blueprint's; the count is the diagram's.")
    top = sorted(lit, key=lambda k: (-len(rev[k]), k))[:TOP_N]
    trows = []
    for k in top:
        n = g.nodes[k]
        chs = {}
        for u in rev[k]:
            ch = g.nodes[u]["_chapter"]
            chs[ch] = chs.get(ch, 0) + 1
        by_ch = ", ".join(f"{v} in `{c_}`" for c_, v in sorted(chs.items(), key=lambda x: -x[1]))
        trows.append([k, n["title"], rich(n.get("source") or "—"), bp.PROV_LABEL[n.get("provenance")],
                      f"{len(rev[k])}: {by_ch}"])
    tw = [330, 520, 620, 200]
    ht = c.table(X0, y, [("Statement", tw[0], {"mono": True}), ("Title", tw[1]), ("Source", tw[2]),
                         ("Provenance", tw[3]), ("Citing statements", WW - sum(tw) - 760)], trows, size=S)
    kx = X1 - 700
    c.card(kx, y, 700, "Checked, and proved", [
        f"The blueprint has {len(g.statements)} statements: " + ", ".join(
            f"{v} {k}" for k, v in sorted({p: sum(1 for s in g.statements if (g.nodes[s].get('provenance') or 'unlabelled') == p)
                                           for p in ('new', 'modified', 'published', 'unlabelled')}.items())) + ".",
        "**Built**: the mirror's notes list independent complete builds of the submission by Lean v4.33.1.",
        "**Judged**: the Comparator run, which replays the five theorems in independent kernels, had no result "
        "recorded at the state drawn. Diagram R1, band 5, has the details.",
    ], "amber", size=S, h=ht)
    return c
