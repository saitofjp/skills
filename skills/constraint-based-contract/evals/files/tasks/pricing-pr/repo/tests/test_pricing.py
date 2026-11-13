import unittest

from src.pricing import calc_total, discount_rate, subtotal


class TestPricing(unittest.TestCase):
    def test_subtotal(self):
        items = [{"price": 1200, "qty": 2}, {"price": 300, "qty": 1}]
        self.assertEqual(subtotal(items), 2700)

    def test_qty_must_be_positive(self):
        with self.assertRaises(ValueError):
            subtotal([{"price": 100, "qty": 0}])

    def test_silver_with_coupon_is_capped(self):
        self.assertEqual(discount_rate("silver", [0.15, 0.10]), 0.20)

    def test_total_with_discount(self):
        items = [{"price": 1000, "qty": 10}]
        self.assertEqual(calc_total(items, rank="silver", coupons=[0.15]), 8000)

    def test_shipping_fee_below_threshold(self):
        items = [{"price": 1000, "qty": 3}]
        self.assertEqual(calc_total(items), 3500)


if __name__ == "__main__":
    unittest.main()
