import asyncio
import json
import random
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Cấu hình bot
BOT_CONFIG = {
    'TOKEN': '7752584378:AAGt2Ykue5Pj3XwgEoP62g0w9b6yLbr5pWo',
    'GROUP_ID': -1002538985524,
    'ADMIN_IDS': [7685822542,5976243149,6787623278,2142585996,7504852292],
}

BALANCE_FILE = "balance.json"
CODE_FILE = "codes.json"
JACKPOT_FILE = "jackpot.json"

def load_codes():
    try:
        with open(CODE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_codes():
    try:
        with open(CODE_FILE, "w", encoding="utf-8") as f:
            json.dump(CODE_STORE, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"⚠️ Lỗi khi lưu mã code: {e}")

def load_balance():
    try:
        with open(BALANCE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_balance():
    try:
        with open(BALANCE_FILE, "w", encoding="utf-8") as f:
            json.dump(user_money, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"⚠️ Lỗi khi lưu số dư: {e}")

def load_jackpot():
    try:
        with open(JACKPOT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"jackpot": 0, "count": 0}

def save_jackpot(data):
    try:
        with open(JACKPOT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"⚠️ Lỗi khi lưu jackpot: {e}")

CODE_STORE = load_codes()
CODE_STORE = {}

user_money = load_balance()
jackpot_data = load_jackpot()
async def send_welcome_message(application: Application):
    welcome_text = "🎲 **Chào mừng đến với bot tài xỉu by 𝗾𝗸!**\n💰 Hãy thử vận may ngay!"
    await application.bot.send_message(chat_id=BOT_CONFIG['GROUP_ID'], text=welcome_text)


async def menu(update: Update, context: CallbackContext):
    menu_text = """📌 *Danh sách lệnh bot:* 

✅ /dangky - Đăng ký tài khoản
🎲 /taixiu <tài/xỉu> <số tiền hoặc 'all'> - Chơi tài xỉu
🏆 /top - Xem bảng xếp hạng
💰 /sodu - Xem số dư
🔑 /codevip <mã code> - Nhập code tiền
🛠 /code <số tiền> (Admin) - Tạo mã code
💰 /admoney <số tiền> (Admin) - Cộng tiền cho user (reply tin nhắn)
💎 /jackpot - Xem quỹ nổ hũ
🛠 /resetjackpot (Admin) - Reset quỹ nổ hũ
🧹 /resets (Admin chính):
   • /resets - Reset toàn bộ về 0
   • /resets all <số tiền> - Reset toàn bộ về số tiền
   • /resets <user_id> - Reset 1 người về 0
   • /resets <user_id> <số tiền> - Reset 1 người về số tiền
📜 /menu - Xem danh sách lệnh"""
    await update.message.reply_text(menu_text, parse_mode="Markdown")


async def dangky(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    if user_id in user_money:
        await update.message.reply_text("✅ Bạn đã đăng ký trước đó!")
        return
    user_money[user_id] = 1000
    save_balance()
    await update.message.reply_text("🎉 Bạn đã đăng ký thành công! Số dư: 1000 VNĐ")

async def sodu(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    balance = user_money.get(user_id, 0)
    await update.message.reply_text(f"💰 **Số dư của bạn:** {balance:,} VNĐ", parse_mode="Markdown")

async def code(update: Update, context: CallbackContext):
    if update.message.from_user.id not in BOT_CONFIG['ADMIN_IDS']:
        await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này!")
        return
    if len(context.args) < 1:
        await update.message.reply_text("📌 **Cú pháp:** /code <số tiền>")
        return
    try:
        amount = int(context.args[0])
        if amount <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Số tiền không hợp lệ! Vui lòng nhập số dương.")
        return
    code = str(random.randint(100000, 999999))
    CODE_STORE[code] = amount
    save_codes()
    await update.message.reply_text(f"✅ **Mã code:** `{code}` - Giá trị: {amount:,} VNĐ", parse_mode="Markdown")

async def codevip(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    if not context.args:
        await update.message.reply_text("📌 **Cú pháp:** /codevip <mã code>")
        return
    code = context.args[0]
    if code in CODE_STORE:
        amount = CODE_STORE.pop(code)
        user_money[user_id] = user_money.get(user_id, 0) + amount
        save_balance()
        save_codes()
        await update.message.reply_text(f"🎉 **Bạn đã nhận được {amount:,} VNĐ!**", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Mã code không hợp lệ hoặc đã được sử dụng!")

async def admoney(update: Update, context: CallbackContext):
    if update.message.from_user.id not in BOT_CONFIG['ADMIN_IDS']:
        await update.message.reply_text("❌ Bạn không có quyền!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("📌 **Reply tin nhắn cần cộng tiền!**")
        return
    try:
        amount = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text("📌 **Cú pháp:** /admoney <số tiền>")
        return
    target_user_id = str(update.message.reply_to_message.from_user.id)
    user_money[target_user_id] = user_money.get(target_user_id, 1000) + amount
    save_balance()
    await update.message.reply_text(f"✅ **Đã cộng {amount} VNĐ!** 💰 Số dư: {user_money[target_user_id]}")

async def top(update: Update, context: CallbackContext):
    if not user_money:
        await update.message.reply_text("📌 **Chưa có ai chơi!**")
        return
    sorted_users = sorted(user_money.items(), key=lambda x: x[1], reverse=True)[:10]
    top_text = "🏆 *BẢNG XẾP HẠNG ĐẠI GIA* 🏆\n"
    medals = ["🥇", "🥈", "🥉"] + ["🎖️"] * 7
    for i, (user_id, balance) in enumerate(sorted_users):
        top_text += f"{medals[i]} *User {user_id}* ─ 💵 *{balance:,} VNĐ*\n"
    await update.message.reply_text(top_text, parse_mode="Markdown")
async def jackpot(update: Update, context: CallbackContext):
    await update.message.reply_text(
        f"💰 **Jackpot hiện tại:** {jackpot_data['jackpot']:,} VNĐ\n🎯 Số ván đã chơi: {jackpot_data['count']}/50",
        parse_mode="Markdown"
    )

async def resetjackpot(update: Update, context: CallbackContext):
    if update.message.from_user.id not in BOT_CONFIG['ADMIN_IDS']:
        await update.message.reply_text("❌ Bạn không có quyền!")
        return
    jackpot_data["jackpot"] = 0
    jackpot_data["count"] = 0
    save_jackpot(jackpot_data)
    await update.message.reply_text("✅ Đã reset jackpot thành công!")

async def taixiu(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    if user_id not in user_money:
        await update.message.reply_text("⚠️ Bạn chưa đăng ký! Hãy dùng /dangky trước.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("📌 **Cú pháp:** /taixiu <tài/xỉu> <số tiền hoặc 'all'>")
        return

    bet_choice = context.args[0].lower()
    bet_amount = context.args[1]
    if bet_choice not in ["tài", "xỉu"]:
        await update.message.reply_text("❌ Bạn chỉ có thể chọn 'tài' hoặc 'xỉu'.")
        return

    balance = user_money.get(user_id, 0)
    if bet_amount == "all":
        bet_amount = balance
    else:
        try:
            bet_amount = int(bet_amount)
            if bet_amount <= 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text("❌ Số tiền cược không hợp lệ!")
            return

    if bet_amount > balance:
        await update.message.reply_text("❌ Bạn không có đủ tiền để cược!")
        return

    # Trích 10% vào jackpot
    contribute = int(bet_amount * 0.10)
    jackpot_data["jackpot"] += contribute
    save_jackpot(jackpot_data)

    user_money[user_id] -= bet_amount
    save_balance()

    jackpot_data["count"] += 1
    save_jackpot(jackpot_data)

    dice_results = []
    total_points = 0
    for _ in range(3):
        msg = await update.message.reply_dice(emoji="🎲")
        dice_value = msg.dice.value
        dice_results.append(dice_value)
        total_points += dice_value
        await asyncio.sleep(3)

    result = "tài" if total_points >= 11 else "xỉu"
    special_win = False
    jackpot_message = ""

    # Check nổ hũ theo xúc xắc + đúng tài/xỉu
    
    if dice_results == [1, 1, 1] and bet_choice == "xỉu":
        winnings = bet_amount * 5
        user_money[user_id] += winnings
        jackpot_message = "✨ Bạn đặt XỈU ra 3 con 1! NỔ HŨ x5 tiền cược!"
        special_win = True
    elif dice_results == [6, 6, 6] and bet_choice == "tài":
        winnings = bet_amount * 5
        user_money[user_id] += winnings
        jackpot_message = "✨✨✨ Bạn đặt TÀI ra 3 con 6! NỔ HŨ x5 tiền cược!"
        special_win = True
    
    elif dice_results == [6, 6, 6] and bet_choice == "tài":
        winnings = bet_amount * 5
        user_money[user_id] += winnings
        jackpot_message = "✨✨✨ Bạn đặt TÀI ra 3 con 6! Đại thắng x5 tiền cược!"
        special_win = True
    
    elif jackpot_data["count"] >= 50:
        if bet_choice == result:
            winnings = jackpot_data["jackpot"]
            user_money[user_id] += winnings
            jackpot_message = f"🔥 JACKPOT NỔ HŨ! Bạn nhận thêm {winnings:,} VNĐ vì đặt đúng {bet_choice.upper()}!"
            special_win = True
        else:
            jackpot_message = "💥 JACKPOT đã kích hoạt nhưng bạn đặt sai nên không nhận thưởng."
        jackpot_data["jackpot"] = 0
        jackpot_data["count"] = 0
        save_jackpot(jackpot_data)
    
        special_win = True

    save_balance()

    if special_win:
        await update.message.reply_text(
            f"{jackpot_message}\n\n🎲 **Kết quả:** {dice_results} = {total_points} ({result.upper()})\n💰 Số dư mới: {user_money[user_id]:,} VNĐ",
            parse_mode="Markdown"
        )
    else:
        if result == bet_choice:
            winnings = bet_amount * 2
            user_money[user_id] += winnings
            save_balance()
            await update.message.reply_text(
                f"🎉 **Bạn thắng!** +{bet_amount:,} VNĐ\n🎲 **Kết quả:** {dice_results} = {total_points} ({result.upper()})\n💰 Số dư mới: {user_money[user_id]:,} VNĐ",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                f"😢 **Bạn thua!** -{bet_amount:,} VNĐ\n🎲 **Kết quả:** {dice_results} = {total_points} ({result.upper()})\n💰 Số dư mới: {user_money[user_id]:,} VNĐ",
                parse_mode="Markdown"
            )


async def resets(update: Update, context: CallbackContext):
    # Chỉ admin chính mới được dùng
    if update.message.from_user.id != 5976243149:
        await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này!")
        return

    args = context.args

    if not args:
        # /resets → reset toàn bộ về 0
        for uid in user_money:
            user_money[uid] = 0
        save_balance()
        await update.message.reply_text("✅ Đã reset toàn bộ số dư về 0!")
        return

    if args[0] == "all":
        # /resets all <số tiền>
        try:
            amount = int(args[1])
        except (IndexError, ValueError):
            await update.message.reply_text("📌 Cú pháp: /resets all <số tiền>")
            return
        for uid in user_money:
            user_money[uid] = amount
        save_balance()
        await update.message.reply_text(f"✅ Đã reset toàn bộ số dư về {amount:,} VNĐ!")
        return

    # /resets <user_id> [số tiền]
    uid = args[0]
    if uid not in user_money:
        await update.message.reply_text("❌ Không tìm thấy user ID trong dữ liệu!")
        return

    if len(args) == 2:
        try:
            amount = int(args[1])
        except ValueError:
            await update.message.reply_text("📌 Số tiền không hợp lệ.")
            return
        user_money[uid] = amount
        save_balance()
        await update.message.reply_text(f"✅ Đã reset số dư user {uid} về {amount:,} VNĐ!")
    else:
        user_money[uid] = 0
        save_balance()
        await update.message.reply_text(f"✅ Đã reset số dư user {uid} về 0 VNĐ!")


async def main():
    app = Application.builder().token(BOT_CONFIG["TOKEN"]).build()
    app.add_handler(CommandHandler("dangky", dangky))
    app.add_handler(CommandHandler("sodu", sodu))
    app.add_handler(CommandHandler("code", code))
    app.add_handler(CommandHandler("codevip", codevip))
    app.add_handler(CommandHandler("admoney", admoney))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("taixiu", taixiu))
    app.add_handler(CommandHandler("jackpot", jackpot))
    app.add_handler(CommandHandler("resetjackpot", resetjackpot))
    app.add_handler(CommandHandler("resets", resets))

    print("🤖 Bot đang chạy...")
    await app.initialize()
    await app.start()
    await send_welcome_message(app)
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

async def resets(update: Update, context: CallbackContext):
    if update.message.from_user.id not in BOT_CONFIG['ADMIN_IDS']:
        await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này!")
        return

    if context.args:
        uid = context.args[0]
        if uid in user_money:
            user_money[uid] = 0
            save_balance()
            await update.message.reply_text(f"✅ Đã reset số dư của user {uid}!")
        else:
            await update.message.reply_text("❌ Không tìm thấy user ID trong dữ liệu!")
    else:
        for uid in user_money:
            user_money[uid] = 0
        save_balance()
        await update.message.reply_text("✅ Đã reset toàn bộ số dư!")
