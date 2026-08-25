import requests
import logging

# ===== CẤU HÌNH LOGGING =====
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===== THÔNG TIN TELEGRAM =====
BOT_TOKEN = "8892269519:AAEtTq9n74OWVRN1CKmzIy5M1dfBbOJUToA"
CHAT_ID = "7176458499"

def test_telegram():
    """Test gửi tin nhắn Telegram"""
    logger.info("=" * 60)
    logger.info("🧪 BẮT ĐẦU TEST TELEGRAM")
    logger.info("=" * 60)
    
    # Kiểm tra token và chat ID
    logger.info(f"Bot Token: {'***' + BOT_TOKEN[-8:] if BOT_TOKEN else 'KHÔNG CÓ'}")
    logger.info(f"Chat ID: {CHAT_ID}")
    
    if not BOT_TOKEN or not CHAT_ID:
        logger.error("❌ Bot Token hoặc Chat ID bị thiếu!")
        return False
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    logger.info(f"API URL: {url}")
    
    # Test message
    test_message = """🌍 <b>TEST BOT TELEGRAM</b> 🌍

✅ Nếu bạn nhìn thấy tin nhắn này = Bot hoạt động tốt!

🕒 Thời gian: Test
━━━━━━━━━━━━━━━━━━━━━
💰 Giá Vàng SJC
Mua: 7.850.000 VNĐ/chỉ
Bán: 7.920.000 VNĐ/chỉ
━━━━━━━━━━━━━━━━━━━━━

Nếu không nhìn thấy tin nhắn này, hãy check:
1️⃣ Bot Token có đúng không?
2️⃣ Chat ID có đúng không?
3️⃣ Bot có được add vào chat không?
"""
    
    data = {
        "chat_id": CHAT_ID,
        "text": test_message,
        "parse_mode": "HTML"
    }
    
    try:
        logger.info("📤 Đang gửi tin nhắn test...")
        logger.debug(f"Dữ liệu gửi: {data}")
        
        response = requests.post(url, data=data, timeout=10)
        logger.info(f"HTTP Status Code: {response.status_code}")
        logger.debug(f"Response Headers: {response.headers}")
        
        result = response.json()
        logger.debug(f"Response JSON: {result}")
        
        if result.get('ok'):
            logger.info("✅ ✅ ✅ GỬI TELEGRAM THÀNH CÔNG! ✅ ✅ ✅")
            logger.info(f"Message ID: {result.get('result', {}).get('message_id')}")
            return True
        else:
            error_code = result.get('error_code')
            error_desc = result.get('description')
            logger.error(f"❌ Telegram API lỗi:")
            logger.error(f"   Error Code: {error_code}")
            logger.error(f"   Description: {error_desc}")
            
            # Giải thích lỗi
            if error_code == 400:
                logger.error("   → Chat ID sai hoặc bot không được thêm vào chat")
            elif error_code == 401:
                logger.error("   → Bot Token sai")
            elif error_code == 403:
                logger.error("   → Bot bị block hoặc chat bị xóa")
            
            return False
            
    except requests.exceptions.Timeout:
        logger.error("❌ Timeout - Mất kết nối với Telegram API")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("❌ Connection Error - Kiểm tra kết nối mạng")
        return False
    except Exception as e:
        logger.error(f"❌ Lỗi không xác định: {e}")
        logger.error(f"   Type: {type(e).__name__}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_api_calls():
    """Test các API khác"""
    logger.info("\n" + "=" * 60)
    logger.info("🧪 TEST CÁC API LẤY GIÁ VÀNG")
    logger.info("=" * 60)
    
    # Test vang.today SJC
    try:
        logger.info("📡 Test API vang.today SJC...")
        res = requests.get("https://www.vang.today/api/prices?type=SJL1L10", timeout=15)
        logger.info(f"   HTTP {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            if data.get('success'):
                logger.info(f"   ✅ Dữ liệu: {data}")
            else:
                logger.warning(f"   ⚠️ API trả về: {data}")
    except Exception as e:
        logger.error(f"   ❌ Lỗi: {e}")
    
    # Test gold-api XAU
    try:
        logger.info("📡 Test API gold-api XAU...")
        res = requests.get("https://api.gold-api.com/price/XAU", timeout=10)
        logger.info(f"   HTTP {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            logger.info(f"   ✅ Giá XAU: {data}")
    except Exception as e:
        logger.error(f"   ❌ Lỗi: {e}")
    
    logger.info("")

if __name__ == "__main__":
    # Test API lấy giá
    test_api_calls()
    
    # Test Telegram
    success = test_telegram()
    
    logger.info("\n" + "=" * 60)
    if success:
        logger.info("✅ ĐỨC LẬP được tin nhắn Telegram!")
        logger.info("💡 Nếu vậy thì gold_bot.py sẽ hoạt động tốt")
    else:
        logger.error("❌ KHÔNG GỬI ĐƯỢC tin nhắn Telegram!")
        logger.error("💡 Hãy kiểm tra:")
        logger.error("   1. Bot Token: Chính xác không?")
        logger.error("   2. Chat ID: Chính xác không?")
        logger.error("   3. Bot được add vào chat chưa?")
        logger.error("   4. Kết nối mạng bình thường không?")
    logger.info("=" * 60)
