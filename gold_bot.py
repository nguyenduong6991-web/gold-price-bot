import requests
import datetime
import os
from apscheduler.schedulers.background import BackgroundScheduler
import logging

# ===== CẤU HÌNH LOGGING =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===== LẤY TOKEN TỪ ENVIRONMENT VARIABLES =====
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8892269519:AAEtTq9n74OWVRN1CKmzIy5M1dfBbOJUToA")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "7176458499")

# ===== BIẾN GLOBAL LƯU GIÁ TỪ LẦN CHẠY TRƯỚC =====
price_state = {
    "prev_sjc_buy": 0,
    "prev_sjc_sell": 0,
    "prev_ring_buy": 0,
    "prev_ring_sell": 0,
    "prev_silver_buy": 52000,
    "prev_silver_sell": 58000,
    "prev_xau": 0,
    "prev_xag": 0,
    "first_run": True
}

def verify_telegram_connection():
    """Kiểm tra kết nối Telegram có hoạt động không"""
    logger.info("🔍 Đang kiểm tra kết nối Telegram...")
    
    if not BOT_TOKEN or not CHAT_ID:
        logger.error("❌ BOT_TOKEN hoặc CHAT_ID bị thiếu!")
        return False
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                logger.info(f"✅ Bot hoạt động: {bot_info.get('first_name')} (@{bot_info.get('username')})")
                return True
            else:
                logger.error(f"❌ Token không hợp lệ: {data.get('description')}")
                return False
        else:
            logger.error(f"❌ HTTP {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Lỗi kết nối Telegram: {e}")
        return False

def get_gold_prices():
    """Lấy giá vàng từ các API"""
    logger.info("=" * 50)
    logger.info("BẮT ĐẦU LẤY GIÁ VÀNG")
    logger.info("=" * 50)
    
    sjc_buy, sjc_sell = 0, 0
    ring_buy, ring_sell = 0, 0
    xau_price, xag_price = 0, 0
    
    # ===== LẤY GIÁ VÀNG MIẾNG SJC từ vang.today =====
    try:
        res_sjc = requests.get("https://www.vang.today/api/prices?type=SJL1L10", timeout=15)
        logger.info(f"API vang.today SJC: HTTP {res_sjc.status_code}")
        
        if res_sjc.status_code == 200:
            data_sjc = res_sjc.json()
            logger.debug(f"Dữ liệu nhận được: {data_sjc}")
            
            if data_sjc.get("success"):
                buy_val = float(data_sjc.get("buy", 0))
                sell_val = float(data_sjc.get("sell", 0))
                logger.info(f"Giá gốc từ API - Mua: {buy_val}, Bán: {sell_val}")
                
                if buy_val >= 10000000 and sell_val >= 10000000:
                    sjc_buy = int(buy_val / 10)
                    sjc_sell = int(sell_val / 10)
                    logger.info(f"✅ Vàng miếng SJC: Mua={sjc_buy:,} - Bán={sjc_sell:,} VNĐ/chỉ")
                elif buy_val > 0 and sell_val > 0:
                    sjc_buy = int(buy_val)
                    sjc_sell = int(sell_val)
                    logger.info(f"✅ Vàng miếng SJC: Mua={sjc_buy:,} - Bán={sjc_sell:,} VNĐ/chỉ")
        else:
            logger.warning(f"API vang.today trả về lỗi: {res_sjc.status_code}")
    except Exception as e:
        logger.error(f"Lỗi lấy giá SJC miếng: {e}")
    
    # ===== LẤY GIÁ VÀNG NHẪN SJC =====
    try:
        res_ring = requests.get("https://www.vang.today/api/prices?type=SJ9999", timeout=15)
        logger.info(f"API vang.today Nhẫn: HTTP {res_ring.status_code}")
        
        if res_ring.status_code == 200:
            data_ring = res_ring.json()
            logger.debug(f"Dữ liệu nhận được: {data_ring}")
            
            if data_ring.get("success"):
                buy_val = float(data_ring.get("buy", 0))
                sell_val = float(data_ring.get("sell", 0))
                if buy_val >= 10000000 and sell_val >= 10000000:
                    ring_buy = int(buy_val / 10)
                    ring_sell = int(sell_val / 10)
                    logger.info(f"✅ Vàng nhẫn SJC: Mua={ring_buy:,} - Bán={ring_sell:,} VNĐ/chỉ")
                elif buy_val > 0 and sell_val > 0:
                    ring_buy = int(buy_val)
                    ring_sell = int(sell_val)
                    logger.info(f"✅ Vàng nhẫn SJC: Mua={ring_buy:,} - Bán={ring_sell:,} VNĐ/chỉ")
        else:
            logger.warning(f"API vang.today nhẫn trả về lỗi: {res_ring.status_code}")
    except Exception as e:
        logger.error(f"Lỗi lấy giá SJC nhẫn: {e}")
    
    # ===== LẤY GIÁ THẾ GIỚI =====
    try:
        res_xau = requests.get("https://api.gold-api.com/price/XAU", timeout=10)
        if res_xau.status_code == 200:
            data_xau = res_xau.json()
            xau_price = float(data_xau.get("price", 0))
            logger.info(f"✅ Vàng XAU/USD: {xau_price:.2f} USD/oz")
        else:
            logger.warning(f"API XAU trả về lỗi: {res_xau.status_code}")
    except Exception as e:
        logger.error(f"Lỗi lấy giá XAU: {e}")
    
    try:
        res_xag = requests.get("https://api.gold-api.com/price/XAG", timeout=10)
        if res_xag.status_code == 200:
            data_xag = res_xag.json()
            xag_price = float(data_xag.get("price", 0))
            logger.info(f"✅ Bạc XAG/USD: {xag_price:.2f} USD/oz")
        else:
            logger.warning(f"API XAG trả về lỗi: {res_xag.status_code}")
    except Exception as e:
        logger.error(f"Lỗi lấy giá XAG: {e}")
    
    # ===== GIÁ DỰ PHÒNG =====
    if sjc_buy == 0 or sjc_sell == 0:
        logger.warning("⚠️ Không lấy được giá SJC từ API → dùng giá dự phòng")
        if price_state["first_run"]:
            sjc_buy, sjc_sell = 7850000, 7920000
        else:
            sjc_buy = price_state["prev_sjc_buy"]
            sjc_sell = price_state["prev_sjc_sell"]
    else:
        logger.info("✅ Đã lấy được giá SJC thực tế!")
    
    if ring_buy == 0 or ring_sell == 0:
        ring_buy = sjc_buy + 150000
        ring_sell = sjc_sell + 250000
        logger.info(f"Tính giá nhẫn dựa trên giá miếng: Mua={ring_buy:,} - Bán={ring_sell:,}")
    
    if xau_price == 0:
        xau_price = 2450.5 if price_state["first_run"] else price_state["prev_xau"]
        logger.warning(f"Dùng giá dự phòng XAU: {xau_price}")
    
    if xag_price == 0:
        xag_price = 29.5 if price_state["first_run"] else price_state["prev_xag"]
        logger.warning(f"Dùng giá dự phòng XAG: {xag_price}")
    
    return {
        "sjc_buy": sjc_buy,
        "sjc_sell": sjc_sell,
        "ring_buy": ring_buy,
        "ring_sell": ring_sell,
        "silver_buy": price_state["prev_silver_buy"],
        "silver_sell": price_state["prev_silver_sell"],
        "xau": round(xau_price, 2),
        "xag": round(xag_price, 2)
    }

