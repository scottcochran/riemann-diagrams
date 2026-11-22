"""T2 — The chain to Landau's theorem: the analytic end of the proof, from the Riemann Hypothesis down.

The chain is computed by trace.py; EXPECTED records it at the blueprint commit the diagrams were written against,
and the build fails if the blueprint now gives another."""
import trace

ID, SLUG = "T2", "trace-landau"
TARGET = "thm-landau-windows"
EXPECTED = [
    "thm-riemann-hypothesis", "thm-half-plane", "thm-grh-from-galois", "thm-zero-free-from-connected",
    "thm-zero-free-from-windows", "thm-landau-windows",
]


def build():
    return trace.build(ID, TARGET, EXPECTED,
                       "The chain to Landau's theorem: from a theorem of 1905 up to the Riemann Hypothesis",
                       "This is the analytic end of the proof in six steps: Landau's theorem on Dirichlet series "
                       "with non-negative coefficients turns a bound on windows into a zero-free half-plane, and "
                       "the four reductions above it carry that half-plane to the Riemann Hypothesis.")
