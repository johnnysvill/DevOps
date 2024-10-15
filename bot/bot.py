import logging
import psycopg2
import re
import paramiko
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from dotenv import load_dotenv
import os
from psycopg2 import OperationalError
import subprocess

load_dotenv()

# Получаем значения из переменных окружения
TOKEN = os.getenv('TOKEN')
RM_HOST = os.getenv('RM_HOST')
RM_PORT = os.getenv('RM_PORT')
RM_USER = os.getenv('RM_USER')
RM_PASSWORD = os.getenv('RM_PASSWORD')
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_REPL_USER = os.getenv("DB_REPL_USER")
DB_REPL_PASSWORD = os.getenv("DB_REPL_PASSWORD")
DB_REPL_HOST = os.getenv("DB_REPL_HOST")
DB_REPL_PORT = os.getenv("DB_REPL_PORT")

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def run_ssh_command(command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=RM_HOST, port=int(RM_PORT), username=RM_USER, password=RM_PASSWORD)
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    client.close()
    return output

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def helpCommand(update: Update, context):
    update.message.reply_text('Help!')


def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'findPhoneNumbers'


def findPhoneNumbers(update: Update, context):
    user_input = update.message.text  # Получаем текст, содержащий(или нет) номера телефонов
    phoneNumRegex = re.compile(
        r'\+?7[ -]?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}|\+?7[ -]?\d{10}|8[ -]?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}|8[ -]?\d{10}')
    phoneNumberList = phoneNumRegex.findall(user_input)  # Ищем номера телефонов
    if not phoneNumberList:  # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return  # Завершаем выполнение функции

    phoneNumbers = ''  # Создаем строку, в которую будем записывать номера телефонов
    for i, p in enumerate(phoneNumberList):
        phoneNumber = ''.join(p)
        phoneNumbers += f'{i + 1}. {phoneNumber}\n'  # Записываем очередной номер

    update.message.reply_text(phoneNumbers)  # Отправляем сообщение пользователю
    update.message.reply_text('Хотите записать найденные телефонные номера в базу данных? (Да/Нет)')

    # Сохраняем найденные номера телефонов в user_data
    context.user_data['phone_numbers_to_write'] = phoneNumberList  # Используем user_data для хранения

    return 'confirm_phone_write'

def findEmailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска email-адресов: ')

    return 'findEmails'


def findEmails(update: Update, context):
    user_input = update.message.text
    email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    email_list = email_regex.findall(user_input)

    if not email_list:
        update.message.reply_text('Email-адреса не найдены')
        return

    emails = ''
    for i, email in enumerate(email_list):
        emails += f'{i + 1}. {email}\n'

    update.message.reply_text(emails)
    update.message.reply_text('Хотите записать найденные email-адреса в базу данных? (Да/Нет)')

    # Сохраняем email-адреса в context.user_data
    context.user_data['emails_to_write'] = email_list
    return 'confirm_email_write'

def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки: ')
    return 'verifyPassword'

def verifyPassword(update: Update, context):
    user_input = update.message.text
    password_regex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()]).{8,}$')
    if password_regex.match(user_input):
        update.message.reply_text('Пароль сложный')
    else:
        update.message.reply_text('Пароль простой')
    return ConversationHandler.END

def get_release(update, context):
    output = run_ssh_command('cat /etc/*-release')
    update.message.reply_text(output)

def get_uname(update, context):
    output = run_ssh_command('uname -a')
    update.message.reply_text(output)

def get_uptime(update, context):
    output = run_ssh_command('uptime')
    update.message.reply_text(output)

def get_df(update, context):
    output = run_ssh_command('df -h')
    update.message.reply_text(output)

def get_free(update, context):
    output = run_ssh_command('free -h')
    update.message.reply_text(output)

def get_mpstat(update, context):
    output = run_ssh_command('mpstat')
    update.message.reply_text(output)

def get_w(update, context):
    output = run_ssh_command('w')
    update.message.reply_text(output)

def get_auths(update, context):
    output = run_ssh_command('last -n 10')
    update.message.reply_text(output)

def get_critical(update, context):
    output = run_ssh_command('journalctl -p crit -n 5')
    update.message.reply_text(output)

def get_ps(update, context):
    output = run_ssh_command('ps aux | head -n 10')
    update.message.reply_text(output)

def get_ss(update, context):
    output = run_ssh_command('ss -tuln')
    update.message.reply_text(output)

def get_apt_list_command(update: Update, context):
    update.message.reply_text("Введите 'all' для вывода всех установленных пакетов или введите название пакета для поиска информации о нем:")
    return 'get_apt_list'

def get_apt_list(update: Update, context):
    user_input = update.message.text.strip().lower()

    # Определяем команду для выполнения на удаленном сервере
    if user_input == 'all':
        ssh_command = "apt list --installed | tail -n 10"
    else:
        ssh_command = f"apt list --installed | grep {user_input} | tail -n 20"

    # Используем уже имеющуюся функцию для выполнения команды
    output = run_ssh_command(ssh_command)

    # Проверяем, есть ли вывод, и отправляем результат
    if output:
        logging.info(f"Command output: {output}")
        update.message.reply_text(output)  # Отправляем вывод пользователю
    else:
        update.message.reply_text("Команда не вернула никаких данных.")  # Сообщаем, если нет данных

    return ConversationHandler.END

def get_services(update, context):
    output = run_ssh_command('systemctl list-units --type=service --state=running | head -n 10')
    update.message.reply_text(output)