def calc_change(current, previous):
    """Tính thay đổi giá"""
    if previous == 0 or price_state["first_run"]:
        return 0, 0
    change = current - previous
    change_percent = (change / previous) * 100 if previous != 0 else 0
    return change, change_percent

def format_number(num):
    """Format số thành chuỗi với dấu phân cách"""
    return f"{num:,.0f}".replace(",", ".")

def get_icon(val):
    """Trả về icon dựa trên giá trị"""
    if val > 0:
        return "📈 +"
    elif val < 0:
        return "📉 "
    else:
        return "➖ "

def send_telegram_message(text, is_test=False):
    """Gửi tin nhắn tới Telegram"""
    if not BOT_TOKEN:
        logger.error("❌ Chưa có BOT_TOKEN")
        return False
    if not CHAT_ID:
        logger.error("❌ Chưa có CHAT_ID")
        return False
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    
    try:
        if is_test:
            logger.info("🧪 Đang gửi tin nhắn TEST...")
        else:
            logger.info("📤 Đang gửi tin nhắn giá vàng...")
        
        response = requests.post(url, data=data, timeout=10)
        result = response.json()
        
        if result.get('ok'):
            if is_test:
                logger.info("✅ ✅ ✅ GỬI TEST TELEGRAM THÀNH CÔNG! ✅ ✅ ✅")
            else:
                logger.info("✅ Gửi Telegram thành công!")
            return True
        else:
            error_code = result.get('error_code')
            error_msg = result.get('description', 'Unknown error')
            logger.error(f"❌ Telegram API lỗi ({error_code}): {error_msg}")
            
            # Giải thích lỗi chi tiết
            if error_code == 400:
                logger.error("   💡 Nguyên nhân: Chat ID sai hoặc bot chưa được add vào chat")
                logger.error(f"   💡 Chat ID hiện tại: {CHAT_ID}")
                logger.error("   💡 Cách fix: Kiểm tra Chat ID và thêm bot vào chat/group")
            elif error_code == 401:
                logger.error("   💡 Nguyên nhân: Bot Token không hợp lệ")
                logger.error("   💡 Cách fix: Regenerate token trên @BotFather")
            elif error_code == 403:
                logger.error("   💡 Nguyên nhân: Bot bị block hoặc chat bị xóa")
                logger.error("   💡 Cách fix: Unblock bot và thêm lại vào chat")
            
            return False
            
    except requests.exceptions.Timeout:
        logger.error("❌ Timeout - Mất kết nối với Telegram API")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("❌ Connection Error - Kiểm tra kết nối mạng")
        return False
    except Exception as e:
        logger.error(f"❌ Lỗi gửi Telegram: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Hàm chính - lấy giá và gửi thông báo"""
    logger.info("🚀 BẮT ĐẦU LƯỢT CẬP NHẬT")
    
    prices = get_gold_prices()
    if not prices:
        send_telegram_message("⚠️ Lỗi: Không lấy được dữ liệu giá!")
        logger.error("❌ Không thể lấy dữ liệu giá")
        return
    
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # Tính thay đổi giá
    sjc_buy_change, sjc_buy_pct = calc_change(prices["sjc_buy"], price_state["prev_sjc_buy"])
    sjc_sell_change, sjc_sell_pct = calc_change(prices["sjc_sell"], price_state["prev_sjc_sell"])
    ring_buy_change, ring_buy_pct = calc_change(prices["ring_buy"], price_state["prev_ring_buy"])
    ring_sell_change, ring_sell_pct = calc_change(prices["ring_sell"], price_state["prev_ring_sell"])
    silver_buy_change, silver_buy_pct = calc_change(prices["silver_buy"], price_state["prev_silver_buy"])
    silver_sell_change, silver_sell_pct = calc_change(prices["silver_sell"], price_state["prev_silver_sell"])
    xau_change, xau_pct = calc_change(prices["xau"], price_state["prev_xau"])
    xag_change, xag_pct = calc_change(prices["xag"], price_state["prev_xag"])
    
    # Tạo tin nhắn
    msg = f"""🌍 <b>GIÁ VÀNG & BẠC HÀNG NGÀY</b> 🌍
🕒 {now}
━━━━━━━━━━━━━━━━━━━━━
🇻🇳 <b>Vàng SJC 9999</b>
💰 Giá Mua Vào: <b>{format_number(prices['sjc_buy'])} VNĐ/chỉ</b>
   {get_icon(sjc_buy_change)}{abs(sjc_buy_change):,.0f} ({sjc_buy_pct:+.2f}%)
💰 Giá Bán Ra: <b>{format_number(prices['sjc_sell'])} VNĐ/chỉ</b>
   {get_icon(sjc_sell_change)}{abs(sjc_sell_change):,.0f} ({sjc_sell_pct:+.2f}%)
━━━━━━━━━━━━━━━━━━━━━
💍 <b>Vàng Nhẫn SJC 9999</b>
💰 Giá Mua Vào: <b>{format_number(prices['ring_buy'])} VNĐ/chỉ</b>
   {get_icon(ring_buy_change)}{abs(ring_buy_change):,.0f} ({ring_buy_pct:+.2f}%)
💰 Giá Bán Ra: <b>{format_number(prices['ring_sell'])} VNĐ/chỉ</b>
   {get_icon(ring_sell_change)}{abs(ring_sell_change):,.0f} ({ring_sell_pct:+.2f}%)
━━━━━━━━━━━━━━━━━━━━━
🥈 <b>Bạc 999</b>
💰 Giá Mua Vào: <b>{format_number(prices['silver_buy'])} VNĐ/chỉ</b>
   {get_icon(silver_buy_change)}{abs(silver_buy_change):,.0f} ({silver_buy_pct:+.2f}%)
💰 Giá Bán Ra: <b>{format_number(prices['silver_sell'])} VNĐ/chỉ</b>
   {get_icon(silver_sell_change)}{abs(silver_sell_change):,.0f} ({silver_sell_pct:+.2f}%)
━━━━━━━━━━━━━━━━━━━━━
🌎 <b>Thị trường thế giới</b>
📈 Vàng XAU/USD: <b>{prices['xau']:.1f}</b> USD/oz
   {get_icon(xau_change)}{abs(xau_change):.2f} ({xau_pct:+.2f}%)
📈 Bạc XAG/USD: <b>{prices['xag']:.1f}</b> USD/oz
   {get_icon(xag_change)}{abs(xag_change):.2f} ({xag_pct:+.2f}%)
━━���━━━━━━━━━━━━━━━━━━
🔄 Cập nhật tự động mỗi giờ lúc 00 phút
"""
    
    send_telegram_message(msg)
    logger.info("✅ Đã gửi thông báo giá!")
    
    # CẬP NHẬT GIÁ VÀO STATE - ĐÂY LÀ PHẦN QUAN TRỌNG!
    price_state["prev_sjc_buy"] = prices["sjc_buy"]
    price_state["prev_sjc_sell"] = prices["sjc_sell"]
    price_state["prev_ring_buy"] = prices["ring_buy"]
    price_state["prev_ring_sell"] = prices["ring_sell"]
    price_state["prev_silver_buy"] = prices["silver_buy"]
    price_state["prev_silver_sell"] = prices["silver_sell"]
    price_state["prev_xau"] = prices["xau"]
    price_state["prev_xag"] = prices["xag"]
    
    if price_state["first_run"]:
        logger.info("ℹ️ Lần đầu chạy — từ giờ sẽ tự so sánh với giá giờ trước")
        price_state["first_run"] = False

def start_scheduler():
    """Khởi động scheduler để chạy tự động"""
    logger.info("🕐 Khởi động scheduler...")
    
    scheduler = BackgroundScheduler()
    # Chạy lúc :00 của mỗi giờ (00:00, 01:00, 02:00, ...)
    scheduler.add_job(
        func=main,
        trigger="cron",
        minute="0",
        second="0",
        id="gold_price_job",
        name="Cập nhật giá vàng",
        misfire_grace_time=60
    )
    
    scheduler.start()
    logger.info("✅ Scheduler đã khởi động!")
    logger.info("📅 Tin nhắn sẽ được gửi vào lúc 00 phút của mỗi giờ")
    
    return scheduler

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🌟 KHỞI ĐỘNG BOT GIÁ VÀNG")
    logger.info("=" * 60)
    logger.info(f"Bot Token: {'***' + BOT_TOKEN[-8:] if BOT_TOKEN else 'Chưa có'}")
    logger.info(f"Chat ID: {CHAT_ID}")
    
    # Kiểm tra kết nối Telegram
    logger.info("")
    if not verify_telegram_connection():
        logger.error("❌ ❌ ❌ BOT KHÔNG THỂ KẾT NỐI TELEGRAM ❌ ❌ ❌")
        logger.error("Hãy kiểm tra:")
        logger.error("1. Bot Token có đúng không?")
        logger.error("2. Có kết nối internet không?")
        exit(1)
    
    # Gửi tin nhắn test
    logger.info("")
    logger.info("Gửi tin nhắn test...")
    test_msg = """🌟 <b>BOT GIÁ VÀNG ĐÃ KHỞI ĐỘNG THÀNH CÔNG!</b> 🌟

✅ Bot đã sẵn sàng gửi thông báo giá vàng
🕒 Tin nhắn giá sẽ được gửi mỗi giờ lúc :00 phút

📱 Chat ID: <code>""" + CHAT_ID + """</code>

🔧 Nếu không muốn nhận thông báo, xóa chat này hoặc block bot
"""
    
    if send_telegram_message(test_msg, is_test=True):
        logger.info("✅ Tin nhắn test gửi thành công!")
    else:
        logger.error("❌ ❌ ❌ KHÔNG GỬI ĐƯỢC TIN NHẮN TEST ❌ ❌ ❌")
        logger.error("Chat ID của bạn có thể sai!")
        logger.error("")
        logger.error("📝 Cách xác định Chat ID đúng:")
        logger.error("1. Forward tin nhắn từ chat này tới @userinfobot")
        logger.error("2. Bot sẽ trả về Chat ID đúng")
        logger.error("3. Update CHAT_ID trong code hoặc env variable")
        exit(1)
    
    # Chạy lần đầu ngay lập tức
    logger.info("")
    logger.info("Chạy lần đầu lấy giá vàng ngay bây giờ...")
    main()
    
    # Khởi động scheduler
    logger.info("")
    scheduler = start_scheduler()
    
    try:
        logger.info("⏳ Bot đang chạy. Nhấn Ctrl+C để dừng...")
        # Giữ scheduler chạy
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Đang dừng scheduler...")
        scheduler.shutdown()
        logger.info("✅ Bot đã dừng")
