from django.shortcuts import render

from .forms import StateForm
from .schmidt import EXAMPLE_STATES, format_vector, schmidt_decomposition


def index(request):
    example = request.GET.get("example")

    if request.method == "POST":
        form = StateForm(request.POST)
    elif example in EXAMPLE_STATES:
        form = StateForm.from_example(example)
    else:
        form = StateForm()

    result = None
    if form.is_bound and form.is_valid():
        data = form.cleaned_data
        result = schmidt_decomposition(data["amplitudes"], data["dim_a"], data["dim_b"])

    context = {
        "form": form,
        "result": result,
        "terms": _terms_for_display(result) if result else [],
        "examples": {key: name for key, (name, *_) in EXAMPLE_STATES.items()},
    }
    return render(request, "calculator/index.html", context)


def _terms_for_display(result):
    largest = max(result.coefficients)
    return [
        {
            "index": k + 1,
            "coefficient": term.coefficient,
            "probability": term.coefficient**2,
            "bar_percent": 100 * term.coefficient / largest,
            "vector_a": format_vector(term.vector_a),
            "vector_b": format_vector(term.vector_b),
        }
        for k, term in enumerate(result.terms)
    ]
