import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_LINK = "https://t.me/Pump_Signals_Official"

user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🚀 Nominate Token", callback_data="nominate")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"⚠️ One vote per user\n👉 Channel: {CHANNEL_LINK}",
        reply_markup=reply_markup,
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "nominate":
        keyboard = [
            [InlineKeyboardButton("ETH", callback_data="chain_ETH")],
            [InlineKeyboardButton("Base", callback_data="chain_Base")],
            [InlineKeyboardButton("BNB Chain (BSC)", callback_data="chain_BNB")],
            [InlineKeyboardButton("Solana", callback_data="chain_Solana")],
        ]
        markup = InlineKeyboardMarkup(keyboard)
        user_states[user_id] = {}
        await query.edit_message_text("Choose chain 👇", reply_markup=markup)

    elif query.data.startswith("chain_"):
        chain = query.data.split("_")[1]
        user_states[user_id]["chain"] = chain
        await query.edit_message_text("Please send the ticker ($TOKEN). For example: $BONK, $PEPE")

    elif query.data == "confirm_yes":
        info = user_states.get(user_id, {})
        token = info.get("token", "?")
        ca = info.get("ca", "?")
        chain = info.get("chain", "?")
        await query.edit_message_text(
            f"✅ Thank you, we registered your vote.\n\n"
            f"We select a coin that meets the requirements listed above. Maybe the next signal will be your coin. So keep a sharp eye on our channel.\n\n"
            f"Token: {token}\nCA: {ca}\nChain: {chain}\n\n"
            f"Invite your friends to vote for your favorite coin to be pumped: @Pump_Signals_Official_Bot on our channel @Pump_Signals_Official"
        )
        user_states.pop(user_id, None)

    elif query.data == "confirm_no":
        await query.edit_message_text("Let's start over. Please use /start again.")
        user_states.pop(user_id, None)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id not in user_states:
        await update.message.reply_text("Please start with /start")
        return

    data = user_states[user_id]

    if "chain" in data and "token" not in data:
        if not text.startswith("$"):
            await update.message.reply_text("Please enter token like this: $TOKEN")
            return
        data["token"] = text
        await update.message.reply_text("Please send the CA (contract address) of your token:")

    elif "token" in data and "ca" not in data:
        data["ca"] = text
        keyboard = [
            [
                InlineKeyboardButton("✅ Yes", callback_data="confirm_yes"),
                InlineKeyboardButton("❌ No (edit)", callback_data="confirm_no"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Verify information:\n\n"
            f"Token: {data['token']}\n"
            f"CA: {data['ca']}\n"
            f"Chain: {data['chain']}\n\n"
            f"Is everything correct?",
            reply_markup=reply_markup
        )

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    print("✅ Coin Vote Bot is running...")
    app.run_polling()
