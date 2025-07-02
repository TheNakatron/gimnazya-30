import os
import datetime
import logging
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)

load_dotenv()

from models import Teacher, Event, EventImage, SessionLocal

# ---------------------------
# Настройка логирования
# ---------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------
# Состояния для add_teacher
# ---------------------------
PHOTO, NAME, POSITION, EXPERIENCE, T_LINK = range(5)

# ---------------------------
# Состояния для add_event
# ---------------------------
(
    EV_IMG,      # 0 — главное изображение
    EV_TITLE,    # 1 — заголовок
    EV_DESC,     # 2 — описание
    EV_DATE,     # 3 — дата
    EV_GALLERY,  # 4 — доп. фото
    EV_ARTICLE,  # 5 — статья
    EV_LINK      # 6 — внешняя ссылка вместо статьи
) = range(5, 12)

# ---------------------------
# Создаём папки для загрузки
# ---------------------------
os.makedirs("static/teachers", exist_ok=True)
os.makedirs("static/events", exist_ok=True)

# ==============================================================================
#                          ФУНКЦИИ ДЛЯ add_teacher
# ==============================================================================

async def start_teacher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📷 Пришлите фото преподавателя:")
    return PHOTO

async def receive_teacher_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # принимаем фото или документ-изображение
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
    elif update.message.document and update.message.document.mime_type.startswith("image/"):
        file = await update.message.document.get_file()
    else:
        await update.message.reply_text("❌ Пришлите изображение (фото или документ).")
        return PHOTO

    fn = f"{update.effective_chat.id}_{file.file_id}.jpg"
    path = os.path.join("static/teachers", fn)
    await file.download_to_drive(path)
    context.user_data["photo"] = fn

    await update.message.reply_text("👤 Теперь введите ФИО:")
    return NAME

async def receive_teacher_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("📌 Введите должность:")
    return POSITION

async def receive_teacher_position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["position"] = update.message.text
    await update.message.reply_text("🧪 Введите опыт преподавателя в годах:")
    return EXPERIENCE

async def receive_teacher_experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["experience"] = update.message.text
    await update.message.reply_text(
        "🔗 Пришлите внешнюю ссылку на профиль преподавателя или /skip_link, если её нет."
    )
    return T_LINK

async def skip_teacher_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["link"] = None
    return await save_teacher(update, context)

async def receive_teacher_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["link"] = update.message.text
    return await save_teacher(update, context)

async def save_teacher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data
    db = SessionLocal()
    teacher = Teacher(
        name=data["name"],
        position=data["position"],
        experience=data["experience"],
        photo=data["photo"],
        link=data.get("link")
    )
    db.add(teacher)
    db.commit()
    tid = teacher.id
    db.close()

    await update.message.reply_text(f"✅ Преподаватель сохранён (ID {tid}).")
    return ConversationHandler.END

# ==============================================================================
#                          ФУНКЦИИ ДЛЯ delete_teacher
# ==============================================================================

async def delete_teacher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    teachers = db.query(Teacher).order_by(Teacher.id).all()
    db.close()

    if not teachers:
        return await update.message.reply_text("❌ В базе нет ни одного преподавателя.")

    # строим клавиатуру
    keyboard = []
    for t in teachers:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{t.id} — {t.name}",
                callback_data=f"del_teacher:{t.id}"
            )
        ])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Выберите преподавателя, которого хотите удалить:",
        reply_markup=reply_markup
    )

# обработчик нажатия на кнопку
async def cb_delete_teacher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # чтобы убрать «часики»

    # получаем ID
    _, tid_str = query.data.split(":")
    tid = int(tid_str)

    db = SessionLocal()
    teacher = db.query(Teacher).get(tid)
    if not teacher:
        text = f"❌ Преподаватель с ID {tid} не найден."
    else:
        name = teacher.name
        db.delete(teacher)
        db.commit()
        text = f"🗑️ Преподаватель *{name}* (ID {tid}) удалён."
    db.close()

    # меняем сообщение с кнопками на итоговое
    await query.edit_message_text(text, parse_mode="Markdown")

# ==============================================================================
#                          ФУНКЦИИ ДЛЯ add_event
# ==============================================================================

async def start_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["extra_images"] = []
    await update.message.reply_text(
        "🖼 Пришлите главное изображение события или /skip_image:"
    )
    return EV_IMG

async def receive_event_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.photo[-1].get_file()
    fn = f"{update.effective_chat.id}_{file.file_id}.jpg"
    path = os.path.join("static/events", fn)
    await file.download_to_drive(path)
    context.user_data["image"] = f"events/{fn}"
    await update.message.reply_text("📝 Введите название события:")
    return EV_TITLE

async def skip_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["image"] = "assets/img/placeholder.jpg"
    await update.message.reply_text("📝 Введите название события:")
    return EV_TITLE

async def receive_event_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["title"] = update.message.text
    await update.message.reply_text("📖 Введите краткое описание:")
    return EV_DESC

async def receive_event_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["description"] = update.message.text
    await update.message.reply_text("📅 Введите дату события (ГГГГ-ММ-ДД):")
    return EV_DATE

async def receive_event_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        dt = datetime.datetime.strptime(update.message.text, "%Y-%m-%d").date()
    except ValueError:
        await update.message.reply_text("❌ Формат должен быть ГГГГ-ММ-ДД. Попробуйте ещё раз:")
        return EV_DATE
    context.user_data["date"] = dt
    await update.message.reply_text(
        "📷 Отправьте доп. фото (до 20) или /done_gallery:"
    )
    return EV_GALLERY

