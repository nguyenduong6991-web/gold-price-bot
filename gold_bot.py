import requests
import datetime
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

prev_sjc_buy = 0
prev_sjc_sell = 0
prev_ring_buy = 0
prev_ring_sell = 0
prev_silver_buy = 52000
prev_silver_sell = 58000
prev_xau = 0
prev_xag = 0
first_run = True

def get_gold_prices():
    global first_run, prev_sjc_buy, prev_sjc_sell, prev_ring_buy, prev_ring_sell
    global prev_silver_buy, prev_silver_sell, prev_xau, prev_xag
    
    print("="*50)
    print("GIÁ VÀNG TỰ ĐỘNG")
    print("="*50)
    
    sjc_buy, sjc_sell = 0, 0
    ring_buy, ring_sell = 0, 0
    xau_price, xag_price = 0, 0

        # ===== LẤY GIÁ VÀNG MIẾNG SJC từ vang.today =====
    try:
        res_sjc = requests.get("https://www.vang.today/api/prices?type=SJL1L10", timeout=15)
        print(f"API vang.today SJC: HTTP {res_sjc.status_code}")
        data_sjc = res_sjc.json()
        print(f"Dữ liệu nhận được: {data_sjc}")
        
        # API trả về object trực tiếp
        if data_sjc.get("success"):
            buy_val = float(data_sjc.get("buy", 0))
            sell_val = float(data_sjc.get("sell", 0))
            print(f"Giá gốc từ API - Mua: {buy_val}, Bán: {sell_val}")
            
            if buy_val > 1000000 and sell_val > 1000000:  # > 1 triệu = VNĐ/lượng
                sjc_buy = int(buy_val / 10)  # chia 10 ra VNĐ/chỉ
                sjc_sell = int(sell_val / 10)
                print(f"✅ Vàng miếng SJC: Mua={sjc_buy:,} - Bán={sjc_sell:,} VNĐ/chỉ")
            elif buy_val > 0 and sell_val > 0:  # đã là VNĐ/chỉ
                sjc_buy = int(buy_val)
                sjc_sell = int(sell_val)
                print(f"✅ Vàng miếng SJC: Mua={sjc_buy:,} - Bán={sjc_sell:,} VNĐ/chỉ")
            else:
                print("⚠️ Giá API quá nhỏ, dùng dự phòng")
    except Exception as e:
        print(f"Lỗi lấy giá SJC miếng: {e}")

    
    # ===== LẤY GIÁ VÀNG MIẾNG SJC từ vang.today =====
    try:
        res_sjc = requests.get("https://www.vang.today/api/prices?type=SJL1L10", timeout=15)
        print(f"API vang.today SJC: HTTP {res_sjc.status_code}")
        data_sjc = res_sjc.json()
        print(f"Dữ liệu nhận được: {data_sjc}")
        
        # API trả về object trực tiếp, không phải list
        if data_sjc.get("success"):
            buy_val = float(data_sjc.get("buy", 0))
            sell_val = float(data_sjc.get("sell", 0))
            if buy_val > 0 and sell_val > 0:
                sjc_buy = int(buy_val / 10)  # VNĐ/lượng → chia 10 = VNĐ/chỉ
                sjc_sell = int(sell_val / 10)
                print(f"✅ Vàng miếng SJC: Mua={sjc_buy:,} - Bán={sjc_sell:,} VNĐ/chỉ")
    except Exception as e:
        print(f"Lỗi lấy giá SJC miếng: {e}")
    
    # ===== LẤY GIÁ VÀNG NHẪN SJC =====
    try:
        res_ring = requests.get("https://www.vang.today/api/prices?type=SJ9999", timeout=15)
        print(f"API vang.today Nhẫn: HTTP {res_ring.status_code}")
        data_ring = res_ring.json()
        print(f"Dữ liệu nhận được: {data_ring}")
        
        if data_ring.get("success"):
            buy_val = float(data_ring.get("buy", 0))
            sell_val = float(data_ring.get("sell", 0))
            if buy_val > 0 and sell_val > 0:
                ring_buy = int(buy_val / 10)
                ring_sell = int(sell_val / 10)
                print(f"✅ Vàng nhẫn SJC: Mua={ring_buy:,} - Bán={ring_sell:,} VNĐ/chỉ")
    except Exception as e:
        print(f"Lỗi lấy giá SJC nhẫn: {e}")
    
    # ===== LẤY GIÁ THẾ GIỚI =====
    try:
        res_xau = requests.get("https://api.gold-api.com/price/XAU", timeout=10)
        if res_xau.status_code == 200:
            data_xau = res_xau.json()
            xau_price = float(data_xau.get("price", 0))
        print(f"✅ Vàng XAU/USD: {xau_price:.2f} USD/oz")
    except Exception as e:
        print(f"Lỗi lấy giá XAU: {e}")
    
    try:
        res_xag = requests.get("https://api.gold-api.com/price/XAG", timeout=10)
        if res_xag.status_code == 200:
            data_xag = res_xag.json()
            xag_price = float(data_xag.get("price", 0))
        print(f"✅ Bạc XAG/USD: {xag_price:.2f} USD/oz")
    except Exception as e:
        print(f"Lỗi lấy giá XAG: {e}")
    
    # ===== GIÁ DỰ PHÒNG =====
    if sjc_buy == 0 or sjc_sell == 0:
        print("⚠️ Không lấy được giá SJC từ API → dùng giá dự phòng")
        if first_run:
            sjc_buy, sjc_sell = 7850000, 7920000
        else:
            sjc_buy, sjc_sell = prev_sjc_buy, prev_sjc_sell
    else:
        print("✅ Đã lấy được giá SJC thực tế!")
    
    if ring_buy == 0 or ring_sell == 0:
        ring_buy = sjc_buy + 150000
        ring_sell = sjc_sell + 250000
    
    if xau_price == 0:
        xau_price = 2450.5 if first_run else prev_xau
    
    if xag_price == 0:
        xag_price = 29.5 if first_run else prev_xag
    
    return {
        "sjc_buy": sjc_buy,
        "sjc_sell": sjc_sell,
        "ring_buy": ring_buy,
        "ring_sell": ring_sell,
        "silver_buy": prev_silver_buy,
        "silver_sell": prev_silver_sell,
        "xau": round(xau_price, 2),
        "xag": round(xag_price, 2)
    }

