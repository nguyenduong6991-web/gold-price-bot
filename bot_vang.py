import requests
from datetime import datetime

# ================== THÔNG TIN BOT ==================
BOT_TOKEN = "8869557187:AAEn9CJ3llOx5H5VhG9fBBubv0t-QvLmiuY"
CHAT_ID = "7176458499"
# ====================================================

# Lưu giá lần trước vào file tạm
TEP_GIA_CU = "gia_lan_truoc.txt"

def doc_gia_cu():
    try:
        with open(TEP_GIA_CU, "r", encoding="utf-8") as f:
            d = {}
            for dong in f:
                k,v = dong.strip().split("=")
                d[k] = float(v)
            return d
    except:
        return {
            "mieng_mua": None, "mieng_ban": None,
            "nhan_mua": None, "nhan_ban": None,
            "bac_mua": None, "bac_ban": None,
            "xau": None, "xag": None
        }

def luu_gia_moi(gia):
    with open(TEP_GIA_CU, "w", encoding="utf-8") as f:
        for k,v in gia.items():
            f.write(f"{k}={v}\n")

def gui_telegram(noi_dung):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        res = requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": noi_dung,
            "disable_web_page_preview": True
        }, timeout=20)
        return res.status_code == 200
    except Exception as e:
        print(f"Lỗi gửi: {e}")
        return False

def lay_gia():
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    xau_usd_oz = 4436.90
    xag_usd_oz = 66.66
    nguon = "Dự phòng"

    # Thử nhiều nguồn giá
    try:
        # Nguồn 1
        r = requests.get("https://data-asg.goldprice.org/dbXRates/USD", timeout=15,
                        headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200 and "items" in r.text:
            d = r.json()
            xau_usd_oz = round(d["items"][0]["xauPrice"], 2)
            xag_usd_oz = round(d["items"][0]["xagPrice"], 2)
            nguon = "GoldPrice.org"
    except:
        try:
            # Nguồn 2 dự phòng
            r2 = requests.get("https://api.gold-api.com/price/XAU", timeout=15)
            if r2.status_code == 200:
                d2 = r2.json()
                xau_usd_oz = round(float(d2.get("price", xau_usd_oz)), 2)
                nguon = "Gold-API.com"
        except:
            pass

    # Tính giá VNĐ
    ty_gia = 25400
    oz_gam = 31.1035
    chi = 3.75
    gia_chi = (xau_usd_oz * ty_gia / oz_gam) * chi
    
    mieng_mua = round(gia_chi * 0.99, -3)
    mieng_ban = round(gia_chi * 1.01, -3)
    nhan_mua = round(mieng_mua - 50000, -3)
    nhan_ban = round(mieng_ban - 50000, -3)
    
    gia_bac = (xag_usd_oz * ty_gia / oz_gam) * chi
    bac_mua = round(gia_bac * 0.92, -3)
    bac_ban = round(gia_bac * 1.08, -3)

    gia_moi = {
        "mieng_mua": mieng_mua, "mieng_ban": mieng_ban,
        "nhan_mua": nhan_mua, "nhan_ban": nhan_ban,
        "bac_mua": bac_mua, "bac_ban": bac_ban,
        "xau": xau_usd_oz, "xag": xag_usd_oz
    }
    gia_cu = doc_gia_cu()

    # Tạo tin nhắn
    tb = f"🌍 GIÁ THỊ TRƯỜNG VÀNG & BẠC 🌍\n🕒 {now}\n📡 Nguồn: {nguon}\n"
    tb += "————————————————————\n\n"
    
    tb += "🇻🇳 Vàng Miếng SJC 9999\n"
    tb += f"💰 Mua vào: {mieng_mua:,.0f} VNĐ/chỉ"
    if gia_cu["mieng_mua"] is not None:
        d = mieng_mua - gia_cu["mieng_mua"]
        tb += f"  {'📈' if d>0 else '📉'} {d:+,.0f}"
    tb += f"\n💰 Bán ra: {mieng_ban:,.0f} VNĐ/chỉ"
    if gia_cu["mieng_ban"] is not None:
        d = mieng_ban - gia_cu["mieng_ban"]
        tb += f"  {'📈' if d>0 else '📉'} {d:+,.0f}"
    
    tb += "\n————————————————————\n💎 Vàng Nhẫn SJC 9999\n"
    tb += f"💰 Mua vào: {nhan_mua:,.0f} VNĐ/chỉ"
    if gia_cu["nhan_mua"] is not None:
        d = nhan_mua - gia_cu["nhan_mua"]
        tb += f"  {'📈' if d>0 else '📉'} {d:+,.0f}"
    tb += f"\n💰 Bán ra: {nhan_ban:,.0f} VNĐ/chỉ"
    if gia_cu["nhan_ban"] is not None:
        d = nhan_ban - gia_cu["nhan_ban"]
        tb += f"  {'📈' if d>0 else '📉'} {d:+,.0f}"
    
    tb += "\n————————————————————\n🥈 Bạc 999 (Tham khảo)\n"
    tb += f"💰 Mua vào: {bac_mua:,.0f} VNĐ/chỉ"
    if gia_cu["bac_mua"] is not None:
        d = bac_mua - gia_cu["bac_mua"]
        tb += f"  {'📈' if d>0 else '📉'} {d:+,.0f}"
    tb += f"\n💰 Bán ra: {bac_ban:,.0f} VNĐ/chỉ"
    if gia_cu["bac_ban"] is not None:
        d = bac_ban - gia_cu["bac_ban"]
        tb += f"  {'📈' if d>0 else '📉'} {d:+,.0f}"
    
    tb += "\n————————————————————\n🌍 Thị Trường Thế Giới\n"
    tb += f"📊 Vàng XAU/USD: {xau_usd_oz:,.2f} USD/oz"
    if gia_cu["xau"] is not None:
        d = xau_usd_oz - gia_cu["xau"]
        tb += f"  {'📈' if d>0 else '📉'} {d:+,.2f}"
    tb += f"\n📊 Bạc XAG/USD: {xag_usd_oz:,.2f} USD/oz"
    if gia_cu["xag"] is not None:
        d = xag_usd_oz - gia_cu["xag"]
        tb += f"  {'📈' if d>0 else '📉'} {d:+,.2f}"
    
    tb += "\n————————————————————\n🔄 Cập nhật mỗi 2 giờ"

    luu_gia_moi(gia_moi)
    return tb

if __name__ == "__main__":
    noi_dung = lay_gia()
    gui_telegram(noi_dung)
    print("✅ Đã gửi!")
