from django import forms

class EmailLoginForm(forms.Form):
    email = forms.EmailField(
        label="Adresse e-mail",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "exemple@domaine.com"
        })
    )

