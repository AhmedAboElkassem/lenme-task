# Lending Platform

## Configuration

1. Clone the repository.
2. Create a virtual environment and activate it.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Endpoints

### Authentication

- **Register**: `POST /api/auth/register/`
- **Login**: `POST /api/auth/login/`

### Loans

- **Create Loan**: `POST /api/loans/`
- **List Loans**: `GET /api/loans/`
- **Loan Detail**: `GET /api/loans/<id>/`
- **Update Loan**: `PUT /api/loans/<id>/`
- **Delete Loan**: `DELETE /api/loans/<id>/`

### Offers

- **Create Offer**: `POST /api/offers/`
- **List Offers**: `GET /api/offers/`
- **Accept Offer**: `POST /api/offers/<id>/accept/`

### Payments

- **Make Payment**: `POST /api/payments/<id>/`

## Models

- **User**: Standard Django user model.
- **Profile**: Extends the user model with a balance.
- **Loan**: Represents a loan with an amount, period, interest rate, status, and funded date.
- **Offer**: Represents an offer with a lender, loan, lenme fee, and accepted status.
- **Payment**: Represents a payment with a loan, amount, and date.

## Unit Testing

Run unit tests with:

```bash
python manage.py test
```
