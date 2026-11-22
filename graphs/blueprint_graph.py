#!/usr/bin/env python3
"""Read the riemann-blueprint into a theorem dependency graph.

Each statement in the blueprint is one Markdown file with TOML front matter:
its kind, title, provenance, the Lean declarations it stands for, and `uses`,
the statements it refers to. Its proof is a sibling `.proof.md` with its own
`uses`. This module reads all of them into one graph: the raw state space the
diagrams are cut from.
"""

import os
import json
import tomllib
import textwrap
from collections import deque

STATEMENT_KINDS = ("theorem", "proposition", "lemma", "corollary", "definition", "remark")
STRUCTURE_KINDS = ("chapter", "section")

# Fill colours per provenance, the same as the blueprint site (blueprint.toml).
PROVENANCE_COLOR = {
    "published": "#e3ecf8",   # a published theorem, used as published
    "modified": "#f7eed6",    # a published theorem in a modified or weaker form
    "new": "#dff1e3",         # new in Alpöge's proof
    None: "#f2f2f2",
}
ROOT_COLOR = "#fff3b0"        # the statements of Main.lean
LEAF_COLOR = "#f4c7c3"        # the end of a trace

# The theorems of Main.lean in the mirror, and the blueprint node each one lives in.
MAIN_LEAN_THEOREMS = {
    "riemannHypothesis": "thm-riemann-hypothesis",
    "riemannZeta_eq_zero_re": "thm-riemann-hypothesis",
    "LFunction_ne_zero_of_half_lt_re": "thm-half-plane",
    "LFunction_eq_zero_re": "thm-critical-line",
    "LFunction_eq_zero_re_of_isPrimitive": "thm-critical-line-primitive",
}


def default_blueprint_dir():
    env = os.environ.get("RIEMANN_BLUEPRINT")
    if env:
        return env
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", "riemann-blueprint", "blueprint"))


def output_dir():
    """Where the scripts write: beside themselves, whatever the working directory."""
    return os.path.dirname(os.path.abspath(__file__))


