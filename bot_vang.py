import os
import requests
from telegram import Bot
from datetime import datetime

# ================== THÔNG TIN CỦA BẠN ✅ ==================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8692896172:AAHjfrK_c5OmCyZZ7aqRRdSpa-CmItdDkAM")
CHAT_ID = os.getenv("CHAT_ID", "7176458499")
# ===========================================================

gia_cu = {"vang_mua": None, "vang_ban": None, "gia_the_gioi": None}

def lay_gia_vang():
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get("https://sjc.com.vn/Service/GetGoldPrice.ashx", headers=headers, timeout=20)
        data = res.json()
        mua, ban = None, None
        for item in data:
            if item.get("Type") == "SJC":
                mua = float(item["BuyPrice"].replace(",", "").replace(".", "")) * 10
                ban = float(item["SellPrice"].replace(",", "").replace(".", "")) * 10
                break
        if not mua or not ban: raise ValueError("Không tìm thấy SJC")
        tg = lay_gia_tg()
        print(f"✅ [{now}] MUA: {mua:,} | BÁN: {ban:,} | TG: {tg}")
        return {"mua": mua, "ban": ban, "tg": tg, "now": now}
    except Exception as e:
        print(f"⚠️ SJC lỗi: {e} → thử PNJ")
        try:
            d = requests.get("https://api.pnj.vn/public/price", timeout=20).json()
            mua = float(d["gold"]["SJC"]["buy"])
            ban = float(d["gold"]["SJC"]["sell"])
            tg = float(d["gold"]["world_price"])
            print(f"✅ [{now}] PNJ — MUA: {mua:,} | BÁN: {ban:,}")
            return {"mua": mua, "ban": ban, "tg": tg, "now": now}
        except Exception as e2:
            print(f"❌ PNJ cũng lỗi: {e2}")
            return None

def lay_gia_tg():
    try:
        d = requests.get("https://data-asg.goldprice.org/dbXRates/USD", timeout=15).json()
        return round(d["items"][0]["xauPrice"], 2)
    except:
        return 0

def tao_thong_bao(moi):
    global gia_cu
    tb = f"📊 **BÁO GIÁ VÀNG SJC — {moi['now']}**\n"
    tb += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    tb += f"💰 GIÁ MUA: {moi['mua']:,} VNĐ/lượng\n"
    if gia_cu["vang_mua"]:
        hieu = moi["mua"] - gia_cu["vang_mua"]
        pct = (hieu / gia_cu["vang_mua"]) * 100
        tb += f"   → {'📈 TĂNG' if hieu>0 else '📉 GIẢM'} {abs(hieu):,} VNĐ ({pct:+.3f}%)\n"
    else: tb += "   → ⏹ Lần đầu theo dõi\n"
    tb += f"💰 GIÁ BÁN: {moi['ban']:,} VNĐ/lượng\n"
    if gia_cu["vang_ban"]:
        hieu = moi["ban"] - gia_cu["vang_ban"]
        pct = (hieu / gia_cu["vang_ban"]) * 100
        tb += f"   → {'📈 TĂNG' if hieu>0 else '📉 GIẢM'} {abs(hieu):,} VNĐ ({pct:+.3f}%)\n"
    else: tb += "   → ⏹ Lần đầu theo dõi\n"
    tb += f"🌍 GIÁ TG: {moi['tg']:,} USD/ounce\n"
    if gia_cu["gia_the_gioi"]:
        hieu = moi["tg"] - gia_cu["gia_the_gioi"]
        pct = (hieu / gia_cu["gia_the_gioi"]) * 100
        tb += f"   → {'📈 TĂNG' if hieu>0 else '📉 GIẢM'} {abs(hieu):.2f} USD ({pct:+.3f}%)\n"
    tb += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    gia_cu.update({"vang_mua": moi["mua"], "vang_ban": moi["ban"], "gia_the_gioi": moi["tg"]})
    return tb

def gui_den_telegram(gia_moi):
    bot = Bot(token=BOT_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=tao_thong_bao(gia_moi), parse_mode="Markdown")

if __name__ == "__main__":
    print("🤖 BOT ĐANG LẤY GIÁ VÀNG...")
    gia = lay_gia_vang()
    if gia:
        gui_den_telegram(gia)
        print("✅ ĐÃ GỬI BÁO GIÁ LÊN TELEGRAM THÀNH CÔNG!")
    else:
        print("❌ LỖI: Không lấy được giá vàng!")
