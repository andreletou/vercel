from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User

INPUT = (
    "w-full rounded-xl border border-[#20221e]/12 bg-white px-4 py-3.5 text-sm "
    "outline-none focus:border-[#c77746]"
)


class StyledMixin:
    placeholders = {}

    def _style(self):
        for name, field in self.fields.items():
            field.widget.attrs["class"] = INPUT
            if name in self.placeholders:
                field.widget.attrs["placeholder"] = self.placeholders[name]
            field.help_text = ""


class LoginForm(StyledMixin, AuthenticationForm):
    placeholders = {"username": "Nom d’utilisateur", "password": "Mot de passe"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()
        self.fields["username"].label = ""
        self.fields["password"].label = ""
        self.fields["username"].widget.attrs["autocomplete"] = "username"
        self.fields["password"].widget.attrs["autocomplete"] = "current-password"


class RegisterForm(StyledMixin, UserCreationForm):
    phone = forms.CharField(max_length=20, label="", required=True)
    placeholders = {
        "username": "Votre nom",
        "phone": "Numéro de téléphone",
        "password1": "Mot de passe",
        "password2": "Confirmer le mot de passe",
    }

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "phone")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()
        for f in self.fields.values():
            f.label = ""
        self.fields["phone"].widget.attrs["autocomplete"] = "tel"
        self.fields["phone"].widget.input_type = "tel"


class JoinForm(forms.Form):
    quantity = forms.IntegerField(label="Quantité", min_value=1, initial=1)

    def __init__(self, *args, product=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product
        attrs = {"class": INPUT, "min": 1}
        if product is not None:
            attrs["max"] = product.stock
        self.fields["quantity"].widget.attrs.update(attrs)

    def clean_quantity(self):
        qty = self.cleaned_data["quantity"]
        if self.product and qty > self.product.stock:
            raise forms.ValidationError(f"Il ne reste que {self.product.stock} place(s) pour cette offre.")
        return qty
