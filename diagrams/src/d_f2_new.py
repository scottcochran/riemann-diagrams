"""F2 — What is new: the statements new in Alpöge's proof, where they sit, how they lean on each other, and what
they take from the literature.

Every other poster colours provenance; this one is organised by it. The 200 new statements are too many for one
card each (their own graph has 263 proof-use edges and chains 16 statements long), so the poster works at the level
above: the chapters as cards holding only their new work, arrows for the proof uses between the new statements
of different chapters, labelled with their counts; a chapter-by-chapter matrix of those counts; a table of every
section with its statements by provenance, which is where the new work concentrates; the published and modified
results the new statements lean on most; and the new lemmas that published results' proofs use. The build fails
if the counts, the pairs or the tops differ from what is recorded here."""
import collections

import bp
from bp import code, names
from chapter import band
from lib import Canvas

ID, SLUG = "F2", "new"

W = 3400
G = 64
VG = 120
S = 13.5
NCOLS = 5
TOP_N = 20

# Where each chapter sits, as on R2: id -> (row, column, columns spanned).
PLACE = {
    "chap-literature": (0, 0, 3),
    "chap-theta": (1, 0, 2), "chap-heights": (1, 2, 1), "chap-galois": (1, 3, 2),
    "chap-sha": (2, 2, 3),
    "chap-families": (3, 0, 3),
    "chap-zero-free": (4, 0, 3),
    "architecture": (5, 0, 3), "main-theorems": (5, 3, 2),
}
SHORT = {
    "main-theorems": "Main theorems", "architecture": "Outline", "chap-zero-free": "Zero-free",
    "chap-families": "Families", "chap-theta": "Theta", "chap-heights": "Heights", "chap-sha": "Sha",
    "chap-galois": "Galois", "chap-literature": "Literature",
}
COUNTS = {"new": 200, "modified": 61, "published": 142, "unlabelled": 13}
# Proof uses between new statements of different chapters, (used chapter, user chapter) -> count.
EXPECTED = {
    ("architecture", "chap-families"): 1, ("architecture", "chap-galois"): 1, ("architecture", "chap-sha"): 5,
    ("architecture", "main-theorems"): 1,
    ("chap-families", "architecture"): 2, ("chap-families", "chap-sha"): 2, ("chap-families", "chap-theta"): 1,
    ("chap-galois", "chap-sha"): 3,
    ("chap-heights", "chap-families"): 11,
    ("chap-literature", "chap-galois"): 7, ("chap-literature", "chap-heights"): 4,
    ("chap-sha", "architecture"): 1, ("chap-sha", "chap-families"): 1,
    ("chap-theta", "chap-families"): 16, ("chap-theta", "chap-sha"): 1,
    ("chap-zero-free", "architecture"): 4,
}
# The reading the matrix card gives of the two heaviest cross-chapter flows. The build fails if they are no
# longer these two pairs, so that the sentence is re-read rather than left standing.
HEAVIEST = {("chap-theta", "chap-families"), ("chap-heights", "chap-families")}
# The new statements that no new statement's proof or statement uses: the tops of the new work.
TOPS = [
    "lem-hilbert-samuel-block", "lem-kodaira-spencer-from-rigid-charts", "lem-p-divisible-period-matrices",
    "lem-siegel-minimal-blowup-smooth", "lem-siegel-weil-singular-coefficients", "lem-uniformisation-labelled-cover",
    "thm-additive-characteristic-classes", "thm-critical-line", "thm-critical-line-primitive",
    "thm-galois-reps-from-geometry-and-theta", "thm-kato-zeta-integral", "thm-principalisation-reduces-dimension",
    "thm-reciprocity-fixed-exponent", "thm-riemann-hypothesis", "thm-theta-inputs",
    "thm-universal-first-order-deformation",
]


