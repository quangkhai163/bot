import asyncio
import random
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_CONFIG = {
    'TOKEN': '7819864046:AAFd24PGlIf8xm4lR1ewCjLTY2Oq3glldL0',
    'USER_ID': 5976243149
}

# --- Các lệnh bot gái ---
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
🔥 MENU BOT 🔥

👩‍🦰 GÁI GÚ:
- /videogai : Random video gái cực phẩm TVM
- /anhgai : Random ảnh gái xinh

🛡️ QUẢN LÝ NHÓM:
- /ban (reply) : Ban thành viên
- /unban (reply) : Gỡ ban thành viên
- /mute (reply) : Mute thành viên
- /unmute (reply) : Gỡ mute thành viên
- /kickrandom : Kick random thành viên

⚡ TÍNH NĂNG VUI:
- /spam [sdt] : Spam SMS cực mạnh
- /tiktok [link] : Tải video TikTok không logo
- /addfr [UID] : Gửi kết bạn UID Free Fire

💬 By Admin Quang Khải
""")

async def videogai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        res = requests.get("https://api.ffcommunity.site/randomvideo.php").json()
        video_url = res['url']
        captions = [
            "Vitamin gái đẹp mỗi ngày!",
            "Gái đẹp tiếp thêm năng lượng!",
            "Cùng ngắm gái xinh nào bro!",
            "Gái đẹp giúp giảm stress cực mạnh!"
        ]
        caption = random.choice(captions)
        await update.message.reply_video(video=video_url, caption=caption)
    except:
        await update.message.reply_text("❌ Không lấy được video gái!")

async def anhgai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        res = requests.get("https://api.leanhtruong.net/api/v2/image/gai.php").json()
        img_url = res['data']['url']
        await update.message.reply_photo(photo=img_url, caption="📸 Gái xinh đây bro!")
    except:
        await update.message.reply_text("❌ Không lấy được ảnh gái!")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        await update.effective_chat.ban_member(update.message.reply_to_message.from_user.id)
        await update.message.reply_text("✅ Đã ban thành viên!")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        await update.effective_chat.unban_member(update.message.reply_to_message.from_user.id)
        await update.message.reply_text("✅ Đã gỡ ban thành viên!")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        permissions = Update.default_permissions(can_send_messages=False)
        await update.effective_chat.restrict_member(update.message.reply_to_message.from_user.id, permissions)
        await update.message.reply_text("✅ Đã mute thành viên!")

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        permissions = Update.default_permissions(can_send_messages=True)
        await update.effective_chat.restrict_member(update.message.reply_to_message.from_user.id, permissions)
        await update.message.reply_text("✅ Đã gỡ mute thành viên!")

async def kickrandom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    members = await update.effective_chat.get_members()
    user = random.choice(members)
    await update.effective_chat.kick_member(user.user.id)
    await update.message.reply_text(f"✅ Đã kick random: {user.user.first_name}")

async def spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("📥 Dùng: /spam [số điện thoại]")
        return
    phone = context.args[0]
    try:
        requests.post("https://vietteltelecom.vn/api/Account/SendOTP", json={"phoneNumber": phone})
        requests.post("https://fptplay.net/api/user/sendOTP", json={"phone": phone})
        await update.message.reply_text(f"✅ Đã gửi spam tới {phone}!")
    except:
        await update.message.reply_text("❌ Lỗi spam!")

async def tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("📥 Dùng: /tiktok [link]")
        return
    link = context.args[0]
    try:
        res = requests.get(f"https://tikwm.com/api/?url={link}").json()
        video_url = res['data']['play']
        await update.message.reply_video(video=video_url, caption="✅ Tải thành công TikTok!")
    except:
        await update.message.reply_text("❌ Lỗi tải TikTok!")

async def addfr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("📥 Dùng: /addfr [UID]")
        return
    uid = context.args[0]
    await update.message.reply_text(f"✅ Đã gửi kết bạn tới UID: {uid}")

# --- Hàm gửi gái khi có thành viên mới ---
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        api_video_list = [
            "https://api.ffcommunity.site/randomvideo.php",
            "https://api.leanhtruong.net/api/v2/video/gai.php",
            "https://api-ttk3.hoanghao.click/api/video/gai.php"
        ]
        api_image = "https://api.leanhtruong.net/api/v2/image/gai.php"

        captions = [
            "Chào mừng bro mới bằng gái đẹp nè!",
            "Gia nhập group nhận ngay gái xinh!",
            "Món quà chào mừng: vitamin gái cực mạnh!",
            "Mở màn bằng gái đẹp, vào group cực phê!",
            "Anh em welcome thành viên mới với gái đẹp!",
            "Gái đẹp - Thành viên mới, combo hoàn hảo!",
            "Gái xinh chào đón bạn bro!"
        ]

        video_url = None

        # Thử lần lượt các API video
        for api_url in random.sample(api_video_list, len(api_video_list)):
            try:
                res = requests.get(api_url, timeout=5).json()
                if 'url' in res:
                    video_url = res['url']
                elif 'data' in res and 'url' in res['data']:
                    video_url = res['data']['url']
                if video_url:
                    break
            except Exception as e:
                print(f"⚠️ API lỗi {api_url}: {e}")

        # Nếu không lấy được video -> lấy ảnh gái
        if not video_url:
            try:
                res_img = requests.get(api_image, timeout=5).json()
                if 'data' in res_img and 'url' in res_img['data']:
                    image_url = res_img['data']['url']
                    caption = random.choice(captions)
                    for member in update.message.new_chat_members:
                        await update.message.reply_photo(photo=image_url, caption=f"{caption}\n(Ảnh gái xinh thay thế)")
                    return
            except Exception as e:
                print(f"❌ Lỗi lấy ảnh gái: {e}")
            # Nếu cả ảnh cũng fail
            await update.message.reply_text("❌ Không lấy được gái đẹp để chào mừng!")
            return

        # Nếu lấy được video
        caption = random.choice(captions)
        for member in update.message.new_chat_members:
            await update.message.reply_video(video=video_url, caption=caption)

    except Exception as e:
        print(f"❌ Lỗi tổng quát welcome_new_member: {e}")

# --- Alive ping ---
async def ping_alive(application: Application):
    while True:
        try:
            await application.bot.send_message(chat_id=BOT_CONFIG['USER_ID'], text="#bot_alive_qk")
        except Exception as e:
            print(f"⚠️ Lỗi alive: {e}")
        await asyncio.sleep(30)

# --- MAIN ---
async def main():
    app = Application.builder().token(BOT_CONFIG['TOKEN']).build()

    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("videogai", videogai))
    app.add_handler(CommandHandler("anhgai", anhgai))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("kickrandom", kickrandom))
    app.add_handler(CommandHandler("spam", spam))
    app.add_handler(CommandHandler("tiktok", tiktok))
    app.add_handler(CommandHandler("addfr", addfr))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))

    print("🤖 BOT GÁI QK3 chạy rồi...")
    await app.initialize()
    await app.start()
    await app.bot.send_message(chat_id=BOT_CONFIG['USER_ID'], text="✅ BOT GÁI QKHAI đã hoạt động!")

    asyncio.create_task(ping_alive(app))

    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())