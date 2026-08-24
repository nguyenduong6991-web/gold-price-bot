import requests
import datetime
import os

# ==== CẤU HÌNH ====
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Token bot Telegram của bạn
CHAT_ID = os.getenv("CHAT_ID")      # ID chat nhận thông báo

# Giá tham chiếu hôm trước (sẽ tự cập nhật sau mỗi lần chạy)
# Lưu ý: Lần đầu chạy bạn có thể điền số liệu thực tế, bot sẽ tự cập nhật sau
prev_sjc_buy = 7850000
prev_sjc_sell = 7920000
prev_silver_buy = 85000
prev_silver_sell = 88000
prev_xau = 2450.5

def get_gold_prices():
    """Lấy giá vàng từ nguồn dữ liệu"""
    try:
        # === LẤY GIÁ VÀNG SJC ===
        # Bạn có thể thay bằng API nguồn thực tế, đây là ví dụ cấu trúc
        sjc_buy = 7850000   # VNĐ/chỉ
        sjc_sell = 7920000  # VNĐ/chỉ
        
        # === LẤY GIÁ BẠC ===
        silver_buy = 85000   # VNĐ/chỉ
        silver_sell = 88000 # VNĐ/chỉ
        
        # === LẤY GIÁ VÀNG THẾ GIỚI ===
        xau_price = 2450.5  # USD/oz
        
        return {
            "sjc_buy": sjc_buy,
            "sjc_sell": sjc_sell,
            "silver_buy": silver_buy,
            "silver_sell": silver_sell,
            "xau": xau_price
        }
    except Exception as e:
        print(f"Lỗi lấy giá: {e}")
        return None

def calc_change(current, previous):
    """Tính toán thay đổi: số tiền và phần trăm"""
    change = current - previous
    change_percent = (change / previous) * 100 if previous != 0 else 0
    return change, change_percent

def format_number(num):
    """Định dạng số dễ đọc"""
    return f"{num:,.0f}".replace(",", ".")

def send_telegram_message(text):
    """Gửi tin nhắn đến Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=data)
    return response.json()

def main():
    global prev_sjc_buy, prev_sjc_sell, prev_silver_buy, prev_silver_sell, prev_xau
    
    prices = get_gold_prices()
    if not prices:
        send_telegram_message("⚠️ Lỗi: Không lấy được dữ liệu giá!")
        return
    
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # === Tính toán thay đổi % ===
    sjc_buy_change, sjc_buy_pct = calc_change(prices["sjc_buy"], prev_sjc_buy)
    sjc_sell_change, sjc_sell_pct = calc_change(prices["sjc_sell"], prev_sjc_sell)
    silver_buy_change, silver_buy_pct = calc_change(prices["silver_buy"], prev_silver_buy)
    silver_sell_change, silver_sell_pct = calc_change(prices["silver_sell"], prev_silver_sell)
    xau_change, xau_pct = calc_change(prices["xau"], prev_xau)
    
    # === Tạo biểu tượng tăng/giảm ===
    def get_icon(val):
        if val > 0: return "📈 +"
        elif val < 0: return "📉 "
        else: return "➖ "
    
    # === Tạo nội dung tin nhắn ===
    msg = f"""🌍 <b>GIÁ VÀNG & BẠC HÀNG NGÀY</b> 🌍
🕒 {now}
━━━━━━━━━━━━━━━━━━━━━
🇻🇳 <b>Vàng SJC 9999</b>
💰 Giá Mua Vào: {format_number(prices['sjc_buy'])} VNĐ/chỉ
{get_icon(sjc_buy_change)}{format_number(sjc_buy_change)} VNĐ ({sjc_buy_pct:+.2f}%)
💰 Giá Bán Ra: {format_number(prices['sjc_sell'])} VNĐ/chỉ
{get_icon(sjc_sell_change)}{format_number(sjc_sell_change)} VNĐ ({sjc_sell_pct:+.2f}%)
━━━━━━━━━━━━━━━━━━━━━
🥈 <b>Bạc 999</b>
💰 Giá Mua Vào: {format_number(prices['silver_buy'])} VNĐ/chỉ
{get_icon(silver_buy_change)}{format_number(silver_buy_change)} VNĐ ({silver_buy_pct:+.2f}%)
💰 Giá Bán Ra: {format_number(prices['silver_sell'])} VNĐ/chỉ
{get_icon(silver_sell_change)}{format_number(silver_sell_change)} VNĐ ({silver_sell_pct:+.2f}%)
━━━━━━━━━━━━━━━━━━━━━
🌐 <b>Vàng Thế Giới</b>
📊 XAU/USD: {prices['xau']:.2f} USD/oz
{get_icon(xau_change)}{xau_change:+.2f} USD ({xau_pct:+.2f}%)
━━━━━━━━━━━━━━━━━━━━━
🔄 Cập nhật mỗi 1 giờ
"""
    
    # === Gửi tin nhắn ===
    send_telegram_message(msg)
    print("✅ Đã gửi thông báo giá!")
    
    # === Cập nhật giá tham chiếu cho lần sau ===
    prev_sjc_buy = prices["sjc_buy"]
    prev_sjc_sell = prices["sjc_sell"]
    prev_silver_buy = prices["silver_buy"]
    prev_silver_sell = prices["silver_sell"]
    prev_xau = prices["xau"]

if __name__ == "__main__":
    main()
