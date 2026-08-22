import requests
import datetime

# === CẤU HÌNH ===
TELEGRAM_TOKEN = "8892269519:AAEtTq9n74OWVRN1CKmzIy5M1dfBbOJUToA"
CHAT_ID = "7176458499"

def lay_gia_vang():
    try:
        # Lấy giá vàng từ API SJC
        url = "https://api.btmc.vn/api/price/gold/sjc"
        response = requests.get(url, timeout=15)
        data = response.json()
        
        # Trích xuất dữ liệu (đơn vị: VND/ lượng → chuyển đổi VND/chỉ)
        gia_mua = data.get('buy_price', 0)  # giá mua vào / lượng
        gia_ban = data.get('sell_price', 0) # giá bán ra / lượng
        
        # 1 lượng = 10 chỉ → chia cho 10 để ra giá / chỉ
        gia_mua_chi = gia_mua / 10
        gia_ban_chi = gia_ban / 10
        
        return {
            "gia_mua": gia_mua_chi,
            "gia_ban": gia_ban_chi,
            "nguon": "SJC - BTMC",
            "thoi_gian": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
    except Exception as e:
        print(f"Lỗi lấy giá: {e}")
        return None

def gui_telegram(thong_tin):
    if not thong_tin:
        noi_dung = "⚠️ Không thể lấy dữ liệu giá vàng. Vui lòng thử lại sau!"
    else:
        noi_dung = f"""🪙 **BÁO GIÁ VÀNG SJC** 🪙
⏰ Thời gian: {thong_tin['thoi_gian']}
📌 Nguồn: {thong_tin['nguon']}

💰 **Giá Mua Vào:** {thong_tin['gia_mua']:,.0f} VNĐ/chỉ
💰 **Giá Bán Ra:** {thong_tin['gia_ban']:,.0f} VNĐ/chỉ

---
🔄 Cập nhật mỗi giờ đúng phút 00
"""
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": noi_dung,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=data)
    print("Đã gửi tin nhắn:", response.status_code)

if __name__ == "__main__":
    thong_tin = lay_gia_vang()
    gui_telegram(thong_tin)
