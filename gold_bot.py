import requests
import telegram
from telegram.ext import Updater, CommandHandler
import time
from datetime import datetime

# 🔧 THÔNG SỐ CẤU HÌNH — Điền thông tin của bạn vào đây
BOT_TOKEN = "TOKEN_BOT_TELEGRAM_CỦA_BẠN"
CHAT_ID = "ID_NHẬN_THÔNG_BÁO"
UPDATE_INTERVAL = 300  # Cập nhật mỗi 5 phút = 300 giây (tùy chỉnh được)

# Biến lưu trữ giá cũ để tính % thay đổi
gia_cu = {
    "vang_mua": None,
    "vang_ban": None,
    "gia_the_gioi": None
}

# Hàm lấy giá vàng — SỬA LẠI để đảm bảo lấy dữ liệu MỚI mỗi lần gọi
def lay_gia_vang():
    try:
        # Nguồn dữ liệu — có thể đổi nguồn khác nếu cần
        url = "https://api.pnj.vn/price/gold"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=15)
        data = response.json()
        
        # Trích xuất dữ liệu — điều chỉnh khớp với cấu trúc API bạn dùng
        gia_mua = float(data.get("SJC_mua", 0))
        gia_ban = float(data.get("SJC_ban", 0))
        gia_the_gioi = float(data.get("gia_the_gioi", 0))
        
        if gia_mua == 0 or gia_ban == 0:
            print(f"[{datetime.now()}] ⚠️ Dữ liệu không hợp lệ, bỏ qua lần này")
            return None
            
        return {
            "mua": gia_mua,
            "ban": gia_ban,
            "the_gioi": gia_the_gioi,
            "thoi_gian": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
    except Exception as e:
        print(f"Lỗi lấy giá: {str(e)}")
        return None

# Hàm tính toán % thay đổi & tạo nội dung thông báo
def tao_thong_bao(gia_moi):
    global gia_cu
    tb = f"📊 **BÁO GIÁ VÀNG SJC — {gia_moi['thoi_gian']}**\n"
    tb += "━━━━━━━━━━━━━━━━━━━━━\n"
    
    # Giá mua
    tb += f"💰 Giá MUA: {gia_moi['mua']:,} VNĐ/lượng\n"
    if gia_cu["vang_mua"] is not None:
        hieu_so = gia_moi['mua'] - gia_cu["vang_mua"]
        phan_tram = (hieu_so / gia_cu["vang_mua"]) * 100
        huong = "📈 TĂNG" if hieu_so > 0 else "📉 GIẢM" if hieu_so < 0 else "➖ KHÔNG ĐỔI"
        tb += f"   → {huong} {abs(hieu_so):,} VNĐ ({phan_tram:+.2f}%)\n"
    
    # Giá bán
    tb += f"💰 Giá BÁN: {gia_moi['ban']:,} VNĐ/lượng\n"
    if gia_cu["vang_ban"] is not None:
        hieu_so = gia_moi['ban'] - gia_cu["vang_ban"]
        phan_tram = (hieu_so / gia_cu["vang_ban"]) * 100
        huong = "📈 TĂNG" if hieu_so > 0 else "📉 GIẢM" if hieu_so < 0 else "➖ KHÔNG ĐỔI"
        tb += f"   → {huong} {abs(hieu_so):,} VNĐ ({phan_tram:+.2f}%)\n"
    
    # Giá thế giới
    tb += f"🌍 Giá TG: {gia_moi['the_gioi']:,} USD/ounce\n"
    if gia_cu["gia_the_gioi"] is not None:
        hieu_so = gia_moi['the_gioi'] - gia_cu["gia_the_gioi"]
        phan_tram = (hieu_so / gia_cu["gia_the_gioi"]) * 100
        huong = "📈 TĂNG" if hieu_so > 0 else "📉 GIẢM" if hieu_so < 0 else "➖ KHÔNG ĐỔI"
        tb += f"   → {huong} {abs(hieu_so):.2f} USD ({phan_tram:+.2f}%)\n"
    
    tb += "━━━━━━━━━━━━━━━━━━━━━"
    
    # CẬP NHẬT giá cũ = giá mới cho lần sau
    gia_cu["vang_mua"] = gia_moi['mua']
    gia_cu["vang_ban"] = gia_moi['ban']
    gia_cu["gia_the_gioi"] = gia_moi['the_gioi']
    
    return tb

# Lệnh /batdau
def batdau(update, context):
    update.message.reply_text("✅ Bot bắt đầu theo dõi giá vàng! Tôi sẽ cập nhật mỗi {} phút ⏱️".format(UPDATE_INTERVAL//60))
    context.job_queue.run_repeat(gui_thong_bao_dinhky, UPDATE_INTERVAL, context=update.message.chat_id)

# Hàm gửi thông báo định kỳ
def gui_thong_bao_dinhky(context):
    chat_id = context.job.context
    gia_moi = lay_gia_vang()
    
    if gia_moi:  # Chỉ gửi khi có dữ liệu hợp lệ
        noi_dung = tao_thong_bao(gia_moi)
        bot = telegram.Bot(token=BOT_TOKEN)
        bot.send_message(chat_id=chat_id, text=noi_dung, parse_mode='Markdown')

# Hàm chính chạy bot
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('batdau', batdau))
    updater.start_polling()
    print("🤖 Bot đang chạy...")
    updater.idle()

if __name__ == "__main__":
    main()
