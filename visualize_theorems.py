#!/usr/bin/env python3
"""Generate a depth-limited visualization of the theorem dependency graph.

The dependency graph drawn as a state space: the main theorems of Main.lean
are the start state, a `uses` edge is a move, and the diagram shows every
statement within `max_depth` reductions of the main theorems.

    uv run visualize_theorems.py [max_depth] [--blueprint DIR]
    uv run visualize_theorems.py --chapters      # the nine chapters and their uses edges
    uv run visualize_theorems.py --full          # every statement, as riemann_full.dot/.svg
"""

import sys
import graphviz
from blueprint_graph import Graph, default_blueprint_dir, summary, PROVENANCE_COLOR, ROOT_COLOR


def legend(dot):
    with dot.subgraph(name="cluster_legend") as s:
        s.attr(label="Legend", fontname="Courier", fontsize="11", style="rounded", color="gray60")
        s.attr("node", shape="box", fontname="Courier", fontsize="10", style="filled", margin="0.1")
        s.node("L0", "Main.lean theorem", fillcolor=ROOT_COLOR)
        s.node("L1", "new in Alpöge's proof", fillcolor=PROVENANCE_COLOR["new"])
        s.node("L2", "modified from literature", fillcolor=PROVENANCE_COLOR["modified"])
        s.node("L3", "published result", fillcolor=PROVENANCE_COLOR["published"])
        s.node("L4", "definition", fillcolor="white", style="filled,dashed")
        s.edge("L0", "L1", label="proof uses", fontname="Courier", fontsize="9")
        s.edge("L1", "L2", label="statement uses", style="dashed", fontname="Courier", fontsize="9")
        s.edge("L2", "L3", style="invis")
        s.edge("L3", "L4", style="invis")


def create_visualization(g, max_depth=3):
    roots = g.roots()
    depth, _ = g.depths(roots)
    dot = graphviz.Digraph("RiemannTheorems", format="png")
    # Graphviz caps a PNG at 32767 px; past depth 3 the tree is wider than that at 150 dpi.
    dot.attr(rankdir="TB", bgcolor="white", dpi="150" if max_depth <= 3 else "60",
             ranksep="1.0", nodesep="0.3")
    dot.attr("node", shape="box", fontname="Courier", fontsize="11", margin="0.15")
    dot.attr("edge", fontsize="9", arrowsize="0.7")

    visible = {oid for oid, d in depth.items() if d <= max_depth}
    by_depth = {}
    for oid in visible:
        by_depth.setdefault(depth[oid], []).append(oid)

    for d in sorted(by_depth):
        with dot.subgraph() as s:
            s.attr(rank="same")
            for oid in sorted(by_depth[d], key=lambda i: (g.nodes[i]["_chapter"], i)):
                hidden = [u for u in g.uses(oid) if u not in visible]
                footer = f"+{len(hidden)} more below depth {max_depth}" if hidden else None
                s.node(oid, g.label(oid, footer=footer), style=g.style(oid), fillcolor=g.fill(oid))

    for oid in visible:
        for u in g.proof_uses(oid):
            if u in visible:
                dot.edge(oid, u)
        for u in g.statement_uses(oid):
            if u in visible:
                dot.edge(oid, u, style="dashed", color="gray40")
    legend(dot)
    return dot, len(visible)


def create_chapter_overview(g):
    dot = graphviz.Digraph("RiemannChapters", format="png")
    dot.attr(rankdir="TB", bgcolor="white", dpi="150", ranksep="0.7", nodesep="0.4")
    dot.attr("node", shape="box", fontname="Courier", fontsize="11", margin="0.2", style="filled,rounded")
    dot.attr("edge", arrowsize="0.7")
    counts = {}
    for oid in g.statements:
        counts[g.nodes[oid]["_chapter"]] = counts.get(g.nodes[oid]["_chapter"], 0) + 1
    for cid in sorted(g.chapters, key=lambda c: g.nodes[c].get("order", 0)):
        n = g.nodes[cid]
        prov = {}
        for oid in g.statements:
            if g.nodes[oid]["_chapter"] == cid:
                p = g.nodes[oid].get("provenance") or "other"
                prov[p] = prov.get(p, 0) + 1
        label = (f"{n.get('order', '')}. {n['title']}\n[{cid}]\n"
                 f"{counts.get(cid, 0)} statements: "
                 + ", ".join(f"{v} {k}" for k, v in sorted(prov.items())))
        if cid == "main-theorems":
            color = ROOT_COLOR
        elif cid == "chap-literature":
            color = PROVENANCE_COLOR["published"]
        else:
            color = PROVENANCE_COLOR["new"]
        dot.node(cid, label, fillcolor=color)
    for cid in g.chapters:
        for u in g.nodes[cid].get("uses", []):
            if u in g.chapters:
                dot.edge(cid, u)
    return dot


def create_full_graph(g):
    """Every statement and every uses edge."""
    dot = graphviz.Digraph("RiemannFull", format="svg")
    dot.attr(rankdir="TB", bgcolor="white", ranksep="2.0", nodesep="0.15", concentrate="true")
    dot.attr("node", shape="box", fontname="Courier", fontsize="9", margin="0.08", style="filled")
    dot.attr("edge", arrowsize="0.5", color="gray50")
    depth, _ = g.depths(g.roots())
    for oid in sorted(g.statements):
        n = g.nodes[oid]
        label = f"{oid}\n{n['kind']} · {n.get('provenance') or '—'}"
        dot.node(oid, label, style=g.style(oid), fillcolor=g.fill(oid),
                 tooltip=n.get("title", oid), URL=f"https://riemann.fuxi.merten.dev/#{oid}")
    for oid in g.statements:
        for u in g.proof_uses(oid):
            dot.edge(oid, u)
        for u in g.statement_uses(oid):
            dot.edge(oid, u, style="dashed")
    return dot


def main():
    args = sys.argv[1:]
    bp = default_blueprint_dir()
    if "--blueprint" in args:
        i = args.index("--blueprint")
        bp = args[i + 1]
        del args[i:i + 2]
    print(f"Reading blueprint at {bp} ...")
    g = Graph(bp)
    print(f"Found {len(g.statements)} statements, "
          f"{sum(len(g.uses(k)) for k in g.statements)} uses edges, "
          f"{len(g.chapters)} chapters")

    if "--chapters" in args:
        dot = create_chapter_overview(g)
        dot.render("riemann_chapters", cleanup=True)
        print("Generated riemann_chapters.png")
        return
    if "--full" in args:
        dot = create_full_graph(g)
        dot.save("riemann_full.dot")
        dot.render("riemann_full", cleanup=True)
        print("Generated riemann_full.dot and riemann_full.svg")
        return

    max_depth = int(args[0]) if args else 3
    print(f"Creating visualization (depth <= {max_depth}) ...")
    dot, n = create_visualization(g, max_depth=max_depth)
    out = f"riemann_depth{max_depth}"
    dot.render(out, cleanup=True)
    print(f"Generated {out}.png with {n} statements")
    if max_depth > 3:
        dot.format = "svg"
        dot.render(out, cleanup=True)
        print(f"Generated {out}.svg (the PNG is at low resolution; use the SVG to read it)")
    summary(g)


if __name__ == "__main__":
    main()
