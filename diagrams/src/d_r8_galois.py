"""R8 — Galois representations, every statement of the chapter, and what each one rests on.

The layout is computed by chapter.py from the chapter's own edges. EXPECTED records the proof-use edges within
the chapter at the blueprint commit the diagrams were written against, and HYPOTHESES the results that proofs name
without listing as uses; the build fails if the blueprint now differs."""
import chapter

ID, SLUG, CH = "R8", "galois", "chap-galois"

# (used, user): the proof-use edges within the chapter
EXPECTED = [
    ("thm-charpoly-de-rham-abelian", "lem-de-rham-eigenpart-rank"),
    ("lem-de-rham-eigenpart-rank", "lem-first-order-deformation-count"),
    ("thm-hecke-bound-base-change", "thm-base-change-unitary"),
    ("thm-twisted-trace-lowest-type", "thm-base-change-unitary"),
    ("thm-unitary-shimura-integral-models", "thm-coincidence-points-cm"),
    ("thm-depth-zero-base-change-principal-series", "thm-compatibility-depth-zero"),
    ("thm-etale-finiteness", "thm-eigenspaces-crystalline"),
    ("thm-projective-bundle-formula", "thm-eigenspaces-crystalline"),
    ("thm-proper-base-change", "thm-eigenspaces-crystalline"),
    ("thm-additive-characteristic-classes", "thm-etale-finiteness"),
    ("thm-projective-bundle-formula", "thm-etale-finiteness"),
    ("thm-proper-base-change", "thm-etale-finiteness"),
    ("thm-galois-reps-unramified-compatible", "thm-galois-reps-from-geometry-and-theta"),
    ("thm-local-global-ramified", "thm-galois-reps-from-geometry-and-theta"),
    ("thm-projective-bundle-formula", "thm-galois-reps-hecke-eigenspaces"),
    ("thm-proper-base-change", "thm-galois-reps-hecke-eigenspaces"),
    ("thm-galois-reps-from-geometry-and-theta", "thm-galois-reps-polarized"),
    ("thm-geometric-galois-odd-rank", "thm-galois-reps-polarized"),
    ("thm-theta-lift-nonvanishing", "thm-galois-reps-polarized"),
    ("thm-galois-reps-hecke-eigenspaces", "thm-galois-reps-polarized"),
    ("thm-kuga-sato-unitary-shimura", "thm-galois-reps-polarized"),
    ("thm-unitary-shimura-integral-models", "thm-galois-reps-polarized"),
    ("thm-base-change-unitary", "thm-galois-reps-polarized"),
    ("thm-local-global-ramified", "thm-galois-reps-polarized"),
    ("thm-galois-reps-csd-above-l", "thm-galois-reps-polarized-cuspidal"),
    ("thm-labesse-base-change", "thm-galois-reps-unramified-compatible"),
    ("thm-twisted-trace-lowest-type", "thm-galois-reps-unramified-compatible"),
    ("thm-hecke-bound-base-change", "thm-galois-reps-unramified-compatible"),
    ("thm-jacquet-rallis-fundamental-lemma", "thm-galois-reps-unramified-compatible"),
    ("thm-base-change-unitary", "thm-galois-reps-unramified-compatible"),
    ("thm-wave-kernels-gln-c", "thm-galois-reps-unramified-compatible"),
    ("thm-eigenspaces-crystalline", "thm-geometric-galois-odd-rank"),
    ("thm-hodge-tate-weights-eigenspaces", "thm-geometric-galois-odd-rank"),
    ("thm-kuga-sato-unitary-shimura", "thm-geometric-galois-odd-rank"),
    ("thm-transfer-unitary-shimura", "thm-geometric-galois-odd-rank"),
    ("thm-galois-reps-hecke-eigenspaces", "thm-geometric-galois-odd-rank"),
    ("thm-jacquet-rallis-fundamental-lemma", "thm-hecke-bound-base-change"),
    ("thm-wave-kernels-gln-c", "thm-hecke-bound-base-change"),
    ("thm-coincidence-points-cm", "thm-hecke-fixed-points-kuga-sato"),
    ("thm-unitary-shimura-integral-models", "thm-hecke-fixed-points-kuga-sato"),
    ("thm-hecke-fixed-points-kuga-sato", "thm-hodge-numbers-eigenspaces"),
    ("thm-unitary-shimura-integral-models", "thm-hodge-numbers-eigenspaces"),
    ("thm-projective-bundle-formula", "thm-hodge-tate-decomposition"),
    ("thm-hodge-tate-decomposition", "thm-hodge-tate-functorial"),
    ("thm-projective-bundle-formula", "thm-hodge-tate-functorial"),
    ("thm-eigenspaces-crystalline", "thm-hodge-tate-weights-eigenspaces"),
    ("thm-etale-finiteness", "thm-hodge-tate-weights-eigenspaces"),
    ("thm-hodge-tate-functorial", "thm-hodge-tate-weights-eigenspaces"),
    ("thm-projective-bundle-formula", "thm-hodge-tate-weights-eigenspaces"),
    ("thm-proper-base-change", "thm-hodge-tate-weights-eigenspaces"),
    ("thm-hecke-fixed-points-kuga-sato", "thm-kuga-sato-unitary-shimura"),
    ("thm-hodge-numbers-eigenspaces", "thm-kuga-sato-unitary-shimura"),
    ("thm-unitary-shimura-integral-models", "thm-kuga-sato-unitary-shimura"),
    ("thm-base-change-unitary", "thm-labesse-base-change"),
    ("thm-bz-derivative-leibniz", "thm-labesse-base-change"),
    ("thm-compatibility-depth-zero", "thm-local-global-ramified"),
    ("thm-universal-first-order-deformation", "thm-unitary-moduli-smooth"),
    ("thm-unitary-moduli-representable", "thm-unitary-shimura-integral-models"),
    ("thm-unitary-moduli-smooth", "thm-unitary-shimura-integral-models"),
    ("lem-first-order-deformation-count", "thm-universal-first-order-deformation"),
]

# (named, in the proof of): results a proof names in its text without listing them as uses
HYPOTHESES = [
    ("thm-galois-reps-polarized", "thm-galois-reps-csd-above-l"),
    ("thm-galois-reps-polarized", "thm-galois-reps-polarized-cuspidal"),
]


def build():
    return chapter.build(ID, CH, EXPECTED, HYPOTHESES)
