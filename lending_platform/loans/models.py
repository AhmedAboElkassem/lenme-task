from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

class Loan(models.Model):
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    period = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15.0)
    status = models.CharField(max_length=20, default='Pending')
    funded_date = models.DateField(null=True, blank=True)

class Offer(models.Model):
    lender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers')
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='offers')
    lenme_fee = models.DecimalField(max_digits=10, decimal_places=2)
    accepted = models.BooleanField(default=False)

class Payment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)