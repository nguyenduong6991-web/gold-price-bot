import requests
import telegram
from telegram.ext import Updater, CommandHandler
from datetime import datetime

# ================== THÔNG TIN CỦA BẠN — ĐÃ ĐIỀN SẴN ✅ ==================
BOT_TOKEN = "8692896172:AAHjfrK_c5OmCyZZ7aqRRdSpa-CmItdDkAM"
CHAT_ID = "7176458499"
UPDATE_INTERVAL = 180  # Cập nhật mỗi 3 phút
# =========================================================================

gia_cu = {
    "vang_mua": None,
    "vang_ban": None,
    "gia_the_gioi": None
}

def lay_gia_vang():
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    try:
        # Lấy giá từ SJC
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get("https://sjc.com.vn/Service/GetGoldPrice.ashx", headers=headers, timeout=20)
        data = res.json()
        mua, ban = None, None
        for item in data:
            if item.get("Type") == "SJC":
                mua = float(item["BuyPrice"].replace(",", "").replace(".", "")) * 10
                ban = float(item["SellPrice"].replace(",", "").replace(".", "")) * 10
                break
        if not mua or not ban:
            raise ValueError("Không tìm thấy giá SJC")
        # Lấy giá thế giới
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
    else:
        tb += "   → ⏹ Lần đầu theo dõi\n"
    tb += f"💰 GIÁ BÁN: {moi['ban']:,} VNĐ/lượng\n"
    if gia_cu["vang_ban"]:
        hieu = moi["ban"] - gia_cu["vang_ban"]
        pct = (hieu / gia_cu["vang_ban"]) * 100
        tb += f"   → {'📈 TĂNG' if hieu>0 else '📉 GIẢM'} {abs(hieu):,} VNĐ ({pct:+.3f}%)\n"
    else:
        tb += "   → ⏹ Lần đầu theo dõi\n"
    tb += f"🌍 GIÁ TG: {moi['tg']:,} USD/ounce\n"
    if gia_cu["gia_the_gioi"]:
        hieu = moi["tg"] - gia_cu["gia_the_gioi"]
        pct = (hieu / gia_cu["gia_the_gioi"]) * 100
        tb += f"   → {'📈 TĂNG' if hieu>0 else '📉 GIẢM'} {abs(hieu):.2f} USD ({pct:+.3f}%)\n"
    tb += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🔄 Cập nhật mỗi 3 phút"
    # Cập nhật giá cũ
    gia_cu["vang_mua"] = moi["mua"]
    gia_cu["vang_ban"] = moi["ban"]
    gia_cu["gia_the_gioi"] = moi["tg"]
    return tb

def batdau(update, context):
    global gia_cu
    gia_cu = {"vang_mua": None, "vang_ban": None, "gia_the_gioi": None}
    update.message.reply_text("✅ **BOT BẮT ĐẦU THEO DÕI GIÁ VÀNG!**\n🔄 Cập nhật mỗi 3 phút", parse_mode='Markdown')
    context.job_queue.run_repeat(gui_thong_bao, UPDATE_INTERVAL, context=update.message.chat_id, first=1)

def gui_thong_bao(context):
    chat_id = context.job.context
    gia_moi = lay_gia_vang()
    if gia_moi:
        bot = telegram.Bot(token=BOT_TOKEN)
        bot.send_message(chat_id=chat_id, text=tao_thong_bao(gia_moi), parse_mode='Markdown')

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('batdau', batdau))
    updater.start_polling()
    print("🤖 BOT SẴN SÀNG — Gõ /batdau trên Telegram!")
    updater.idle()

if __name__ == "__main__":
    main()
