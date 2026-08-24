import os
import json
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

# =========================================================
# CẤU HÌNH
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "DAN_BOT_TOKEN_VAO_DAY")

CHAT_ID = os.getenv("CHAT_ID", "DAN_CHAT_ID_VAO_DAY")

API_KEY = os.getenv("VIETDATAVERSE_API_KEY", "DAN_API_KEY_VAO_DAY")

BASE_URL = "https://api.vietdataverse.online/api/v1"

# 60 phút cập nhật 1 lần
UPDATE_INTERVAL = 60 * 60

HISTORY_FILE = "market_history.json"

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


# =========================================================
# CÁC MÃ SẢN PHẨM
# =========================================================

GOLD_PRODUCTS = {
    "sjc": "SJC",
    "doji": "DOJI HN",
    "pnj": "PNJ",
    "btmc": "BTMC"
}


# =========================================================
# HÀM GỌI API
# =========================================================

def api_get(endpoint, params=None):

    headers = {
        "X-API-Key": API_KEY
    }

    url = f"{BASE_URL}/{endpoint}"

    try:

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

        result = response.json()

        if not result.get("success", True):
            print("API trả lỗi:", result)
            return None

        return result

    except Exception as e:

        print("API ERROR:", e)

        return None


# =========================================================
# LẤY GIÁ VÀNG
# =========================================================

def get_gold(product_type):

    data = api_get(
        "gold",
        {
            "type": product_type,
            "period": "7d"
        }
    )

    if not data:
        return None

    rows = data.get("data")

    if not rows:
        return None

    # API trả danh sách dữ liệu lịch sử
    if isinstance(rows, list):

        row = rows[-1]

        return {
            "buy": float(row["buy_price"]),
            "sell": float(row["sell_price"]),
            "updated": row.get("period")
        }

    # Trường hợp API trả dạng dictionary
    if isinstance(rows, dict):

        dates = rows.get("dates", [])
        buys = rows.get("buy_prices", [])
        sells = rows.get("sell_prices", [])

        if not dates:
            return None

        return {
            "buy": float(buys[-1]),
            "sell": float(sells[-1]),
            "updated": dates[-1]
        }

    return None


# =========================================================
# LẤY USD VIETCOMBANK
# =========================================================

def get_usd():

    data = api_get(
        "sbv-rate",
        {
            "bank": "VCB",
            "currency": "USD",
            "period": "7d"
        }
    )

    if not data:
        return None

    rows = data.get("data")

    if not rows:
        return None

    row = rows[-1]

    return {
        "buy": float(row.get("buy", 0)),
        "sell": float(row.get("sell", 0)),
        "updated": row.get("period")
    }


# =========================================================
# LẤY BẠC PHÚ QUÝ
# =========================================================

def get_silver():

    data = api_get(
        "silver",
        {
            "period": "7d"
        }
    )

    if not data:
        return None

    rows = data.get("data")

    if not rows:
        return None

    row = rows[-1]

    return {
        "buy": float(
            row.get("buy_price")
            or row.get("buy")
            or 0
        ),

        "sell": float(
            row.get("sell_price")
            or row.get("sell")
            or 0
        ),

        "updated": row.get("period")
    }


# =========================================================
# QUY ĐỔI
# =========================================================

def gold_to_chi(value):

    if value is None:
        return None

    # API vàng thường trả VND/lượng
    # 1 lượng = 10 chỉ

    return value / 10


def silver_to_chi(value):

    if value is None:
        return None

    # Nếu API trả VND/lượng
    return value / 10


# =========================================================
# LẤY TOÀN BỘ THỊ TRƯỜNG
# =========================================================

