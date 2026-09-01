import sqlite3
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# =========================
# TOKENNI SHU YERGA YOZING
# =========================
TOKEN = "8893791649:AAGFTNGeZiGu5rIpuSaGtoC9MPXn5x4cHRw"

# =========================
# BAZA
# =========================
db = sqlite3.connect("pul_hisobi.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL,
    description TEXT
)
""")
db.commit()


# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
👋 Assalomu alaykum!

💰 Men sizning pul hisobingizni yuritaman.

Pul qo‘shish:
+50000 maosh

Xarajat yozish:
-15000 ovqat

Buyruqlar:

💵 /balans — balans
📊 /hisobot — hisobot
🗑 /tozalash — barcha hisobni o‘chirish
ℹ️ /help — yordam
"""
    await update.message.reply_text(text)


# =========================
# YORDAM
# =========================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Misollar:\n\n"
        "+100000 maosh\n"
        "-25000 ovqat\n"
        "-10000 transport\n"
        "+50000 boshqa daromad\n\n"
        "/balans\n"
        "/hisobot"
    )


# =========================
# PUL KIRITISH
# =========================
async def add_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text.strip()

    try:
        parts = message.split(maxsplit=1)

        amount = float(parts[0])
        description = parts[1] if len(parts) > 1 else "Nomsiz"

        if amount == 0:
            await update.message.reply_text("❌ Summa 0 bo‘lishi mumkin emas.")
            return

        cursor.execute(
            "INSERT INTO transactions (user_id, amount, description) VALUES (?, ?, ?)",
            (user_id, amount, description)
        )
        db.commit()

        if amount > 0:
            await update.message.reply_text(
                f"✅ Daromad qo‘shildi: +{amount:,.0f} so‘m\n"
                f"📝 {description}"
            )
        else:
            await update.message.reply_text(
                f"💸 Xarajat qo‘shildi: {amount:,.0f} so‘m\n"
                f"📝 {description}"
            )

    except ValueError:
        await update.message.reply_text(
            "❌ To‘g‘ri yozing.\n\n"
            "Masalan:\n"
            "+50000 maosh\n"
            "-15000 ovqat"
        )


# =========================
# BALANS
# =========================
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    cursor.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE user_id=?",
        (user_id,)
    )

    result = cursor.fetchone()[0]

    await update.message.reply_text(
        f"💰 Sizning balansingiz:\n\n"
        f"💵 {result:,.0f} so‘m"
    )


# =========================
# HISOBOT
# =========================
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    cursor.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END), 0)
        FROM transactions
        WHERE user_id=?
    """, (user_id,))

    income, expense = cursor.fetchone()
    balance_value = income - expense

    await update.message.reply_text(
        "📊 HISOBOT\n\n"
        f"💰 Daromad: +{income:,.0f} so‘m\n"
        f"💸 Xarajat: -{expense:,.0f} so‘m\n"
        f"💵 Balans: {balance_value:,.0f} so‘m"
    )


# =========================
# TOZALASH
# =========================
async def clear_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    cursor.execute(
        "DELETE FROM transactions WHERE user_id=?",
        (user_id,)
    )
    db.commit()

    await update.message.reply_text(
        "🗑 Barcha hisoblaringiz o‘chirildi."
    )


# =========================
# BOTNI ISHGA TUSHIRISH
# =========================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("balans", balance))
    app.add_handler(CommandHandler("hisobot", report))
    app.add_handler(CommandHandler("tozalash", clear_data))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, add_transaction)
    )

    print("🤖 Bot ishga tushdi!")
    app.run_polling()


if __name__ == "__main__":
    main()
