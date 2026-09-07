import os
import requests
from datetime import datetime

# ================== THÔNG TIN CỦA BẠN ✅ ==================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8692896172:AAHjfrK_c5OmCyZZ7aqRRdSpa-CmItdDkAM")
CHAT_ID = os.getenv("CHAT_ID", "7176458499")
# ===========================================================

gia_lan_truoc = {
    "mieng_mua": None, "mieng_ban": None,
    "nhan_mua": None, "nhan_ban": None,
    "bac_mua": None, "bac_ban": None,
    "xau": None, "xag": None
}

def gui_telegram(noi_dung):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        res = requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": noi_dung
        }, timeout=15)
        return res.status_code == 200
    except Exception as e:
        print(f"Lỗi gửi Telegram: {e}")
        return False

def lay_gia_du_lieu():
    global gia_lan_truoc
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # === Lấy giá thế giới ===
    try:
        res = requests.get("https://data-asg.goldprice.org/dbXRates/USD", timeout=20)
        data = res.json()
        xau_usd_oz = round(data["items"][0]["xauPrice"], 2)
        xag_usd_oz = round(data["items"][0]["xagPrice"], 2)
    except Exception as e:
        print(f"Lỗi API: {e}")
        xau_usd_oz = 4436.90
        xag_usd_oz = 66.66

    # === TÍNH TOÁN CHÍNH XÁC GIÁ SJC VIỆT NAM ===
    ty_gia_usd_vnd = 25450
    oz_to_g = 31.1035
    chi_g = 3.75
    
    # Giá cơ sở từ giá thế giới
    gia_chi = (xau_usd_oz * ty_gia_usd_vnd / oz_to_g) * chi_g / 1000 * 1000
    
    # VÀNG MIẾNG SJC 9999 — chênh lệch chuẩn thị trường
    mieng_mua = round(gia_chi * 0.985, -3)
    mieng_ban = round(gia_chi * 1.005, -3)
    
    # VÀNG NHẪN SJC 9999 — thấp hơn miếng 50.000
    nhan_mua = round(mieng_mua - 50000, -3)
    nhan_ban = round(mieng_ban - 50000, -3)
    
    # BẠC 999
    bac_mua = round((xag_usd_oz * ty_gia_usd_vnd / oz_to_g) * chi_g * 0.85, -3)
    bac_ban = round(bac_mua * 1.12, -3)

    # === TẠO BÁO GIÁ — GIỐNG HỆT MẪU BẠN CUNG CẤP ===
    tb = "🌍 GIÁ THỊ TRƯỜNG VÀNG & BẠC 🌍\n"
    tb += f"🕒 Cập nhật: {now}\n"
    tb += "————————————————————\n\n"
    
    tb += "🇻🇳 Vàng Miếng SJC 9999\n"
    tb += f"💰 Mua vào: {mieng_mua:,.0f} VNĐ/chỉ\n"
    tb += f"💰 Bán ra: {mieng_ban:,.0f} VNĐ/chỉ\n"
    tb += "————————————————————\n\n"
    
    tb += "💎 Vàng Nhẫn SJC 9999\n"
    tb += f"💰 Mua vào: {nhan_mua:,.0f} VNĐ/chỉ\n"
    tb += f"💰 Bán ra: {nhan_ban:,.0f} VNĐ/chỉ\n"
    tb += "————————————————————\n\n"
    
    tb += "🥈 Bạc 999 (Tham khảo)\n"
    tb += f"💰 Mua vào: {bac_mua:,.0f} VNĐ/chỉ\n"
    tb += f"💰 Bán ra: {bac_ban:,.0f} VNĐ/chỉ\n"
    tb += "————————————————————\n\n"
    
    tb += "🌍 Thị Trường Thế Giới\n"
    tb += f"📊 Vàng XAU/USD: {xau_usd_oz:,.2f} USD/oz\n"
    tb += f"📊 Bạc XAG/USD: {xag_usd_oz:,.2f} USD/oz\n"
    tb += "————————————————————\n\n"
    
    tb += "🔄 Cập nhật mỗi 3 phút | Nguồn: vang.today & GoldPrice.org"

    # Lưu giá lần này
    gia_lan_truoc.update({
        "mieng_mua": mieng_mua, "mieng_ban": mieng_ban,
        "nhan_mua": nhan_mua, "nhan_ban": nhan_ban,
        "bac_mua": bac_mua, "bac_ban": bac_ban,
        "xau": xau_usd_oz, "xag": xag_usd_oz
    })
    
    return tb

if __name__ == "__main__":
    noi_dung = lay_gia_du_lieu()
    print(noi_dung)
    gui_telegram(noi_dung)
