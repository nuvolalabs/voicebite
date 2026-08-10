"""Stripe Payment Links + SMS. Both degrade gracefully when unconfigured
so the app runs end-to-end in demo mode (prints links instead of sending)."""
from __future__ import annotations
from app import config


def create_payment_link(amount: float, order_id: str, customer_name: str) -> str:
    """Create a Stripe Payment Link and return its hosted URL.

    amount is in the major currency unit (e.g. dollars), Stripe wants cents.
    order_id is stored in metadata so the webhook can mark the order paid.
    """
    if not config.is_configured():
        # Demo mode: fake but realistic-looking link
        return f"https://pay.demo.example/plink/{order_id}?amt={amount}"

    import stripe
    stripe.api_key = config.STRIPE_SECRET_KEY

    product = stripe.Product.create(
        name=f"Takeout order for {customer_name}",
        description=f"Order {order_id}",
    )
    price = stripe.Price.create(
        product=product.id,
        unit_amount=int(round(amount * 100)),
        currency="usd",
    )
    link = stripe.PaymentLink.create(
        line_items=[{"price": price.id, "quantity": 1}],
        metadata={"order_id": order_id or ""},
        after_completion={
            "type": "redirect",
            "redirect": {"url": config.STRIPE_SUCCESS_URL},
        },
    )
    return link.url


def send_sms(phone: str, body: str) -> bool:
    """Send an SMS via Twilio. Returns True if sent, False if demo-mode/failed."""
    if not config.is_configured():
        print(f"[DEMO SMS -> {phone}] {body}")
        return False
    try:
        from twilio.rest import Client
        client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
        client.messages.create(body=body, from_=config.TWILIO_FROM_NUMBER, to=phone)
        return True
    except Exception as e:  # noqa: BLE001
        print(f"[SMS ERROR -> {phone}] {e}")
        return False
