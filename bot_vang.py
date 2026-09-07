import os
import requests
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN", "8692896172:AAHjfrK_c5OmCyZZ7aqRRdSpa-CmItdDkAM")
CHAT_ID = os.getenv("CHAT_ID", "7176458499")

def gui_telegram(noi_dung):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        res = requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": noi_dung,
            "parse_mode": "Markdown"
        }, timeout=15)
        if res.status_code == 200:
            print("✅ ĐÃ GỬI TIN NHẮN THÀNH CÔNG!")
            return True
        else:
            print(f"❌ LỖI TELEGRAM: {res.text}")
            return False
    except Exception as e:
        print(f"❌ LỖI KẾT NỐI: {e}")
        return False

def lay_gia_vang():
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    try:
        # Lấy giá từ SJC
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get("https://sjc.com.vn/Service/GetGoldPrice.ashx", headers=headers, timeout=20)
        data = res.json()
        mua, ban = None, None
        for item in data:
            if item.get("Type") == "SJC":
                mua = float(item["BuyPrice"].replace(",", "").replace(".", ""))
                ban = float(item["SellPrice"].replace(",", "").replace(".", ""))
                break
        if not mua:
            raise ValueError("Không tìm thấy giá SJC")
        
        # Lấy giá thế giới
        tg = 0
        try:
            d = requests.get("https://data-asg.goldprice.org/dbXRates/USD", timeout=15).json()
            tg = round(d["items"][0]["xauPrice"], 2)
        except: pass

        # Tạo nội dung báo giá
        tb = f"📊 *BÁO GIÁ VÀNG SJC — {now}*\n"
        tb += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        tb += f"💰 MUA: {mua:,.0f} VNĐ/chỉ\n"
        tb += f"💰 BÁN: {ban:,.0f} VNĐ/chỉ\n"
        if tg > 0:
            tb += f"🌍 TG: {tg:,.2f} USD/ounce\n"
        tb += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        tb += "🔄 Cập nhật tự động mỗi 3 phút"
        return tb
    except Exception as e:
        return f"❌ *LỖI LẤY GIÁ:* {e}"

if __name__ == "__main__":
    print("🤖 ĐANG LẤY GIÁ VÀNG...")
    noi_dung = lay_gia_vang()
    print("Nội dung:", noi_dung)
    gui_telegram(noi_dung)
