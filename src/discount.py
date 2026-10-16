"""Cart discounts with decimal arithmetic and explicit input validation."""

from decimal import Context, Decimal, ROUND_HALF_UP, localcontext


BASE_DISCOUNT_THRESHOLD = Decimal("15000")
BASE_PRICE_FACTOR = Decimal("0.85")
SUMMER_DISCOUNT = Decimal("500")
VIP_PRICE_FACTOR = Decimal("0.90")
TIER_PRICE_FACTORS = {
    0: Decimal("1"),
    1: Decimal("0.97"),
    2: Decimal("0.93"),
}
MINIMUM_PRICE_FACTOR = Decimal("0.70")
MONEY_QUANTUM = Decimal("0.01")
MAX_CART_SUM = Decimal("999999999999.99")
CALCULATION_PRECISION = 40


def calculate_cart_total(
    cart_sum: int | float | Decimal,
    tier: int,
    promos: list[str] | tuple[str, ...],
) -> Decimal:
    """Return a Decimal rounded to cents, preserving legacy discount order.

    Accept a finite nonnegative int, float or Decimal up to MAX_CART_SUM,
    tier 0/1/2, and a list/tuple of promo strings. Unknown codes do nothing.
    Repeated codes apply repeatedly as in the legacy function; the final
    discount is capped at 30%. Promo eligibility belongs to the calling service.
    """
    if isinstance(cart_sum, bool) or not isinstance(
        cart_sum, (int, float, Decimal)
    ):
        raise TypeError("cart_sum must be int, float or Decimal")
    amount = Decimal(str(cart_sum))
    if not amount.is_finite() or not Decimal("0") <= amount <= MAX_CART_SUM:
        raise ValueError("cart_sum must be finite and within allowed limits")
    if isinstance(tier, bool) or not isinstance(tier, int):
        raise TypeError("tier must be an integer")
    if tier not in TIER_PRICE_FACTORS:
        raise ValueError("tier must be 0, 1 or 2")
    if not isinstance(promos, (list, tuple)):
        raise TypeError("promos must be a list or tuple of strings")
    if any(not isinstance(promo, str) for promo in promos):
        raise TypeError("each promo must be a string")

    # A fresh context also isolates traps and exponent limits, not just prec.
    with localcontext(Context(
        prec=CALCULATION_PRECISION, rounding=ROUND_HALF_UP
    )):
        price = amount
        if amount > BASE_DISCOUNT_THRESHOLD:
            price *= BASE_PRICE_FACTOR
        for promo in promos:
            if promo == "SUMMER":
                price -= SUMMER_DISCOUNT
            elif promo == "VIP":
                price *= VIP_PRICE_FACTOR
        price *= TIER_PRICE_FACTORS[tier]
        price = max(price, amount * MINIMUM_PRICE_FACTOR)
        return price.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)
