# Triage: a failing check after a pin move, and its fix

Each row is a kind of failure the generator of a pinned diagram set reports, and what fixes it without loosening
anything. The wording of the messages differs between projects; the kinds do not. In every row, "set" means
writing the value the source now has, with the source line in the running list.

| The build says | What moved | Fix |
|---|---|---|
| the checkout is at another commit than the pin | the pin or the checkout | Check the checkout out at the new pin. If it was moved on purpose, bump the pin. |
| the source pins another commit than expected (a lakefile `rev`) | the upstream re-pinned its own dependency | Bump that pin too. The derived files were read at the old one: rebuild them (extracting-lean-deps). |
| the edges between drawn nodes differ from `EXPECTED` | the source's `uses` changed | Diff the list against the source. Add the arrows the source now makes and drop the ones it no longer makes, each with its statement file. Look at the poster: a new edge may cross the layout. |
| a statement named in `EXPECTED` or a layout is not in the source | an id was renamed, moved or deleted | Find the rename in the upstream diff (`git log --follow`, or a search for its title). Rename it everywhere the module names it, including hand layouts and trace paths. |
| a trace's chain differs from its expected path | the deepest chain, or a chain to a target, changed | Set the path to the new chain, and re-read the trace's own prose (its subtitle and intro), which describes the chain. |
| a computed count differs from its guard (`N_*`, `TOP`, `YEARS`, a histogram) | the source has more or fewer of something | Set the guard. Then grep the docs and the poster's own sentences for the old number, since prose that states it is not computed. |
| results named in a proof's text without `uses` differ from `HYPOTHESES` | the source's prose or its `uses` changed | Set the list, and re-read the card text that explains those arrows. |
| an arrow's verdict differs from `VERDICTS` | the derived edge file was rebuilt, or the edges moved | Only after the derived file was rebuilt at the new pins: set the verdicts, and re-read the prose that quotes them (an EDGES-style document). |
| a derived file hashes to another value, or was read from other commits | the derived file is stale | Rebuild it with extracting-lean-deps. Never set the hash to make the build pass. |
| a re-read hash differs (notes, checked pages) | prose the poster paraphrases changed | moving-pins A: re-read, then set the hash. |
| a reference has no paper, or a paper has no reference | the bibliography changed | linking-papers. |
| a title does not fit its card, or two texts overlap | longer text at the new pin | A layout fix (drawing-posters), not a check to relax. Shorten nothing that is quoted unless the poster marks abridgement. |
| a drawn declaration has no signature in the facts index | the Lean name was renamed or dropped | Check the facts index at the new pin. If the statement now names another declaration, the source did it; if the index lost it, report it upstream rather than draw around it. |
| a link names a card no poster draws | an anchor moved | Run the generator a second time, after the manifest update. If it persists, the target was removed: the link follows the source. |

When a failure fits no row, read the check's code before changing anything: its docstring or comment says what it
protects.
