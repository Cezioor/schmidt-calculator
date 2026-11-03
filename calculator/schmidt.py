"""
Schmidt decomposition of pure bipartite quantum states.

A pure state |psi> of a system split into parts A (dimension d_A) and
B (dimension d_B) can always be written as

    |psi> = sum_k  lambda_k |a_k> (x) |b_k>

where lambda_k > 0 are the Schmidt coefficients and {|a_k>}, {|b_k>} are
orthonormal sets. The number of non-zero coefficients is the Schmidt rank:
rank 1 means the state is a product state, rank > 1 means it is entangled.

Numerically, the decomposition is the singular value decomposition (SVD)
of the state's amplitudes reshaped into a d_A x d_B matrix.
"""

from dataclasses import dataclass

import numpy as np
from scipy.linalg import svd

TOLERANCE = 1e-10


@dataclass(frozen=True)
class SchmidtTerm:
    """One term lambda_k |a_k> (x) |b_k> of the decomposition."""

    coefficient: float
    vector_a: np.ndarray
    vector_b: np.ndarray


@dataclass(frozen=True)
class SchmidtResult:
    dim_a: int
    dim_b: int
    state: np.ndarray
    terms: list[SchmidtTerm]
    entropy: float

    @property
    def rank(self) -> int:
        return len(self.terms)

    @property
    def coefficients(self) -> list[float]:
        return [term.coefficient for term in self.terms]

    @property
    def is_entangled(self) -> bool:
        return self.rank > 1

    @property
    def max_entropy(self) -> float:
        """Entropy of a maximally entangled state of these dimensions."""
        return float(np.log2(min(self.dim_a, self.dim_b)))

    @property
    def purity(self) -> float:
        """Purity Tr(rho_A^2) of the reduced state; 1 for product states."""
        return float(sum(c**4 for c in self.coefficients))


def parse_state(text: str) -> np.ndarray:
    """
    Parse amplitudes from text such as "1, 0, 0, 1", "[0.6 0 0 0.8]"
    or "1, 0, 0, i". Both "i" and "j" are accepted as the imaginary unit.
    """
    cleaned = text.strip().strip("[]()").replace("i", "j").replace(" ", ",")
    parts = [p for p in cleaned.split(",") if p]
    if not parts:
        raise ValueError("Enter at least one amplitude.")
    try:
        return np.array([complex(p) for p in parts])
    except ValueError:
        raise ValueError(
            "Could not read the amplitudes. Use numbers separated by commas, "
            "e.g. 1, 0, 0, 1 or 0.5+0.5j, 0, 0, 0.5."
        ) from None


def normalize(state: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(state)
    if norm < TOLERANCE:
        raise ValueError("The state vector cannot be all zeros.")
    return state / norm


def schmidt_decomposition(state: np.ndarray, dim_a: int, dim_b: int) -> SchmidtResult:
    """Normalise the state and compute its Schmidt decomposition."""
    if state.size != dim_a * dim_b:
        raise ValueError(
            f"A {dim_a} x {dim_b} system needs {dim_a * dim_b} amplitudes, "
            f"but {state.size} were given."
        )

    state = normalize(state.astype(complex))
    matrix = state.reshape(dim_a, dim_b)
    u, singular_values, vh = svd(matrix, full_matrices=False)

    terms = [
        SchmidtTerm(coefficient=float(s), vector_a=u[:, k], vector_b=vh[k, :])
        for k, s in enumerate(singular_values)
        if s > TOLERANCE
    ]

    probabilities = np.array([t.coefficient**2 for t in terms])
    entropy = float(-np.sum(probabilities * np.log2(probabilities)))

    return SchmidtResult(
        dim_a=dim_a,
        dim_b=dim_b,
        state=state,
        terms=terms,
        entropy=max(entropy, 0.0),  # avoid printing -0.0
    )


def format_vector(vector: np.ndarray, digits: int = 3) -> str:
    """Readable form of a (possibly complex) vector, e.g. (0.707, 0.707i)."""

    def fmt(z: complex) -> str:
        # "+ 0.0" turns -0.0 into 0.0 so the page never shows "-0"
        re, im = round(z.real, digits) + 0.0, round(z.imag, digits) + 0.0
        if abs(im) < 10**-digits:
            return f"{re:g}"
        if abs(re) < 10**-digits:
            return f"{im:g}i"
        sign = "+" if im > 0 else "-"
        return f"{re:g}{sign}{abs(im):g}i"

    return "(" + ", ".join(fmt(z) for z in vector) + ")"


SQRT2 = np.sqrt(2)

EXAMPLE_STATES = {
    "bell_phi_plus": ("Bell |Φ+⟩ = (|00⟩ + |11⟩)/√2", "0.7071, 0, 0, 0.7071", 2, 2),
    "bell_psi_minus": ("Bell |Ψ−⟩ = (|01⟩ − |10⟩)/√2", "0, 0.7071, -0.7071, 0", 2, 2),
    "product_00": ("Product |0⟩⊗|0⟩", "1, 0, 0, 0", 2, 2),
    "product_plus": ("Product |+⟩⊗|+⟩", "0.5, 0.5, 0.5, 0.5", 2, 2),
    "partial": ("Partially entangled 0.8|00⟩ + 0.6|11⟩", "0.8, 0, 0, 0.6", 2, 2),
    "complex": ("Complex phase (|00⟩ + i|11⟩)/√2", "1, 0, 0, i", 2, 2),
    "qutrits": ("Maximally entangled qutrits (3×3)", "1,0,0, 0,1,0, 0,0,1", 3, 3),
}
