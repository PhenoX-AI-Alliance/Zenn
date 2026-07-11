
import stripe
import os

stripe.api_key = os.environ.get('API_STRIPE_SECRET_KEY')

def create_checkout_session(price_tier):
    prices = {
        'basic': 'price_basic_id_placeholder',
        'pro': 'price_pro_id_placeholder',
        'enterprise': 'price_enterprise_id_placeholder'
    }
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price': prices[price_tier], 'quantity': 1}],
            mode='subscription',
            success_url='https://example.com/success',
            cancel_url='https://example.com/cancel',
        )
        return session.url
    except Exception as e:
        print(f"Stripe Error: {e}")
        return None
