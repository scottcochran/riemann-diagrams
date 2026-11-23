"""F6 — Depth as geometry: every statement of the blueprint on one wheel, rings by distance from the main
theorems, sectors by chapter.

The three theorems nothing uses sit at the centre. A statement's ring is its breadth-first depth from them
along the `uses` edges, the measure the Graphviz depth graphs and R1's depth table use; its sector is its
chapter, and within the sector its position is its place in the chapter's order. Each statement is a dot in its
provenance colour with its id set along the radius. The two chains T1 and T2 draw are traced through the rings.
No other edge is drawn: 1986 of them would be a hairball, and the chapter posters have them. The build fails
if the depth histogram, the unreached statements or the two chains differ from what is recorded here."""
import collections
import math

import bp
from bp import PROV_ACCENT, names
from chapter import band
from d_t1_deepest import EXPECTED as CHAIN_T1
from d_t2_landau import EXPECTED as CHAIN_T2
from lib import Canvas, escape, fill, fs, sonly
import lib

ID, SLUG = "F6", "depth"

W = 3400
G = 64
S = 13.5
NCOLS = 5
R0, DR = 130, 138                 # the radius of ring 0 and the spacing of the rings
PITCH = 13                        # the smallest arc between two dots whose labels share a band, in pixels
LABEL = 10                      # the size of the ids along the radius
SHORT = {
    "main-theorems": "Main theorems", "architecture": "Outline", "chap-zero-free": "Zero-free",
    "chap-families": "Families", "chap-theta": "Theta", "chap-heights": "Heights", "chap-sha": "Sha",
    "chap-galois": "Galois", "chap-literature": "Literature",
}
# Sectors clockwise from the top, the chapters in the blueprint's order.
EXPECTED_DEPTHS = {0: 3, 1: 4, 2: 3, 3: 17, 4: 120, 5: 131, 6: 76, 7: 38, 8: 13, 9: 3, 10: 1}
UNREACHED = ["def-automorphic-galois-inputs", "def-local-rep-theory-package", "def-non-endoscopic-package",
             "rem-local-parameters-weak", "rem-points-to-check", "thm-shintani-casselman-shalika", "thm-theta-inputs"]


