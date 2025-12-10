Projet PAYsible

Ceci est le backend de l'application PAYsible, construit avec FastAPI, une API web rapide et moderne pour Python.

Le projet utilise une architecture modulaire pour séparer les pages Web (/web) des services d'API (/api).

Prérequis

Vous devez avoir Python 3.10 ou supérieur installé sur votre système.

🚀 Guide de Démarrage Rapide

Suivez ces étapes pour mettre en place et lancer l'application localement.

1. Cloner le dépôt et navigation

```bash
git clone [https://github.com/b3rnvrd/PAYsible](https://github.com/b3rnvrd/PAYsible)

cd PAYsible
```

2. Création et activation de l'environnement virtuel

Il est crucial d'utiliser un environnement virtuel pour isoler les dépendances du projet.

# Créer l'environnement virtuel
```bash
python3 -m venv .venv
```
# Activer l'environnement virtuel
# Sur Linux/macOS
```bash
source .venv/bin/activate
```
# Sur Windows (PowerShell)
```powershell
.venv\Scripts\Activate.ps1
```

3. Installation des dépendances

Installez toutes les bibliothèques nécessaires listées dans requirements.txt :
```bash
pip install -r requirements.txt
```

4. Initialisation de la Base de Données (Seed)

Pour tester l'application avec des données réalistes (utilisateurs, comptes, historique de transactions), vous devez exécuter le script de "seed".

> **⚠️ Attention** : Ce script réinitialise complètement la base de données locale (suppression et recréation des tables).

Assurez-vous que votre environnement virtuel est activé, puis lancez :

```bash
python seed.py
```

Vous pourrez vous connecter à l'application avec les comptes suivants :

| Utilisateur | Email de connexion | Description |
| :--- | :--- | :--- |
| **Elon Musk** | `client@paysible.com` | **Compte Principal** (Nombreuses transactions & comptes) |
| **Jeff Bezos** | `jeff@amazon.com` | Utilisateur secondaire |
| **Bernard Arnault** | `bernard@lvmh.com` | Utilisateur secondaire |

5. Lancement du serveur de développement

Lancez l'application en utilisant Uvicorn avec le mode rechargement (--reload) pour que les changements de code soient pris en compte automatiquement.

Assurez-vous d'être dans le dossier racine PAYsible et exécutez la commande :
```bash
uvicorn app.main:app --reload
```

Le serveur devrait démarrer et être accessible à l'adresse suivante :

http://127.0.0.1:8000

Endpoints Utiles

Documentation interactive (Swagger UI) : http://127.0.0.1:8000/docs

Accueil Web : http://127.0.0.1:8000/

Vérification de l'état : http://127.0.0.1:8000/status