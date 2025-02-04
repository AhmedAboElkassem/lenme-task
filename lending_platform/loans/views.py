from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from .models import Loan, Offer, Payment, Profile
from .serializers import RegisterSerializer, LoanSerializer, OfferSerializer, PaymentSerializer
from datetime import datetime
from django.contrib.auth.models import User

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
# @permission_classes([AllowAny])
def loan_list_create(request):
    if request.method == 'POST':
        serializer = LoanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(borrower=request.user)
            # Invalidate the cache when a new loan is created
            cache.delete('loan_list')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        return cached_loan_list_create(request)

@cache_page(60 * 1, key_prefix='loan_list')
@permission_classes([IsAuthenticated])
# @permission_classes([AllowAny])
def cached_loan_list_create(request):
    loans = Loan.objects.all()
    serializer = LoanSerializer(loans, many=True)
    print("Data from database")
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@cache_page(60 * 1)
@permission_classes([AllowAny])
def cached_loan_list(request):
    loans = Loan.objects.all()
    serializer = LoanSerializer(loans, many=True)
    return Response(serializer.data)



@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def loan_detail(request, pk):
    try:
        loan = Loan.objects.get(pk=pk)
    except Loan.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = LoanSerializer(loan)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = LoanSerializer(loan, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        loan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def offer_list_create(request):
    if request.method == 'POST':
        serializer = OfferSerializer(data=request.data)
        if serializer.is_valid():
            loan = serializer.validated_data['loan']
            total_loan_amount = loan.amount + serializer.validated_data['lenme_fee']
            lender_profile = Profile.objects.get(user=request.user)

            if lender_profile.balance >= total_loan_amount:
                lender_profile.balance -= total_loan_amount
                lender_profile.save()
                offer = serializer.save(lender=request.user)
                loan.status = 'Funded'
                loan.funded_date = datetime.now().date()
                loan.save()
                return Response(OfferSerializer(offer).data, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET': 
        offers = Offer.objects.all()
        serializer = OfferSerializer(offers, many=True)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_offer(request, pk):
    try:
        offer = Offer.objects.get(pk=pk, loan__borrower=request.user)
    except Offer.DoesNotExist:
        return Response({'error': 'Offer not found or you are not authorized to accept this offer'}, status=status.HTTP_404_NOT_FOUND)
    
    offer.accepted = True
    offer.save()
    return Response({'status': 'Offer accepted'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_payment(request, pk):
    try:
        loan = Loan.objects.get(pk=pk, borrower=request.user)
    except Loan.DoesNotExist:
        return Response({'error': 'Loan not found or you are not authorized to make payments for this loan'}, status=status.HTTP_404_NOT_FOUND)
    
    if loan.status != 'Funded':
        return Response({'error': 'Loan not funded'}, status=status.HTTP_400_BAD_REQUEST)

    monthly_interest_rate = loan.interest_rate / 100 / 12
    monthly_payment_amount = (loan.amount * monthly_interest_rate) / (1 - (1 + monthly_interest_rate) ** -loan.period)
    payment_amount = float(request.data['amount'])

    if abs(payment_amount - float(round(monthly_payment_amount, 2))) > 0.01:
        return Response({'error': f'Incorrect payment amount. Expected {round(monthly_payment_amount, 2)}'}, status=status.HTTP_400_BAD_REQUEST)

    new_payment = Payment.objects.create(
        loan=loan,
        amount=payment_amount
    )

    total_paid = sum(float(payment.amount) for payment in loan.payments.all()) + new_payment.amount

    if total_paid >= loan.amount + (loan.amount * (loan.interest_rate / 100)):
        loan.status = 'Completed'
        loan.save()

    return Response({'message': 'Payment successful'})