from django import forms

from .schmidt import EXAMPLE_STATES, parse_state

MAX_DIM = 8


class StateForm(forms.Form):
    """Validates user input before any maths runs."""

    amplitudes = forms.CharField(
        label="State amplitudes",
        help_text=(
            "Comma-separated, in the basis |00⟩, |01⟩, … "
            "Complex numbers allowed (e.g. 0.5+0.5i)."
        ),
        widget=forms.Textarea(attrs={"rows": 3, "spellcheck": "false"}),
    )
    dim_a = forms.IntegerField(label="Dimension of A", min_value=2, max_value=MAX_DIM, initial=2)
    dim_b = forms.IntegerField(label="Dimension of B", min_value=2, max_value=MAX_DIM, initial=2)

    def clean_amplitudes(self):
        try:
            return parse_state(self.cleaned_data["amplitudes"])
        except ValueError as error:
            raise forms.ValidationError(str(error)) from None

    def clean(self):
        cleaned = super().clean()
        state, dim_a, dim_b = (cleaned.get(k) for k in ("amplitudes", "dim_a", "dim_b"))
        if state is not None and dim_a and dim_b and state.size != dim_a * dim_b:
            raise forms.ValidationError(
                f"A {dim_a} × {dim_b} system needs {dim_a * dim_b} amplitudes, "
                f"but {state.size} were given."
            )
        if state is not None and not state.any():
            raise forms.ValidationError("The state vector cannot be all zeros.")
        return cleaned

    @classmethod
    def from_example(cls, key: str) -> "StateForm":
        _, amplitudes, dim_a, dim_b = EXAMPLE_STATES[key]
        return cls(data={"amplitudes": amplitudes, "dim_a": dim_a, "dim_b": dim_b})