class Graph:
    def __init__(self, root):
        self.root = root
        self.nodes = {}      # id -> front matter + _path, _chapter
        self.proofs = {}     # statement id -> proof front matter
        self.lean_facts = {} # lean name -> {file, startLine, ...} if available
        self._read()
        self._facts()

    # -- reading ------------------------------------------------------------

    def _read(self):
        for d, _, files in os.walk(self.root):
            for f in sorted(files):
                if not f.endswith(".md"):
                    continue
                path = os.path.join(d, f)
                with open(path, encoding="utf-8") as fh:
                    text = fh.read()
                if not text.startswith("+++"):
                    continue
                fm = tomllib.loads(text.split("+++", 2)[1])
                if f.endswith(".proof.md"):
                    self.proofs[fm["of"]] = fm
                    continue
                base = f[:-3]
                oid = fm.get("id") or (os.path.basename(d) if base == "_section" else base)
                rel = os.path.relpath(path, self.root)
                fm["_path"] = rel
                fm["_chapter"] = rel.split(os.sep)[0]
                self.nodes[oid] = fm
        self.statements = {k for k, v in self.nodes.items() if v["kind"] in STATEMENT_KINDS}
        self.chapters = {k for k, v in self.nodes.items() if v["kind"] == "chapter"}

    def _facts(self):
        facts = os.path.join(self.root, "..", "lean-facts.json")
        if os.path.exists(facts):
            with open(facts, encoding="utf-8") as fh:
                self.lean_facts = json.load(fh).get("decls", {})

    # -- edges --------------------------------------------------------------

    def statement_uses(self, oid):
        return [u for u in self.nodes[oid].get("uses", []) if u in self.statements]

    def proof_uses(self, oid):
        seen = set(self.statement_uses(oid))
        out = []
        for u in self.proofs.get(oid, {}).get("uses", []):
            if u in self.statements and u not in seen and u != oid:
                out.append(u)
                seen.add(u)
        return out

    def uses(self, oid):
        """Everything oid depends on: proof uses first (the reductions), then statement uses."""
        return self.proof_uses(oid) + self.statement_uses(oid)

    def used_by(self):
        rev = {k: [] for k in self.statements}
        for k in sorted(self.statements):
            for u in self.uses(k):
                rev[u].append(k)
        return rev

    def main_theorems(self):
        """The blueprint nodes that carry the theorems of Main.lean, in blueprint order."""
        ids = []
        for oid in MAIN_LEAN_THEOREMS.values():
            if oid not in ids:
                ids.append(oid)
        return sorted(ids, key=lambda i: self.nodes[i].get("order", 0))

    def roots(self):
        """Main-theorem nodes that nothing else uses: where every trace begins."""
        rev = self.used_by()
        return [m for m in self.main_theorems() if not rev[m]]

    # -- search -------------------------------------------------------------

    def depths(self, starts):
        """Breadth-first depth of every statement reachable from `starts`, with a parent map."""
        depth = {s: 0 for s in starts}
        parent = {s: None for s in starts}
        q = deque(starts)
        while q:
            x = q.popleft()
            for u in self.uses(x):
                if u not in depth:
                    depth[u] = depth[x] + 1
                    parent[u] = x
                    q.append(u)
        return depth, parent

    def deepest_trace(self, starts):
        """A shortest path from the roots to the statement farthest from them."""
        depth, parent = self.depths(starts)
        far = max(depth, key=lambda k: (depth[k], k))
        path = []
        while far is not None:
            path.append(far)
            far = parent[far]
        return list(reversed(path))

    def first_use_trace(self, start):
        """Follow the first proof use from `start`, result to result, until one uses nothing.

        Definitions and remarks are skipped as steps: a reduction goes to a theorem,
        proposition, lemma or corollary, which is what the blueprint lists first."""
        results = ("theorem", "proposition", "lemma", "corollary")
        path = [start]
        seen = {start}
        while True:
            nxt = [u for u in self.uses(path[-1])
                   if u not in seen and self.nodes[u]["kind"] in results]
            if not nxt:
                return path
            path.append(nxt[0])
            seen.add(nxt[0])

    # -- labels -------------------------------------------------------------

    def lean_location(self, name):
        f = self.lean_facts.get(name)
        if not f or not f.get("range"):
            return None
        file = f["range"]["file"].split(".lake/packages/tree/")[-1]
        return f"{file}:{f['range']['startLine']}"

    def label(self, oid, header=None, width=36, footer=None):
        """A plain-text card for a node."""
        n = self.nodes[oid]
        lines = []
        if header:
            lines.append(header)
            lines.append("─" * width)
        lines.extend(textwrap.wrap(n.get("title", oid), width) or [oid])
        prov = n.get("provenance") or "—"
        lines.append(f"[{oid}]")
        lines.append(f"{n['kind']} · {prov}")
        lean = n.get("lean", [])
        if lean:
            first = lean[0]
            more = f" (+{len(lean) - 1})" if len(lean) > 1 else ""
            lines.extend(textwrap.wrap(f"Lean: {first}{more}", width, subsequent_indent="      "))
            loc = self.lean_location(first)
            if loc:
                lines.extend(textwrap.wrap(f"at {loc}", width, subsequent_indent="   "))
        chap = self.nodes.get(n["_chapter"], {}).get("title", n["_chapter"])
        lines.append(f"Chapter: {chap}")
        if footer:
            lines.append("─" * width)
            lines.extend(textwrap.wrap(footer, width))
        return "\n".join(lines)

    def fill(self, oid):
        if oid in self.main_theorems():
            return ROOT_COLOR
        return PROVENANCE_COLOR.get(self.nodes[oid].get("provenance"))

    def style(self, oid):
        n = self.nodes[oid]
        if n["kind"] == "definition":
            return "filled,dashed"
        if n["kind"] == "remark":
            return "filled,dotted"
        return "filled"


def summary(g):
    """State distribution by depth."""
    depth, _ = g.depths(g.roots())
    by = {}
    for oid, d in depth.items():
        row = by.setdefault(d, {"count": 0, "published": 0, "modified": 0, "new": 0})
        row["count"] += 1
        p = g.nodes[oid].get("provenance")
        if p in row:
            row[p] += 1
    print("\nStatement distribution by depth from the main theorems:")
    print("Depth | Statements | Published | Modified | New")
    print("------+------------+-----------+----------+-----")
    for d in sorted(by):
        r = by[d]
        print(f"  {d:2d}  |    {r['count']:4d}    |   {r['published']:4d}    |  {r['modified']:4d}    | {r['new']:4d}")
    unreached = g.statements - set(depth)
    print(f"\n{len(depth)} statements reachable from the main theorems, {len(unreached)} not reachable.")
