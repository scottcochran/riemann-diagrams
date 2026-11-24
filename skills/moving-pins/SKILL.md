---
name: moving-pins
description: "Moves generated diagrams to new commits of the sources they are drawn from, and re-reads the poster's own prose when a source it paraphrases changes. Bumps the pins, regenerates, and fixes each failing check by recording what the source now says, never by loosening the check; ends with the list of posters a reader must re-read. Use when an upstream source (a blueprint, a mirror of a formal proof) has new commits; when asked to bump a pin such as BP_COMMIT; when the build stops on a pin, on a re-read hash such as NOTES_SHA256 or CHECKS_SHA256, or on a derived file's hash; or when the scheduled sources check failed even though no pin moved. Not for adding or redrawing a poster (drawing-posters), not for a missing paper link alone (linking-papers), not for rebuilding the Lean-derived files (extracting-lean-deps), and not for tagging the result (cutting-releases)."
---

# Moving pins

A poster here is a second reading of its sources, pinned to exact commits. When a source moves, the drawing
follows only after someone reads what changed. The checks make that reading unavoidable, so that a source change
shows up as a failing check and is never silently redrawn. This skill does the reading.

## Contents

- Setup: the project's config
- The rule that does not bend
- A. A re-read hash failed and no pin moved
- B. A source moved
- C. Finish: what a reader must re-read
- Check before you stop

## Setup: the project's config

Read `proof-posters.toml` at the root of the repository. It names the pins file, each commit pin (and where its
checkout is), the re-read hashes with the prose each one guards, the derived files, the regenerate commands and
the names of the recorded expectations (`[build].expected_names`). If the file is missing, stop and ask: the
skill does not guess a project's layout. The project's `CLAUDE.md` holds its shared rules.

Then see where things stand:

```sh
python3 ${CLAUDE_SKILL_DIR}/scripts/pin-status.py --fetch
```

It prints each pin, its checkout's HEAD, the commits between the two, and every hash pinned besides.

## The rule that does not bend

A failing check is fixed by recording what the source now says. Never:

- delete an expected edge, list entry or count guard so that a check passes, unless the source no longer has it;
- widen a tolerance, catch the exception, skip a poster or turn an ERROR into a WARNING;
- set a hash to the new value before the prose it guards has been re-read against the new text.

Each changed expectation must trace to a line of the source at the new pin. Keep a running list of each change
and its source line as you go: the commit message and the tag message are written from it.

## A. A re-read hash failed and no pin moved

This is what a failed scheduled sources check means: a page the poster paraphrases has changed.

1. Fetch the pages again and keep them: run the `refresh` command of the failing `[[pins.reread]]` (it updates
   the recorded hashes and saves each page). The scheduled run's artifact also holds each page as fetched.
2. Diff the old passage against the new one. Use the saved page and the old reading: the artifact from the last
   passing run, or the Wayback Machine. Then sort the change into one of three kinds:
   - **substance**: a claim, a number, a status (a check finished, a caveat added or dropped);
   - **wording**: the same claims, said differently;
   - **layout**: markup only. This should not change the hash, but sometimes does.
3. Re-read the prose named in `reread` against the new text. A paraphrase changes only where the substance did.
   A quoted sentence is quoted exactly, or the quote is replaced. Keep the structure the config describes (for
   example, "arranged by the four questions").
4. Set the hash in the pins file to the new value, regenerate both sets (`[build].regenerate`), and make sure
   no `failure_markers` line is printed.
5. A wording-only or layout-only change still gets its hash bumped, with a commit that says the prose was
   re-read and why it was left alone.

## B. A source moved

1. **Read before you bump.** Run `git log` and `git diff --stat` between the old pin and the new commit in the
   checkout. Look closely at the files the build reads: statement files, `uses` lists, the index of Lean facts,
   the main theorem files, the verification notes. Note reorganisations (renamed ids, moved files) first, since
   they cause the most failures.
2. **Bump** the pins in `[pins].file`. A pin read from another source's file (`read_in`/`read_file`) moves when
   that file says so, not on its own. If it moved, the derived files were read at the old value: see step 5.
3. **Regenerate** both sets and collect every ERROR and WARNING. Work through them one poster at a time, in the
   build's order. `references/triage.md` maps each kind of failure to its fix.
4. **Set each expectation** to what the source says (the rule above), with the source line in your running list.
   - A hand layout (a `PLACE`-style dict) needs new cards placed by hand.
   - A computed layout takes the move without hand work; look at the result anyway.
   - A count in prose that a guard checks (`N_REFS`, a "416 statements" in a README) changes everywhere it is
     written: grep the docs in `[project].docs` for the old number.
5. **Derived files:** if a derived file's hash or its recorded commits fail, the file was read at the old pins.
   Rebuild it with **extracting-lean-deps**, then set its hash. Do not set a derived hash by hand to make the
   build pass.
6. **A reference with no paper** (or a paper with no reference): hand it to **linking-papers**.
7. **Re-read hashes** that fail as well (new verification notes usually come with a newer mirror): do A.3 to A.4
   for each one.
8. **Regenerate until it is clean.** If a run reports that anchors moved and exits 1, run it again. Do both sets.

## C. Finish: what a reader must re-read

Write a short summary, since **cutting-releases** builds the tag message from it:

- the kind of move: which pins moved, from what to what, and how many upstream commits each;
- what changed in the sources, in a sentence each;
- every poster whose drawing changed (`git diff --stat` over `[build].outputs` and the manifests' card and
  arrow counts), and every poster whose prose was re-read: these are the ones a reader must re-read;
- every expectation that changed, and why.

Update the docs that state counts or describe the sources (`[project].docs`). Add a note in the plan if it keeps
one. Stage files by name, never a whole directory, and commit.

## Check before you stop

- Both sets regenerate with no WARNING or ERROR, and running them a second time changes no byte.
- `git diff` over the poster modules shows only expectations that each trace to a source line in your list.
- No check was removed or widened, and no hash was set before its prose was re-read.
- The summary names the posters to re-read.
