import os
import requests
from datetime import datetime

# ================== THÔNG TIN BOT ==================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8692896172:AAHjfrK_c5OmCyZZ7aqRRdSpa-CmItdDkAM")
CHAT_ID = os.getenv("CHAT_ID", "7176458499")
# ====================================================

# Lưu giá lần trước để so sánh
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
        print(f"Gửi thành công: {res.status_code}")
        return res.status_code == 200
    except Exception as e:
        print(f"Lỗi gửi Telegram: {e}")
        return False

def lay_gia_tu_api():
    global gia_lan_truoc
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # === LẤY GIÁ THẾ GIỚI MỖI LẦN CHẠY ===
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get("https://data-asg.goldprice.org/dbXRates/USD", headers=headers, timeout=20)
        data = res.json()
        xau_usd_oz = round(data["items"][0]["xauPrice"], 2)
        xag_usd_oz = round(data["items"][0]["xagPrice"], 2)
        print(f"✅ Lấy giá mới: XAU={xau_usd_oz} | XAG={xag_usd_oz}")
    except Exception as e:
        print(f"⚠️ API lỗi: {e} — dùng giá dự phòng")
        xau_usd_oz = 4436.90
        xag_usd_oz = 66.66

    # === TÍNH TOÁN ĐƠN VỊ VIỆT NAM ===
    ty_gia_usd_vnd = 25400
    oz_to_gam = 31.1035
    chi_gam = 3.75
    
    gia_chi_vnd = (xau_usd_oz * ty_gia_usd_vnd / oz_to_gam) * chi_gam
    
    # VÀNG MIẾNG SJC
    mieng_mua = round(gia_chi_vnd * 0.99, -3)
    mieng_ban = round(gia_chi_vnd * 1.01, -3)
    
    # VÀNG NHẪN SJC
    nhan_mua = round(mieng_mua - 50000, -3)
    nhan_ban = round(mieng_ban - 50000, -3)
    
    # BẠC 999
    gia_bac_chi = (xag_usd_oz * ty_gia_usd_vnd / oz_to_gam) * chi_gam
    bac_mua = round(gia_bac_chi * 0.92, -3)
    bac_ban = round(gia_bac_chi * 1.08, -3)

    # === TẠO BÁO GIÁ ĐÚNG ĐỊNH DẠNG ===
    tb = "🌍 GIÁ THỊ TRƯỜNG VÀNG & BẠC 🌍\n"
    tb += f"🕒 Cập nhật: {now}\n"
    tb += "————————————————————\n\n"
    
    tb += "🇻🇳 Vàng Miếng SJC 9999\n"
    tb += f"💰 Mua vào: {mieng_mua:,.0f} VNĐ/chỉ"
    if gia_lan_truoc["mieng_mua"] is not None:
        d = mieng_mua - gia_lan_truoc["mieng_mua"]
        tb += f"  {'📈' if d>0 else '📉'} {d:+,.0f}"
    tb += "\n"
    tb += f"💰 Bán ra: {mieng_ban:,.0f} VNĐ/chỉ"
    if gia_lan_truoc["mieng_ban"] is not None:
        d = mieng_ban - gia_lan_truoc["mieng_ban"]
        tb += f"  {'📈' if d>0 else '📉'} {d:+,.0f}"
    tb += "\n————————————————————\n\n"
    
    tb += "💎 Vàng Nhẫn SJC 9999\n"
    tb += f"💰 Mua vào: {nhan_mua:,.0f} VNĐ/chỉ"
    if gia_lan_truoc["nhan_mua"] is not None:
        d = nhan_mua - gia_lan_truoc["nhan_mua"]
        tb += f"  {'📈' if d>0 else '📉'} {d:+,.0f}"
    tb += "\n"
    tb += f"💰 Bán ra: {nhan_ban:,.0f} VNĐ/chỉ"
    if gia_lan_truoc["nhan_ban"] is not None:
        d = nhan_ban - gia_lan_truoc["nhan_ban"]
        tb += f"  {'📈' if d>0 else '📉'} {d:+,.0f}"
    tb += "\n————————————————————\n\n"
    
    tb += "🥈 Bạc 999 (Tham khảo)\n"
    tb += f"💰 Mua vào: {bac_mua:,.0f} VNĐ/chỉ"
    if gia_lan_truoc["bac_mua"] is not None:
        d = bac_mua - gia_lan_truoc["bac_mua"]
        tb += f"  {'📈' if d>0 else '📉'} {d:+,.0f}"
    tb += "\n"
    tb += f"💰 Bán ra: {bac_ban:,.0f} VNĐ/chỉ"
    if gia_lan_truoc["bac_ban"] is not None:
        d = bac_ban - gia_lan_truoc["bac_ban"]
        tb += f"  {'📈' if d>0 else '📉'} {d:+,.0f}"
    tb += "\n————————————————————\n\n"
    
    tb += "🌍 Thị Trường Thế Giới\n"
    tb += f"📊 Vàng XAU/USD: {xau_usd_oz:,.2f} USD/oz"
    if gia_lan_truoc["xau"] is not None:
        d = xau_usd_oz - gia_lan_truoc["xau"]
        tb += f"  {'📈' if d>0 else '📉'} {d:+,.2f}"
    tb += "\n"
    tb += f"📊 Bạc XAG/USD: {xag_usd_oz:,.2f} USD/oz"
    if gia_lan_truoc["xag"] is not None:
        d = xag_usd_oz - gia_lan_truoc["xag"]
        tb += f"  {'📈' if d>0 else '📉'} {d:+,.2f}"
    tb += "\n————————————————————\n\n"
    
    tb += "🔄 Cập nhật mỗi 2 giờ | Nguồn: GoldPrice.org & vang.today"

    # Lưu giá lần này
    gia_lan_truoc.update({
        "mieng_mua": mieng_mua, "mieng_ban": mieng_ban,
        "nhan_mua": nhan_mua, "nhan_ban": nhan_ban,
        "bac_mua": bac_mua, "bac_ban": bac_ban,
        "xau": xau_usd_oz, "xag": xag_usd_oz
    })
    
    return tb

if __name__ == "__main__":
    noi_dung = lay_gia_tu_api()
    print(noi_dung)
    gui_telegram(noi_dung)
