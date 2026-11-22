"""F5 — The sections, the middle level: every section of the blueprint as a card, chapter by chapter, with the
proof uses between sections as arrows.

Between the nine chapters of R2 and the 416 statements of R3 to R8 sit 58 sections. This poster is R2 one step
down: one band per chapter, its sections laid out by their own edges so that a section stands above the
sections whose proofs use it, an arrow between two sections labelled with the number of proof uses, and each
card saying what the section holds, which of its statements other sections use, and what it takes from and
gives to other chapters. The statements at a chapter's root, outside every section, are a card of their own.
The build fails if the section count, the units, the per-chapter edge counts or the edges that would point
upward differ from what is recorded here."""
import collections

import bp
from bp import abridge, names, node, paragraphs, rich
from chapter import band, layout
from lib import Canvas

ID, SLUG = "F5", "sections"

W = 3400
G = 64
S = 13.5
NCOLS = 5
N_SECTIONS = 58
N_UNITS = 66            # sections plus the chapter roots that hold statements
# The chapters top to bottom, as R2 places them: used above user.
ORDER = ["chap-literature", "chap-theta", "chap-heights", "chap-galois", "chap-sha", "chap-families",
         "chap-zero-free", "architecture", "main-theorems"]
SHORT = {
    "main-theorems": "Main theorems", "architecture": "Outline", "chap-zero-free": "Zero-free",
    "chap-families": "Families", "chap-theta": "Theta", "chap-heights": "Heights", "chap-sha": "Sha",
    "chap-galois": "Galois", "chap-literature": "Literature",
}
# Per chapter: (pairs of sections joined by a proof use, proof uses between them). The build fails on a change.
EXPECTED = {
    "main-theorems": (0, 0), "architecture": (2, 4), "chap-zero-free": (3, 4), "chap-families": (6, 7),
    "chap-theta": (24, 46), "chap-heights": (12, 28), "chap-sha": (10, 21), "chap-galois": (12, 23),
    "chap-literature": (13, 31),
}
# Pairs that would close a cycle, so are listed rather than drawn: (used, user).
UPWARD = [
    ("chap-sha/root", "sec-sha-kato"), ("sec-sha-gsp4", "chap-sha/root"), ("sec-sha-h2", "chap-sha/root"),
    ("sec-lit-p-adic-hodge", "sec-lit-galois-cohomology"),
]


