from django.shortcuts import render, redirect
from .forms import EmailLoginForm
from .models import BankUser


def login_view(request):
    """
    Page de login à la racine :
    - Affiche un formulaire avec champ email
    - Vérifie si cet email existe dans BankUser
    - Si oui : stocke l'utilisateur en session
    - Si non : affiche un message d'erreur
    """
    message = None

    if request.method == "POST":
        form = EmailLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].strip()

            user_qs = BankUser.objects.filter(email=email)

            if user_qs.exists():
                user = user_qs.first()

                # On mémorise l'utilisateur dans la session
                request.session["bankuser_id"] = user.id
                request.session["bankuser_name"] = user.name
                request.session["bankuser_last_name"] = user.last_name
                request.session["bankuser_email"] = user.email

                # 🔁 À ADAPTER : nom de la page vers laquelle vous voulez rediriger après login
                # Demande à ton groupe quel url-name sera utilisé pour la page d'accueil
                return redirect("home")
            else:
                message = "Cet e-mail n'existe pas dans notre base."
    else:
        form = EmailLoginForm()

    context = {
        "form": form,
        "message": message,
    }
    return render(request, "login.html", context)