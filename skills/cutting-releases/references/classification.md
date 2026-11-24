# What the number says

The default table, adapted from what a release can change for a reader of a cited poster. A project's plan may
refine it (`[release].classification` names where); the project's table wins.

| Part | When it changes | What a reader of a cited poster has to do |
|---|---|---|
| MAJOR | The checks change: what a poster is verified against (a kind of check added, removed or redefined), or the source of the edges is replaced | Re-read every poster: the arrows may mean something else |
| MINOR | A source pin moves, or a poster is added or removed | Re-read the posters the tag message names; the others are the same drawing at a new date |
| PATCH | Layout, wording or library changes; no pin moves and every expected list is unchanged | Nothing: the same statements and arrows, drawn again |

Reading it:

- **A new derived file pinned for a new poster** is MINOR (a poster added). It is MAJOR only if existing posters
  are now checked against it in a new way.
- **A new kind of check on existing posters** (for example, verdicts against a formal proof, where before there
  were only the blueprint's edges) is MAJOR. Before 1.0, it may go out as MINOR, and the tag message then says it
  is a change in what is checked.
- **A re-read hash that moved** (new verification notes, a changed page) is at least PATCH. It is MINOR when it
  came with a pin move, or when it changes what a poster says.
- **The posters' date in the file name** changes with every regeneration. That alone is not a move.
- **Several kinds in one release** take the highest.
