---
name: cutting-releases
description: "Prepares a release of generated posters as an annotated, signed version tag: decides MAJOR, MINOR or PATCH from what moved since the last tag, drafts the tag message (the kind of move, what changed, which posters a reader must re-read), hands the tag and push to the custodian, then checks the release run, the release's checksums against the tree at the tag and the Pages site, and writes the plan's done note. Never edits, moves, deletes or re-points a published release or tag. Use when asked to cut, tag or prepare a release; when a phase or a pin move has landed and a release is due; or to check a published release. Not for the pin move itself (moving-pins) or a new poster (the project's own poster skill)."
---

# Cutting releases

A release is how a poster gets cited. "R3 of v0.6.0" names one drawing, from one set of sources, that anyone can
fetch after the tree has moved on. That holds only if a published release is never changed.

## The rule, first

**Never edit, move, re-point, delete or re-create a published release or tag, or suggest doing so.** That
includes its notes and its assets. A release found wrong gets a successor tag, whose message says what was wrong.
Tags are pushed by the custodian (`[project].custodian`), not by you: you draft, they sign and push.

## Setup

Read `[release]` and `[project]` in `proof-posters.toml`. They give the classification table (in the plan), the
tag form and the glob that finds the last tag (`tag_match`), the release and Pages workflows, the site's address,
the asset globs, the checksum file, and the file the workflow writes to record the release (`metadata`, naming its
tag under `metadata_tag`). `release-facts.py` also reads `[build]`: the manifests and the counts in them
(`manifest_counts`), and which recorded expectations make a release MINOR when they change (`minor_names`).

## Steps

1. **Is a release due?** Releases go out when a pin moves, a poster is added or removed, or the checks change.
   A wording fix waits for the next of those, unless it changes what a poster says. Posters that land as a phase
   go out together when the phase is done.
2. **Facts:**

   ```sh
   python3 ${CLAUDE_SKILL_DIR}/scripts/release-facts.py            # since the last tag, to HEAD
   python3 ${CLAUDE_SKILL_DIR}/scripts/release-facts.py --to origin/main
   ```

   It prints the pins at both ends, the derived and re-read hashes that moved, the posters added and removed,
   the cards and arrows that changed, the expectations that changed in each poster module, the commits, and a
   suggested class. It prints ERROR and suggests no class when it cannot read something it needs: a pin the
   config names that the pins file does not assign, a module that is not Python, a manifest of another shape. Run it against the commit that will be tagged, which is on the default branch after the
   merge.
3. **Classify** with the project's table (`references/classification.md` gives the default and how to read it):
   - **MAJOR**: what a poster is verified against changed. The script cannot see this, so decide it.
   - **MINOR**: a pin moved, or a poster was added or removed.
   - **PATCH**: layout, wording or library only, with every expected list unchanged.

   Before 1.0, a MAJOR change may take a MINOR. Give the class and one line on why.
4. **Draft the tag message** in the form of the previous ones. Read the last two with
   `git tag -l --format='%(contents)' <tag>`, and follow `references/tag-message.md`. The message must say what
   a reader of a cited poster has to do. Write it to a file in the scratchpad, not the repository.
5. **Hand over.** Give the custodian the commit, the file and the commands, and stop:

   ```sh
   git tag -s vX.Y.Z <commit> -F <message file>
   git push origin vX.Y.Z
   ```

   Do not create or push the tag yourself, even if you can.
6. **After the push**, once the custodian says it is pushed: watch the release workflow
   (`gh run list --workflow <release workflow> -L 1`, then `gh run watch`). When it passes, run:

   ```sh
   python3 ${CLAUDE_SKILL_DIR}/scripts/verify-release.py vX.Y.Z
   ```

   It downloads the checksum file and the metadata file (`SHA256SUMS` and `pins.json` here), and checks every
   asset against the tree at the tag (not the working tree). It also checks that the metadata file and the Pages
   site both name the tag. Without `[release].metadata` it checks the assets only, and says so. If something fails,
   report it. The fix is a successor release, never a change to this one.
7. **Done note.** Add to the plan's entry for the phase (`[release].done_note`): the tag, the commit, the run id,
   the asset count, and that the checksums match the tree. Commit it on a branch. It goes in with the next change,
   or in a pull request of its own if the user asks.

## Check before you stop

- The class follows the table, and the message says what to re-read.
- You pushed no tag, and you touched no published release.
- `verify-release.py` passed, or its failure is reported with the successor it calls for.
