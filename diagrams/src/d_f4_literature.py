"""F4 — The proof as literature: the references of the blueprint on a timeline, which statements cite each, and
what falls if one is wrong.

The blueprint's reference list is 209 entries with author, title, journal and year, and 196 statements carry a
`source` line citing one or more of them. This poster puts every reference on a timeline by decade, a chip each,
with the number of statements that cite it; tables the references the proof leans on most, with the upward cone
of each (every statement that, through the `uses` edges, rests on a statement citing it); and lists the
references no statement cites. The build fails if the reference count, the year range, the citing counts or the
most-cited references differ from what is recorded here."""
import collections
import re

import bp
from bp import abridge, code, names, rich
from chapter import band
from lib import Canvas, render_line, wrap
import lib

ID, SLUG = "F4", "literature"

W = 3400
G = 64
S = 13.5
NCOLS = 5
N_REFS = 209
YEARS = (1859, 2026)
N_CITING = 196          # statements with a `source` line
TOP = ["bernstein-zelevinsky-1977", "faltings-chai-1990", "harish-chandra-1966", "tate-1963"]   # most cited, in order
TOP_N = 25
CHIPS_PER_ROW = 10
SHORT = {
    "main-theorems": "Main theorems", "architecture": "Outline", "chap-zero-free": "Zero-free",
    "chap-families": "Families", "chap-theta": "Theta", "chap-heights": "Heights", "chap-sha": "Sha",
    "chap-galois": "Galois", "chap-literature": "Literature",
}
MAINS = ["thm-riemann-hypothesis", "thm-half-plane", "thm-critical-line", "thm-critical-line-primitive",
         "lem-zeta-nonvanishing"]
CITE = re.compile(r"\[([a-z0-9-]+)(?:,[^\]]*)?\]")      # [id] or [id, Lemma 4.9]


def surnames(authors):
    """'A. Abbes', 'T. Bouche' -> 'Abbes–Bouche'; three or more -> 'Artin, Grothendieck, Verdier'."""
    s = [a.split()[-1] for a in authors]
    return "–".join(s) if len(s) <= 2 else ", ".join(s)


