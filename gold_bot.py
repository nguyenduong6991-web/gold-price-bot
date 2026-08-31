import requests
import telegram
from telegram.ext import Updater, CommandHandler
import time
from datetime import datetime

# ================== CẤU HÌNH ==================
BOT_TOKEN = "8692896172:AAHjfrK_c5OmCyZZ7aqRRdSpa-CmItdDkAM"        # ⚠️ Đổi thật
CHAT_ID = "7176458499"        # ⚠️ Đổi thật
UPDATE_INTERVAL = 180  # ⏱️ 3 phút = 180 giây (ngắn hơn kiểm tra dễ)
# ==============================================

# ✅ Dùng biến TOÀN CỤC, KHỞI TẠO 1 LẦN DUY NHẤT lúc chạy
gia_cu = {
    "vang_mua": None,
    "vang_ban": None,
    "gia_the_gioi": None,
    "lan_cap_nhat_cu": None
}

# 🔄 HÀM LẤY GIÁ VỚI 2 NGUỒN DỮ LIỆU + DEBUG + KIỂM TRA THAY ĐỔI
def lay_gia_vang():
    thoi_gian_hien_tai = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # ⚡ Nguồn 1: SJC chính thức
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        # Dùng nguồn đáng tin, không bị cache
        url = "https://sjc.com.vn/Service/GetGoldPrice.ashx"
        res = requests.get(url, headers=headers, timeout=20)
        res.encoding = 'utf-8'
        data = res.json()
        
        # Trích xuất đúng cấu trúc SJC
        for item in data:
            if item.get("Type") == "SJC":
                gia_mua = float(item["BuyPrice"].replace(",", "").replace(".", "")) * 10
                gia_ban = float(item["SellPrice"].replace(",", "").replace(".", "")) * 10
                break
        else:
            raise Exception("Không tìm thấy giá SJC")
            
        gia_tg = lay_gia_the_gioi()  # Lấy giá thế giới riêng
        
        print(f"✅ [{thoi_gian_hien_tai}] LẤY ĐƯỢC DỮ LIỆU | MUA: {gia_mua:,} | BÁN: {gia_ban:,} | TG: {gia_tg}")
        return {"mua": gia_mua, "ban": gia_ban, "the_gioi": gia_tg, "thoi_gian": thoi_gian_hien_tai}
    
    except Exception as e:
        print(f"❌ Nguồn SJC lỗi: {str(e)} → thử nguồn phụ...")
    
    # ⚡ Nguồn 2 dự phòng: PNJ
    try:
        url = "https://api.pnj.vn/public/price"
        res = requests.get(url, timeout=20)
        data = res.json()
        gia_mua = float(data["gold"]["SJC"]["buy"])
        gia_ban = float(data["gold"]["SJC"]["sell"])
        gia_tg = float(data["gold"]["world_price"])
        
        print(f"✅ [{thoi_gian_hien_tai}] [NGUỒN PNJ] MUA: {gia_mua:,} | BÁN: {gia_ban:,}")
        return {"mua": gia_mua, "ban": gia_ban, "the_gioi": gia_tg, "thoi_gian": thoi_gian_hien_tai}
    except Exception as e2:
        print(f"❌ Nguồn PNJ cũng lỗi: {str(e2)}")
        return None

def lay_gia_the_gioi():
    try:
        url = "https://data-asg.goldprice.org/dbXRates/USD"
        res = requests.get(url, timeout=15)
        data = res.json()
        return round(data["items"][0]["xauPrice"], 2)
    except:
        return 0

