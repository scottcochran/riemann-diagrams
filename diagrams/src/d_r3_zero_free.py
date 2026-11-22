"""R3 — The zero-free chapter from the inside: from prime sums to the zero-free half-plane, lemma by lemma.

Every statement of the blueprint's chapter `chap-zero-free` is a card (bp.statement_card): the Lean signature, the
statement, the proof, the uses. Solid arrows are the proof uses within the chapter, and the build fails if they are
not exactly EXPECTED. Dashed arrows are the two hypotheses the chapter theorem takes rather than proves: the
blueprint's proof text names their sources, but its `uses` list does not, and the build checks the text."""
import bp
from bp import PROV_ACCENT, abridge, names, node, paragraphs, rich
from lib import Canvas

ID, SLUG = "R3", "zero-free"
CH = "chap-zero-free"
THM = "thm-zero-free-from-connected"

W = 3400
G = 64
VG = 96
S = 13.5

# Where each statement sits: id -> (row, column, columns spanned). Used statements sit above their users; the
# definitions are the top row, the chapter's theorem the foot. Read down the columns: Landau's theorem on the
# left, the core inequality next to it, the lattice argument across the top and down the right.
PLACE = {
    "def-chebyshev-weighted": (0, 0, 1), "def-zero-free-primitive": (0, 1, 1), "def-auxiliary-field-data": (0, 2, 1),
    "def-slope-data": (0, 3, 1), "def-connected-families": (0, 4, 1),
    "thm-mean-value-bad-shares": (1, 0, 1), "prop-block-sums-ranges": (1, 1, 1), "prop-block-bounds-from-four": (1, 2, 1),
    "thm-fock-bad-share-mean": (1, 3, 1), "thm-local-estimate-inert-primes": (1, 4, 1),
    "thm-landau-windows": (2, 0, 1), "thm-chain-averaging": (2, 1, 1), "thm-large-summand-low-degree": (2, 2, 1),
    "thm-prime-sums-lattice-gains": (2, 3, 1), "lem-served-twists-prime-sums": (2, 4, 1),
    "thm-zero-free-from-windows": (3, 0, 1), "thm-member-gap-bound": (3, 1, 1), "lem-behrend-sets": (3, 2, 1),
    "thm-twisted-admissibility": (3, 4, 1),
    "lem-good-auxiliary-primes": (4, 0, 1), "thm-core-inequality": (4, 1, 1), "thm-families-connected": (4, 3, 1),
    "thm-auxiliary-fields": (5, 0, 1), THM: (5, 1, 3),
}
# The proof-use edges within the chapter, (used, user). The build fails if the blueprint has others.
EXPECTED = [
    ("thm-mean-value-bad-shares", "prop-block-sums-ranges"), ("prop-block-sums-ranges", "prop-block-bounds-from-four"),
    ("prop-block-bounds-from-four", "thm-fock-bad-share-mean"),
    ("thm-fock-bad-share-mean", "thm-prime-sums-lattice-gains"),
    ("thm-local-estimate-inert-primes", "thm-prime-sums-lattice-gains"),
    ("thm-large-summand-low-degree", "thm-prime-sums-lattice-gains"),
    ("lem-served-twists-prime-sums", "thm-twisted-admissibility"),
    ("thm-prime-sums-lattice-gains", "thm-families-connected"), ("lem-behrend-sets", "thm-families-connected"),
    ("thm-twisted-admissibility", "thm-families-connected"),
    ("thm-landau-windows", "thm-zero-free-from-windows"), ("thm-zero-free-from-windows", THM),
    ("thm-chain-averaging", "thm-core-inequality"), ("thm-member-gap-bound", "thm-core-inequality"),
    ("thm-core-inequality", THM), ("def-slope-data", THM),
    ("lem-good-auxiliary-primes", "thm-auxiliary-fields"),
]
# The hypotheses: named in the proof text of THM as the source of its two hypotheses, absent from its uses.
HYPOTHESES = [("thm-families-connected", THM), ("thm-auxiliary-fields", THM)]
# The cards that are not statements: row -> (column, columns spanned, title, accent, body key)
EXTRA = {3: (3, 1, "How to read a node", "grey", "key"), 4: (2, 1, "The two hypotheses", "amber", "hyp"),
         5: (4, 1, "What the chapter uses from outside", "grey", "imports")}


def band(c, x, y, title, sub=None):
    c.text(x, y + 22, title, 22, "ink", bold=True)
    if sub:
        return y + 40 + c.para(x, y + 36, c.x1 - x, sub, 14.5, "muted") + 14
    return y + 54


