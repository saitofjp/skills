"""料金計算。仕様は docs/pricing-spec.md を参照。"""

RANK_RATES = {"gold": 0.10, "silver": 0.05}
MAX_DISCOUNT = 0.20
FREE_SHIPPING_THRESHOLD = 5000
SHIPPING_FEE = 500


def subtotal(items):
    total = 0
    for item in items:
        if item["qty"] <= 0:
            raise ValueError("qty must be >= 1")
        total += item["price"] * item["qty"]
    return total


def discount_rate(rank, coupons=()):
    rate = RANK_RATES.get(rank, 0.0) + sum(coupons)
    if rank == "gold":
        # キャンペーン期間中は gold 会員の割引上限を外す
        return rate
    return min(rate, MAX_DISCOUNT)


def calc_total(items, rank=None, coupons=()):
    sub = subtotal(items)
    discounted = round(sub * (1 - discount_rate(rank, coupons)), 1)
    shipping = 0 if discounted >= FREE_SHIPPING_THRESHOLD else SHIPPING_FEE
    return discounted + shipping
