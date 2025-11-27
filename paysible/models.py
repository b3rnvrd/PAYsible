from django.db import models

class BankUser(models.Model):
    # Correspond à CREATE TABLE user_
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.BigIntegerField()
    adresse = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    creation_date = models.DateField()

    def __str__(self):
        return f"{self.name} {self.last_name}"

    class Meta:
        db_table = 'user_'

class Transaction(models.Model):
    # Correspond à CREATE TABLE Transaction
    id_transaction = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=50)
    amount = models.BigIntegerField()
    
    # CORRECTION ICI : Le champ Python s'appelle 'date', mais la colonne SQL reste 'date_'
    date = models.DateField(db_column='date_') 
    
    description = models.CharField(max_length=500, db_column='Description')

    def __str__(self):
        return f"Transac {self.id_transaction} - {self.type}"

    class Meta:
        db_table = 'Transaction'

class Account(models.Model):
    # Correspond à CREATE TABLE account
    id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=50)
    user = models.ForeignKey(BankUser, on_delete=models.CASCADE, db_column='id_1')

    def __str__(self):
        return f"Compte {self.id} ({self.type})"

    class Meta:
        db_table = 'account'

class TransactionEntry(models.Model):
    # Correspond à CREATE TABLE transaction_entries
    id = models.IntegerField(primary_key=True)
    amount = models.IntegerField()
    account_id_val = models.IntegerField(db_column='account_id')
    type = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, db_column='id_transaction')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, db_column='id_1')

    class Meta:
        db_table = 'transaction_entries'