# 📊 TẠO NỘI DUNG THÔNG BÁO + TÍNH % + BẢO TOÀN GIÁ CŨ
def tao_thong_bao(gia_moi):
    global gia_cu  # ✅ Dùng đúng biến toàn cục, KHÔNG reset
    
    tb = f"📊 **BÁO GIÁ VÀNG SJC — {gia_moi['thoi_gian']}**\n"
    tb += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

    # === GIÁ MUA ===
    tb += f"💰 GIÁ MUA: {gia_moi['mua']:,} VNĐ/lượng\n"
    if gia_cu["vang_mua"] is not None and gia_cu["vang_mua"] != gia_moi["mua"]:
        hieu = gia_moi['mua'] - gia_cu["vang_mua"]
        pct = (hieu / gia_cu["vang_mua"]) * 100
        huong = "📈 TĂNG" if hieu > 0 else "📉 GIẢM"
        tb += f"    └─ {huong} {abs(hieu):,} VNĐ ({pct:+.3f}%)\n"
    else:
        tb += f"    └─ ⏹ GIỐNG GIÁ CŨ / LẦN ĐẦU THEO DÕI\n"

    # === GIÁ BÁN ===
    tb += f"💰 GIÁ BÁN: {gia_moi['ban']:,} VNĐ/lượng\n"
    if gia_cu["vang_ban"] is not None and gia_cu["vang_ban"] != gia_moi["ban"]:
        hieu = gia_moi['ban'] - gia_cu["vang_ban"]
        pct = (hieu / gia_cu["vang_ban"]) * 100
        huong = "📈 TĂNG" if hieu > 0 else "📉 GIẢM"
        tb += f"    └─ {huong} {abs(hieu):,} VNĐ ({pct:+.3f}%)\n"
    else:
        tb += f"    └─ ⏹ GIỐNG GIÁ CŨ / LẦN ĐẦU THEO DÕI\n"

    # === GIÁ THẾ GIỚI ===
    tb += f"🌍 GIÁ TG: {gia_moi['the_gioi']:,} USD/ounce\n"
    if gia_cu["gia_the_gioi"] is not None and gia_cu["gia_the_gioi"] != gia_moi["the_gioi"]:
        hieu = gia_moi['the_gioi'] - gia_cu["gia_the_gioi"]
        pct = (hieu / gia_cu["gia_the_gioi"]) * 100
        huong = "📈 TĂNG" if hieu > 0 else "📉 GIẢM"
        tb += f"    └─ {huong} {abs(hieu):.2f} USD ({pct:+.3f}%)\n"

    tb += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    tb += "🔄 Tự động cập nhật mỗi 3 phút"

    # ✅ CẬP NHẬT GIÁ MỚI → LƯU LẠI cho lần sau — BƯỚC QUAN TRỌNG NHẤT
    gia_cu["vang_mua"] = gia_moi["mua"]
    gia_cu["vang_ban"] = gia_moi["ban"]
    gia_cu["gia_the_gioi"] = gia_moi["the_gioi"]
    gia_cu["lan_cap_nhat_cu"] = gia_moi["thoi_gian"]

    return tb

# 🤖 LỆNH TELEGRAM
def batdau(update, context):
    # Reset giá cũ khi khởi động lại bot để tính lại từ đầu
    global gia_cu
    gia_cu = {"vang_mua": None, "vang_ban": None, "gia_the_gioi": None, "lan_cap_nhat_cu": None}
    
    update.message.reply_text("""
✅ **BOT BẮT ĐẦU HOẠT ĐỘNG**
🔄 Cập nhật mỗi 3 phút
📊 Hiển thị: Giá MUA / BÁN + % thay đổi + chênh lệch VNĐ
🔗 Nguồn: SJC + PNJ (dự phòng)
    """, parse_mode='Markdown')
    
    # Bắt đầu gửi định kỳ
    context.job_queue.run_repeat(gui_thong_bao, UPDATE_INTERVAL, context=update.message.chat_id, first=1)

def gui_thong_bao(context):
    chat_id = context.job.context
    gia_moi = lay_gia_vang()
    
    if gia_moi:
        nd = tao_thong_bao(gia_moi)
        bot = telegram.Bot(token=BOT_TOKEN)
        bot.send_message(chat_id=chat_id, text=nd, parse_mode='Markdown')
    else:
        print("⚠️ Bỏ vòng này — chưa có dữ liệu hợp lệ")

# 🚀 CHẠY BOT
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('batdau', batdau))
    updater.start_polling()
    print("🤖 BOT ĐANG CHẠY — Gõ /batdau trên Telegram để bắt đầu!")
    updater.idle()

if __name__ == "__main__":
    main()
