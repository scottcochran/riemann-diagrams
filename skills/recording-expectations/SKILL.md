---
name: recording-expectations
description: "Writes or changes a generated output drawn from pinned sources (a poster, a figure, a table) so that it cannot drift from them without a check failing: every fact read from the sources at build time, what the output expects them to say recorded as module-level literals that the build compares in both directions, every sentence quoted, computed, framing, or an interpretation a check guards, the output byte-deterministic, and every doc that lists or counts outputs changed with it. Use when an output is added, or when what one reads, draws or says changes; the project's own poster skill, if it has one, then gives the layout and the look. Not for moving a pin (moving-pins), a paper link (linking-papers), rebuilding the Lean-derived files (extracting-lean-deps), or tagging (cutting-releases)."
---

# Recording expectations

An output drawn from pinned sources is a second reading of them. It stays true only if every change in a source
that touches it stops the build, so that the reading is redone by a person rather than redrawn in silence. This
skill is how an output is written so that this holds. The drawing is the easy part; the checks are the work.

To learn it, start with `references/example.md`: a 54-line output module written this way, run, then broken by
four changes to its source, with what the build printed each time, what happens with its checks taken out, and
what the check script and a release see.

## Contents

- Setup
- 1. Read, don't restate
- 2. Record what you expect
- 3. Every sentence is one of four kinds
- 4. Deterministic bytes
- 5. Say what the checks do not cover
- 6. The docs that list or count outputs
- Check before you stop

## Setup

Read `proof-posters.toml`. `[build].modules` is where the output modules are, `[build].expected_names` the
names of the expectations they record, `[build].minor_names` those whose change makes a release MINOR,
`[build].regenerate` and `[build].outputs` how they are built, and `[project].docs` the docs that list or count
them. Read the project's `CLAUDE.md` for its rules. If `[project].poster_skill` names a skill, read it too: it
says how a module is laid out, which library draws it, and how it is looked at. That skill applies this one.

## 1. Read, don't restate

Every node, edge, count and quotation an output shows comes from the pinned sources at build time, or from a
file derived from them that is pinned by its hash. Nothing the sources say is typed into the module, where it
would stand after the source changed. A fact the sources do not hold yet comes from a new derived file, built
and pinned first (extracting-lean-deps, for a formal proof).

## 2. Record what you expect

Reading is not enough: an output that reads its sources redraws itself when they move, silently. So it also
records what it expects them to say, and the build compares the two.

- **Ask what change should stop this output.** An edge appearing or vanishing between items it draws, a count
  it states, a ranking it shows, a path it traces, a verdict it colours by. Each answer is an expectation.
- **Record each as a module-level literal** under a name in `[build].expected_names`: a list of edges as
  (used, user) pairs, a count, a top-k list, a path. `cutting-releases`' `release-facts.py` reads these names by
  parsing the module as Python and compares their values between a tag and HEAD, so a literal is a fact it can
  report, and a computed value is only code to it. A new kind of expectation adds its name to `expected_names`;
  whether a change to it makes a release MINOR is the project's release table's call (`minor_names`).
- **Compare in both directions.** Something drawn that the source does not have fails, and so does something the
  source has, between items drawn, that is not drawn.
- **Fail the build, and say what to re-read.** Raise an error, never a warning, with both values and the source
  file or id that changed, so that the person moving a pin knows where to look.
- **Never soften a comparison**: no tolerance, no caught exception, no skipped item. Loosening a check is the one
  thing moving-pins forbids, so it must not be built in.
- **Check the record:**

  ```sh
  python3 ${CLAUDE_SKILL_DIR}/scripts/check-expectations.py
  ```

  It fails on a module that records no expectation, a name recorded and never read in its module (it checks
  nothing), a name assigned twice, a name in `expected_names` no module records, and a `minor_names` entry outside
  `expected_names`; it lists each value that is not a literal. It cannot see whether a name that is read is
  compared, or in both directions: that is checked by reading.

## 3. Every sentence is one of four kinds

No sentence may state a fact the build does not check. Each one is:

- **quoted**: from a source file, marked as a quotation (italics, a code panel) and linked to the file, abridged
  with ` …` where cut;
- **computed**: a template filled at build time; the numbers are data and only the wording is the output's;
- **framing**: titles, legends, how-to-read notes, and the caveats of section 5, in the output's own voice;
- **an interpretation**: what the data shows, in the output's own voice and marked as such. It is computed, so
  that its wording follows the data, or it stands behind an assertion that fails the build when the data no
  longer supports it, so that a pin move forces it to be re-read.

A reader must be able to tell a quotation from the output's own words. A relation the generator infers rather
than reads (a link the source's text makes but its data omits) is said to be inferred where it appears, and the
module records the ones it expects. A count written in a doc (a README's "416 statements") is an expectation too:
compute it or guard it.

## 4. Deterministic bytes

Unchanged inputs give unchanged bytes, so that a diff in an output means a source moved.

- Sort every ranking by count, then by name. Never iterate over a set, or a dict whose order comes from hashing.
- Use no time, randomness or environment in the output, except a date the project declares.
- Check it with moving-pins' `determinism.py` (`${CLAUDE_SKILL_DIR}/../moving-pins/scripts/determinism.py` in
  the plugin). It builds everything in two rounds that differ only by `[build].vary_env` and compares every byte.

## 5. Say what the checks do not cover

An output says what it is not. Where nothing was built or proved, it says so; a card that shows a statement says
what the statement is, not that it is proved; an output that shows a verdict says where the verdict came from.
These caveats are framing, and they are written once, where a reader meets the claim.

## 6. The docs that list or count outputs

An output added or changed updates every doc that lists or counts outputs or names their checks, in the same
commit: the ones in `[project].docs`, and the plan's entry if the project keeps one. An output added or removed
is a MINOR release (cutting-releases).

## Check before you stop

- Every fact shown is read from the pinned sources or a pinned derived file.
- Every expectation is a module-level literal under a name in `expected_names`, compared in both directions, and
  its failure says what to re-read. `check-expectations.py` passes.
- Every sentence is quoted, computed, framing, or a guarded interpretation.
- `determinism.py` passes, and the committed outputs are the regenerated ones.
- Every doc that lists or counts outputs says the same as the build.
