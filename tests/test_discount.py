"""Business rules, input validation and money precision regression tests."""

from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP, localcontext
from fractions import Fraction
import random
import unittest

from src.discount import calculate_cart_total


class DiscountTests(unittest.TestCase):
    def test_business_rules(self):
        cases = [
            (0, 0, [], "0.00"),
            (10000, 0, [], "10000.00"),
            (15000, 0, [], "15000.00"),
            (Decimal("15000.01"), 0, [], "12750.01"),
            (20000, 0, [], "17000.00"),
            (10000, 0, ["SUMMER"], "9500.00"),
            (10000, 0, ["VIP"], "9000.00"),
            (10000, 1, [], "9700.00"),
            (10000, 2, [], "9300.00"),
            (20000, 2, ["SUMMER", "VIP"], "14000.00"),
            (100, 2, ["SUMMER"], "70.00"),
            (10000, 0, ["SUMMER", "VIP"], "8550.00"),
            (10000, 0, ["VIP", "SUMMER"], "8500.00"),
            (10000, 0, ["SUMMER", "SUMMER"], "9000.00"),
            (10000, 0, ["VIP"] * 20, "7000.00"),
            (10000, 0, ["UNKNOWN", "vip"], "10000.00"),
            (10000, 0, ("VIP",), "9000.00"),
            (0.1, 0, [], "0.10"),
            (Decimal("1.005"), 0, [], "1.01"),
            (Decimal("999999999999.99"), 0, [], "849999999999.99"),
        ]
        for amount, tier, promos, expected in cases:
            with self.subTest(amount=amount, tier=tier, promos=promos):
                actual = calculate_cart_total(amount, tier, promos)
                self.assertIsInstance(actual, Decimal)
                self.assertEqual(actual, Decimal(expected))
                self.assertEqual(actual.as_tuple().exponent, -2)

    def test_invalid_amount_types(self):
        for amount in [True, None, "100", [], 1 + 2j]:
            with self.subTest(amount=amount):
                with self.assertRaises(TypeError):
                    calculate_cart_total(amount, 0, [])

    def test_invalid_amount_values(self):
        for amount in [-1, float("nan"), float("inf"),
                       Decimal("-Infinity"), Decimal("sNaN"),
                       Decimal("1000000000000")]:
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    calculate_cart_total(amount, 0, [])

    def test_invalid_tiers(self):
        for tier in [True, 1.0, "1", None]:
            with self.subTest(tier=tier):
                with self.assertRaises(TypeError):
                    calculate_cart_total(100, tier, [])
        for tier in [-1, 3]:
            with self.subTest(tier=tier):
                with self.assertRaises(ValueError):
                    calculate_cart_total(100, tier, [])

    def test_invalid_promos(self):
        for promos in [None, "VIP", {"VIP"}, 1, [None], ["VIP", 1]]:
            with self.subTest(promos=promos):
                with self.assertRaises(TypeError):
                    calculate_cart_total(100, 0, promos)

    def test_caller_decimal_precision_does_not_change_result(self):
        with localcontext() as context:
            context.prec = 3
            context.rounding = ROUND_DOWN
            self.assertEqual(
                calculate_cart_total(Decimal("15000.01"), 0, []),
                Decimal("12750.01"),
            )
            self.assertEqual(context.prec, 3)

    def test_total_stays_within_rounded_discount_bounds(self):
        for amount in [Decimal("0.01"), Decimal("1.005"),
                       Decimal("14999.99"), Decimal("15000.01"),
                       Decimal("20000")]:
            for tier in [0, 1, 2]:
                for promos in [[], ["VIP"], ["SUMMER"] * 20,
                               ["SUMMER", "VIP"] * 10]:
                    with self.subTest(a=amount, t=tier, p=promos):
                        result = calculate_cart_total(amount, tier, promos)
                        lower = (amount * Decimal("0.70")).quantize(
                            Decimal("0.01"), rounding=ROUND_HALF_UP
                        )
                        upper = amount.quantize(
                            Decimal("0.01"), rounding=ROUND_HALF_UP
                        )
                        self.assertGreaterEqual(result, lower)
                        self.assertLessEqual(result, upper)

    def test_caller_decimal_traps_do_not_change_result(self):
        with localcontext() as context:
            for signal in context.traps:
                context.traps[signal] = True
            before_traps = dict(context.traps)
            before_flags = dict(context.flags)
            self.assertEqual(
                calculate_cart_total(Decimal("15000.01"), 0, []),
                Decimal("12750.01"),
            )
            self.assertEqual(dict(context.traps), before_traps)
            self.assertEqual(dict(context.flags), before_flags)

    def test_caller_exponent_limits_do_not_change_result(self):
        with localcontext() as context:
            context.prec = 3
            context.Emax = 2
            context.Emin = -2
            self.assertEqual(
                calculate_cart_total(Decimal("999999999999.99"), 0, []),
                Decimal("849999999999.99"),
            )
            self.assertEqual((context.prec, context.Emax, context.Emin),
                             (3, 2, -2))

    def test_1000_scenarios_against_exact_fraction_oracle(self):
        rng = random.Random(20261017)
        codes = ["SUMMER", "VIP", "UNKNOWN"]
        for case in range(1000):
            amount = Decimal(rng.randrange(100000001)).scaleb(-3)
            tier = rng.randrange(3)
            promos = [rng.choice(codes) for _ in range(rng.randrange(13))]
            original = Fraction(amount)
            price = original
            if original > 15000:
                price *= Fraction(85, 100)
            for promo in promos:
                if promo == "SUMMER":
                    price -= 500
                elif promo == "VIP":
                    price *= Fraction(90, 100)
            price *= [Fraction(1), Fraction(97, 100),
                      Fraction(93, 100)][tier]
            price = max(price, original * Fraction(70, 100))
            scaled = price * 100
            # Exact ROUND_HALF_UP for nonnegative rational values.
            cents = (2 * scaled.numerator + scaled.denominator) // (
                2 * scaled.denominator
            )
            expected = Decimal(cents).scaleb(-2)
            with self.subTest(case=case, amount=amount,
                              tier=tier, promos=promos):
                self.assertEqual(
                    calculate_cart_total(amount, tier, promos), expected
                )

    def test_input_promo_list_is_not_mutated(self):
        promos = ["SUMMER", "VIP", "UNKNOWN", "SUMMER"]
        before = promos.copy()
        first = calculate_cart_total(10000, 1, promos)
        self.assertEqual(promos, before)
        self.assertEqual(calculate_cart_total(10000, 1, promos), first)

    def test_validation_failure_preserves_caller_context(self):
        with localcontext() as context:
            context.prec = 3
            before_flags = dict(context.flags)
            before_traps = dict(context.traps)
            with self.assertRaises(ValueError):
                calculate_cart_total(-1, 0, [])
            self.assertEqual(context.prec, 3)
            self.assertEqual(dict(context.flags), before_flags)
            self.assertEqual(dict(context.traps), before_traps)


if __name__ == "__main__":
    unittest.main()