def build():
    g = bp.load()
    mirror = bp.read_mirror()
    if set(SHORT) != g.chapters:
        raise ValueError("F6: SHORT must name exactly the blueprint's chapters")
    chapters = sorted(g.chapters, key=lambda ch: (g.nodes[ch].get("order", 0), ch))
    depth, parent = g.depths(g.roots())
    hist = collections.Counter(depth.values())
    if dict(hist) != EXPECTED_DEPTHS:
        raise ValueError(f"F6: the depth histogram is {dict(sorted(hist.items()))}, written for {EXPECTED_DEPTHS}")
    unreached = sorted(k for k in g.statements if k not in depth)
    if unreached != UNREACHED:
        raise ValueError(f"F6: the unreached statements are {unreached}, written for {UNREACHED}")
    for chain in (CHAIN_T1, CHAIN_T2):
        for a, b in zip(chain, chain[1:]):
            if a not in g.uses(b) and b not in g.uses(a):
                raise ValueError(f"F6: the chain step {a} – {b} is not a use in the blueprint")
    D = max(hist)

    def chap(k):
        return g.nodes[k]["_chapter"]

    def order_key(k):
        return (g.nodes[k]["_path"], k)

    at = collections.defaultdict(list)                  # (chapter, depth) -> statements, in the chapter's order
    for k in sorted(g.statements, key=order_key):
        if k in depth:
            at[(chap(k), depth[k])].append(k)
    # A label is longer than the ring spacing, so a ring's labels reach into the next ring's band; a dot must
    # therefore keep PITCH pixels of arc from the dots of its own ring and of the ring inside it. A sector's width
    # is set by the fullest such pair of rings, and the dots of each ring are placed in the gaps the ring inside
    # leaves.
    if max(len(k) for k in depth) * lib.MONO_EM * LABEL + 10 > 2 * DR:
        raise ValueError("F6: an id is longer than two rings; the placement rule assumes labels span at most two")
    need = {}
    for ch in chapters:
        need[ch] = max(((len(at[(ch, d)]) + len(at[(ch, d - 1)]) + 1) * PITCH / (R0 + d * DR)
                        for d in range(D + 1)), default=0) + 0.04

    def place(ch, a0, width):
        """The angle of every statement of chapter `ch` in a sector [a0, a0 + width), or None if a ring does not
        fit: each ring's dots go into the gaps between the angles of the ring inside, every dot at least PITCH
        pixels of arc from its neighbours on either ring, spread evenly within each gap."""
        out, inner = {}, []
        for d in range(D + 1):
            ks = at[(ch, d)]
            if not ks:
                inner = []
                continue
            sp = PITCH / (R0 + d * DR)
            walls = [a0 - sp] + sorted(inner) + [a0 + width + sp]      # the sector's edges count as half a gap
            gaps = [(walls[i], walls[i + 1]) for i in range(len(walls) - 1)]
            cap = [max(0, int((b - a) / sp + 1e-9) - 1) for a, b in gaps]
            if sum(cap) < len(ks):
                return None
            take = [len(ks) * c // sum(cap) for c in cap]
            rest = len(ks) - sum(take)
            order = sorted(range(len(gaps)), key=lambda i: (-(len(ks) * cap[i] / sum(cap) - take[i]), i))
            for i in order:
                if rest == 0:
                    break
                if take[i] < cap[i]:
                    take[i] += 1
                    rest -= 1
            angles = []
            for (a, b), m in zip(gaps, take):
                angles += [a + (b - a) * (i + 1) / (m + 1) for i in range(m)]
            angles.sort()
            inner = angles
            out.update(zip(ks, angles))
        return out

    for _ in range(200):                               # widen a sector that does not fit, and lay out again
        total = sum(need.values())
        start, sector, angles, short = {}, {}, {}, None
        a = -math.pi / 2
        for ch in chapters:
            start[ch], sector[ch] = a, 2 * math.pi * need[ch] / total
            a += sector[ch]
            got = place(ch, start[ch], sector[ch])
            if got is None:
                short = ch
                break
            angles.update(got)
        if short is None:
            break
        need[short] *= 1.06
    else:
        raise ValueError("F6: the sectors could not be widened to fit every ring")
    pos, ang = {}, {}
    for k, th in angles.items():
        r = R0 + depth[k] * DR
        ang[k] = th
        pos[k] = (r * math.cos(th), r * math.sin(th))
    reach = {ch: [depth[k] for k in g.statements if chap(k) == ch and k in depth] for ch in chapters}

    c = Canvas(ID, f"Depth as geometry: every statement of the blueprint on one wheel, rings by distance from "
               "the main theorems, sectors by chapter",
               f"The three theorems nothing else uses sit at the centre. A statement's ring is its distance from "
               "them along the `uses` edges, counted breadth-first: the number of reductions between the Riemann "
               "Hypothesis and the statement, the measure R1's depth table and the Graphviz depth graphs use. Its "
               "sector is its chapter, and within the sector its place is its place in the chapter's order. "
               f"Each of the {len(depth)} reached statements is a dot in its provenance colour with its id set "
               f"along the radius; the {len(unreached)} that no edge reaches are listed below the wheel. The two "
               "chains of T1 and T2 are traced through the rings; no other edge is drawn, since the "
               f"{sum(len([u for u in g.uses(k) if u in g.statements]) for k in g.statements)} of them would be "
               "a hairball, and R3 to R8 have them. The wheel is the one frame where all the statements fit one "
               "page: it shows how far each chapter reaches down, and where the proof is wide. **No Lean was "
               "built**: see diagram R1, band 5."
               + (" **Map mode**: this poster draws ids only, in either form." if bp.MAP else ""),
               W, f"`riemann-blueprint` at {g.bp_commit} (every statement's chapter, path, provenance and uses); "
               f"`leanprover-community/riemann-hypothesis` at {mirror['commit']} (`src/Main.lean`). The depths, "
               "the sectors and the chains are computed; the sector widths are the diagram's own, sized so that "
               "no ring of a sector is crowded.",
               state=f"State drawn: riemann-blueprint at {g.bp_commit}, which pins the mirror at {g.mirror_pin}; "
                     f"Main.lean from the mirror at {mirror['commit']}")
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    CW = (WW - 4 * G) / 5

    def colx(i):
        return X0 + i * (CW + G)

    def span(n):
        return n * CW + (n - 1) * G

    # ---------------------------------------------------------------------------------- the wheel
    y = c.y
    y = band(c, X0, y, "1 · The wheel")
    y += c.legend(X0, y, [("box", "green", "new in Alpöge's proof"), ("box", "amber", "modified from the literature"),
                          ("box", "blue", "published"), ("box", "grey", "unlabelled"),
                          ("line", "red", "T1, the deepest chain"), ("line", "violet", "T2, the chain to Landau's theorem")],
                  title="Legend") + 20
    RMAX = R0 + D * DR + 190
    cx, cy = W / 2, y + RMAX
    out = []
    for d in range(D + 1):                              # the rings
        r = R0 + d * DR
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" {sonly("line")} stroke-width="1"/>')
    for d in range(D + 1):                              # the ring numbers, down the vertical axis
        r = R0 + d * DR
        out.append(f'<text x="{cx + 6:.1f}" y="{cy - r - 5:.1f}" font-family="{lib.SANS}" font-size="12" '
                   f'{fill("faint")}>{d}</text>')
    for ch in chapters:                                 # the sector lines and labels
        th = start[ch]
        out.append(f'<line x1="{cx + R0 * 0.55 * math.cos(th):.1f}" y1="{cy + R0 * 0.55 * math.sin(th):.1f}" '
                   f'x2="{cx + (RMAX - 60) * math.cos(th):.1f}" y2="{cy + (RMAX - 60) * math.sin(th):.1f}" '
                   f'{sonly("line")} stroke-width="1" stroke-dasharray="4 4"/>')
        mid = start[ch] + sector[ch] / 2
        lx, ly = cx + (RMAX - 24) * math.cos(mid), cy + (RMAX - 24) * math.sin(mid)
        deg = math.degrees(mid) + (90 if math.cos(mid) >= 0 else -90)
        n_ch = sum(len(at[(ch, d)]) for d in range(D + 1))
        label = f"{g.nodes[ch].get('order')}. {SHORT[ch]} · {n_ch}"
        out.append(f'<text x="{lx:.1f}" y="{ly:.1f}" transform="rotate({deg:.1f} {lx:.1f} {ly:.1f})" '
                   f'font-family="{lib.SANS}" font-size="15" font-weight="bold" text-anchor="middle" '
                   f'{fill("muted")}>{escape(label)}</text>')
    for chain, acc in ((CHAIN_T1, "red"), (CHAIN_T2, "violet")):
        pts = " L ".join(f"{cx + pos[k][0]:.1f} {cy + pos[k][1]:.1f}" for k in chain if k in pos)
        out.append(f'<path d="M {pts}" {sonly(acc)} stroke-width="3" stroke-opacity="0.75" '
                   f'stroke-linejoin="round"/>')
    # The dots and the ids. Each id is a mono <tspan> inside its <text>, so that Canvas.link makes it a link as it
    # does every code run: to the statement's card on the poster that draws it in full, else to its file in the
    # blueprint at BP_COMMIT.
    for k, (px, py) in pos.items():
        acc = PROV_ACCENT[g.nodes[k].get("provenance")]
        x, yy = cx + px, cy + py
        out.append(f'<circle cx="{x:.1f}" cy="{yy:.1f}" r="4.2" {fs(acc, "bg")} stroke-width="1.2"/>')
        th = ang[k]
        deg = math.degrees(th)
        flip = math.cos(th) < 0
        tx, ty = x + 8 * math.cos(th), yy + 8 * math.sin(th)
        out.append(f'<text x="{tx:.1f}" y="{ty + LABEL * 0.35:.1f}" '
                   f'transform="rotate({deg + (180 if flip else 0):.1f} {tx:.1f} {ty:.1f})" '
                   f'font-size="{LABEL}" text-anchor="{"end" if flip else "start"}" '
                   f'{fill(acc)}><tspan font-family="{lib.MONO}">{escape(k)}</tspan></text>')
    c.add("\n".join(out), cy + RMAX)
    c.blocks.append((cx - RMAX, cy - RMAX, cx + RMAX, cy + RMAX, "wheel"))
    y = cy + RMAX + 50

    # ---------------------------------------------------------------------------------- reading it
    y = band(c, X0, y, "2 · Reading the wheel, and how far each chapter reaches")
    key = [
        "**Ring** n holds the statements n uses from a main theorem: ring 0 is the three theorems nothing else "
        "uses, ring 1 what their statements and proofs use, and so on outward, each statement at the first ring "
        "that reaches it. A use can go inward, outward or along a ring; only the shortest path sets the ring.",
        "**Sector** is chapter, in the blueprint's order clockwise from the top. A sector's width is set by its "
        "fullest ring, so that no two dots of one ring sit closer than the height of their labels; it is not the "
        "chapter's size. The label at the rim counts the chapter's reached statements.",
        "**The ids** read outward along the radius, in the colour of the statement's provenance; a dot's place "
        "within its sector and ring is the statement's place in the chapter's files. The chapter posters give "
        "each statement's card.",
        f"**The chains** are T1, {len(CHAIN_T1)} statements from the main theorems down to "
        f"`{CHAIN_T1[-1]}`, and T2, {len(CHAIN_T2)} down to `{CHAIN_T2[-1]}`: two shortest paths, each one step "
        "outward per ring.",
    ]
    nums = [
        f"**{len(depth)} of {len(g.statements)} statements** are reached from the main theorems; the deepest "
        f"ring is {D}. By ring: " + ", ".join(f"{hist[d]} at {d}" for d in sorted(hist)) + ".",
        f"**The wide rings** are 4 and 5, with {hist[4]} and {hist[5]} statements: the stage chapters' results "
        "and the literature they cite, which is where the proof is broad.",
        "**Unreached**: " + names(unreached, 8) + ". Two are remarks and three are the literature chapter's "
        "input packages; a chapter theorem and one published result have no user the blueprint resolved.",
    ]
    rows = []
    for ch in chapters:
        ds = sorted(reach[ch])
        rows.append([f"{g.nodes[ch].get('order')}. {g.nodes[ch]['title']}", str(len(ds)),
                     str(sum(1 for k in g.statements if chap(k) == ch and k not in depth)),
                     str(ds[0]) if ds else "—", str(ds[len(ds) // 2]) if ds else "—", str(ds[-1]) if ds else "—",
                     ", ".join(f"{d}: {len(at[(ch, d)])}" for d in range(D + 1) if at[(ch, d)])])
    hk = max(c.card(0, 0, span(2), "How to read the wheel", key, draw=False, size=S),
             c.card(0, 0, span(1), "In numbers", nums, draw=False, size=S))
    c.card(colx(0), y, span(2), "How to read the wheel", key, "grey", h=hk, size=S, tint=False)
    c.card(colx(2), y, span(1), "In numbers", nums, "grey", h=hk, size=S, tint=False)
    c.table(colx(3), y, [("Chapter", 400), ("Reached", 90), ("Not", 60), ("Nearest", 90), ("Median", 90),
                         ("Deepest", 90), ("By ring", span(2) - 400 - 90 - 60 - 90 - 90 - 90)], rows, size=S)
    return c
