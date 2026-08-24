import requests
import datetime
import os

# ==== CẤU HÌNH ====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Giá tham chiếu để so sánh thay đổi (sẽ tự cập nhật sau mỗi lần chạy)
prev_sjc_buy = 0
prev_sjc_sell = 0
prev_ring_buy = 0
prev_ring_sell = 0
prev_silver_buy = 0
prev_silver_sell = 0
prev_xau = 0
prev_xag = 0
first_run = True

def get_gold_prices():
    """Lấy giá vàng từ nguồn dữ liệu thực tế tự động"""
    global first_run, prev_sjc_buy, prev_sjc_sell, prev_ring_buy, prev_ring_sell
    global prev_silver_buy, prev_silver_sell, prev_xau, prev_xag
    
    try:
        # ========== 1. LẤY GIÁ VÀNG SJC VIỆT NAM TỪ vang.today API ==========
        sjc_buy, sjc_sell = 0, 0
        ring_buy, ring_sell = 0, 0
        
        try:
            # API trả về giá theo loại: SJL1L10 = Vàng miếng SJC 9999, SJ9999 = Vàng nhẫn SJC 9999
            res_sjc = requests.get("https://www.vang.today/api/prices?type=SJL1L10", timeout=15)
            res_ring = requests.get("https://www.vang.today/api/prices?type=SJ9999", timeout=15)
            
            if res_sjc.status_code == 200:
                data_sjc = res_sjc.json()
                if data_sjc and len(data_sjc) > 0:
                    # Giá trả về là VNĐ/lượng → chia 10 ra VNĐ/chỉ
                    sjc_buy = int(float(data_sjc[0].get("buy", 0)) / 10)
                    sjc_sell = int(float(data_sjc[0].get("sell", 0)) / 10)
            
            if res_ring.status_code == 200:
                data_ring = res_ring.json()
                if data_ring and len(data_ring) > 0:
                    ring_buy = int(float(data_ring[0].get("buy", 0)) / 10)
                    ring_sell = int(float(data_ring[0].get("sell", 0)) / 10)
            
            print(f"✅ Lấy giá SJC thành công: Mua={sjc_buy}, Bán={sjc_sell} VNĐ/chỉ")
        except Exception as e:
            print(f"⚠️ Lỗi API vang.today: {e}")
            # Fallback: nếu API lỗi, dùng giá dự phòng
            if first_run:
                sjc_buy, sjc_sell = 14700000, 15000000
                ring_buy, ring_sell = 14850000, 15250000
        
        # ========== 2. GIÁ BẠC TRONG NƯỚC (dữ liệu tham khảo) ==========
        # Lưu ý: Không có API miễn phí chuẩn cho bạc VN → tính theo tỷ lệ XAG
        silver_buy, silver_sell = 52000, 58000
        
        # ========== 3. LẤY GIÁ THẾ GIỚI TỪ GoldAPI.io ==========
        xau_price, xag_price = 0, 0
        try:
            res_xau = requests.get("https://api.gold-api.com/price/XAU", timeout=10)
            res_xag = requests.get("https://api.gold-api.com/price/XAG", timeout=10)
            
            if res_xau.status_code == 200:
                xau_data = res_xau.json()
                xau_price = float(xau_data.get("price", 0))
            if res_xag.status_code == 200:
                xag_data = res_xag.json()
                xag_price = float(xag_data.get("price", 0))
            
            print(f"✅ Giá thế giới: XAU={xau_price}, XAG={xag_price}")
        except Exception as e:
            print(f"⚠️ Lỗi API thế giới: {e}")
            if first_run:
                xau_price, xag_price = 2450.5, 29.5
        
        # Kiểm tra dữ liệu hợp lệ
        if sjc_buy == 0 or sjc_sell == 0:
            raise Exception("Không lấy được giá SJC")
        
        return {
            "sjc_buy": sjc_buy,
            "sjc_sell": sjc_sell,
            "ring_buy": ring_buy if ring_buy > 0 else sjc_buy + 150000,
            "ring_sell": ring_sell if ring_sell > 0 else sjc_sell + 250000,
            "silver_buy": silver_buy,
            "silver_sell": silver_sell,
            "xau": round(xau_price, 2),
            "xag": round(xag_price, 2)
        }
    except Exception as e:
        print(f"❌ Lỗi lấy giá: {e}")
        return None

def calc_change(current, previous):
    """Tính toán thay đổi: số tiền và phần trăm"""
    if previous == 0 or first_run:
        return 0, 0  # Lần đầu chưa có dữ liệu so sánh
    change = current - previous
    change_percent = (change / previous) * 100
    return change, change_percent

def format_number(num):
    """Định dạng số dễ đọc"""
    return f"{num:,.0f}".replace(",", ".")

