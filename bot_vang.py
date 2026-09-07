import os
import requests
from datetime import datetime

# ================== THÔNG TIN CỦA BẠN ✅ ==================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8692896172:AAHjfrK_c5OmCyZZ7aqRRdSpa-CmItdDkAM")
CHAT_ID = os.getenv("CHAT_ID", "7176458499")
# ===========================================================

# Lưu giá lần trước để tính % thay đổi
gia_lan_truoc = {"mua": None, "ban": None, "tg": None}

def gui_telegram(noi_dung):
    """Gửi tin nhắn đến Telegram trực tiếp qua API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        res = requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": noi_dung,
            "parse_mode": "Markdown"
        }, timeout=15)
        if res.status_code == 200:
            print("✅ ĐÃ GỬI TIN THÀNH CÔNG!")
            return True
        else:
            print(f"❌ LỖI TELEGRAM: {res.text}")
            return False
    except Exception as e:
        print(f"❌ LỖI KẾT NỐI TELEGRAM: {e}")
        return False

def lay_gia_tu_pnj():
    """Lấy giá từ PNJ — ổn định & đáng tin cậy hơn"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get("https://api.pnj.vn/public/price", headers=headers, timeout=20)
        res.raise_for_status()
        data = res.json()
        mua = float(data["gold"]["SJC"]["buy"])
        ban = float(data["gold"]["SJC"]["sell"])
        tg = float(data["gold"]["world_price"])
        return round(mua, 0), round(ban, 0), round(tg, 2)
    except Exception as e:
        print(f"⚠️ PNJ lỗi: {e}")
        return None, None, None

def lay_gia_vang():
    """Lấy giá với nhiều nguồn dự phòng"""
    global gia_lan_truoc
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # Thử PNJ trước
    mua, ban, tg = lay_gia_tu_pnj()
    
    if not mua or not ban:
        return f"❌ *KHÔNG LẤY ĐƯỢC GIÁ VÀNG*\nThời gian: {now}\nVui lòng thử lại sau."
    
    # Tính % thay đổi
    tb = f"📊 *BÁO GIÁ VÀNG SJC — {now}*\n"
    tb += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    tb += f"💰 *GIÁ MUA:* {mua:,.0f} VNĐ/chỉ\n"
    if gia_lan_truoc["mua"]:
        d_mua = mua - gia_lan_truoc["mua"]
        p_mua = (d_mua / gia_lan_truoc["mua"]) * 100
        tb += f"   → {'📈 TĂNG' if d_mua>0 else '📉 GIẢM'} {abs(d_mua):,.0f} VNĐ ({p_mua:+.2f}%)\n"
    else:
        tb += "   → ⏹ Lần đầu theo dõi\n"
    
    tb += f"💰 *GIÁ BÁN:* {ban:,.0f} VNĐ/chỉ\n"
    if gia_lan_truoc["ban"]:
        d_ban = ban - gia_lan_truoc["ban"]
        p_ban = (d_ban / gia_lan_truoc["ban"]) * 100
        tb += f"   → {'📈 TĂNG' if d_ban>0 else '📉 GIẢM'} {abs(d_ban):,.0f} VNĐ ({p_ban:+.2f}%)\n"
    else:
        tb += "   → ⏹ Lần đầu theo dõi\n"
    
    tb += f"🌍 *GIÁ TG:* {tg:,.2f} USD/ounce\n"
    if gia_lan_truoc["tg"]:
        d_tg = tg - gia_lan_truoc["tg"]
        p_tg = (d_tg / gia_lan_truoc["tg"]) * 100
        tb += f"   → {'📈 TĂNG' if d_tg>0 else '📉 GIẢM'} {abs(d_tg):,.2f} USD ({p_tg:+.2f}%)\n"
    
    tb += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🔄 Cập nhật mỗi 3 phút | Nguồn: PNJ"
    
    # Cập nhật giá cũ
    gia_lan_truoc["mua"] = mua
    gia_lan_truoc["ban"] = ban
    gia_lan_truoc["tg"] = tg
    
    return tb

if __name__ == "__main__":
    print("🤖 ĐANG LẤY GIÁ VÀNG...")
    noi_dung = lay_gia_vang()
    print("NỘI DUNG:", noi_dung)
    gui_telegram(noi_dung)