def calc_change(current, previous):
    if previous == 0 or first_run:
        return 0, 0
    change = current - previous
    change_percent = (change / previous) * 100
    return change, change_percent

def format_number(num):
    return f"{num:,.0f}".replace(",", ".")

def get_icon(val):
    if val > 0: return "📈 +"
    elif val < 0: return "📉 "
    else: return "➖ "

def send_telegram_message(text):
    if not BOT_TOKEN:
        print("❌ Chưa có BOT_TOKEN")
        return None
    if not CHAT_ID:
        print("❌ Chưa có CHAT_ID")
        return None
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    print("📤 Đang gửi đến Telegram...")
    response = requests.post(url, data=data)
    result = response.json()
    print(f"📨 Kết quả gửi: {result.get('ok', False)}")
    return result

def main():
    global first_run, prev_sjc_buy, prev_sjc_sell, prev_ring_buy, prev_ring_sell
    global prev_silver_buy, prev_silver_sell, prev_xau, prev_xag
    
    prices = get_gold_prices()
    if not prices:
        send_telegram_message("⚠️ Lỗi: Không lấy được dữ liệu giá!")
        return
    
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    sjc_buy_change, sjc_buy_pct = calc_change(prices["sjc_buy"], prev_sjc_buy)
    sjc_sell_change, sjc_sell_pct = calc_change(prices["sjc_sell"], prev_sjc_sell)
    ring_buy_change, ring_buy_pct = calc_change(prices["ring_buy"], prev_ring_buy)
    ring_sell_change, ring_sell_pct = calc_change(prices["ring_sell"], prev_ring_sell)
    silver_buy_change, silver_buy_pct = calc_change(prices["silver_buy"], prev_silver_buy)
    silver_sell_change, silver_sell_pct = calc_change(prices["silver_sell"], prev_silver_sell)
    xau_change, xau_pct = calc_change(prices["xau"], prev_xau)
    xag_change, xag_pct = calc_change(prices["xag"], prev_xag)
    
    msg = f"""🌍 <b>GIÁ VÀNG & BẠC HÀNG NGÀY</b> 🌍
🕒 {now}
━━━━━━━━━━━━━━━━━━━━━
🇻🇳 <b>Vàng SJC 9999</b>
💰 Giá Mua Vào: {format_number(prices['sjc_buy'])} VNĐ/chỉ
💰 Giá Bán Ra: {format_number(prices['sjc_sell'])} VNĐ/chỉ
━━━━━━━━━━━━━━━━━━━━━
💍 <b>Vàng Nhẫn SJC 9999</b>
💰 Giá Mua Vào: {format_number(prices['ring_buy'])} VNĐ/chỉ
💰 Giá Bán Ra: {format_number(prices['ring_sell'])} VNĐ/chỉ
━━━━━━━━━━━━━━━━━━━━━
🥈 <b>Bạc 999</b>
💰 Giá Mua Vào: {format_number(prices['silver_buy'])} VNĐ/chỉ
💰 Giá Bán Ra: {format_number(prices['silver_sell'])} VNĐ/chỉ
━━━━━━━━━━━━━━━━━━━━━
🌎 <b>Thị trường thế giới</b>
📈 Vàng XAU/USD: {prices['xau']:.1f} USD/oz
📈 Bạc XAG/USD: {prices['xag']:.1f} USD/oz
━━━━━━━━━━━━━━━━━━━━━
🔄 Cập nhật mỗi giờ đúng phút 00
"""
    
    send_telegram_message(msg)
    print("✅ Đã gửi thông báo giá!")
    
    prev_sjc_buy = prices["sjc_buy"]
    prev_sjc_sell = prices["sjc_sell"]
    prev_ring_buy = prices["ring_buy"]
    prev_ring_sell = prices["ring_sell"]
    prev_silver_buy = prices["silver_buy"]
    prev_silver_sell = prices["silver_sell"]
    prev_xau = prices["xau"]
    prev_xag = prices["xag"]
    
    if first_run:
        print("ℹ️ Lần đầu chạy — từ giờ sẽ tự so sánh với giá giờ trước")
        first_run = False

if __name__ == "__main__":
    main()