def build():
    g = bp.load()
    mirror = bp.read_mirror()
    if set(ORDER) != g.chapters or set(SHORT) != g.chapters:
        raise ValueError("F5: ORDER and SHORT must name exactly the blueprint's chapters")
    rev = g.used_by()

    def chap(k):
        return g.nodes[k]["_chapter"]

    secs = sorted((k for k, v in g.nodes.items() if v["kind"] == "section"),
                  key=lambda k: (g.nodes[chap(k)].get("order", 0), g.nodes[k].get("order", 0), k))
    if len(secs) != N_SECTIONS:
        raise ValueError(f"F5: {len(secs)} sections, the poster is written for {N_SECTIONS}")
    sec_dir = {s: g.nodes[s]["_path"].rsplit("/", 1)[0] + "/" for s in secs}

    def unit_of(k):
        p = g.nodes[k]["_path"]
        for s in secs:
            if chap(s) == chap(k) and p.startswith(sec_dir[s]):
                return s
        return chap(k) + "/root"

    unit = {k: unit_of(k) for k in sorted(g.statements)}
    units = sorted(set(unit.values()))
    if len(units) != N_UNITS:
        raise ValueError(f"F5: {len(units)} units (sections and roots), the poster is written for {N_UNITS}")
    held = collections.defaultdict(list)
    for k in sorted(g.statements):
        held[unit[k]].append(k)

    def uchap(u):
        return u.split("/")[0] if u.endswith("/root") else chap(u)

    E = collections.Counter()
    for b in sorted(g.statements):
        for a in g.proof_uses(b):
            if a in unit and unit[a] != unit[b]:
                E[(unit[a], unit[b])] += 1
    inside = {ch: {p: n for p, n in E.items() if uchap(p[0]) == ch and uchap(p[1]) == ch} for ch in ORDER}
    got = {ch: (len(inside[ch]), sum(inside[ch].values())) for ch in ORDER}
    if got != EXPECTED:
        raise ValueError(f"F5: section edges per chapter are {got}, the poster is written for {EXPECTED}")

    def acyclic(pairs):
        """The pairs, heaviest first, that keep the graph acyclic; and the rest."""
        succ = collections.defaultdict(set)

        def reaches(x, y):
            seen, st = set(), [x]
            while st:
                v = st.pop()
                if v == y:
                    return True
                for z in sorted(succ[v]):
                    if z not in seen:
                        seen.add(z)
                        st.append(z)
            return False

        keep, drop = [], []
        for (a, b), n in sorted(pairs.items(), key=lambda t: (-t[1], t[0])):
            if reaches(b, a):
                drop.append((a, b))
            else:
                succ[a].add(b)
                keep.append((a, b))
        return keep, sorted(drop)

    drawn, upward = {}, []
    for ch in ORDER:
        drawn[ch], d = acyclic(inside[ch])
        upward += d
    if sorted(upward) != sorted(UPWARD):
        raise ValueError(f"F5: the pairs that would point upward are {sorted(upward)}, not {sorted(UPWARD)}")
    takes = collections.defaultdict(collections.Counter)      # unit -> chapter -> proof uses taken from it
    gives = collections.defaultdict(collections.Counter)
    for (a, b), n in E.items():
        if uchap(a) != uchap(b):
            takes[b][uchap(a)] += n
            gives[a][uchap(b)] += n
    heads = {u: [k for k in held[u] if any(unit[x] != u for x in rev[k])] for u in units}
    depth, _ = g.depths(g.roots())
    main_names = {t["name"] for t in mirror["theorems"]}
    cross = sum(n for (a, b), n in E.items() if uchap(a) != uchap(b))

    c = Canvas(ID, f"The sections, the middle level: the {len(secs)} sections of the blueprint as cards, chapter "
               "by chapter, and the proof uses between them",
               f"Between the nine chapters of diagram R2 and the {len(g.statements)} statements of R3 to R8 sit "
               f"{len(secs)} sections. This poster is R2 one step down. Each band is a chapter, in R2's order from "
               "the literature at the top to the main theorems at the foot; within a band each section is a card, "
               "standing above the sections whose proofs use it, and **an arrow from A to B, labelled n**, says "
               "that proofs in section B use n statements of section A. **Read each band from its foot up.** A card "
               "gives the section's statements by provenance, its introduction, the statements of it that other "
               "sections use, and what it takes from and gives to other chapters; the statements at a chapter's "
               "root, outside every section, are a card of their own. Proof uses between chapters are counted on "
               "the cards and drawn on R2, not here. **No Lean was built**: see diagram R1, band 5."
               + (" **Map mode**: nothing of the blueprint's text or the proof's source is quoted." if bp.MAP else ""),
               W, f"`riemann-blueprint` at {g.bp_commit} (every section's `_section.md`: title, order and "
               "introduction; every statement's section, provenance and uses); `leanprover-community/"
               f"riemann-hypothesis` at {mirror['commit']} (`src/Main.lean`). The layout is computed from the "
               "sections' own edges; the counts and the abridgements are the diagram's own.",
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
    y += c.legend(X0, y, [("box", "teal", "a section"), ("box", "grey", "the statements at a chapter's root"),
                          ("arrow", "teal", "A → B, n: proofs in section B use n statements of section A")],
                  title="Legend") + 26
    key = [
        "**A card** is one section of the blueprint, numbered as the chapter numbers it. The pill counts its "
        "statements and how many are new. **The line in italics** is the first paragraph of the section's own "
        "introduction, abridged where marked with ….",
        "**Used by other sections** lists the section's statements that a proof outside the section uses, "
        "anywhere in the blueprint: what the section is for, as the rest of the proof sees it. The statements a "
        "section holds are on R3 to R8 and in the blueprint path at the card's foot.",
        "**Takes** and **gives** count proof uses across chapters, by chapter: what the section's proofs use from "
        "other chapters' statements, and what other chapters' proofs use of the section's. The arrows draw only "
        "the uses within a chapter; R2 draws the flow between chapters.",
        "**Rows** within a band are computed from the arrows: a section stands above the sections whose proofs "
        "use it. A pair of sections that use each other would close a cycle; the lighter direction is listed in "
        "the band's note and not drawn.",
    ]
    if bp.MAP:
        key[0] = ("**A card** is one section of the blueprint, numbered as the chapter numbers it. The pill counts "
                  "its statements and how many are new. The italic line gives how many paragraphs the section's "
                  "introduction has; the text is not quoted. " + bp.NOT_QUOTED)
    nums = [
        f"**{len(secs)} sections** in {sum(1 for ch in ORDER if any(chap(s) == ch for s in secs))} chapters, and "
        f"{sum(1 for u in units if u.endswith('/root'))} chapter roots holding statements outside every section: "
        f"{len(units)} cards.",
        f"**{sum(E.values())} proof uses cross a section boundary**: {sum(E.values()) - cross} within a chapter, "
        f"drawn as {sum(len(v) for v in drawn.values())} arrows; {cross} between chapters, counted on the cards.",
        "**Most arrows** " + ", ".join(f"{SHORT[ch]} {len(drawn[ch])}" for ch in sorted(ORDER, key=lambda ch: -len(drawn[ch]))[:3])
        + "; **heaviest** " + ", ".join(f"`{a.split('/')[0] if a.endswith('/root') else a}` → `{b.split('/')[0] if b.endswith('/root') else b}` ({n})"
                                        for (a, b), n in sorted(E.items(), key=lambda t: (-t[1], t[0]))[:3]) + ".",
        f"**{len(upward)} pairs would point upward** and are listed instead of drawn: " + ", ".join(
            f"`{a}` → `{b}`" for a, b in upward) + ".",
        f"**Sections nothing outside them uses**: " + (names([u for u in units if not heads[u]], 6) or "none") + ".",
    ]
    hk = max(c.card(0, 0, span(3), "How to read a card", key, draw=False, size=S),
             c.card(0, 0, span(2), "The sections in numbers", nums, draw=False, size=S))
    c.card(colx(0), y, span(3), "How to read a card", key, "grey", h=hk, size=S, tint=False)
    c.card(colx(3), y, span(2), "The sections in numbers", nums, "teal", h=hk, size=S, tint=False)
    y += hk + 50

    # ---------------------------------------------------------------------------------- the bands
    def card_of(u, w):
        root = u.endswith("/root")
        ks = held[u]
        prov = collections.Counter(g.nodes[k].get("provenance") or "unlabelled" for k in ks)
        if root:
            ch = u.split("/")[0]
            name = f"At the root of {g.nodes[ch]['title']}"
            say = "The chapter's statements outside every section: " + names(ks, 6) + "."
        else:
            n = g.nodes[u]
            name = f"{n.get('order')}. {n['title']}"
            paras = paragraphs(bp.body(g, u))
            if bp.MAP:
                say = f"`{u}`: {len(paras)} paragraph(s) of introduction."
            else:
                say = abridge(rich(paras[0]), 340) if paras else "The blueprint gives this section no introduction."
        bullets = ["**Used by other sections** " + (names(heads[u], 5) if heads[u] else "no statement of it")]
        foot = [
            "**Takes** " + (", ".join(f"{n_} from {SHORT[ch]}" for ch, n_ in sorted(takes[u].items(), key=lambda t: (-t[1], t[0])))
                            if takes[u] else "nothing from another chapter"),
            "**Gives** " + (", ".join(f"{n_} to {SHORT[ch]}" for ch, n_ in sorted(gives[u].items(), key=lambda t: (-t[1], t[0])))
                            if gives[u] else "nothing to another chapter"),
            "Blueprint " + bp.code((u.split("/")[0] + "/") if root else sec_dir[u], 44),
        ]
        pill = f"{len(ks)} statement{'s' if len(ks) != 1 else ''} · {prov['new']} new"
        return dict(anchor=None if root else u, name=name, accent="grey" if root else "teal", pill=pill, formula=[], say=say, bullets=bullets,
                    foot=foot, dash="6 4" if root else None)

    for ch in ORDER:
        mine = sorted((u for u in units if uchap(u) == ch),
                      key=lambda u: (u.endswith("/root"), g.nodes[u].get("order", 0) if not u.endswith("/root") else 99))
        edges = drawn[ch]
        orderof = {u: (99 if u.endswith("/root") else g.nodes[u].get("order", 0)) for u in mine}
        rows, _ = layout(mine, edges, [], lambda u: f"{orderof[u]:03d}{u}", lambda u: 0)
        n_lane = collections.Counter()
        rowof_tmp = {u: i for i, row in enumerate(rows) for u, _ in row}
        for a, b in edges:
            n_lane[rowof_tmp[a]] += 1
            n_lane[rowof_tmp[b] - 1] += 1
        VG = max(96, 14 * max(n_lane.values(), default=0) + 24)
        n_ch = g.nodes[ch]
        note = (f"{len(mine)} cards, {len(edges)} arrows for {sum(inside[ch].values())} proof uses within the "
                f"chapter; {sum(takes[u].total() for u in mine)} taken from other chapters, "
                f"{sum(gives[u].total() for u in mine)} given to them.")
        up_here = [(a, b) for a, b in upward if uchap(a) == ch]
        if up_here:
            note += " Not drawn, it would point upward: " + ", ".join(
                f"`{a}` → `{b}` ({inside[ch][(a, b)]})" for a, b in up_here) + "."
        y = band(c, X0, y, f"{n_ch.get('order')} · {n_ch['title']}", note)
        pos, rowof = {}, {}
        for r, row in enumerate(rows):
            items = [(u, i, card_of(u, CW)) for u, i in row]
            hh = max(node(c, 0, 0, CW, draw=False, **kw) for _, _, kw in items)
            for u, i, kw in items:
                node(c, colx(i), y, CW, h=hh, **kw)
                pos[u] = (colx(i), y, CW, hh)
                rowof[u] = r
            y += hh + VG
        y -= VG
        bp.arrows(c, pos, rowof, sorted(edges), lambda a: "teal", VG, G, X0, X1, NCOLS, colx,
                  labels={p: str(inside[ch][p]) for p in edges})
        y += 70
    return c