def get_market():

    market = {}

    # -----------------------------
    # VÀNG
    # -----------------------------

    for key, api_name in GOLD_PRODUCTS.items():

        data = get_gold(api_name)

        if data:

            market[key] = {
                "buy": gold_to_chi(data["buy"]),
                "sell": gold_to_chi(data["sell"]),
                "updated": data["updated"]
            }

        else:

            market[key] = {
                "buy": None,
                "sell": None,
                "updated": None
            }

    # -----------------------------
    # BẠC
    # -----------------------------

    silver = get_silver()

    if silver:

        market["silver"] = {
            "buy": silver_to_chi(silver["buy"]),
            "sell": silver_to_chi(silver["sell"]),
            "updated": silver["updated"]
        }

    else:

        market["silver"] = {
            "buy": None,
            "sell": None,
            "updated": None
        }

    # -----------------------------
    # USD
    # -----------------------------

    usd = get_usd()

    if usd:

        market["usd"] = usd

    else:

        market["usd"] = {
            "buy": None,
            "sell": None,
            "updated": None
        }

    return market


# =========================================================
# LỊCH SỬ
# =========================================================

def load_history():

    if not os.path.exists(HISTORY_FILE):
        return {}

    try:

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except:

        return {}


def save_history(history):

    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            history,
            f,
            ensure_ascii=False,
            indent=2
        )


# =========================================================
# LẤY GIÁ NGÀY HÔM TRƯỚC
# =========================================================

def get_previous_day(history, today):

    dates = []

    for date in history:

        if date < today:
            dates.append(date)

    if not dates:
        return None

    return max(dates)


# =========================================================
# TÍNH THAY ĐỔI
# =========================================================

def calculate_changes(current, previous):

    result = {}

    if not previous:
        return result

    for product in current:

        result[product] = {}

        current_data = current[product]
        previous_data = previous.get(product)

        if not previous_data:
            continue

        for field in ["buy", "sell"]:

            now = current_data.get(field)
            old = previous_data.get(field)

            if now is None or old is None:
                result[product][field] = None

            else:

                result[product][field] = now - old

    return result


# =========================================================
# LƯU GIÁ TRONG NGÀY
# =========================================================

def save_today_market(market):

    history = load_history()

    now = datetime.now(VN_TZ)

    today = now.strftime("%Y-%m-%d")

    previous_day = get_previous_day(
        history,
        today
    )

    previous = history.get(previous_day)

    changes = calculate_changes(
        market,
        previous
    )

    # Lưu giá hiện tại
    history[today] = market

    save_history(history)

    return previous_day, changes


# =========================================================
# FORMAT TIỀN
# =========================================================

def fmt(value):

    if value is None:
        return "---"

    return f"{round(value):,}".replace(",", ".")


def fmt_change(value):

    if value is None:
        return "—"

    value = round(value)

    if value > 0:

        return (
            f"🔺 +{value:,}"
            .replace(",", ".")
        )

    if value < 0:

        return (
            f"🔻 {value:,}"
            .replace(",", ".")
        )

    return "➡️ 0"


# =========================================================
# TẠO BẢNG TELEGRAM
# =========================================================

