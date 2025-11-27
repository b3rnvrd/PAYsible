from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum

class User(AbstractUser):
    # 'name', 'last_name', 'email', 'date_joined' sont déjà inclus dans AbstractUser
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Account(models.Model):
    TYPE_CHOICES = [
        ('CURRENT', 'Compte Courant'),
        ('SAVINGS', 'Épargne'),
    ]

    # Relation : one to many avec User
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='CURRENT')
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()} - {self.user.username}"

    @property
    def balance(self):
        """
        Calcule le solde en sommant toutes les entrées liées à ce compte.
        """
        # On somme le champ 'amount' de toutes les transaction_entries liées
        total = self.entries.aggregate(Sum('amount'))['amount__sum']
        return total or 0  # Retourne 0 si aucune transaction

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('TRANSFER', 'Virement'),
        ('PAYMENT', 'Paiement'),
        ('DEPOSIT', 'Dépôt'),
    ]

    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"Transaction {self.id} - {self.date}"

class TransactionEntry(models.Model):
    ENTRY_TYPES = [
        ('DEBIT', 'Débit'),
        ('CREDIT', 'Crédit'),
    ]
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='entries')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='entries')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=10, choices=ENTRY_TYPES)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.type} : {self.amount}€ sur {self.account}"