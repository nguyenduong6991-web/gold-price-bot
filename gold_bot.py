import requests
import datetime

# === CẤU HÌNH ===
TELEGRAM_TOKEN = "8892269519:AAEtTq9n74OWVRN1CKmzIy5M1dfBbOJUToA"
CHAT_ID = "7176458499"

def lay_gia_vang():
    """Lấy giá vàng"""
    try:
        url = "https://api.npoint.io/9b4f4c8e6d7a5f4c3d2b1"
        res = requests.get(url, timeout=15)
        
        if res.status_code != 200:
            return 78500000, 79200000, 2450.50
        
        data = res.json()
        
        sjc_mua = data.get('sjc_buy', 78500000)
        sjc_ban = data.get('sjc_sell', 79200000)
        xau = data.get('xau', 2450.50)
        
        print(f"✅ SJC Mua: {sjc_mua:,} | Bán: {sjc_ban:,}")
        print(f"✅ XAU/USD: {xau}")
        
        return sjc_mua, sjc_ban, xau
        
    except Exception as e:
        print(f"⚠️ Dùng dữ liệu mẫu: {e}")
        return 78500000, 79200000, 2450.50

def gui_thong_bao_telegram(sjc_mua, sjc_ban, xau):
    """Gửi thông báo qua Telegram"""
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    
    tin_nhan = f"""
🪙 **GIÁ VÀNG HÀNG NGÀY** — {now}
━━━━━━━━━━━━━━━━━━━━━
🇻🇳 **Vàng SJC 9999**
💰 Mua vào: {sjc_mua:,} VNĐ/lượng
💰 Bán ra:  {sjc_ban:,} VNĐ/lượng
━━━━━━━━━━━━━━━━━━━━━
🌍 **Vàng thế giới**
📈 XAU/USD: {xau} USD/oz
━━━━━━━━━━━━━━━━━━━━━
🔄 Cập nhật mỗi 1 giờ
    """
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {
        "chat_id": CHAT_ID,
        "text": tin_nhan,
        "parse_mode": "Markdown"
    }
    
    try:
        res = requests.post(url, data=params, timeout=15)
        result = res.json()
        
        if result.get("ok"):
            print("✅ THÀNH CÔNG! Kiểm tra Telegram 📱")
            return True
        else:
            print(f"⚠️ Lỗi: {result.get('description')}")
            return False
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Đang xử lý...")
    sjc_mua, sjc_ban, xau = lay_gia_vang()
    gui_thong_bao_telegram(sjc_mua, sjc_ban, xau)

