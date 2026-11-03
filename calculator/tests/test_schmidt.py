import numpy as np
import pytest

from calculator.schmidt import format_vector, parse_state, schmidt_decomposition

SQRT2 = np.sqrt(2)


def test_bell_state_is_maximally_entangled():
    result = schmidt_decomposition(np.array([1, 0, 0, 1]), 2, 2)

    assert result.rank == 2
    assert result.is_entangled
    assert result.coefficients == pytest.approx([1 / SQRT2, 1 / SQRT2])
    assert result.entropy == pytest.approx(1.0)
    assert result.purity == pytest.approx(0.5)


def test_product_state_has_rank_one():
    plus = np.array([1, 1]) / SQRT2
    result = schmidt_decomposition(np.kron(plus, plus), 2, 2)

    assert result.rank == 1
    assert not result.is_entangled
    assert result.entropy == pytest.approx(0.0)
    assert result.purity == pytest.approx(1.0)


def test_partially_entangled_state():
    result = schmidt_decomposition(np.array([0.8, 0, 0, 0.6]), 2, 2)

    assert result.coefficients == pytest.approx([0.8, 0.6])
    expected_entropy = -(0.64 * np.log2(0.64) + 0.36 * np.log2(0.36))
    assert result.entropy == pytest.approx(expected_entropy)


def test_unnormalised_input_is_normalised():
    result = schmidt_decomposition(np.array([3, 0, 0, 4]), 2, 2)
    assert result.coefficients == pytest.approx([0.8, 0.6])


def test_complex_phase_does_not_change_entanglement():
    result = schmidt_decomposition(np.array([1, 0, 0, 1j]), 2, 2)
    assert result.rank == 2
    assert result.entropy == pytest.approx(1.0)


def test_decomposition_reconstructs_the_state():
    rng = np.random.default_rng(seed=0)
    state = rng.normal(size=12) + 1j * rng.normal(size=12)
    result = schmidt_decomposition(state, 3, 4)

    rebuilt = sum(t.coefficient * np.kron(t.vector_a, t.vector_b) for t in result.terms)
    assert np.allclose(rebuilt, result.state)


def test_maximally_entangled_qutrits():
    state = np.eye(3).flatten()
    result = schmidt_decomposition(state, 3, 3)

    assert result.rank == 3
    assert result.entropy == pytest.approx(np.log2(3))
    assert result.entropy == pytest.approx(result.max_entropy)


def test_wrong_number_of_amplitudes_raises():
    with pytest.raises(ValueError, match="needs 4 amplitudes"):
        schmidt_decomposition(np.array([1, 0, 1]), 2, 2)


def test_zero_vector_raises():
    with pytest.raises(ValueError, match="all zeros"):
        schmidt_decomposition(np.zeros(4), 2, 2)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("1, 0, 0, 1", [1, 0, 0, 1]),
        ("[0.6 0 0 0.8]", [0.6, 0, 0, 0.8]),
        ("1, 0, 0, i", [1, 0, 0, 1j]),
        ("0.5+0.5j, 0, 0, 0.5", [0.5 + 0.5j, 0, 0, 0.5]),
    ],
)
def test_parse_state(text, expected):
    assert np.allclose(parse_state(text), expected)


def test_parse_state_rejects_garbage():
    with pytest.raises(ValueError, match="Could not read"):
        parse_state("one, two")


def test_format_vector():
    assert format_vector(np.array([1 / SQRT2, 1j / SQRT2])) == "(0.707, 0.707i)"


def test_format_vector_has_no_negative_zero():
    assert format_vector(np.array([-0.0, -1.0, -1e-9])) == "(0, -1, 0)"
