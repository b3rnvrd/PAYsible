from app.core.database import SessionLocal, engine, Base
from app.models.user import UserDB
from app.models.account import AccountDB
# IMPORTANT : On importe bien les deux classes Transaction depuis le bon fichier
from app.models.transaction import TransactionDB, TransactionEntryDB
# IMPORTANT : On importe BeneficiaryDB pour que la relation dans AccountDB ne plante pas
from app.models.beneficiary import BeneficiaryDB

from datetime import datetime, timedelta
import random

# --- FONCTION UTILITAIRE POUR LES DATES ---
def random_date(start_days_ago=180):
    """Retourne une date aléatoire dans les X derniers jours."""
    days = random.randint(0, start_days_ago)
    return datetime.now() - timedelta(days=days)

# 1. Reset complet de la base
print("💥 Suppression de l'ancienne base de données...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()
print("🌱 Initialisation de la base de données XXL...")

# --- 2. CRÉATION DES UTILISATEURS ---
users_data = [
    {
        "name": "Elon", "last_name": "Musk", "email": "client@paysible.com",
        "phone": "0600000001", "addr": "Starbase, Texas"
    },
    {
        "name": "Jeff", "last_name": "Bezos", "email": "jeff@amazon.com",
        "phone": "0600000002", "addr": "Seattle, WA"
    },
    {
        "name": "Bernard", "last_name": "Arnault", "email": "bernard@lvmh.com",
        "phone": "0600000003", "addr": "Paris, France"
    }
]

created_users = []
for u in users_data:
    user = UserDB(
        name=u["name"], last_name=u["last_name"], email=u["email"],
        phone_number=u["phone"], address=u["addr"], creation_date=datetime.now()
    )
    db.add(user)
    created_users.append(user)

db.commit()
for u in created_users: db.refresh(u)
print(f"✅ 3 Utilisateurs créés (Testez avec {created_users[0].email})")

# --- 3. CRÉATION DES COMPTES ---
# On va donner des comptes variés à Elon (notre user principal)
acc_courant = AccountDB(type="Courant", iban="FR76 1000 0000 0001", user_id=created_users[0].id)
acc_epargne = AccountDB(type="Epargne", iban="FR76 2000 0000 0002", user_id=created_users[0].id)
acc_pro = AccountDB(type="Professionnel", iban="FR76 3000 0000 0003", user_id=created_users[0].id)

# Un compte pour les autres
acc_jeff = AccountDB(type="Courant", iban="FR76 9999 9999 9999", user_id=created_users[1].id)

db.add_all([acc_courant, acc_epargne, acc_pro, acc_jeff])
db.commit()
print("✅ 4 Comptes bancaires créés")

# --- 4. GÉNÉRATION MASSIVE DE TRANSACTIONS ---
descriptions_depenses = [
    ("Supermarché", -50, -200), ("Restaurant", -15, -120),
    ("Uber", -10, -40), ("Abonnement Netflix", -17.99, -17.99),
    ("Facture EDF", -80, -150), ("Loyer", -1200, -1200),
    ("Shopping", -30, -300), ("Essence", -40, -90),
    ("Cinéma", -12, -24), ("Boulangerie", -2, -10)
]

descriptions_revenus = [
    ("Salaire SpaceX", 4500, 5000),
    ("Remboursement Sécu", 20, 100),
    ("Vente Vinted", 10, 80),
    ("Dividendes", 100, 500)
]

# On génère 40 transactions aléatoires pour le compte courant d'Elon
for _ in range(40):
    is_expense = random.random() > 0.2  # 80% de chances que ce soit une dépense
    
    if is_expense:
        desc, min_amt, max_amt = random.choice(descriptions_depenses)
        type_t = "Paiement"
    else:
        desc, min_amt, max_amt = random.choice(descriptions_revenus)
        type_t = "Virement"

    amount = round(random.uniform(min_amt, max_amt), 2)
    date_t = random_date()

    # Transaction globale
    txn = TransactionDB(type=type_t, amount=abs(amount), description=desc, date=date_t)
    db.add(txn)
    db.commit()
    db.refresh(txn)

    # Entrée sur le compte
    entry = TransactionEntryDB(
        amount=amount,
        type="DEBIT" if amount < 0 else "CREDIT",
        description=desc,
        account_id=acc_courant.id,
        transaction_id=txn.id
    )
    db.add(entry)

# Quelques transactions pour le compte Épargne (Virements mensuels)
for i in range(6):
    date_t = datetime.now() - timedelta(days=i*30)
    
    # 1. Débit du compte courant
    txn_vir = TransactionDB(type="Virement Interne", amount=500.0, description="Epargne Mensuelle", date=date_t)
    db.add(txn_vir)
    db.commit()
    db.refresh(txn_vir)

    entry_out = TransactionEntryDB(
        amount=-500.0, type="DEBIT", description="Vers Livret A",
        account_id=acc_courant.id, transaction_id=txn_vir.id
    )
    # 2. Crédit du compte épargne
    entry_in = TransactionEntryDB(
        amount=500.0, type="CREDIT", description="Depuis Compte Courant",
        account_id=acc_epargne.id, transaction_id=txn_vir.id
    )
    db.add(entry_out)
    db.add(entry_in)

print("✅ 50+ Transactions générées")

# --- 5. AJOUT DE BÉNÉFICIAIRES ---
benefs = [
    BeneficiaryDB(name="Maman Maye", iban="FR76 0001 0001", account_id=acc_courant.id),
    BeneficiaryDB(name="Propriétaire", iban="FR76 0002 0002", account_id=acc_courant.id),
    BeneficiaryDB(name="Frère Kimbal", iban="FR76 0003 0003", account_id=acc_courant.id),
]
db.add_all(benefs)
db.commit()
print("✅ Bénéficiaires ajoutés")

db.close()
print("\n🚀 TOUT EST PRÊT ! Lancez le serveur et connectez-vous avec : client@paysible.com")
