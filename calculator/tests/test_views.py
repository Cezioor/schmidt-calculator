from django.test import Client
from django.urls import reverse

URL = reverse("calculator:index")


def test_empty_page_loads():
    response = Client().get(URL)
    assert response.status_code == 200
    assert b"Enter a state" in response.content


def test_post_bell_state_shows_entangled():
    response = Client().post(URL, {"amplitudes": "1, 0, 0, 1", "dim_a": 2, "dim_b": 2})
    assert response.status_code == 200
    assert response.context["result"].rank == 2
    assert b"Entangled" in response.content


def test_example_link_prefills_and_computes():
    response = Client().get(URL, {"example": "product_00"})
    assert response.context["result"].rank == 1


def test_unknown_example_is_ignored():
    response = Client().get(URL, {"example": "does_not_exist"})
    assert response.status_code == 200
    assert response.context["result"] is None


def test_dimension_mismatch_shows_error():
    response = Client().post(URL, {"amplitudes": "1, 0, 0", "dim_a": 2, "dim_b": 2})
    assert response.context["result"] is None
    assert b"needs 4 amplitudes" in response.content


def test_dimension_limit_is_enforced():
    response = Client().post(URL, {"amplitudes": "1", "dim_a": 100, "dim_b": 2})
    assert response.context["result"] is None
    assert not response.context["form"].is_valid()