def build():
    g = bp.load()
    mirror = bp.read_mirror()
    if set(SHORT) != g.chapters:
        raise ValueError("F4: SHORT must name exactly the blueprint's chapters")
    rev = g.used_by()
    refs = sorted(k for k, n in g.nodes.items() if n["kind"] == "reference")
    if len(refs) != N_REFS:
        raise ValueError(f"F4: {len(refs)} references, the poster is written for {N_REFS}")
    for r in refs:
        if not g.nodes[r].get("year") or not g.nodes[r].get("year").isdigit():
            raise ValueError(f"F4: reference {r} has no year")
    year = {r: int(g.nodes[r]["year"]) for r in refs}
    if (min(year.values()), max(year.values())) != YEARS:
        raise ValueError(f"F4: years run {min(year.values())}–{max(year.values())}, the poster is written for {YEARS}")
    cites = collections.defaultdict(list)        # reference -> statements whose source cites it
    citing = []
    plain = []
    for k in sorted(g.statements):
        s = g.nodes[k].get("source")
        if not s:
            continue
        citing.append(k)
        ids = CITE.findall(s)
        if not ids:
            plain.append(k)
        for i in ids:
            if i not in g.nodes or g.nodes[i]["kind"] != "reference":
                raise ValueError(f"F4: {k} cites [{i}], which is not a reference")
            cites[i].append(k)
    if len(citing) != N_CITING:
        raise ValueError(f"F4: {len(citing)} statements carry a source line, the poster is written for {N_CITING}")
    ranked = sorted(refs, key=lambda r: (-len(cites[r]), r))
    if ranked[:len(TOP)] != TOP:
        raise ValueError(f"F4: the most cited references are {ranked[:len(TOP)]}, not {TOP}")
    uncited = [r for r in refs if not cites[r]]
    mains = set(MAINS)
    if not mains <= set(g.statements):
        raise ValueError("F4: MAINS are not all statements")

    def cone(starts):
        seen, stack = set(), list(starts)
        while stack:
            v = stack.pop()
            for u in rev.get(v, []):
                if u not in seen:
                    seen.add(u)
                    stack.append(u)
        return seen

    cones = {r: cone(cites[r]) for r in refs if cites[r]}
    reach = [r for r in cones if cones[r] & mains]
    decades = sorted({(y // 10) * 10 for y in year.values()})
    by_decade = {d: sorted((r for r in refs if (year[r] // 10) * 10 == d), key=lambda r: (year[r], r)) for d in decades}
    n_cites = sum(len(v) for v in cites.values())
    multi = sum(1 for k in citing if len(CITE.findall(g.nodes[k]["source"])) > 1)
    prov_citing = collections.Counter(g.nodes[k].get("provenance") or "unlabelled" for k in citing)

    def label(r):
        n = g.nodes[r]
        return f"{surnames(n['author']) if n.get('author') else r} {year[r]}"

    def title(r):
        n = g.nodes[r]
        return rich(n.get("title") or n.get("howpublished") or "")

    c = Canvas(ID, f"The proof as literature: the {len(refs)} references of the blueprint on a timeline, which "
               "statements cite each, and what falls if one is wrong",
               f"The blueprint's reference list runs from Riemann's paper of {YEARS[0]} to Alpöge's announcement of "
               f"{YEARS[1]}, and {len(citing)} of its statements carry a source line citing one or more entries. "
               "This poster reads the proof as a history. **The timeline** puts every reference in its decade, a "
               "chip each, with the number of statements that cite it: the published and modified results the proof "
               "takes from it. **The table** ranks the references the proof leans on most, and gives each one's "
               "upward cone, every statement that rests on a statement citing it through the blueprint's `uses` "
               "edges, which is what would fall if the result were wrong; T1 and T2 descend from the top, this "
               "ascends from a leaf. **The last card** lists the references no statement cites. A citation here is "
               "the blueprint's attribution of a statement to a source, not a claim that the source proves it as "
               "stated. **No Lean was built**: see diagram R1, band 5."
               + (" **Map mode**: this poster quotes bibliographic data only, in either form." if bp.MAP else ""),
               W, f"`riemann-blueprint` at {g.bp_commit} (`references/`: every entry's author, title, journal and "
               "year; every statement's `source`, chapter and uses); `leanprover-community/riemann-hypothesis` at "
               f"{mirror['commit']} (`src/Main.lean`). The decades, the citation counts, the cones and the author "
               "labels are the diagram's own; titles are abridged where marked with ….",
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
    y += c.legend(X0, y, [("box", "blue", "a reference cited by a statement's source line"),
                          ("box", "grey", "a reference no statement cites (dashed)", "6 4")],
                  title="Legend") + 26
    key = [
        "**A chip** is one entry of the blueprint's reference list: the authors' surnames and the year, the "
        "title abridged, and the number of statements whose `source` line cites it. Chips stand in their "
        "decade, in order of year, and a decade's row says how many of its references are cited.",
        "**Cited by** counts statements, not uses: a statement citing a reference is a published or modified "
        f"result the blueprint attributes to it. {multi} statements cite more than one source, and a few cite a "
        "section or lemma of one.",
        "**The upward cone** of a reference is every statement that rests, through the `uses` edges, on a "
        "statement citing it: the statements citing it, their users, their users' users, up to the main "
        "theorems. Its size is a measure of how much of the proof stands on the result; whether the cone reaches "
        "a theorem of `Main.lean` says whether the Riemann Hypothesis itself does.",
        "**Not cited** means no statement's source line names the reference. The blueprint lists it; the "
        "diagram cannot say why, and does not.",
    ]
    nums = [
        f"**{len(refs)} references** from {YEARS[0]} to {YEARS[1]}, in {len(decades)} decades; the fullest are "
        + ", ".join(f"the {d}s ({len(by_decade[d])})" for d in sorted(decades, key=lambda d: -len(by_decade[d]))[:3]) + ".",
        f"**{len(citing)} statements carry a source line**: {prov_citing['published']} published, "
        f"{prov_citing['modified']} modified" + (f", {prov_citing['new']} new" if prov_citing['new'] else "")
        + f"; {len(plain)} of them name no entry (`classical`, or a source the list does not hold).",
        f"**{len(cones)} references are cited**, {n_cites} citations in all; {len(uncited)} are cited by no "
        f"statement. Citations per reference: " + ", ".join(
            f"{v} cited {k} time{'s' if k != 1 else ''}" for k, v in sorted(collections.Counter(len(cites[r]) for r in refs).items()) if k) + ".",
        f"**Most cited** " + ", ".join(f"`{r}` ({len(cites[r])})" for r in ranked[:5]) + ".",
        f"**{len(reach)} of the {len(cones)} cited references** have a cone that reaches a theorem of "
        f"`Main.lean`; the Riemann Hypothesis rests on all of them. The other {len(cones) - len(reach)}: "
        + (names([r for r in cones if r not in reach], 6) if len(cones) > len(reach) else "none") + ".",
    ]
    hk = max(c.card(0, 0, span(3), "How to read the poster", key, draw=False, size=S),
             c.card(0, 0, span(2), "The literature in numbers", nums, draw=False, size=S))
    c.card(colx(0), y, span(3), "How to read the poster", key, "grey", h=hk, size=S, tint=False)
    c.card(colx(3), y, span(2), "The literature in numbers", nums, "blue", h=hk, size=S, tint=False)
    y += hk + 50

    # ---------------------------------------------------------------------------------- the timeline
    y = band(c, X0, y, "2 · The references, decade by decade",
             f"Every entry of the reference list, in its decade, from {YEARS[0]} to {YEARS[1]}. A chip's pill is the "
             "number of statements citing it; a dashed chip is cited by none.")
    LX = 190                                    # the decade label column
    GAP = 12
    CHW = (WW - LX - (CHIPS_PER_ROW - 1) * GAP) / CHIPS_PER_ROW
    CHH = 74
    for d in decades:
        rs = by_decade[d]
        rows = [rs[i:i + CHIPS_PER_ROW] for i in range(0, len(rs), CHIPS_PER_ROW)]
        top = y
        cited_here = sum(1 for r in rs if cites[r])
        c.text(X0, y + 20, f"{d}s", 19, "ink", bold=True)
        c.text(X0, y + 42, f"{len(rs)} reference{'s' if len(rs) != 1 else ''}, {cited_here} cited", 12.5, "muted")
        for row in rows:
            for j, r in enumerate(row):
                x = X0 + LX + j * (CHW + GAP)
                acc = "blue" if cites[r] else "grey"
                c.rect(x, y, CHW, CHH, acc, tint=bool(cites[r]), dash=None if cites[r] else "6 4", rx=6, sw=1.2)
                c.blocks.append((x, y, x + CHW, y + CHH, "chip " + r))
                pill = str(len(cites[r])) if cites[r] else "0"
                pw = lib.text_width(pill, 11, bold=True) + 18
                lab = wrap(label(r), CHW - 20 - pw, 13, bold=True)[0]
                c.add(render_line(x + 10, y + 19, lab, 13, acc, bold=True))
                c.pill(x + CHW - 8, y + 6, pill, acc, 11, anchor="end", solid=bool(cites[r]))
                tl = wrap(abridge(title(r), 150), CHW - 20, 11.5)[:2]
                for i, ln in enumerate(tl):
                    c.add(render_line(x + 10, y + 36 + i * 15.5, ln, 11.5, "muted"))
                c.add(render_line(x + 10, y + 68, [(r, "m", None)], 10.5, "faint"))
            y += CHH + GAP
        c.line(X0, y + 4, X1, y + 4, "line", sw=1)
        y += 16
    y += 30

    # ---------------------------------------------------------------------------------- the table
    y = band(c, X0, y, "3 · What the proof leans on most, and what falls if it is wrong",
             f"The {TOP_N} references cited by the most statements. The cone is every statement that rests on a "
             "statement citing the reference, counted over the whole blueprint and broken down by the chapters "
             "that hold the most of it; the last column says whether a theorem of `Main.lean` is in the cone.")
    trows = []
    for r in ranked[:TOP_N]:
        n = g.nodes[r]
        cn = cones[r]
        chs = collections.Counter(g.nodes[u]["_chapter"] for u in cn)
        where = ", ".join(f"{SHORT[ch]} {v}" for ch, v in sorted(chs.items(), key=lambda t: (-t[1], t[0]))[:3])
        pub = " ".join(x for x in (n.get("journal"), n.get("volume")) if x)
        trows.append([r, label(r), abridge(title(r), 90), rich(pub) if pub else "—", str(len(cites[r])),
                      names(cites[r], 3), str(len(cn)), where, "yes" if cn & mains else "no"])
    tcols = [("Reference", 300, {"mono": True}), ("Authors, year", 300), ("Title", 560), ("Where", 360),
             ("Cited by", 100), ("Citing statements", 560), ("Cone", 80), ("Mostly in", 400),
             ("Main.lean", WW - 300 - 300 - 560 - 360 - 100 - 560 - 80 - 400)]
    y += c.table(X0, y, tcols, trows, size=S) + 50

    # ---------------------------------------------------------------------------------- the rest
    y = band(c, X0, y, "4 · The references no statement cites, and the sources that name no entry")
    unc = [f"{len(uncited)} entries of the reference list are cited by no statement's source line: "
           + ", ".join(f"`{r}`" for r in uncited) + "."]
    pl = [f"{len(plain)} statements carry a source line that names no entry of the list: "
          + ", ".join(f"`{k}` ({rich(g.nodes[k]['source'])})" for k in plain) + "."]
    dec_rows = [[f"{d}s", str(len(by_decade[d])), str(sum(1 for r in by_decade[d] if cites[r])),
                 str(sum(len(cites[r]) for r in by_decade[d])),
                 str(max((len(cones[r]) for r in by_decade[d] if cites[r]), default=0))] for d in decades]
    hk = max(c.card(0, 0, span(2), "Not cited", unc, draw=False, size=S),
             c.card(0, 0, span(1), "Sources without an entry", pl, draw=False, size=S))
    c.card(colx(0), y, span(2), "Not cited", unc, "grey", h=hk, size=S, tint=False)
    c.card(colx(2), y, span(1), "Sources without an entry", pl, "grey", h=hk, size=S, tint=False)
    c.table(colx(3), y, [("Decade", 140), ("References", 150), ("Cited", 110), ("Citations", 130),
                         ("Largest cone", span(2) - 140 - 150 - 110 - 130)], dec_rows, size=S)
    return c
