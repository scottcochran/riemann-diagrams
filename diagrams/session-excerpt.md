My recommendation: R3, the zero-free chapter from the inside

It is the analytic half of the proof, 24 statements across five sections, which is poster-sized. The blueprint itself says the square root in the core inequality is the Riemann Hypothesis, so it is where the mathematics is.
The cards already carry statement, proof and uses; the new work is laying out a real chain: Landau's theorem on windows, the auxiliary fields, the core inequality, slope data, the local link at inert primes.
It would be the first poster whose arrows are the argument rather than the architecture, which tests whether the format can carry proof content at all. If it works, the same module template covers the other four stage chapters.
Two smaller steps worth doing either way

A GitHub Actions workflow that checks out the blueprint at the pinned commit, regenerates the posters, and fails on any byte difference. The build is already deterministic and strict, so this turns "the sources moved under the diagram" into a red check instead of a surprise.
A trace mode for the posters: a single chain from riemannHypothesis to one leaf, drawn as cards instead of Graphviz boxes, which is the one Graphviz diagram the posters do not yet replace.
The bigger step, when it becomes possible

Everything here rests on edges resolved from source text, and every status reads absent. Running the blueprint's extract against built oleans would replace approximate edges with real ones and fill in proof statuses. That needs the community build cache and a machine with a lot of memory, and the mirror's notes say the Comparator run itself is still pending. When that lands, a status band on R1 is the diagram to update first.
