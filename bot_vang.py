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
    
    # === NGUỒN 1: GoldPrice.org — API miễn phí, không chặn ===
    try:
        res = requests.get("https://data-asg.goldprice.org/dbXRates/USD", timeout=15)
        data = res.json()
        gia_tg = round(data["items"][0]["xauPrice"], 2)
        
        # Giá tham khảo thị trường Việt Nam
        ty_gia_USD_VND = 25400
        gia_mua = round(gia_tg * ty_gia_USD_VND / 31.1035 * 1.01, -3)
        gia_ban = round(gia_tg * ty_gia_USD_VND / 31.1035 * 1.03, -3)
        
    except Exception as e:
        print(f"Lỗi lấy giá: {e}")
        return f"❌ *LỖI LẤY DỮ LIỆU*\nThời gian: {now}\nVui lòng thử lại sau."
    
    # === Tính % thay đổi ===
    tb = f"📊 *BÁO GIÁ VÀNG SJC — {now}*\n"
    tb += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    tb += f"💰 *GIÁ MUA:* {gia_mua:,.0f} VNĐ/chỉ\n"
    if gia_lan_truoc["mua"]:
        d_mua = gia_mua - gia_lan_truoc["mua"]
        p_mua = (d_mua / gia_lan_truoc["mua"]) * 100
        tb += f"   → {'📈 TĂNG' if d_mua>0 else '📉 GIẢM'} {abs(d_mua):,.0f} VNĐ ({p_mua:+.2f}%)\n"
    else:
        tb += "   → ⏹ Lần đầu theo dõi\n"
    
    tb += f"💰 *GIÁ BÁN:* {gia_ban:,.0f} VNĐ/chỉ\n"
    if gia_lan_truoc["ban"]:
        d_ban = gia_ban - gia_lan_truoc["ban"]
        p_ban = (d_ban / gia_lan_truoc["ban"]) * 100
        tb += f"   → {'📈 TĂNG' if d_ban>0 else '📉 GIẢM'} {abs(d_ban):,.0f} VNĐ ({p_ban:+.2f}%)\n"
    else:
        tb += "   → ⏹ Lần đầu theo dõi\n"
    
    tb += f"🌍 *GIÁ TG:* {gia_tg:,.2f} USD/ounce\n"
    if gia_lan_truoc["tg"]:
        d_tg = gia_tg - gia_lan_truoc["tg"]
        p_tg = (d_tg / gia_lan_truoc["tg"]) * 100
        tb += f"   → {'📈 TĂNG' if d_tg>0 else '📉 GIẢM'} {abs(d_tg):,.2f} USD ({p_tg:+.2f}%)\n"
    
    tb += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    tb += "🔄 Cập nhật mỗi 3 phút | Nguồn: GoldPrice.org\n"
    tb += "💡 *Giá Việt Nam là tham khảo, chênh lệch tùy đơn vị*"
    
    # Lưu giá lần này
    gia_lan_truoc["mua"] = gia_mua
    gia_lan_truoc["ban"] = gia_ban
    gia_lan_truoc["tg"] = gia_tg
    
    return tb

if __name__ == "__main__":
    noi_dung = lay_gia_vang()
    print(noi_dung)
    gui_telegram(noi_dung)
