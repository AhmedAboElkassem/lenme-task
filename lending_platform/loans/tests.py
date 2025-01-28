from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient # type: ignore
from .models import Loan, Offer, Payment, Profile

class LoanTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.borrower = User.objects.create_user(username='borrower', password='password')
        self.lender = User.objects.create_user(username='lender', password='password')
        
       
        if not Profile.objects.filter(user=self.borrower).exists():
            Profile.objects.create(user=self.borrower, balance=0.0)
        
        if not Profile.objects.filter(user=self.lender).exists():
            Profile.objects.create(user=self.lender, balance=10000.0)
        
        self.client.force_authenticate(user=self.borrower)
        self.loan = Loan.objects.create(borrower=self.borrower, amount=5000, period=6, status='Funded')

    def test_create_loan(self):
        self.client.force_authenticate(user=self.borrower)
        response = self.client.post('/api/loans/', {'borrower': self.borrower.id, 'amount': 5000, 'period': 6})
        self.assertEqual(response.status_code, 201)

    def test_create_offer(self):
        self.client.force_authenticate(user=self.lender)
        response = self.client.post('/api/offers/', {'lender': self.lender.id, 'loan': self.loan.id, 'lenme_fee': 3.75})
        self.assertEqual(response.status_code, 201)

    def test_accept_offer(self):
        self.client.force_authenticate(user=self.lender)
        offer = Offer.objects.create(lender=self.lender, loan=self.loan, lenme_fee=3.75)
        self.client.force_authenticate(user=self.borrower)
        response = self.client.post(f'/api/offers/{offer.id}/accept/')
        self.assertEqual(response.status_code, 200)
        offer.refresh_from_db()
        self.assertTrue(offer.accepted)

    def test_make_payment(self):
        self.client.force_authenticate(user=self.borrower)
        loan = Loan.objects.create(borrower=self.borrower, amount=5000, period=6, status='Funded')

       
        monthly_interest_rate = loan.interest_rate / 100 / 12
        monthly_payment_amount = (loan.amount * monthly_interest_rate) / (1 - (1 + monthly_interest_rate) ** -loan.period)

        payment_amount = round(monthly_payment_amount, 2)

        response = self.client.post(f'/api/payments/{loan.id}/', {'amount': payment_amount})
        
        
        print(f"Expected payment amount: {payment_amount}")
        print(f"Sent payment amount: {response.data}")

        self.assertEqual(response.status_code, 200)
        loan.refresh_from_db()
        self.assertEqual(loan.status, 'Funded' if loan.payments.count() < 6 else 'Completed')