def build():
    g = bp.load()
    mirror = bp.read_mirror()
    if set(PLACE) != g.chapters or set(SHORT) != g.chapters:
        raise ValueError("F2: PLACE and SHORT must name exactly the blueprint's chapters")
    chapters = sorted(g.chapters, key=lambda ch: (g.nodes[ch].get("order", 0), ch))
    rev = g.used_by()

    def prov(k):
        return g.nodes[k].get("provenance") or "unlabelled"

    def chap(k):
        return g.nodes[k]["_chapter"]

    by_prov = collections.Counter(prov(k) for k in g.statements)
    if dict(by_prov) != COUNTS:
        raise ValueError(f"F2: statements by provenance are {dict(by_prov)}, the poster is written for {COUNTS}")
    new = sorted(k for k in g.statements if prov(k) == "new")
    N = set(new)
    e_proof = [(a, b) for b in new for a in g.proof_uses(b) if a in N]
    e_all = [(a, b) for b in new for a in g.uses(b) if a in N]
    cross = collections.Counter((chap(a), chap(b)) for a, b in e_proof if chap(a) != chap(b))
    if dict(cross) != EXPECTED:
        diff = {p: (cross.get(p), EXPECTED.get(p)) for p in set(cross) | set(EXPECTED) if cross.get(p) != EXPECTED.get(p)}
        raise ValueError(f"F2: cross-chapter proof uses among new statements differ: {diff}")
    users = {k: set() for k in new}
    for a, b in e_all:
        users[a].add(b)
    tops = sorted(k for k in new if not users[k])
    memo = {}

    def depth_below(k):                      # the longest chain of new statements built on k
        if k not in memo:
            memo[k] = 0 if not users[k] else 1 + max(depth_below(b) for b in users[k])
        return memo[k]

    longest = max(depth_below(k) for k in new) + 1
    if tops != TOPS:
        raise ValueError(f"F2: the tops of the new work differ: {sorted(set(tops) ^ set(TOPS))}")
    bottoms = sorted(k for k in new if not any(a in N for a in g.uses(k)))
    matrix = collections.Counter((chap(a), chap(b)) for a, b in e_proof)
    # inputs: the non-new statements the new ones use, and which chapters' new statements use each
    inputs = collections.Counter()
    by_user = collections.defaultdict(collections.Counter)
    for b in new:
        for a in g.uses(b):
            if a not in N:
                inputs[a] += 1
                by_user[a][chap(b)] += 1
    # exports: new statements that non-new statements use
    exports = {k: sorted(u for u in rev[k] if u not in N) for k in new}
    exports = {k: v for k, v in exports.items() if v}
    sections = sorted((k for k, v in g.nodes.items() if v["kind"] == "section"),
                      key=lambda k: (g.nodes[chap(k)].get("order", 0), g.nodes[k].get("order", 0), k))
    sec_dir = {s: g.nodes[s]["_path"].rsplit("/", 1)[0] + "/" for s in sections}

    def under(sec):
        return sorted(k for k in g.statements if g.nodes[k]["_path"].startswith(sec_dir[sec]))

    def at_root(ch):
        return sorted(k for k in g.statements if chap(k) == ch
                      and not any(g.nodes[k]["_path"].startswith(sec_dir[s]) for s in sections if chap(s) == ch))

    rowof_place = {k: r for k, (r, _, _) in PLACE.items()}
    down = {p: n for p, n in cross.items() if rowof_place[p[0]] <= rowof_place[p[1]]}
    up = {p: n for p, n in cross.items() if rowof_place[p[0]] > rowof_place[p[1]]}
    up_edges = [(a, b) for a, b in e_proof if (chap(a), chap(b)) in up]
    heaviest = sorted(cross.items(), key=lambda t: (-t[1], t[0]))[:2]
    if {p for p, _ in heaviest} != HEAVIEST:
        raise ValueError(f"F2: the two heaviest cross-chapter flows are now {heaviest}, not {sorted(HEAVIEST)}; "
                         "re-read the sentence 'the families are built from what those two chapters prove' on "
                         "the matrix card and update HEAVIEST")
    iface_prov = {k: prov(k) for k in ("def-local-parameters", "def-galois-reps-polarized", "def-sha-bound")}
    if iface_prov != {"def-local-parameters": "modified", "def-galois-reps-polarized": "modified", "def-sha-bound": "new"}:
        raise ValueError(f"F2: the interface definitions' provenance has changed: {iface_prov}")

    c = Canvas(ID, f"What is new: the {len(new)} statements new in Alpöge's proof, where they sit, how they lean "
               "on each other, and what they take from the literature",
               "Every other poster colours provenance; this one is organised by it. The blueprint marks each "
               f"statement **new** in Alpöge's proof ({COUNTS['new']}), **modified** from a published result "
               f"({COUNTS['modified']}), or **published** as it stands ({COUNTS['published']}); "
               f"{COUNTS['unlabelled']} carry no mark. The new statements are too many for a card each: their own "
               f"graph has {len(e_proof)} proof-use edges and chains {longest} statements long. So this poster works one level "
               "up. Each chapter is a card holding only its new work: its sections with how much of each is new, "
               "the new statements that nothing new builds on, and what its new work takes and gives. **An arrow "
               "from A to B**, labelled with a count, says that the proofs of B's new statements use that many "
               "new statements of A; **read it from the foot up**, as diagram R2. The matrix below the cards has "
               "every such count, the arrows that would point upward included. Then every section by provenance, "
               "which is where the new work concentrates; the published and modified results the new statements "
               "lean on most; and the new lemmas that published results' proofs use. **No Lean was built**: see "
               "diagram R1, band 5."
               + (" **Map mode**: this poster quotes nothing in either form." if bp.MAP else ""),
               W, f"`riemann-blueprint` at {g.bp_commit} (every statement's provenance, chapter, section and uses; "
               "every chapter's and section's title and order; `lean-facts.json` for the declaration counts); "
               f"`leanprover-community/riemann-hypothesis` at {mirror['commit']} (`src/Main.lean`). Every count "
               "is the diagram's own, from the blueprint's `uses` edges; the tops and the chapter labels are the "
               "diagram's own.",
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
                          ("box", "blue", "published"), ("box", "grey", "unlabelled"),
                          ("arrow", "green", "A → B, n: the proofs of B's new statements use n new statements of A")],
                  title="Legend") + 26
    key = [
        "**A chapter card** holds only the chapter's new work. The pill counts it against the chapter's "
        "statements. **The bullets** are the chapter's sections, each with its statements by provenance, so a "
        "section that is all new reads `9 of 9 new`.",
        "**Tops** are the new statements of the chapter that no new statement uses, in its statement or its "
        "proof: the chapter's new work ends there, in a theorem the outline uses, or in a lemma a published "
        "result's proof uses (band 6). **On the literature alone** counts the new statements that use no new "
        "statement: the new work begins there.",
        "**Takes** and **gives** are the proof uses between new statements across chapters, the arrows' "
        "counts; **inputs** are the published, modified and unlabelled statements the chapter's new work uses, "
        "with the most used named.",
        "**Rows**: the chapters stand as on diagram R2, used above user, so most arrows point down. The five "
        "pairs that point up are not drawn as arrows: they are listed beside the cards and counted in the "
        "matrix.".replace("The five", f"The {len(up)}"),
    ]
    nums = [
        f"**{len(new)} new statements** in {len({chap(k) for k in new})} chapters: " + ", ".join(
            f"{v} {k}s" for k, v in sorted(collections.Counter(g.nodes[k]['kind'] for k in new).items(),
                                           key=lambda t: -t[1])) + ".",
        f"**{len(e_proof)} proof uses** between new statements, {len(e_all)} uses with stated-with counted; "
        f"{sum(cross.values())} of the proof uses cross a chapter, in {len(cross)} ordered pairs of chapters.",
        f"**{len(tops)} tops**: new statements nothing new builds on. **{len(bottoms)} on the literature "
        "alone**: new statements that use nothing new.",
        f"**{sum(inputs.values())} uses of {len(inputs)} inputs**: " + ", ".join(
            f"{v} {k}" for k, v in sorted(collections.Counter(prov(a) for a in inputs).items())) + " results.",
        f"**{sum(len(v) for v in exports.values())} uses of {len(exports)} new statements** by statements that "
        "are not new: new lemmas inside published results (band 6).",
        f"**{sum(1 for k in new if g.nodes[k].get('lean'))} of the {len(new)}** name a Lean declaration; "
        f"{sum(len(g.nodes[k].get('lean', [])) for k in new)} declarations in all.",
    ]
    hk = max(c.card(0, 0, span(3), "How to read a chapter card", key, draw=False, size=S),
             c.card(0, 0, span(2), "The new work in numbers", nums, draw=False, size=S))
    c.card(colx(0), y, span(3), "How to read a chapter card", key, "grey", h=hk, size=S, tint=False)
    c.card(colx(3), y, span(2), "The new work in numbers", nums, "green", h=hk, size=S, tint=False)
    y += hk + 50

    # ---------------------------------------------------------------------------------- the chapters
    y = band(c, X0, y, "2 · The chapters, new work only",
             "Published results at the top, the five stages in the middle, the outline and the main theorems at "
             "the foot, as on diagram R2. The arrows count proof uses between new statements across chapters.")

    def chapter_card(ch, w):
        n = g.nodes[ch]
        st = [k for k in g.statements if chap(k) == ch]
        mine = [k for k in new if chap(k) == ch]
        secs = [s for s in sections if chap(s) == ch]
        bullets = []
        for s in secs:
            u = under(s)
            cnt = collections.Counter(prov(k) for k in u)
            rest = ", ".join(f"{cnt[p]} {p}" for p in ("modified", "published", "unlabelled") if cnt[p])
            bullets.append(f"**{g.nodes[s]['title']}**: {cnt['new']} of {len(u)} new" + (f" ({rest})" if rest else ""))
        root = at_root(ch)
        if root:
            cnt = collections.Counter(prov(k) for k in root)
            bullets.append(f"**At the chapter's root**: {cnt['new']} of {len(root)} new: " + names(root, 6))
        if not bullets:
            bullets.append("No sections.")
        my_tops = [k for k in tops if chap(k) == ch]
        my_bottoms = [k for k in bottoms if chap(k) == ch]
        takes = sorted(((a, n_) for (a, b), n_ in cross.items() if b == ch), key=lambda t: -t[1])
        gives = sorted(((b, n_) for (a, b), n_ in cross.items() if a == ch), key=lambda t: -t[1])
        my_inputs = collections.Counter()
        for b in mine:
            for a in g.uses(b):
                if a not in N:
                    my_inputs[a] += 1
        foot = [
            "**Tops** " + (names(my_tops, 6) if my_tops else "none: every new statement here is used by new work"),
            f"**On the literature alone** {len(my_bottoms)} of {len(mine)}",
            "**Takes** " + (", ".join(f"{n_} from {SHORT[a]}" for a, n_ in takes) if takes else "nothing new from another chapter"),
            "**Gives** " + (", ".join(f"{n_} to {SHORT[b]}" for b, n_ in gives) if gives else "nothing new to another chapter"),
            f"**Inputs** {sum(my_inputs.values())} uses of {len(my_inputs)} results that are not new"
            + ("; most used " + ", ".join(f"{code(a)} ({n_})" for a, n_ in my_inputs.most_common(3)) if my_inputs else ""),
            f"**Within the chapter** {matrix[(ch, ch)]} proof uses between its new statements",
        ]
        acc = {"chap-literature": "blue", "main-theorems": "amber", "architecture": "grey"}.get(ch, "green")
        return dict(anchor=ch, name=f"{n.get('order', '')}. {n['title']}", accent=acc,
                    pill=f"{len(mine)} new of {len(st)} statements", formula=[], bullets=bullets, foot=foot)

    up_body = ["The chapters stand as on diagram R2, so a proof use from a lower chapter's new statement to a "
               "higher one would point upward. They are counted in the matrix and listed here, not drawn."]
    for (a, b), n_ in sorted(up.items(), key=lambda t: -t[1]):
        es = sorted((x, y_) for x, y_ in up_edges if chap(x) == a and chap(y_) == b)
        up_body.append(f"**{SHORT[a]} → {SHORT[b]}, {n_}**: " + "; ".join(f"`{x}` in the proof of `{y_}`" for x, y_ in es[:4])
                       + (f"; and {len(es) - 4} more" if len(es) > 4 else ""))
    rows, rowof, pos = {}, {}, {}
    for k, (r, i, n_) in PLACE.items():
        rows.setdefault(r, []).append((k, i, n_))
        rowof[k] = r
    EXTRA = {0: (3, 2, "Pointing upward, not drawn", up_body, "amber"),
             2: (0, 2, "What the matrix counts", [
                 "A cell (A, B) counts the proof uses from new statements of chapter A to new statements of "
                 "chapter B: the arrow A → B. The diagonal is the chapter's own new work leaning on itself. "
                 "Stated-with uses are not counted here; the numbers card above has them.",
                 "The heaviest flows are " + " and ".join(
                     f"{SHORT[a]} → {SHORT[b]}, {n_}" for (a, b), n_ in heaviest)
                 + ": the families are built from what those two chapters prove.",
             ], "grey"),
             3: (3, 2, "What the stages pass to each other", [
                 "The three interface definitions of the outline, local parameters, polarised Galois "
                 "representations and the Tate–Shafarevich bound, are what the new work of the arithmetic "
                 "stages hands to the analytic ones; diagram F1 draws them. Only the Tate–Shafarevich bound is "
                 "itself new; the other two are modified from the literature, so they count as inputs here.",
             ], "grey")}
    for r in sorted(rows):
        items = [(k, i, n_, chapter_card(k, span(n_))) for k, i, n_ in rows[r]]
        hh = max(bp.node(c, 0, 0, span(n_), draw=False, **kw) for _, _, n_, kw in items)
        ex = EXTRA.get(r)
        if ex:
            hh = max(hh, c.card(0, 0, span(ex[1]), ex[2], ex[3], draw=False, size=S))
        for k, i, n_, kw in items:
            bp.node(c, colx(i), y, span(n_), h=hh, **kw)
            pos[k] = (colx(i), y, span(n_), hh)
        if ex:
            c.card(colx(ex[0]), y, span(ex[1]), ex[2], ex[3], ex[4], h=hh, size=S, tint=ex[4] == "amber")
            pos[f"_extra{r}"], rowof[f"_extra{r}"] = (colx(ex[0]), y, span(ex[1]), hh), r
        y += hh + VG
    y -= VG
    labels = {p: str(n_) for p, n_ in down.items()}
    bp.arrows(c, pos, rowof, sorted(down), lambda a: "green", VG, G, X0, X1, 5, colx, labels=labels)

    # ---------------------------------------------------------------------------------- the matrix
    y += 60
    y = band(c, X0, y, "3 · Proof uses between new statements, chapter by chapter",
             "Row: the chapter whose new statements are used. Column: the chapter whose new statements' proofs use "
             "them. The diagonal is within the chapter.")
    mcols = [("Used ↓ by →", 330, {"bold": True})] + [(SHORT[ch], (WW - 330 - 150) / len(chapters)) for ch in chapters] + [("Gives", 150, {"bold": True})]
    mrows = []
    for a in chapters:
        cells = [SHORT[a]]
        for b in chapters:
            v = matrix[(a, b)]
            cells.append((f"**{v}**" if a == b else str(v)) if v else "")
        cells.append(str(sum(matrix[(a, b)] for b in chapters)))
        mrows.append(cells)
    mrows.append(["**Takes**"] + [str(sum(matrix[(a, b)] for a in chapters)) for b in chapters] + [str(len(e_proof))])
    y += c.table(X0, y, mcols, mrows, size=S) + 50

    # ---------------------------------------------------------------------------------- the sections
    y = band(c, X0, y, "4 · Every section by provenance: where the new work concentrates",
             f"The {len(sections)} sections of the blueprint in chapter order, each with its statements counted "
             "by provenance, and the statements at each chapter's root. The share is new statements over all.")
    srows = []
    for ch in chapters:
        secs = [s for s in sections if chap(s) == ch]
        root = at_root(ch)
        if not secs and not root:
            continue
        tot = [k for k in g.statements if chap(k) == ch]
        cnt = collections.Counter(prov(k) for k in tot)
        srows.append({"group": f"{g.nodes[ch].get('order')}. {g.nodes[ch]['title']}: {cnt['new']} of {len(tot)} new",
                      "accent": "grey"})
        for s in secs:
            u = under(s)
            cnt = collections.Counter(prov(k) for k in u)
            srows.append({"cells": [s, g.nodes[s]["title"], str(len(u)), str(cnt["new"]) if cnt["new"] else "",
                                    str(cnt["modified"]) if cnt["modified"] else "",
                                    str(cnt["published"]) if cnt["published"] else "",
                                    str(cnt["unlabelled"]) if cnt["unlabelled"] else "",
                                    f"{100 * cnt['new'] // len(u)}%" if u else ""],
                          "accent": "green" if u and cnt["new"] == len(u) else None})
        if root:
            cnt = collections.Counter(prov(k) for k in root)
            srows.append({"cells": ["", "at the chapter's root", str(len(root)), str(cnt["new"]) if cnt["new"] else "",
                                    str(cnt["modified"]) if cnt["modified"] else "",
                                    str(cnt["published"]) if cnt["published"] else "",
                                    str(cnt["unlabelled"]) if cnt["unlabelled"] else "",
                                    f"{100 * cnt['new'] // len(root)}%"], "accent": None})
    half = (len(srows) + 1) // 2
    # split at a group boundary near the middle so no chapter is cut
    cut = min((i for i, r in enumerate(srows) if isinstance(r, dict) and "group" in r and i >= half),
              key=lambda i: i - half, default=half)
    TW = (WW - G) / 2
    scols = [("Section", 300, {"mono": True}), ("Title", TW - 300 - 90 * 6), ("Stmts", 90), ("New", 90),
             ("Modified", 90), ("Published", 90), ("Unlab.", 90), ("Share", 90)]
    h1 = c.table(X0, y, scols, srows[:cut], size=S)
    h2 = c.table(X0 + TW + G, y, scols, srows[cut:], size=S)
    y += max(h1, h2) + 50

    # ---------------------------------------------------------------------------------- inputs
    y = band(c, X0, y, "5 · What the new work takes from the literature",
             f"The {TOP_N} statements that are not new with the most uses by new statements, counted over all "
             f"{len(inputs)} such inputs and {sum(inputs.values())} uses, with the chapters whose new work uses "
             "each. A modified result is a published one restated for the proof.")
    irows = []
    for a, n_ in sorted(inputs.items(), key=lambda t: (-t[1], t[0]))[:TOP_N]:
        na = g.nodes[a]
        by = ", ".join(f"{v} in {SHORT[ch]}" for ch, v in sorted(by_user[a].items(), key=lambda t: (-t[1], t[0])))
        irows.append({"cells": [a, na["title"], bp.PROV_LABEL[na.get("provenance")], SHORT[chap(a)], str(n_), by],
                      "accent": bp.PROV_ACCENT[na.get("provenance")]})
    icols = [("Statement", 380, {"mono": True}), ("Title", 620), ("Provenance", 260), ("Chapter", 160),
             ("Uses by new", 130), ("By the user's chapter", WW - 380 - 620 - 260 - 160 - 130)]
    y += c.table(X0, y, icols, irows, size=S) + 50

    # ---------------------------------------------------------------------------------- exports
    y = band(c, X0, y, "6 · New lemmas inside published results",
             f"The {len(exports)} new statements whose users include a statement that is not new: the proof of a "
             "published or modified result, as the blueprint gives it, leans on them. They are where the new work "
             "reaches into the literature chapter rather than the other way round.")
    erows = []
    for k in sorted(exports, key=lambda k: (g.nodes[chap(k)].get("order", 0), k)):
        used = ", ".join(f"`{u}` ({bp.PROV_SHORT[g.nodes[u].get('provenance')]})" for u in exports[k])
        erows.append([k, g.nodes[k]["title"], SHORT[chap(k)], str(len(exports[k])), used])
    ecols = [("New statement", 380, {"mono": True}), ("Title", 620), ("Chapter", 160), ("Users", 90),
             ("Used by statements that are not new", WW - 380 - 620 - 160 - 90)]
    c.table(X0, y, ecols, erows, size=S)
    return c