def get_repl_logs(update: Update, context):
    logger.info("Пользователь %s запросил логи о репликации.", update.effective_user.full_name)
    command = "cat /var/log/postgresql/postgresql.log | grep 'repl' | tail -n 10"
    res = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0 or res.stderr.decode() != "":
        logger.error("Ошибка при выводе логов репликации: %s", res.stderr.decode())
    else:
        update.message.reply_text(res.stdout.decode().strip('\n'))


def get_emails(update, context):
    try:
        # Подключение к базе данных, используя данные из переменных окружения
        conn = psycopg2.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_DATABASE")
        )

        with conn:
            with conn.cursor() as cur:
                # Выполнение запроса для получения email-адресов
                cur.execute("SELECT * FROM Email;")
                rows = cur.fetchall()

        # Формирование ответа
        if rows:
            response_text = "Список email-адресов:\n"
            for index, row in enumerate(rows, start=1):
                response_text += f"{index}. {row[1]}\n"
        else:
            response_text = "В базе данных нет записей email."

    except OperationalError as e:
        # Обработка ошибки подключения к базе данных
        response_text = f"Ошибка подключения к базе данных: {str(e)}"
    except Exception as e:
        # Обработка остальных ошибок
        response_text = f"Произошла ошибка: {str(e)}"
    finally:
        # Отправляем сообщение пользователю
        update.message.reply_text(response_text)

def get_phone_numbers(update, context):
    try:
        # Подключение к базе данных с использованием переменных окружения
        conn = psycopg2.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_DATABASE")
        )

        # Использование контекстного менеджера для безопасной работы с курсором
        with conn:
            with conn.cursor() as cur:
                # Выполнение запроса для получения номеров телефонов
                cur.execute("SELECT * FROM phone_number;")
                rows = cur.fetchall()

        # Формирование ответа
        if rows:
            response_text = "Список номеров телефонов:\n"
            for index, row in enumerate(rows, start=1):
                response_text += f"{index}. {row[1]}\n"
        else:
            response_text = "В базе данных нет записей номеров телефонов."

    except OperationalError as e:
        # Обработка ошибки подключения к базе данных
        response_text = f"Ошибка подключения к базе данных: {str(e)}"
    except Exception as e:
        # Обработка остальных ошибок
        response_text = f"Произошла ошибка: {str(e)}"
    finally:
        # Отправляем сообщение пользователю
        update.message.reply_text(response_text)

def confirm_email_write(update: Update, context):
    user_response = update.message.text.lower().strip()

    if user_response == 'да':
        try:
            # Извлекаем список email-адресов из context.user_data
            emails = context.user_data.get('emails_to_write', [])

            if not emails:
                update.message.reply_text('Нет email-адресов для записи.')
                return ConversationHandler.END

            # Подключение к базе данных с использованием переменных окружения
            conn = psycopg2.connect(
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                database=os.getenv("DB_DATABASE")
            )

            with conn:
                with conn.cursor() as cur:
                    # Вставка каждого email-адреса в базу данных
                    for email in emails:
                        cur.execute("INSERT INTO email (email_address) VALUES (%s);", (email,))

            # Подтверждение успешной записи
            update.message.reply_text('Email-адреса успешно записаны в базу данных')

        except OperationalError as e:
            update.message.reply_text(f'Ошибка подключения к базе данных: {str(e)}')
        except Exception as e:
            update.message.reply_text(f'Произошла ошибка: {str(e)}')

    else:
        # Сообщаем об отмене записи
        update.message.reply_text('Запись email-адресов в базу данных отменена')

    return ConversationHandler.END


def confirm_phone_write(update: Update, context):
    user_response = update.message.text.lower().strip()

    # Проверяем, что пользователь ответил "да"
    if user_response == 'да':
        try:
            # Преобразуем список номеров в строку, получая его из user_data
            phone_numbers = context.user_data.get('phone_numbers_to_write', [])

            # Подключение к базе данных с использованием переменных окружения
            conn = psycopg2.connect(
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                database=os.getenv("DB_DATABASE")
            )

            with conn:
                with conn.cursor() as cur:
                    # Вставка каждого номера телефона в базу данных
                    for number in phone_numbers:
                        cur.execute("INSERT INTO phone_number (phone_number) VALUES (%s);", (number,))

            # Подтверждаем успешное выполнение записи
            update.message.reply_text('Телефонные номера успешно записаны в базу данных')

        except OperationalError as e:
            update.message.reply_text(f'Ошибка подключения к базе данных: {str(e)}')
        except Exception as e:
            update.message.reply_text(f'Произошла ошибка: {str(e)}')

    else:
        # Сообщаем об отмене записи
        update.message.reply_text('Запись телефонных номеров в базу данных отменена')

    return ConversationHandler.END

def echo(update: Update, context):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'confirm_phone_write': [MessageHandler(Filters.text & ~Filters.command, confirm_phone_write)]
        },
        fallbacks=[]
    )

    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailCommand)],
        states={'findEmails': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
                'confirm_email_write': [MessageHandler(Filters.text & ~Filters.command, confirm_email_write)]
        },
        fallbacks=[]
    )

    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={'verifyPassword': [MessageHandler(Filters.text & ~Filters.command, verifyPassword)]},
        fallbacks=[]
    )

    conv_handler_get_apt_list = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_list_command)],
        states={'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)]},
        fallbacks=[]
    )

    dp.add_handler(conv_handler_get_apt_list)

    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))

    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerVerifyPassword)

    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_apt_list", get_apt_list))
    dp.add_handler(CommandHandler("get_services", get_services))

    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))

    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))

    # Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
