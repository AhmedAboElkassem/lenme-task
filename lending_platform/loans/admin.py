from django.contrib import admin
from .models import Loan, Offer, Payment, Profile
# Register your models here.
admin.site.register(Loan)
admin.site.register(Offer)
admin.site.register(Payment)
admin.site.register(Profile)
