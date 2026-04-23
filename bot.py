from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

from database import (
    init_db, seed_users, get_user_by_username,
    get_categories_by_company, save_file_record, add_company,
    add_category, get_all_companies, get_categories_by_company_id,
    get_all_files, add_user
)

USER_ROLE, ENTER_USERNAME, COMPANY_MENU, SELECT_CATEGORY = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["نماینده شرکت"], ["ادمین"], ["منیجر"]]
    await update.message.reply_text("نقش خود را انتخاب کنید:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return USER_ROLE


async def role_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = update.message.text
    context.user_data["role_selected"] = role
    await update.message.reply_text("یوزرنیم خود را وارد کنید:")
    return ENTER_USERNAME


async def username_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text
    user = get_user_by_username(username)

    if not user:
        await update.message.reply_text("❌ یوزرنیم یافت نشد.")
        return ENTER_USERNAME

    role = user[1]
    context.user_data["real_role"] = role
    context.user_data["username"] = username

    if role == "company":
        return await show_representative_panel(update, context)
    if role == "admin":
        return await show_admin_panel(update, context)
    if role == "manager":
        return await show_manager_panel(update, context)


async def show_representative_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = context.user_data["username"]
    categories = get_categories_by_company(username)

    if not categories:
        await update.message.reply_text("هیچ دسته‌ای برای شرکت شما ثبت نشده.")
        return

    buttons = [[cat[1]] for cat in categories]
    await update.message.reply_text("دسته خود را انتخاب کنید:", reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))

    return SELECT_CATEGORY


async def representative_category_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected = update.message.text
    username = context.user_data["username"]
    categories = get_categories_by_company(username)

    for c in categories:
        if c[1] == selected:
            context.user_data["selected_category_id"] = c[0]
            await update.message.reply_text("فایل خود را ارسال کنید.")
            return COMPANY_MENU

    await update.message.reply_text("دسته معتبر نیست.")
    return SELECT_CATEGORY


async def file_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category_id = context.user_data.get("selected_category_id")

    if not category_id:
        await update.message.reply_text("لطفاً ابتدا دسته را انتخاب کنید.")
        return COMPANY_MENU

    document = update.message.document
    photo = update.message.photo[-1] if update.message.photo else None
    caption = update.message.caption

    if document:
        file_id = document.file_id
        file_name = document.file_name
    elif photo:
        file_id = photo.file_id
        file_name = "photo.jpg"
    else:
        await update.message.reply_text("❌ لطفاً فقط فایل یا عکس ارسال کنید.")
        return COMPANY_MENU

    save_file_record(category_id, file_name, file_id, caption)
    await update.message.reply_text("✔ فایل با موفقیت ذخیره شد.")

    return COMPANY_MENU


# ------------------------------ پنل ادمین ------------------------------

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["➕ افزودن شرکت"],
        ["➕ افزودن دسته"],
        ["📂 مشاهده فایل‌ها"]
    ]
    await update.message.reply_text("پنل ادمین:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return COMPANY_MENU


async def add_company_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["await_add_company"] = True
    await update.message.reply_text("یوزرنیم شرکت را وارد کنید:")
    return COMPANY_MENU


async def add_company_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text
    add_user(username, "company")
    add_company(username, f"شرکت {username}")
    await update.message.reply_text("✔ شرکت اضافه شد.")
    context.user_data["await_add_company"] = False
    return COMPANY_MENU


async def add_category_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    companies = get_all_companies()

    buttons = [
        [InlineKeyboardButton(text=f"{c[1]} ({c[0]})", callback_data=f"select_company:{c[0]}")]
        for c in companies
    ]

    await update.message.reply_text("شرکت را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(buttons))
    return COMPANY_MENU


async def select_company_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    company_username = query.data.split(":")[1]
    context.user_data["selected_company_username"] = company_username

    await query.message.reply_text("نام دسته جدید را وارد کنید:")
    context.user_data["await_new_category"] = True

    return COMPANY_MENU


async def add_new_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    company_username = context.user_data["selected_company_username"]

    add_category(name, company_username)
    await update.message.reply_text("✔ دسته اضافه شد.")
    context.user_data["await_new_category"] = False
    return COMPANY_MENU


# ------------------------------ مدیریت فایل‌ها ------------------------------

async def admin_show_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    files = get_all_files()

    if not files:
        await update.message.reply_text("هیچ فایلی موجود نیست.")
        return COMPANY_MENU

    text = ""
    keyboard = []

    for f in files:
        text += f"📄 {f[1]} — دسته: {f[3]}\n"
        keyboard.append([InlineKeyboardButton(text=f"دانلود {f[1]}", callback_data=f"download_file:{f[2]}")])

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return COMPANY_MENU


async def send_file_by_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    file_id = query.data.split(":")[1]

    try:
        await query.message.reply_document(document=file_id)
    except Exception as e:
        await query.message.reply_text(f"❌ خطا در ارسال فایل: {e}")


# ------------------------------ پنل منیجر ------------------------------

async def show_manager_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["➕ افزودن ادمین"],
        ["📂 مشاهده فایل‌ها"]
    ]
    await update.message.reply_text("پنل منیجر:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return COMPANY_MENU


async def add_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["await_add_admin"] = True
    await update.message.reply_text("یوزرنیم ادمین جدید را وارد کنید:")
    return COMPANY_MENU


async def add_admin_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text
    add_user(username, "admin")
    await update.message.reply_text("✔ ادمین اضافه شد.")
    context.user_data["await_add_admin"] = False
    return COMPANY_MENU


# ------------------------------ هندلرهای اصلی ------------------------------

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    data = context.user_data

    if data.get("await_add_company"):
        return await add_company_process(update, context)

    if data.get("await_new_category"):
        return await add_new_category(update, context)

    if data.get("await_add_admin"):
        return await add_admin_process(update, context)

    if text == "➕ افزودن شرکت":
        return await add_company_menu(update, context)

    if text == "➕ افزودن دسته":
        return await add_category_menu(update, context)

    if text == "📂 مشاهده فایل‌ها":
        return await admin_show_files(update, context)

    if text == "➕ افزودن ادمین":
        return await add_admin_menu(update, context)

    # نماینده شرکت
    username = context.user_data.get("username")
    if username:
        categories = get_categories_by_company(username)
        if any(c[1] == text for c in categories):
            return await representative_category_selected(update, context)

    return COMPANY_MENU


def main():
    init_db()
    seed_users()

    app = Application.builder().token("8313428053:AAG8ClLkYWB2K61DSrufT_M5ylZ06YIX1Ao").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, file_received))

    app.add_handler(CallbackQueryHandler(select_company_menu, pattern="^select_company:.+"))
    app.add_handler(CallbackQueryHandler(send_file_by_id, pattern="^download_file:.+"))

    app.run_polling()


if __name__ == "__main__":
    main()