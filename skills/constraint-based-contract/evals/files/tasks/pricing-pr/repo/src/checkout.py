"""注文確定処理。"""
from src.invoice import format_total
from src.pricing import calc_total


def checkout(cart, user, coupon=None):
    total = calc_total(
        cart["items"],
        rank=user.get("rank"),
        coupon_rate=coupon["rate"] if coupon else 0.0,
    )
    return {"total": total, "display": format_total(total)}
