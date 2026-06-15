import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import Application, MessageHandler, filters, ContextTypes, ChatMemberHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8799575804:AAFrBt65OASPpWJr4iJVxCamIg0jS75Ri_o"
CHANNEL_USERNAME = "@Pekar_tandirshik"
CHANNEL_LINK = "https://t.me/Pekar_tandirshik"
CHANNEL_NAME = "Вакансии пекарь тандерщик-Нонвой шаурмист"

# Xabar matni 3 tilda
SUBSCRIBE_MESSAGE = """
🇷🇺 Уважаемый участник! Чтобы писать в группе, подпишитесь на наш канал.

🇺🇿 Hurmatli obunachi! Guruhda yozish uchun kanalimizga obuna bo'ling.

🇹🇯 Аъзои гиромӣ! Барои навиштан дар гурӯҳ, ба канали мо обуна шавед.
"""

# Raxmat xabari (5+ odam qo'shganda)
THANK_YOU_MESSAGE = """
🎉🇷🇺 Большое спасибо! Вы пригласили 5 и более участников в нашу группу! Вы настоящий помощник!

🎉🇺🇿 Katta rahmat! Siz guruhga 5 va undan ko'p odam taklif qildingiz! Siz haqiqiy yordamchisiz!

🎉🇹🇯 Ташаккури калон! Шумо 5 нафар ва зиёда одамонро ба гурӯҳ даъват кардед! Шумо ёрдамчии воқеӣ ҳастед!
"""

async def check_subscription(bot, user_id):
    """Kanalga obuna bo'lganini tekshirish"""
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in [
            ChatMember.MEMBER,
            ChatMember.ADMINISTRATOR,
            ChatMember.OWNER
        ]
    except Exception as e:
        logger.error(f"Obuna tekshirishda xato: {e}")
        return False

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guruhga kelgan xabarlarni tekshirish"""
    if not update.message:
        return

    user = update.message.from_user
    chat = update.message.chat

    # Faqat guruhda ishlaydi
    if chat.type not in ["group", "supergroup"]:
        return

    # Bot xabarlarini o'chirmaymiz
    if user.is_bot:
        return

    # Kanal egasi yoki admin bo'lsa o'tkazib yuboramiz
    try:
        chat_member = await context.bot.get_chat_member(chat.id, user.id)
        if chat_member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
            return
    except:
        pass

    # Obunani tekshirish
    is_subscribed = await check_subscription(context.bot, user.id)

    if not is_subscribed:
        # Xabarni o'chirish
        try:
            await update.message.delete()
        except Exception as e:
            logger.error(f"Xabarni o'chirishda xato: {e}")

        # Tugma bilan ogohlantirish yuborish
        keyboard = [[
            InlineKeyboardButton(
                f"📢 {CHANNEL_NAME}",
                url=CHANNEL_LINK
            )
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            sent_msg = await context.bot.send_message(
                chat_id=chat.id,
                text=SUBSCRIBE_MESSAGE,
                reply_markup=reply_markup
            )
            # 30 soniyadan keyin ogohlantirishni o'chirish
            await asyncio.sleep(30)
            await sent_msg.delete()
        except Exception as e:
            logger.error(f"Xabar yuborishda xato: {e}")

async def handle_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yangi a'zolar qo'shilganda tekshirish"""
    if not update.message or not update.message.new_chat_members:
        return

    user = update.message.from_user
    new_members = update.message.new_chat_members
    chat = update.message.chat

    # Botni o'zi qo'shilsa o'tkazib yuboramiz
    if any(member.is_bot for member in new_members):
        return

    # Nechta odam qo'shilganini tekshirish
    # Foydalanuvchi qo'shgan odamlar sonini context.user_data da saqlash
    user_id = str(user.id)
    if user_id not in context.bot_data:
        context.bot_data[user_id] = 0

    context.bot_data[user_id] += len(new_members)

    # 5 va undan ko'p odam qo'shilsa raxmat aytish
    if context.bot_data[user_id] >= 5:
        try:
            await context.bot.send_message(
                chat_id=chat.id,
                text=f"@{user.username or user.first_name}\n{THANK_YOU_MESSAGE}"
            )
            # Hisoblagichni nolga qaytarish
            context.bot_data[user_id] = 0
        except Exception as e:
            logger.error(f"Raxmat xabarida xato: {e}")

def main():
    """Botni ishga tushirish"""
    app = Application.builder().token(BOT_TOKEN).build()

    # Xabar handlerlar
    app.add_handler(MessageHandler(
        filters.TEXT & filters.ChatType.GROUPS,
        handle_message
    ))
    app.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS,
        handle_new_members
    ))

    logger.info("Bot ishga tushdi! ✅")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