async def receive_extra_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    imgs = context.user_data["extra_images"]
    if len(imgs) >= 20:
        return await done_gallery(update, context)

    file = await update.message.photo[-1].get_file()
    fn = f"{update.effective_chat.id}_{file.file_id}.jpg"
    path = os.path.join("static/events", fn)
    await file.download_to_drive(path)
    imgs.append(f"events/{fn}")
    await update.message.reply_text(f"📷 Доп. фото {len(imgs)}/20 сохранено.")
    return EV_GALLERY

async def done_gallery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✍️ Введите статью или /skip_article для ссылки:"
    )
    return EV_ARTICLE

async def receive_event_article(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["article"] = update.message.text
    context.user_data["link"] = None
    return await _save_event(update, context)

async def skip_article(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔗 Введите внешнюю ссылку на событие:")
    return EV_LINK

async def receive_event_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["link"] = update.message.text
    context.user_data["article"] = None
    return await _save_event(update, context)

async def _save_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = context.user_data
    db = SessionLocal()
    ev = Event(
        title=d["title"],
        description=d["description"],
        date=d["date"],
        image=d["image"],
        article=d.get("article"),
        link=d.get("link")
    )
    db.add(ev)
    db.flush()
    for img in d["extra_images"]:
        db.add(EventImage(event_id=ev.id, image_path=img))
    db.commit()

    # Оставляем только последние 15
    MAX = 15
    ids = [i for (i,) in db.query(Event.id).order_by(Event.date.desc()).all()]
    if len(ids) > MAX:
        old_ids = ids[MAX:]
        db.query(EventImage).filter(EventImage.event_id.in_(old_ids)).delete(synchronize_session=False)
        db.query(Event).filter(Event.id.in_(old_ids)).delete(synchronize_session=False)
        db.commit()

    db.close()
    await update.message.reply_text("✅ Событие добавлено.")
    return ConversationHandler.END

# ==============================================================================
#                          ФУНКЦИИ ДЛЯ delete_event
# ==============================================================================

async def delete_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    events = db.query(Event).order_by(Event.date.desc()).all()
    db.close()

    if not events:
        return await update.message.reply_text("❌ Нет ни одного события в базе.")

    keyboard = []
    for e in events:
        # короткое описание, чтобы в кнопке было «ID — Заголовок»
        title = (e.title[:30] + '…') if len(e.title) > 30 else e.title
        keyboard.append([
            InlineKeyboardButton(
                text=f"{e.id} — {title}",
                callback_data=f"del_event:{e.id}"
            )
        ])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Выберите событие для удаления:",
        reply_markup=reply_markup
    )

# Обработчик нажатий на кнопки удаления события
async def cb_delete_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # callback_data имеет вид "del_event:<ID>"
    _, eid_str = query.data.split(":")
    eid = int(eid_str)

    db = SessionLocal()
    ev = db.query(Event).get(eid)
    if not ev:
        text = f"❌ Событие с ID {eid} не найдено."
    else:
        title = ev.title
        # удаляем галерею
        db.query(EventImage).filter(EventImage.event_id == eid).delete()
        # удаляем само событие
        db.delete(ev)
        db.commit()
        text = f"🗑️ Событие «{title}» (ID {eid}) удалено."
    db.close()

    # заменяем сообщение с кнопками на итоговое
    await query.edit_message_text(text)

# ---------------------------
# Общий cancel
# ---------------------------
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 Операция отменена.")
    return ConversationHandler.END

# ==============================================================================
#                                  MAIN
# ==============================================================================

def main():
    token = os.getenv("BOT_TOKEN")
    app = Application.builder() \
        .token(token) \
        .build()

    # Handler для add_teacher
    teacher_conv = ConversationHandler(
        entry_points=[CommandHandler("add_teacher", start_teacher)],
        states={
            PHOTO:    [MessageHandler(filters.PHOTO | filters.Document.IMAGE, receive_teacher_photo)],
            NAME:     [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_teacher_name)],
            POSITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_teacher_position)],
            EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_teacher_experience)],
            T_LINK:   [
                CommandHandler("skip_link", skip_teacher_link),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_teacher_link)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Handler для add_event
    event_conv = ConversationHandler(
        entry_points=[CommandHandler("add_event", start_event)],
        states={
            EV_IMG:     [
                MessageHandler(filters.PHOTO | filters.Document.IMAGE, receive_event_image),
                CommandHandler("skip_image", skip_image)
            ],
            EV_TITLE:   [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_event_title)],
            EV_DESC:    [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_event_desc)],
            EV_DATE:    [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_event_date)],
            EV_GALLERY:[
                MessageHandler(filters.PHOTO | filters.Document.IMAGE, receive_extra_photo),
                CommandHandler("done_gallery", done_gallery)
            ],
            EV_ARTICLE:[
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_event_article),
                CommandHandler("skip_article", skip_article)
            ],
            EV_LINK:   [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_event_link)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    # Команды удаления
    delete_teacher_h = CommandHandler("delete_teacher", delete_teacher)
    delete_event_h   = CommandHandler("delete_event",   delete_event)

    app.add_handler(
        CallbackQueryHandler(
            cb_delete_teacher,
            pattern=r"^del_teacher:"  # будем ловить только callback_data, начинающуюся с "del_teacher:"
        )
    )

    app.add_handler(teacher_conv)
    app.add_handler(event_conv)
    app.add_handler(delete_teacher_h)
    app.add_handler(delete_event_h)

    app.add_handler(
        CallbackQueryHandler(
            cb_delete_event,
            pattern=r"^del_event:"
        )
    )

    app.run_polling()

if __name__ == "__main__":
    main()
