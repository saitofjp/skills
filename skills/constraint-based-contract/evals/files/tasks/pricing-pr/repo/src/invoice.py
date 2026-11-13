"""請求書・画面表示用の金額整形。"""


def format_total(total):
    # 金額は整数（円）で受け取る前提
    return f"{total:,d}円"