def make_message():

    market = get_market()

    previous_day, changes = save_today_market(
        market
    )

    now = datetime.now(VN_TZ)

    text = ""

    text += "📊 GIÁ THỊ TRƯỜNG TRONG NƯỚC\n"
    text += "━━━━━━━━━━━━━━━━━━━━\n"

    text += (
        f"📅 {now.strftime('%d/%m/%Y')}\n"
        f"⏰ {now.strftime('%H:%M:%S')}\n\n"
    )

    # =====================================================
    # SJC
    # =====================================================

    text += "🥇 VÀNG MIẾNG SJC\n"

    p = market["sjc"]
    c = changes.get("sjc", {})

    text += (
        f"  Mua: {fmt(p['buy'])} đ/chỉ\n"
        f"  Bán: {fmt(p['sell'])} đ/chỉ\n"
        f"  So hôm trước: "
        f"{fmt_change(c.get('buy'))} / "
        f"{fmt_change(c.get('sell'))}\n\n"
    )

    # =====================================================
    # DOJI
    # =====================================================

    text += "🟠 DOJI\n"

    p = market["doji"]
    c = changes.get("doji", {})

    text += (
        f"  Mua: {fmt(p['buy'])} đ/chỉ\n"
        f"  Bán: {fmt(p['sell'])} đ/chỉ\n"
        f"  So hôm trước: "
        f"{fmt_change(c.get('buy'))} / "
        f"{fmt_change(c.get('sell'))}\n\n"
    )

    # =====================================================
    # PNJ
    # =====================================================

    text += "🟢 PNJ\n"

    p = market["pnj"]
    c = changes.get("pnj", {})

    text += (
        f"  Mua: {fmt(p['buy'])} đ/chỉ\n"
        f"  Bán: {fmt(p['sell'])} đ/chỉ\n"
        f"  So hôm trước: "
        f"{fmt_change(c.get('buy'))} / "
        f"{fmt_change(c.get('sell'))}\n\n"
    )

    # =====================================================
    # BTMC
    # =====================================================

    text += "🔵 BẢO TÍN MINH CHÂU\n"

    p = market["btmc"]
    c = changes.get("btmc", {})

    text += (
        f"  Mua: {fmt(p['buy'])} đ/chỉ\n"
        f"  Bán: {fmt(p['sell'])} đ/chỉ\n"
        f"  So hôm trước: "
        f"{fmt_change(c.get('buy'))} / "
        f"{fmt_change(c.get('sell'))}\n\n"
    )

    # =====================================================
    # BẠC
    # =====================================================

    text += "🪙 BẠC PHÚ QUÝ\n"

    p = market["silver"]
    c = changes.get("silver", {})

    text += (
        f"  Mua: {fmt(p['buy'])} đ/chỉ\n"
        f"  Bán: {fmt(p['sell'])} đ/chỉ\n"
        f"  So hôm trước: "
        f"{fmt_change(c.get('buy'))} / "
        f"{fmt_change(c.get('sell'))}\n\n"
    )

    # =====================================================
    # USD
    # =====================================================

    text += "💵 USD VIETCOMBANK\n"

    p = market["usd"]
    c = changes.get("usd", {})

    text += (
        f"  Mua: {fmt(p['buy'])} đ/USD\n"
        f"  Bán: {fmt(p['sell'])} đ/USD\n"
        f"  So hôm trước: "
        f"{fmt_change(c.get('buy'))} / "
        f"{fmt_change(c.get('sell'))}\n\n"
    )

    # =====================================================

    text += "━━━━━━━━━━━━━━━━━━━━\n"

    text += "📌 Đơn vị vàng/bạc: VND/chỉ\n"

    if previous_day:

        date_show = datetime.strptime(
            previous_day,
            "%Y-%m-%d"
        ).strftime("%d/%m/%Y")

        text += (
            f"📈 Thay đổi so với: {date_show}\n"
        )

    else:

        text += (
            "📈 Chưa có dữ liệu ngày trước để so sánh\n"
        )

    text += "🔄 Tự động cập nhật mỗi 60 phút"

    return text


# =========================================================
# /gia
# =========================================================

async def gia(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    try:

        text = make_message()

        await update.message.reply_text(
            text
        )

    except Exception as e:

        print("ERROR /gia:", e)

        await update.message.reply_text(
            "⚠️ Không lấy được dữ liệu thị trường."
        )


# =========================================================
# TỰ ĐỘNG GỬI
# =========================================================

async def automatic_update(
    context: ContextTypes.DEFAULT_TYPE
):

    try:

        text = make_message()

        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=text
        )

    except Exception as e:

        print(
            "ERROR automatic:",
            e
        )


# =========================================================
# /start
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = """
🤖 BOT GIÁ THỊ TRƯỜNG

/gia - Xem giá vàng, bạc, USD

Bot theo dõi:

🥇 SJC
🟠 DOJI
🟢 PNJ
🔵 BTMC
🪙 Bạc Phú Quý
💵 USD Vietcombank

📊 Vàng/bạc: VND/chỉ
📈 Thay đổi: so với ngày hôm trước
"""

    await update.message.reply_text(
        text
    )


# =========================================================
# CHẠY BOT
# =========================================================

def main():

    print(
        "================================="
    )

    print(
        " BOT GIÁ VÀNG - BẠC - USD"
    )

    print(
        "================================="
    )

    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CommandHandler(
            "gia",
            gia
        )
    )

    # Tự động gửi
    app.job_queue.run_repeating(
        automatic_update,
        interval=UPDATE_INTERVAL,
        first=30
    )

    print(
        "Bot đang chạy..."
    )

    app.run_polling()


if __name__ == "__main__":
    main()
