#!/usr/bin/env python3
"""Generate a visualization of a single chain of reductions through the proof.

One path through the dependency graph: from a main theorem,
one `uses` edge per step, down to a statement that uses nothing. By default it
is the longest such chain (a shortest path from the main theorems to the
statement farthest from them), which is how deep the proof goes.

    uv run trace_proof.py                      # deepest chain
    uv run trace_proof.py --first thm-half-plane   # follow the first proof use at each step
    uv run trace_proof.py --to thm-landau-windows  # chain from the main theorems to one statement
"""

import sys
import graphviz
from blueprint_graph import Graph, default_blueprint_dir, LEAF_COLOR


def trace_label(g, step, oid, prev, last):
    n = g.nodes[oid]
    if step == 0:
        header = "Start: Main.lean"
    else:
        header = f"Step {step}: {prev} uses"
    footer = None
    if last:
        src = n.get("source")
        footer = f"■ END: {src}" if src else "■ END: no further reductions in the blueprint"
    return g.label(oid, header=header, footer=footer)


def create_trace(g, path):
    dot = graphviz.Digraph("RiemannTrace", format="png")
    dot.attr(rankdir="TB", bgcolor="white", dpi="150", ranksep="0.5")
    dot.attr("node", shape="box", fontname="Courier", fontsize="11", margin="0.2")
    dot.attr("edge", arrowsize="0.8", penwidth="1.5")
    for i, oid in enumerate(path):
        last = i == len(path) - 1
        prev = path[i - 1] if i else None
        fill = LEAF_COLOR if last else g.fill(oid)
        dot.node(f"s{i}", trace_label(g, i, oid, prev, last), style=g.style(oid), fillcolor=fill)
        if i:
            siblings = len(g.uses(prev)) - 1
            label = f"  1 of {siblings + 1} uses" if siblings else ""
            dot.edge(f"s{i - 1}", f"s{i}", label=label, fontname="Courier", fontsize="9")
    return dot


def path_to(g, target):
    depth, parent = g.depths(g.roots())
    if target not in depth:
        sys.exit(f"{target} is not reachable from the main theorems")
    path = []
    while target is not None:
        path.append(target)
        target = parent[target]
    return list(reversed(path))


def main():
    args = sys.argv[1:]
    bp = default_blueprint_dir()
    if "--blueprint" in args:
        i = args.index("--blueprint")
        bp = args[i + 1]
        del args[i:i + 2]
    g = Graph(bp)
    if "--first" in args:
        start = args[args.index("--first") + 1]
        path = g.first_use_trace(start)
        out = f"riemann_trace_first_{start}"
    elif "--to" in args:
        target = args[args.index("--to") + 1]
        path = path_to(g, target)
        out = f"riemann_trace_to_{target}"
    else:
        path = g.deepest_trace(g.roots())
        out = "riemann_trace"
    print("Trace:")
    for i, oid in enumerate(path):
        print(f"  {i:2d}. {oid}  ({g.nodes[oid]['kind']}, {g.nodes[oid].get('provenance')})")
    dot = create_trace(g, path)
    dot.render(out, cleanup=True)
    print(f"Generated {out}.png")


if __name__ == "__main__":
    main()
