import stripe
from django.conf import settings
from django.db import transaction

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(name, description):
    """
    Создание продукта в Stripe
    """
    try:
        product = stripe.Product.create(
            name=name,
            description=description,
        )
        return product
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка создания продукта в Stripe: {str(e)}")


def create_stripe_price(amount, product_id):
    """
    Создание цены в Stripe
    """
    try:
        price = stripe.Price.create(
            unit_amount=int(amount * 100),
            currency="rub",
            product=product_id,
        )
        return price
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка создания цены в Stripe: {str(e)}")


def create_stripe_session(price_id):
    """
    Создание сессии оплаты в Stripe
    """
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="http://127.0.0.1:8000/",
        )
        return session
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка создания сессии оплаты: {str(e)}")
