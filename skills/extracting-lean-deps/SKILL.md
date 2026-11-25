---
name: extracting-lean-deps
description: "Reads the real dependency graph of a Lean formal proof without building it, from a published export of the proof (lean4export NDJSON) cross-checked against the project's public build cache of compiled modules, and turns it into small derived files a poster can read: a verdict on every edge a blueprint draws, the assumptions the proof takes, the formal work under each statement, and what changed between two commits. Each file is pinned by its hash and the commits it was read from. Use when a derived Lean file must be rebuilt because a pin moved; when the build stops on a derived file's hash or commits; when a new poster needs a new fact about the formal proof; or when asked whether the Lean bears out a blueprint arrow. Not for regenerating the posters themselves (moving-pins), or for writing a poster that reads the files (recording-expectations)."
---

# Extracting Lean dependencies

A blueprint states which results each statement `uses`, often resolved from the text and sometimes wrong. The
formal proof's own references are the check. This skill gets those references from published files, so that no
Lean is built and the result can be repeated by anyone with the files.

## Setup

Read `[lean]` and `[[pins.derived]]` in `proof-posters.toml`. `[lean].method` is the project's own runbook, with
the exact commands in order, their timings and their sizes. Follow it for the commands. This skill is the
method behind them: what to trust, in what order, and what goes wrong. To learn it, start with
`references/sketch.md`: the method in one picture, a ten-statement example run through the reference tools, each
lesson with what it does to that example, and five questions to check yourself.

The data is large (tens to a hundred GB) and lives outside the repository, on a disk with room. Say how much
before starting, and ask where to put it.

## The two readings

1. **The export: the primary reading.** A published export of the proof (lean4export NDJSON) at the commit the
   blueprint pins. It holds the dependency closure of the main theorems, so a declaration missing from it is one
   the proof does not use. Check its published checksum, packed and unpacked, before using it. Index it once, then
   build the reference graph from the index.
2. **The build cache: the cross-check.** Every compiled module of the mirror at one commit, fetched by the
   receipt the project's `lake exe cache get` reads, and read by a small Lean program with the commit's own
   toolchain. It is a later tree than the export, so where the two disagree on an edge, list the edge (`differs`,
   `moves`) rather than pick one.

Each derived file has a `meta` file beside its tool that records the commits and checksums it was read from. The
build checks both the file's hash and those commits. So moving any pin means rebuilding every derived file read at
it, in dependency order (the edges file first, since others read it), then updating each `meta` and each hash pin.

## Judging an edge

`references/verdicts.md` defines the verdicts, applied in order. Use them as defined and keep them in order: a
poster's legend and its checks depend on the definitions, and changing them is a change in what is checked (a
MAJOR release).

## Pitfalls (each one cost a run)

- **Read a module's parts together.** `.olean`, `.olean.server` and `.olean.private` hold different parts, and
  proofs live in the private part. Read them with `readModuleDataParts`, or the proofs are missing and every edge
  looks `apart`.
- **leantar needs a big stack:** `RUST_MIN_STACK=8388608`.
- **Module names can contain apostrophes**, so pass paths NUL-separated (`find -print0`, `xargs -0`).
- **The toolchain must be the commit's own** (its `lean-toolchain`). A different one reads the modules wrongly or
  not at all.
- **Helpers are not statements.** "Reaches" follows references through every declaration no statement names
  (helper lemmas, `_proof_n`, matchers) until it meets one that a statement names. Stopping at the first helper
  undercounts `direct`.
- **Hypothesis types count as mentions** when testing `beside`: B may only be assumed where A is applied.
- **Library declarations are not the project's.** The tool's docstring gives the rule that separates them. Keep it
  stable, since the weight and drift numbers depend on it.
- **Compiler names change with the Lean version.** Compare user-written, auxiliary and private names separately,
  or a toolchain bump looks like a rewrite.

## Steps

1. Say which derived files must be rebuilt and why (which pin moved, or which file's hash failed), and how much
   disk and time the runbook says it takes.
2. Fetch and verify the export (checksums), and index it. Fetch the cache at the cross-check commit with its
   toolchain, then read it.
3. Build each derived file with the runbook's commands, writing to the repository's derived-file paths and
   passing each tool its `meta` file.
4. Read each file's summary counts against the previous version: totals, verdict counts, `differs`. A large swing
   needs an explanation from the upstream diff before it is drawn.
5. Set each `[[pins.derived]]` hash in the pins file. Regenerate. Every poster that reads the file will fail where
   its recorded verdicts or counts moved: set those as moving-pins does, each traced to the file.
6. Update the document that explains the edges (an EDGES-style file), anywhere its numbers changed.

## Check before you stop

- Each derived file's `meta` names the commits it was read from, and they are the pins.
- Both runs were made, and their disagreements are listed, not resolved by choice.
- No verdict definition changed, or the change is flagged as MAJOR.
