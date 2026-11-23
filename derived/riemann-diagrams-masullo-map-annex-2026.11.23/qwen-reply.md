# The reply the custodian pasted

The custodian's question to Qwen was "Can the riemann-diagrams repo be adapted to mapping the Masullo paper?".
What follows is Qwen's reply, as the custodian pasted it into the session on 2026.11.23. It is kept as the thing
the write-up assesses; its claims are Qwen's, and section 3 of the write-up says which held.

---

Yes — and interestingly, the repo barely needs to change. The work is upstream of it.

**Why it ports cleanly:** riemann-diagrams never reads Lean source. It reads one thing: the [riemann-blueprint](https://github.com/chrisflav/riemann-blueprint) — 416 statements, each a Markdown file with TOML front matter naming its Lean declarations and what it `uses`, plus a `lean-facts.json` giving a signature, file and line per Lean name. Point `RIEMANN_BLUEPRINT` at a different directory and every poster and Graphviz graph is generated from that instead. So "adapting to Masullo" means **authoring a Masullo blueprint**, not editing the generator.

**And the raw material already exists.** There's an active Lean transcription of the paper at [mccorvie/riemann-masullo](https://github.com/mccorvie/riemann-masullo), with `Main.lean`, `Statements.lean`, `comparator.json` — the same three files the community mirror supplies for the Alpöge proof — plus `paper/` and `transcription/`. That gives you the statement inventory and the Lean names the blueprint's front matter needs.

**The real blockers are substantive, not technical:**

1. **Scale and provenance.** ~940 pages will likely yield far more than 416 statements, and the blueprint's three-way `published / modified / new` palette maps poorly. Almost all of Masullo's Hecke-L-function work over number fields is new, so F2 ("What is new") would lose its contrast and the chapter colours would collapse to one fill.
2. **No verification floor.** For Alpöge, R1's band 5 reports hard facts: the archive compiled in full, the kernel checked every declaration, and independent kernels accepted the five theorems. For Masullo there is no such band to draw. Worse, `ERRATA.md` records entries classified as *false as stated* — e.g. F30, Theorem 5.2.4.1(1)–(2), p. 239, where the counterexample concerns compatibility with enlargement of S. A node that is false-as-stated still has incoming `uses` edges, so the dependency graph would faithfully show an argument resting on broken nodes. The current poster format has no state for that, and adding one is the only genuine change the repo needs.
3. **Edges are the weak link already.** The repo itself warns that `uses` edges come from identifiers resolved in Lean source *without building it*, so some are wrong and no proof status is recorded. For a manuscript mid-revision, with Conrad's note that the method can't be judged until it's closer to completion, those edges would be a snapshot of a moving target — you'd need to pin to a draft sha256 (the repo's release/checksum discipline already handles this well).
4. **F3 and F4 have no counterpart.** F3 puts the paper beside the formalisation's modules; there is no Masullo formalisation to put beside. F4's 209-reference timeline would be the richest single gain — a bibliography cone showing what falls if each cited result were wrong — but it depends on extracting the paper's references, which no one has done yet.

**My read:** the honest adaptation is a *diagnostic* tool, not a celebration of it. The posters' value for Alpöge is showing what's verified; for Masullo they'd be most useful inverted — errata entries as coloured nodes on the dependency wheel, so you can see at a glance how deep each disputed step sits and how many statements above it would fall. That is exactly the kind of picture that would help reviewers judge whether the trace formula's problems are local or structural, and it's the one thing no reader of the 940-page PDF can currently get.

The licence is also friendly: Apache-2.0 for code and tooling, CC BY 4.0 for the rendered diagrams, and the drawing library is the same author's — so a fork or a second blueprint target is unobstructed.