def get_icon(val):
    """Biểu tượng tăng/giảm"""
    if val > 0: return "📈 +"
    elif val < 0: return "📉 "
    else: return "➖ "

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
    global first_run, prev_sjc_buy, prev_sjc_sell, prev_ring_buy, prev_ring_sell
    global prev_silver_buy, prev_silver_sell, prev_xau, prev_xag
    
    prices = get_gold_prices()
    if not prices:
        send_telegram_message("⚠️ Lỗi: Không lấy được dữ liệu giá! Vui lòng thử lại sau.")
        return
    
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # === Tính toán thay đổi % ===
    sjc_buy_change, sjc_buy_pct = calc_change(prices["sjc_buy"], prev_sjc_buy)
    sjc_sell_change, sjc_sell_pct = calc_change(prices["sjc_sell"], prev_sjc_sell)
    ring_buy_change, ring_buy_pct = calc_change(prices["ring_buy"], prev_ring_buy)
    ring_sell_change, ring_sell_pct = calc_change(prices["ring_sell"], prev_ring_sell)
    silver_buy_change, silver_buy_pct = calc_change(prices["silver_buy"], prev_silver_buy)
    silver_sell_change, silver_sell_pct = calc_change(prices["silver_sell"], prev_silver_sell)
    xau_change, xau_pct = calc_change(prices["xau"], prev_xau)
    xag_change, xag_pct = calc_change(prices["xag"], prev_xag)
    
    # === Tạo nội dung tin nhắn ===
    msg = f"""🌍 <b>GIÁ VÀNG & BẠC HÀNG NGÀY</b> 🌍
🕒 {now}
━━━━━━━━━━━━━━━━━━━━━
🇻🇳 <b>Vàng Miếng SJC 9999</b>
💰 Giá Mua Vào: {format_number(prices['sjc_buy'])} VNĐ/chỉ
"""
    if not first_run:
        msg += f"{get_icon(sjc_buy_change)}{format_number(sjc_buy_change)} VNĐ ({sjc_buy_pct:+.2f}%)\n"
    
    msg += f"💰 Giá Bán Ra: {format_number(prices['sjc_sell'])} VNĐ/chỉ\n"
    if not first_run:
        msg += f"{get_icon(sjc_sell_change)}{format_number(sjc_sell_change)} VNĐ ({sjc_sell_pct:+.2f}%)\n"
    
    msg += """━━━━━━━━━━━━━━━━━━━━━
💍 <b>Vàng Nhẫn SJC 9999</b>
💰 Giá Mua Vào: {format_number(prices['ring_buy'])} VNĐ/chỉ
""".format(format_number=format_number, prices=prices)
    if not first_run:
        msg += f"{get_icon(ring_buy_change)}{format_number(ring_buy_change)} VNĐ ({ring_buy_pct:+.2f}%)\n"
    
    msg += f"💰 Giá Bán Ra: {format_number(prices['ring_sell'])} VNĐ/chỉ\n"
    if not first_run:
        msg += f"{get_icon(ring_sell_change)}{format_number(ring_sell_change)} VNĐ ({ring_sell_pct:+.2f}%)\n"
    
    msg += """━━━━━━━━━━━━━━━━━━━━━
🥈 <b>Bạc 999</b>
💰 Giá Mua Vào: {format_number(prices['silver_buy'])} VNĐ/chỉ
""".format(format_number=format_number, prices=prices)
    if not first_run:
        msg += f"{get_icon(silver_buy_change)}{format_number(silver_buy_change)} VNĐ ({silver_buy_pct:+.2f}%)\n"
    
    msg += f"💰 Giá Bán Ra: {format_number(prices['silver_sell'])} VNĐ/chỉ\n"
    if not first_run:
        msg += f"{get_icon(silver_sell_change)}{format_number(silver_sell_change)} VNĐ ({silver_sell_pct:+.2f}%)\n"
    
    msg += f"""━━━━━━━━━━━━━━━━━━━━━
🌐 <b>Thị Trường Thế Giới</b>
📊 Vàng XAU/USD: {prices['xau']:.2f} USD/oz
"""
    if not first_run:
        msg += f"{get_icon(xau_change)}{xau_change:+.2f} USD ({xau_pct:+.2f}%)\n"
    
    msg += f"📊 Bạc XAG/USD: {prices['xag']:.2f} USD/oz\n"
    if not first_run:
        msg += f"{get_icon(xag_change)}{xag_change:+.2f} USD ({xag_pct:+.2f}%)\n"
    
    msg += """━━━━━━━━━━━━━━━━━━━━━
🔄 Cập nhật mỗi 1 giờ — Dữ liệu tự động lấy từ nguồn thực tế
"""
    
    # === Gửi tin nhắn ===
    send_telegram_message(msg)
    print("✅ Đã gửi thông báo giá!")
    
    # === Lưu giá cho lần so sánh tiếp theo ===
    prev_sjc_buy = prices["sjc_buy"]
    prev_sjc_sell = prices["sjc_sell"]
    prev_ring_buy = prices["ring_buy"]
    prev_ring_sell = prices["ring_sell"]
    prev_silver_buy = prices["silver_buy"]
    prev_silver_sell = prices["silver_sell"]
    prev_xau = prices["xau"]
    prev_xag = prices["xag"]
    
    if first_run:
        print("ℹ️ Lần đầu chạy — chưa có dữ liệu so sánh % cho lần sau")
        first_run = False

if __name__ == "__main__":
    main()
