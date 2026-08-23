import requests
import datetime

# === CẤU HÌNH ===
TELEGRAM_TOKEN = "8892269519:AAEtTq9n74OWVRN1CKmzIy5M1dfBbOJUToA"
CHAT_ID = "7176458499"

def lay_gia_vang():
    # === GIÁ VÀNG SJC ===
    gia_mua_luong = 78500000  # VNĐ/lượng
    gia_ban_luong = 79200000  # VNĐ/lượng
    
    # Chuyển đổi: 1 lượng = 10 chỉ
    gia_mua_chi = gia_mua_luong / 10
    gia_ban_chi = gia_ban_luong / 10
    
    # === GIÁ BẠC ===
    # Giá bạc tham khảo SJC / thị trường
    gia_bac_mua_luong = 520000   # VNĐ/lượng
    gia_bac_ban_luong = 580000   # VNĐ/lượng
    
    # Chuyển đổi sang VNĐ/chỉ
    gia_bac_mua_chi = gia_bac_mua_luong / 10
    gia_bac_ban_chi = gia_bac_ban_luong / 10
    
    return {
        # Vàng
        "gia_mua_chi": gia_mua_chi,
        "gia_ban_chi": gia_ban_chi,
        # Bạc
        "gia_bac_mua_chi": gia_bac_mua_chi,
        "gia_bac_ban_chi": gia_bac_ban_chi,
        # Thế giới
        "gia_the_gioi": 2450.5,
        "gia_bac_the_gioi": 29.50,  # XAG/USD
        "thoi_gian": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

def gui_telegram(thong_tin):
    noi_dung = f"""🪙 **GIÁ VÀNG & BẠC HÀNG NGÀY** 🪙
🕒 {thong_tin['thoi_gian']}
━━━━━━━━━━━━━━━━━━━━━
🇻🇳 **Vàng SJC 9999**
💰 Giá Mua Vào: **{thong_tin['gia_mua_chi']:,.0f} VNĐ/chỉ**
💰 Giá Bán Ra: **{thong_tin['gia_ban_chi']:,.0f} VNĐ/chỉ**
━━━━━━━━━━━━━━━━━━━━━
🥈 **Bạc 999**
💰 Giá Mua Vào: **{thong_tin['gia_bac_mua_chi']:,.0f} VNĐ/chỉ**
💰 Giá Bán Ra: **{thong_tin['gia_bac_ban_chi']:,.0f} VNĐ/chỉ**
━━━━━━━━━━━━━━━━━━━━━
🌍 **Thị trường thế giới**
📈 Vàng XAU/USD: {thong_tin['gia_the_gioi']} USD/oz
📈 Bạc XAG/USD: {thong_tin['gia_bac_the_gioi']} USD/oz
━━━━━━━━━━━━━━━━━━━━━
🔄 Cập nhật mỗi giờ đúng phút 00
"""
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": noi_dung,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=data)
    print("Đã gửi:", response.status_code)

if __name__ == "__main__":
    thong_tin = lay_gia_vang()
    gui_telegram(thong_tin)
