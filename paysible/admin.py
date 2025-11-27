from django.contrib import admin
from .models import BankUser, Transaction, Account, TransactionEntry

admin.site.register(BankUser)
admin.site.register(Transaction)
admin.site.register(Account)
admin.site.register(TransactionEntry)