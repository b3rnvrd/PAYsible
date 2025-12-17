from app.core.database import SessionLocal, engine, Base
from app.models.user import UserDB
from app.models.account import AccountDB
from app.models.transaction import TransactionDB, TransactionEntryDB
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
# Comptes pour Elon
acc_courant = AccountDB(
    type="Courant", 
    iban="FR7630003000300030003000301",
    user_id=created_users[0].id
)
acc_epargne = AccountDB(
    type="Epargne", 
    iban="FR7630003000300030003000302",
    user_id=created_users[0].id
)
acc_pro = AccountDB(
    type="Professionnel", 
    iban="FR7630003000300030003000303",
    user_id=created_users[0].id
)

# Compte pour Jeff
acc_jeff = AccountDB(
    type="Courant", 
    iban="FR7699999999999999999999999",
    user_id=created_users[1].id
)

# Compte pour Bernard
acc_bernard = AccountDB(
    type="Courant", 
    iban="FR7677777777777777777777777",
    user_id=created_users[2].id
)

db.add_all([acc_courant, acc_epargne, acc_pro, acc_jeff, acc_bernard])
db.commit()
print("✅ 5 Comptes bancaires créés")

# --- 3B. SOLDE DE DÉPART SÉCURISÉ ---
# Augmenté à 20 000€ pour garantir un solde positif malgré les dépenses
INITIAL_BALANCE = 20000.00
date_init = datetime.now() - timedelta(days=181)

comptes_a_crediter = [acc_courant, acc_jeff, acc_bernard]

for compte in comptes_a_crediter:
    txn_init = TransactionDB(
        type="Dépôt Initial", amount=INITIAL_BALANCE, 
        description="Dépôt de Solde Initial", date=date_init
    )
    db.add(txn_init)
    db.commit()
    db.refresh(txn_init)

    entry_init = TransactionEntryDB(
        amount=INITIAL_BALANCE, type="CREDIT", 
        description="Solde de départ",
        account_id=compte.id,
        transaction_id=txn_init.id
    )
    db.add(entry_init)

db.commit()
print(f"💰 Solde initial de +{INITIAL_BALANCE:.2f}€ ajouté aux comptes principaux.")


# --- 4. GÉNÉRATION MASSIVE DE TRANSACTIONS (Uniquement pour Elon) ---
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

for _ in range(40):
    # Ajusté à 0.3 (70% de dépenses) pour être un peu plus raisonnable
    is_expense = random.random() > 0.3
    
    if is_expense:
        desc, min_amt, max_amt = random.choice(descriptions_depenses)
        type_t = "Paiement"
    else:
        desc, min_amt, max_amt = random.choice(descriptions_revenus)
        type_t = "Virement"

    amount = round(random.uniform(min_amt, max_amt), 2)
    date_t = random_date()

    txn = TransactionDB(type=type_t, amount=abs(amount), description=desc, date=date_t)
    db.add(txn)
    db.commit()
    db.refresh(txn)

    entry = TransactionEntryDB(
        amount=amount,
        type="DEBIT" if amount < 0 else "CREDIT",
        description=desc,
        account_id=acc_courant.id,
        transaction_id=txn.id
    )
    db.add(entry)

# Virements épargne Elon (6 mois x 500€ = -3000€)
for i in range(6):
    date_t = datetime.now() - timedelta(days=i*30)
    txn_vir = TransactionDB(type="Virement Interne", amount=500.0, description="Epargne Mensuelle", date=date_t)
    db.add(txn_vir)
    db.commit()
    db.refresh(txn_vir)

    db.add(TransactionEntryDB(
        amount=-500.0, type="DEBIT", description="Vers Livret A",
        account_id=acc_courant.id, transaction_id=txn_vir.id
    ))
    db.add(TransactionEntryDB(
        amount=500.0, type="CREDIT", description="Depuis Compte Courant",
        account_id=acc_epargne.id, transaction_id=txn_vir.id
    ))

db.commit()
print("✅ Transactions de démo générées")

# --- 5. AJOUT DE BÉNÉFICIAIRES MANUELS ---
benefs_manual = [
    BeneficiaryDB(name="Maman Maye", iban="FR7600010001000100010001001", account_id=acc_courant.id),
    BeneficiaryDB(name="Propriétaire", iban="FR7600020002000200020002002", account_id=acc_courant.id),
    BeneficiaryDB(name="Frère Kimbal", iban="FR7600030003000300030003003", account_id=acc_courant.id),
]
db.add_all(benefs_manual)
db.commit()

# --- 6. AJOUT AUTOMATIQUE DE BÉNÉFICIAIRES CROISÉS ---
print("🔄 Génération des bénéficiaires croisés...")

all_users = db.query(UserDB).all()

for user in all_users:
    if not user.accounts:
        continue
        
    mon_compte_principal = user.accounts[0]
    
    for other_user in all_users:
        if user.id == other_user.id:
            continue
            
        if other_user.accounts:
            other_account = other_user.accounts[0]
            benef = BeneficiaryDB(
                name=f"{other_user.name} {other_user.last_name}",
                iban=other_account.iban,
                account_id=mon_compte_principal.id
            )
            db.add(benef)

db.commit()
print("✅ Bénéficiaires croisés ajoutés pour tous les clients")

db.close()
print("\n🚀 TOUT EST PRÊT ! Lancez le serveur et connectez-vous avec :")
print(f"👉 {users_data[0]['email']} (Elon)")
print(f"👉 {users_data[1]['email']} (Jeff)")
print(f"👉 {users_data[2]['email']} (Bernard)")