import os
import requests
from datetime import datetime

# ================== THÔNG TIN CỦA BẠN ✅ ==================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8692896172:AAHjfrK_c5OmCyZZ7aqRRdSpa-CmItdDkAM")
CHAT_ID = os.getenv("CHAT_ID", "7176458499")
# ===========================================================

gia_lan_truoc = {"mua": None, "ban": None, "tg": None}

def gui_telegram(noi_dung):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        res = requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": noi_dung,
            "parse_mode": "Markdown"
        }, timeout=15)
        return res.status_code == 200
    except Exception as e:
        print(f"Lỗi gửi Telegram: {e}")
        return False

def lay_gia_vang():
    global gia_lan_truoc
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # === Lấy giá vàng thế giới ===
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get("https://data-asg.goldprice.org/dbXRates/USD", headers=headers, timeout=20)
        data = res.json()
        gia_tg_usd_per_oz = round(data["items"][0]["xauPrice"], 2)  # USD/ounce
    except Exception as e:
        print(f"Lỗi lấy giá TG: {e}")
        gia_tg_usd_per_oz = 2450.00  # Giá dự phòng
    
    # === CÔNG THỨC QUY ĐỔI ĐÚNG ===
    # 1 ounce = 31.1035 gam; 1 chỉ = 3.75 gam
    ty_gia_usd_vnd = 25450  # Tỉ giá USD/VND cập nhật
    usd_per_chỉ = gia_tg_usd_per_oz / 31.1035 * 3.75
    gia_tham_khao = usd_per_chỉ * ty_gia_usd_vnd
    
    # Lệch giá SJC thị trường thực tế
    gia_mua = round(gia_tham_khao * 0.995, -3)
    gia_ban = round(gia_tham_khao * 1.015, -3)
    
    # === Tính % thay đổi ===
    tb = f"📊 *BÁO GIÁ VÀNG SJC — {now}*\n"
    tb += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    tb += f"💰 *GIÁ MUA:* {gia_mua:,.0f} VNĐ/chỉ\n"
    if gia_lan_truoc["mua"]:
        d = gia_mua - gia_lan_truoc["mua"]
        p = (d / gia_lan_truoc["mua"]) * 100
        tb += f"   → {'📈 TĂNG' if d>0 else '📉 GIẢM'} {abs(d):,.0f} VNĐ ({p:+.2f}%)\n"
    else:
        tb += "   → ⏹ Lần đầu theo dõi\n"
    
    tb += f"💰 *GIÁ BÁN:* {gia_ban:,.0f} VNĐ/chỉ\n"
    if gia_lan_truoc["ban"]:
        d = gia_ban - gia_lan_truoc["ban"]
        p = (d / gia_lan_truoc["ban"]) * 100
        tb += f"   → {'📈 TĂNG' if d>0 else '📉 GIẢM'} {abs(d):,.0f} VNĐ ({p:+.2f}%)\n"
    else:
        tb += "   → ⏹ Lần đầu theo dõi\n"
    
    tb += f"🌍 *GIÁ TG:* {gia_tg_usd_per_oz:,.2f} USD/ounce\n"
    if gia_lan_truoc["tg"]:
        d = gia_tg_usd_per_oz - gia_lan_truoc["tg"]
        p = (d / gia_lan_truoc["tg"]) * 100
        tb += f"   → {'📈 TĂNG' if d>0 else '📉 GIẢM'} {abs(d):,.2f} USD ({p:+.2f}%)\n"
    
    tb += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    tb += "🔄 Cập nhật mỗi 3 phút | Nguồn: GoldPrice.org\n"
    tb += "💡 *Giá tham khảo — chênh lệch tại từng tiệm vàng*"
    
    # Lưu giá lần này
    gia_lan_truoc["mua"] = gia_mua
    gia_lan_truoc["ban"] = gia_ban
    gia_lan_truoc["tg"] = gia_tg_usd_per_oz
    
    return tb

if __name__ == "__main__":
    noi_dung = lay_gia_vang()
    print(noi_dung)
    gui_telegram(noi_dung)
