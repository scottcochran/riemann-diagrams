"""T1 — The deepest chain: from the statement farthest from the main theorems up to the Riemann Hypothesis.

The chain is computed by trace.py; EXPECTED records it at the blueprint commit the diagrams were written against,
and the build fails if the blueprint now gives another."""
import trace

ID, SLUG = "T1", "trace-deepest"
TARGET = None                      # the farthest statement, as blueprint_graph.deepest_trace finds it
EXPECTED = [
    "thm-riemann-hypothesis", "thm-half-plane", "thm-grh-from-galois", "thm-family-data-exists",
    "thm-family-conditions-from-basic", "prop-small-terms-offdiag-level", "thm-offdiagonal-bound",
    "prop-offdiagonal-hypotheses-hold", "prop-pair-coefficient-local-decomposition", "lem-local-partner-counts",
    "lem-local-lattice-counts-isometries",
]


def build():
    return trace.build(ID, TARGET, EXPECTED,
                       "The deepest chain: from a count of lattices by isometries up to the Riemann Hypothesis",
                       "This is how deep the proof goes: no statement of the blueprint is farther from the main "
                       "theorems than the first card. The chain runs through the families, the off-diagonal bound "
                       "of the theta chapter, and down to a local lattice count.")
