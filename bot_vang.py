import os
import requests
from datetime import datetime

# ================== THÔNG TIN BOT ==================
# Kiểm tra lại Token: nói @BotFather gửi /token để xác nhận
BOT_TOKEN = "8692896172:AAHjfrK_c5OmCyZZ7aqRRdSpa-CmItdDkAM"
CHAT_ID = "7176458499"
# ====================================================

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
            "text": noi_dung,
            "disable_web_page_preview": True
        }, timeout=20)
        print(f"📤 Mã trả về: {res.status_code}")
        print(f"📤 Phản hồi: {res.text[:200]}")
        return res.status_code == 200
    except Exception as e:
        print(f"❌ Lỗi kết nối: {str(e)}")
        return False

def lay_gia_tu_api():
    global gia_lan_truoc
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    xau_usd_oz = 4436.90
    xag_usd_oz = 66.66
    
    # Thử nhiều nguồn khác nhau để không bị chặn
    nguon_hop_le = False
    try:
        # Nguồn 1
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get("https://data-asg.goldprice.org/dbXRates/USD", headers=headers, timeout=15)
        if res.status_code == 200 and "items" in res.text:
            data = res.json()
            xau_usd_oz = round(data["items"][0]["xauPrice"], 2)
            xag_usd_oz = round(data["items"][0]["xagPrice"], 2)
            nguon_hop_le = True
            print(f"✅ Nguồn 1 thành công: XAU={xau_usd_oz}")
    except Exception as e:
        print(f"⚠️ Nguồn 1 lỗi: {str(e)}")
    
    if not nguon_hop_le:
        try:
            # Nguồn 2 dự phòng
            res2 = requests.get("https://api.gold-api.com/price/XAU", timeout=15)
            if res2.status_code == 200:
                d2 = res2.json()
                xau_usd_oz = round(float(d2.get("price", 4436.90)), 2)
                print(f"✅ Nguồn 2 thành công: XAU={xau_usd_oz}")
        except Exception as e2:
            print(f"⚠️ Nguồn 2 cũng lỗi: {str(e2)} — dùng giá dự phòng")

    # Tính toán
    ty_gia_usd_vnd = 25400
    oz_to_gam = 31.1035
    chi_gam = 3.75
    
    gia_chi_vnd = (xau_usd_oz * ty_gia_usd_vnd / oz_to_gam) * chi_gam
    
    mieng_mua = round(gia_chi_vnd * 0.99, -3)
    mieng_ban = round(gia_chi_vnd * 1.01, -3)
    nhan_mua = round(mieng_mua - 50000, -3)
    nhan_ban = round(mieng_ban - 50000, -3)
    
    gia_bac_chi = (xag_usd_oz * ty_gia_usd_vnd / oz_to_gam) * chi_gam
    bac_mua = round(gia_bac_chi * 0.92, -3)
    bac_ban = round(gia_bac_chi * 1.08, -3)

    # Tạo tin nhắn
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

    gia_lan_truoc.update({
        "mieng_mua": mieng_mua, "mieng_ban": mieng_ban,
        "nhan_mua": nhan_mua, "nhan_ban": nhan_ban,
        "bac_mua": bac_mua, "bac_ban": bac_ban,
        "xau": xau_usd_oz, "xag": xag_usd_oz
    })
    
    return tb

if __name__ == "__main__":
    print("🚀 Bắt đầu chạy bot...")
    noi_dung = lay_gia_tu_api()
    print("📩 Đang gửi đến Telegram...")
    thanh_cong = gui_telegram(noi_dung)
    if thanh_cong:
        print("=== GỬI THÀNH CÔNG ===")
    else:
        print("=== GỬI THẤT BẠI ===")
        print("⚠️ Kiểm tra:")
        print("1. Gửi /start cho bot trên Telegram chưa?")
        print("2. Token có đúng không? Hỏi @BotFather gửi /token")
        print(f"3. Chat ID: {CHAT_ID}")