def build():
    g = bp.load()
    mirror = bp.read_mirror()
    stmts = sorted(k for k in g.statements if g.nodes[k]["_chapter"] == CH)
    if set(PLACE) != set(stmts):
        raise ValueError(f"R3 does not draw exactly the chapter's statements: {sorted(set(PLACE) ^ set(stmts))}")
    drawn = set(PLACE)
    edges = [(a, b) for b in sorted(drawn) for a in g.proof_uses(b) if a in drawn]
    if set(edges) != set(EXPECTED):
        raise ValueError(f"R3: arrows and proof uses differ: {sorted(set(edges) ^ set(EXPECTED))}")
    thm_proof = bp.proof(g, THM) or ""
    for a, b in HYPOTHESES:
        if f"[{a}]" not in thm_proof:
            raise ValueError(f"R3: the proof of {b} does not name {a}")
        if a in g.uses(b):
            raise ValueError(f"R3: {a} is a use of {b}; draw it solid")
    rev = g.used_by()
    depth, _ = g.depths(g.roots())
    main_names = {t["name"] for t in mirror["theorems"]}
    sections = sorted((k for k, v in g.nodes.items() if v["kind"] == "section" and v["_chapter"] == CH),
                      key=lambda k: g.nodes[k].get("order", 0))
    if len(sections) != 5:
        raise ValueError(f"R3: the chapter has {len(sections)} sections, the diagram draws five")

    def under(sec):
        d = g.nodes[sec]["_path"].rsplit("/", 1)[0] + "/"
        return sorted(k for k in stmts if g.nodes[k]["_path"].startswith(d))

    imports = {k: [u for u in g.uses(k) if u not in drawn] for k in stmts}
    imports = {k: v for k, v in imports.items() if v}
    exported = {k: [u for u in rev[k] if u not in drawn] for k in stmts}
    exported = {k: v for k, v in exported.items() if v}
    ch = g.nodes[CH]

    c = Canvas(ID, f"{ch['title']}: the analytic half of the proof, lemma by lemma",
               "The chapter proves one theorem: if families of definite unitary groups carry slope data, and "
               "auxiliary CM fields exist at every scale of long windows, then no primitive Dirichlet L-function "
               "vanishes right of the critical line. Its blueprint chapter has five sections and 24 statements, and "
               "every one is a card here: the Lean declaration, the statement, the proof and what it uses. "
               "**Read it from the foot up**: the theorem is at the bottom, its two inputs stand on either side, "
               "and each column above is one strand of the argument. An arrow from A to B says that the proof "
               "of B uses A; a dashed arrow says that B takes A as a hypothesis, which the proof text names and "
               "the uses list does not. The blueprint says of this chapter that the square root in the core "
               "inequality is the Riemann Hypothesis. **No Lean was built**: see diagram R1, band 5.",
               W, f"`riemann-blueprint` at {g.bp_commit} (`{ch['_path'].rsplit('/', 1)[0]}/`: the chapter's and "
               "every section's `_section.md`, every statement's front matter, body and proof; `lean-facts.json` "
               "for the signatures, files and lines); `leanprover-community/riemann-hypothesis` at "
               f"{mirror['commit']} (`src/Main.lean`, for the Main.lean pills). The layout, the two hypothesis "
               "arrows, the abridgements and the import table are the diagram's own, as marked.",
               state=f"State drawn: riemann-blueprint at {g.bp_commit}, which pins the mirror at {g.mirror_pin}; "
                     f"Main.lean from the mirror at {mirror['commit']}")
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    CW = (WW - 4 * G) / 5

    def colx(i):
        return X0 + i * (CW + G)

    def span(n):
        return n * CW + (n - 1) * G

    key = [
        "**Title and pill.** The title is the blueprint's; the pill gives the kind and the provenance: **new** in "
        "Alpöge's proof, **modified** from a published result, or **published** as it stands.",
        "**The Lean panel** is the signature of the first declaration the blueprint lists for the statement, as "
        "`lean-facts.json` records it, wrapped and cut at nine lines. The footer gives its file and line in the "
        "mirror and the other declarations.",
        "**The line in italics** is the blueprint's statement, and **the bullets** are its proof, paragraph by "
        "paragraph, abridged where marked with …; links appear as `ids` and maths is rewritten in plain Unicode.",
        "**Stated with**, **Proof uses** and **Used by** are the blueprint's edges. A statement used by nothing in "
        "this chapter is used elsewhere: the footer says where. **An arrow from A to B**: the proof of B uses A, "
        "and the arrow takes A's colour.",
    ]
    hyp = [
        f"`{THM}` is stated with two hypotheses: that families have slope data (`def-connected-families`), and "
        "that auxiliary CM fields with the properties of `thm-auxiliary-fields` exist at the scales of long "
        "windows.",
        "Its proof says that hypothesis 1 comes from `thm-families-connected` and hypothesis 2 from "
        "`thm-auxiliary-fields`, and proves neither: the Lean theorem takes them as arguments. The blueprint's "
        "`uses` list for the proof names neither, so no solid arrow joins them.",
        "The dashed arrows are the diagram's reading of that sentence. The theorem that discharges both "
        "hypotheses is `thm-zero-free-from-families` in the outline chapter (diagram R1, band 3), which cites "
        "all three.",
    ]
    imp = []
    for k in sorted(imports):
        imp.append(f"`{k}` uses " + ", ".join(f"`{u}` ({g.nodes[u]['_chapter'].replace('chap-', '')})"
                                                 for u in imports[k]))
    imp.append("Everything else the chapter uses is in the chapter. Statements used from outside it: "
               + ", ".join(f"`{k}` by {len(v)}" for k, v in sorted(exported.items())) + ".")
    bodies = {"key": key, "hyp": hyp, "imports": imp}

    y = c.y
    y = band(c, X0, y, "The chapter, from its definitions down to its theorem",
             "Top row: the five definitions the chapter is written in. Left column: Landau's theorem, then the "
             "auxiliary fields. Second column: the core inequality. The top row of results and the right half: "
             "the local link at inert primes, from a mean value theorem for bad shares up to the lattice-gain "
             "bound, and slope data from it. Nothing is used before it is proved.")
    y += c.legend(X0, y, [("box", "green", "new in Alpöge's proof"), ("box", "amber", "modified from the literature"),
                          ("box", "blue", "published"),
                          ("arrow", "muted", "A → B: the proof of B uses A (the arrow takes A's colour)"),
                          ("arrow", "amber", "A ⇢ B: B takes A as a hypothesis (dashed; the diagram's reading of the proof text)", "7 5")],
                  title="Legend") + 26
    rows, rowof, pos = {}, {}, {}
    for k, (r, i, n) in PLACE.items():
        rows.setdefault(r, []).append((k, i, n))
        rowof[k] = r
    for r in sorted(rows):
        items = [(k, i, n, bp.statement_card(g, k, span(n), drawn, rev, depth, main_names, "R3")) for k, i, n in rows[r]]
        hh = max(node(c, 0, 0, span(n), draw=False, **kw) for _, _, n, kw in items)
        ex = EXTRA.get(r)
        if ex:
            hh = max(hh, c.card(0, 0, span(ex[1]), ex[2], bodies[ex[4]], draw=False, size=S))
        for k, i, n, kw in items:
            node(c, colx(i), y, span(n), h=hh, **kw)
            pos[k] = (colx(i), y, span(n), hh)
        if ex:
            c.card(colx(ex[0]), y, span(ex[1]), ex[2], bodies[ex[4]], ex[3], h=hh, size=S, tint=ex[3] != "grey")
            pos[f"_extra{r}"], rowof[f"_extra{r}"] = (colx(ex[0]), y, span(ex[1]), hh), r
        y += hh + VG
    y -= VG
    bp.arrows(c, pos, rowof, edges + HYPOTHESES, lambda a: PROV_ACCENT[g.nodes[a].get("provenance")], VG, G, X0, X1,
              5, colx, dashed=HYPOTHESES)

    # ---------------------------------------------------------------------------------- the chapter's own account
    y += 60
    y = band(c, X0, y, "The argument in the chapter's own words, section by section",
             "The first paragraph of each section's introduction in the blueprint, in the chapter's order, with "
             "the statements each section holds. Abridged where marked with ….")
    cards = []
    for i, sec in enumerate(sections):
        n = g.nodes[sec]
        intro = abridge(rich(paragraphs(bp.body(g, sec))[0]), 900)
        held = under(sec)
        body = [intro, "**Holds** " + names(held, 8)]
        cards.append((f"{n.get('order')}. {n['title']}", body))
    hh = max(c.card(0, 0, CW, t, b, draw=False, size=S) for t, b in cards)
    for i, (t, b) in enumerate(cards):
        c.card(colx(i), y, CW, t, b, "teal", h=hh, size=S, tint=False)
    y += hh + 44
    held_all = sum(len(under(s)) for s in sections)
    at_root = [k for k in stmts if g.nodes[k]["_path"].count("/") == 1]
    c.text(X0, y + 15, f"{held_all} statements in the five sections, and {len(at_root)} at the chapter's root: "
           + names(at_root) + ".", 13.5, "muted")
    return c
