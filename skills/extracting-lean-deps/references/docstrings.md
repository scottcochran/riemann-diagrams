# Reading the formalisers' docstrings

Some formalisations annotate their declarations by a convention: a line in a declaration's docstring that names
the paper item it formalises, or records a gap, an input taken from the literature, or where the Lean departs from
the print. Where a project does, its docstrings are data a poster can read: which item each declaration
formalises, which are left open and why, where the formalisation differs from the paper. This page is the method,
from the one project that does it so far.

## The example

riemann-masullo-diagrams reads the docstrings of riemann-masullo, a Lean formalisation of a manuscript. At its
commit `ccc599e` (2026-11-25), `diagrams/src/deps.json` was read from riemann-masullo at `72a10ffc48`, and holds
21,342 user-written declarations: 5,359 with a `Paper:` reference, 1,383 with a `Deviation:` line, 18 with a
`Gap:` line, 9 with a `Classical input:` line, 14,909 with a summary, and 16 open. Its reader is
`tools/deps/build-deps.py`, and `tools/deps/README.md` says where each rule could be wrong. One docstring, from
`RiemannMasullo/AppA_AlgebraicNT/Sec1.lean` at `72a10ffc48` (Apache-2.0):

```lean
/-- Paper: Definition A.1.1.1, p. 539. The restricted product consists of the tuples
eventually in the distinguished subgroups. Boxes of identity neighborhoods which eventually
equal those subgroups form a neighborhood basis at the identity.
Deviation: The printed Cartesian product does not provide the two subsets used in the
definition. We use a finite subset of exceptional indices and its complement. -/
theorem restrictedProduct_description :
```

From it the reader takes the item and pages (`Definition A.1.1.1`, 539), the summary (the paragraph after the
reference, to the next label), and the `Deviation:` text.

## Where docstrings are, and are not

- **Not in the export.** A lean4export export holds kernel declarations: names, levels, expressions, and per
  declaration its type, value and the like. A docstring is none of these. In Sutherland's export of the
  riemann-hypothesis proof, the declaration records carry no docstring field, and the ingest, which stops on any
  record kind it does not know, read all of its lines without meeting one.
- **In the compiled modules**, in the docstring extension, which a Lean program run against the build reads.
  riemann-masullo-diagrams runs the formal project's own `scripts/progress/Deps.lean` against its compiled library,
  which at `72a10ffc48` asks `docStringExt.find? (level := .exported) env name` and, failing that, the same at
  `(level := .server)`. Under the module system a docstring can sit in a module's server part (`.olean.server`),
  so a reader that loads only the public part misses it: load the parts together, as for the proofs.
- **In the source**, as `/-- … -/` before each declaration. Reading the source is simplest, and needs care with
  attributes, `include … in` lines and macros between the comment and the declaration.

So the docstrings come from the cross-check reading or the source, never from the primary one; record which in the
derived file's `meta`.

## The rules to record

- **A label counts only at the start of a line.** `^Deviation:` with multiline matching. The word inside a
  sentence is not the label. Count those near-misses and say how many there are: riemann-masullo-diagrams' README
  records six docstrings that use the word inside a sentence, not counted.
- **Where a labelled part ends:** at a blank line, at the next line that opens a label (`[A-Z][A-Za-z ]+:`), or at
  the end. Write the rule in the reader's docstring, and keep it stable, since every count on a poster rests on it.
- **The reference's form:** the item and its pages, read by one pattern. A reference the pattern does not parse is
  reported, not dropped.
- **The summary:** the paragraph after the reference, or from the start, to the first blank line or label. A
  paragraph that is itself labelled gives none.
- **The labels are the formal project's convention, not the poster project's.** Take them from its contributing
  guide or its own tools, and pin the commit you read them at. When the convention changes there, the reader
  changes with it, and the counts move.

## Pinning and quoting

- The docstring data is a derived file like the others: written by a tool from a pinned commit, its hash pinned,
  its `meta` naming the commit, the toolchain and what it was read from.
- **Quoting a docstring is quoting the formal proof's source.** riemann-masullo is Apache-2.0, so a card may quote
  a docstring's sentence with attribution. A proof published without a licence (the riemann-hypothesis mirror is)
  gives no such permission: count and link, do not quote, until it does.
- A project with no convention has nothing here to read. In the riemann-hypothesis mirror at `c900e67`, 6 of its
  149,217 `.lean` files have a docstring at all, and none has a labelled line.
