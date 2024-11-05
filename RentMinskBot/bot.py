import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import TOKEN, AUTHORIZED_USERS  # Импортируем массив AUTHORIZED_USERS
from parsers.kufar_rooms import parse_kufar_rooms

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Глобальная переменная для отслеживания состояния парсинга
is_parsing = False

# Проверка авторизации пользователя
def is_authorized(user_id: int) -> bool:
    return user_id in AUTHORIZED_USERS  # Проверяем, есть ли user_id в массиве AUTHORIZED_USERS

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if is_authorized(user_id):
        await update.message.reply_text(
            "Привет! Я бот для поиска квартир и комнат в Минске. Используйте /pars для старта парсинга."
        )
    else:
        await update.message.reply_text("Вы не авторизованы для использования этого бота.")

# Команда /pars
async def pars(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global is_parsing
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("Вы не авторизованы для использования этого бота.")
        return

    if is_parsing:
        await update.message.reply_text("Парсинг уже запущен. Используйте /stop для его остановки.")
        return

    is_parsing = True
    await update.message.reply_text("Начинаю парсинг...")

    listings = []

    # Получаем объявления с сайта Kufar
    try:
        listings.extend(parse_kufar_rooms())
    except Exception as e:
        logger.error(f"Ошибка при парсинге: {e}")
        await update.message.reply_text("Произошла ошибка при парсинге данных.")
        is_parsing = False
        return

    # Формируем ответ
    if listings:
        for listing in listings[:10]:  # Ограничиваем количество отправляемых объявлений
            await update.message.reply_text(
                f"Ссылка: {listing['link']}\n"
                f"Адрес: {listing['address']}\n"
                f"Цена: {listing['price']}"
            )
    else:
        await update.message.reply_text("Объявления не найдены.")

    is_parsing = False  # Завершаем парсинг

# Команда /stop
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global is_parsing
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("Вы не авторизованы для использования этого бота.")
        return

    if is_parsing:
        is_parsing = False  # Остановка парсинга
        await update.message.reply_text("Парсинг остановлен.")
    else:
        await update.message.reply_text("Парсинг остановлен.")

def main() -> None:
    # Создаем объект Application и передаем ему токен бота
    application = ApplicationBuilder().token(TOKEN).build()

    # Регистрация команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("pars", pars))
    application.add_handler(CommandHandler("stop", stop))  # Регистрация команды /stop

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
