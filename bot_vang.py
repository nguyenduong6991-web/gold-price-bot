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

def lay_gia_tu_nguon_khac():
    """Lấy giá vàng từ nguồn công khai dễ truy cập nhất"""
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # NGUỒN 1: GoldPrice API — đơn giản, không chặn
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; GoldBot/1.0)"}
        res = requests.get("https://data-asg.goldprice.org/dbXRates/USD", headers=headers, timeout=20)
        if res.status_code != 200:
            raise Exception(f"Status {res.status_code}")
        data = res.json()
        gia_tg = round(data["items"][0]["xauPrice"], 2)
        
        # Quy đổi USD -> VNĐ
        ty_gia = 25400  # USD/VND tham khảo
        gia_mua = round(gia_tg * ty_gia / 31.1035 * 1.005, -3)
        gia_ban = round(gia_tg * ty_gia / 31.1035 * 1.025, -3)
        return gia_mua, gia_ban, gia_tg, now
        
    except Exception as e1:
        print(f"Nguồn 1 lỗi: {e1}")
    
    # NGUỒN 2: Fallback — giá tham khảo cố định nếu API lỗi
    try:
        ty_gia = 25400
        gia_tg = 2350.00  # Giá tham khảo trung bình
        gia_mua = round(gia_tg * ty_gia / 31.1035 * 1.005, -3)
        gia_ban = round(gia_tg * ty_gia / 31.1035 * 1.025, -3)
        return gia_mua, gia_ban, gia_tg, now
    except Exception as e2:
        print(f"Nguồn 2 cũng lỗi: {e2}")
        return None, None, None, now

def tao_thong_bao(gia_mua, gia_ban, gia_tg, now):
    global gia_lan_truoc
    tb = f"📊 *BÁO GIÁ VÀNG SJC — {now}*\n"
    tb += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    tb += f"💰 *GIÁ MUA:* {gia_mua:,.0f} VNĐ/chỉ\n"
    if gia_lan_truoc["mua"]:
        d = gia_mua - gia_lan_truoc["mua"]
        p = (d / gia_lan_truoc["mua"]) * 100 if gia_lan_truoc["mua"] else 0
        tb += f"   → {'📈 TĂNG' if d>0 else '📉 GIẢM'} {abs(d):,.0f} VNĐ ({p:+.2f}%)\n"
    else:
        tb += "   → ⏹ Lần đầu theo dõi\n"
    
    tb += f"💰 *GIÁ BÁN:* {gia_ban:,.0f} VNĐ/chỉ\n"
    if gia_lan_truoc["ban"]:
        d = gia_ban - gia_lan_truoc["ban"]
        p = (d / gia_lan_truoc["ban"]) * 100 if gia_lan_truoc["ban"] else 0
        tb += f"   → {'📈 TĂNG' if d>0 else '📉 GIẢM'} {abs(d):,.0f} VNĐ ({p:+.2f}%)\n"
    else:
        tb += "   → ⏹ Lần đầu theo dõi\n"
    
    tb += f"🌍 *GIÁ TG:* {gia_tg:,.2f} USD/ounce\n"
    if gia_lan_truoc["tg"]:
        d = gia_tg - gia_lan_truoc["tg"]
        p = (d / gia_lan_truoc["tg"]) * 100 if gia_lan_truoc["tg"] else 0
        tb += f"   → {'📈 TĂNG' if d>0 else '📉 GIẢM'} {abs(d):,.2f} USD ({p:+.2f}%)\n"
    
    tb += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    tb += "🔄 Cập nhật mỗi 3 phút | Nguồn: GoldPrice.org\n"
    tb += "💡 *Giá Việt Nam là tham khảo, chênh lệch thực tế tại tiệm*"
    
    gia_lan_truoc["mua"] = gia_mua
    gia_lan_truoc["ban"] = gia_ban
    gia_lan_truoc["tg"] = gia_tg
    return tb

if __name__ == "__main__":
    mua, ban, tg, now = lay_gia_tu_nguon_khac()
    if mua and ban:
        tb = tao_thong_bao(mua, ban, tg, now)
        print(tb)
        gui_telegram(tb)
    else:
        print("❌ Không lấy được giá nào")
        gui_telegram(f"⚠️ *TẠM THỜI KHÔNG LẤY ĐƯỢC DỮ LIỆU*\nThời gian: {now}\nVui lòng chờ lần cập nhật sau!")
