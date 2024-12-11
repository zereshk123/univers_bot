import asyncio
import random
import sqlite3
from datetime import datetime
import sys
sys.stdout.reconfigure(encoding='utf-8') 

try:
    import pytz
    tehran_tz = pytz.timezone('Asia/Tehran')
except ImportError:
    print("please install 'pytz' library => pip install pytz")

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters , CallbackQueryHandler, CallbackContext, Updater
except ImportError:
    print("please install 'python-telegram-bot' library => pip install python-telegram-bot")

try:
    import jdatetime
except ImportError:
    print("please install 'jdatetime' library => pip install jdatetime")


# --- دیتابیس ---
def auth_db():
    with sqlite3.connect('data.db') as connection:
        cursor = connection.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins(
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS message(
            id INTEGER PRIMARY KEY,
            message TEXT NOT NULL
        )''')
    print("database checked✅\n")

app = None

token = "7237654549:AAEv2ygfu56Y3_El9D5vgXE4DbusmN18TT0"
link_web_app = "https://alikakaee.ir/bot/"
waiting_for_message = {}
admin_creation_state = {}
admin_edit_homework_state = {}
admin_del_state = {}
user_status = {}
reminder_state = {}

async def start(update: Update, context: CallbackContext) -> None:
    user_id = str(update.effective_user.id)

    inline_keyboard = [
        [InlineKeyboardButton("🌐 نمایش اطلاعیه ها 🌐",web_app={'url':f'{link_web_app}'})],
        [InlineKeyboardButton("📝 نمایش تکالیف 📝", callback_data="show_homework")]
    ]

    inline_keyboard.append([
        InlineKeyboardButton("™ درباره ما ™", callback_data="about_us"),
        InlineKeyboardButton("👨‍💻 پشتیبانی 👨‍💻", callback_data="talk_admins")
    ])


    #__ دکمه های ادمین __
    with sqlite3.connect('data.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT user_id FROM admins WHERE user_id = ?', (user_id,))
        is_admin = cursor.fetchone()

        if is_admin:
            inline_keyboard.append([InlineKeyboardButton("🟥🟥🟥🟥 دسترسی ادمین ها 🟥🟥🟥🟥", callback_data="no_action")])
            inline_keyboard.append(
                [InlineKeyboardButton("📝 ثبت یادآوری 📝", callback_data="set_reminder")]
            )
            inline_keyboard.append([
                InlineKeyboardButton("👨‍👦‍👦 ادمین ها 👨‍👦‍👦", callback_data="show_admins"),
                InlineKeyboardButton("✍ ویرایش تکالیف ✍", callback_data="edit_homework")
            ])
            inline_keyboard.append([
                InlineKeyboardButton("➕ افزودن ادمین ➕", callback_data="add_admin"),
                InlineKeyboardButton("➖ حذف ادمین ➖", callback_data="del_admin")
            ])
    
    inline_markup = InlineKeyboardMarkup(inline_keyboard)

    if update.message:
        await update.message.reply_text(
            "سلام ببعی جان...\nچه کمکی از دستم بر میاد؟😁",
            reply_markup=inline_markup
        )
    elif update.callback_query:
        await update.callback_query.message.edit_text(
            "سلام ببعی جان...\nچه کمکی از دستم بر میاد؟😁",
            reply_markup=inline_markup
        )



async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    query = update.callback_query
    await query.answer()

    inline_keyboard = [[InlineKeyboardButton("🔙 برگشتن", callback_data="back")]]
    inline_markup = InlineKeyboardMarkup(inline_keyboard)

    if query.data == "about_us":
        await query.edit_message_text(
            "™ تیم سازندگان ربات:\n\n™ محمدرضا حیدری  @mheydari006\n™ علی کاکائی @Akakaee",
            reply_markup=inline_markup
        )
        return

    elif query.data == "back":
        inline_keyboard = [
            [InlineKeyboardButton("🌐 نمایش اطلاعیه ها 🌐", url=f'{link_web_app}')],
            [InlineKeyboardButton("📝 نمایش تکالیف 📝", callback_data="show_homework")]
        ]
        inline_keyboard.append([
            InlineKeyboardButton("™ درباره ما ™", callback_data="about_us"),
            InlineKeyboardButton("👨‍💻 پشتیبانی 👨‍💻", callback_data="talk_admins")
        ])

        inline_markup = InlineKeyboardMarkup(inline_keyboard)

        #__ دکمه های ادمین __
        with sqlite3.connect('data.db') as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT user_id FROM admins WHERE user_id = ?', (user_id,))
            is_admin = cursor.fetchone()

            if is_admin:
                inline_keyboard.append([InlineKeyboardButton("🟥🟥🟥🟥 دسترسی ادمین ها 🟥🟥🟥🟥", callback_data="None")])
        
                inline_keyboard.append(
                    [InlineKeyboardButton("📝 ثبت یادآوری 📝", callback_data="set_reminder")]
                )
                inline_keyboard.append([
                    InlineKeyboardButton("👨‍👦‍👦 ادمین ها 👨‍👦‍👦", callback_data="show_admins"),
                    InlineKeyboardButton("✍ ویرایش تکالیف ✍", callback_data="edit_homework")
                ])
                inline_keyboard.append([
                    InlineKeyboardButton("➕ افزودن ادمین ➕", callback_data="add_admin"),
                    InlineKeyboardButton("➖ حذف ادمین ➖", callback_data="del_admin")
                ])

        inline_markup = InlineKeyboardMarkup(inline_keyboard)

        await query.edit_message_text(
            "سلام ببعی جان...\nچه کمکی از دستم بر میاد؟😁",
            reply_markup=inline_markup
        )
        return
    
    elif query.data == "show_admins":
        user_id = str(update.effective_user.id)

        with sqlite3.connect('data.db') as connection:
                cursor = connection.cursor()
                cursor.execute('SELECT user_id FROM admins WHERE user_id = ?', (user_id,))
                is_admin = cursor.fetchone()

        inline_keyboard = [[InlineKeyboardButton("کدوم دستورات❓", callback_data="back")]]
        inline_markup = InlineKeyboardMarkup(inline_keyboard)
        
        if is_admin: 
            query = update.callback_query
            await query.answer()
            
            with sqlite3.connect('data.db') as connection:
                cursor = connection.cursor()

                cursor.execute('SELECT user_id, name FROM admins')
                admins = cursor.fetchall()
                
                if admins:
                    inline_keyboard = [
                        [InlineKeyboardButton(f"{idx + 1}) {name}  /--/  USER-ID: {admin_id})", callback_data="_")]
                        for idx, (admin_id, name) in enumerate(admins)
                    ]

                    inline_keyboard.append([
                        InlineKeyboardButton("🔙 برگشتن", callback_data="back")
                    ])

                    inline_markup = InlineKeyboardMarkup(inline_keyboard)
                    message = "🔶 لیست ادمین‌ها:\n\n"
                else:
                    message = "چیز عجیبیه ولی ادمینی وجود نداره🤔"
                    inline_markup = InlineKeyboardMarkup([])

                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=message,
                    reply_to_message_id=update.effective_message.id,
                    reply_markup=inline_markup
                )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="فضولیت گل کرده ها😂\nاین دستورا برا بزرگتراس تو فقط میتونی با دستوراتی که بهت میدم کار کنی😁👌",
                reply_to_message_id=update.effective_message.id,
                reply_markup=inline_markup
            )

        return

    elif query.data == "add_admin":
        user_id = str(update.effective_user.id)

        with sqlite3.connect('data.db') as connection:
                cursor = connection.cursor()
                cursor.execute('SELECT user_id FROM admins WHERE user_id = ?', (user_id,))
                is_admin = cursor.fetchone()

        inline_keyboard = [[InlineKeyboardButton("کدوم دستورات❓", callback_data="back")]]
        inline_markup = InlineKeyboardMarkup(inline_keyboard)
        
        if is_admin:    
            admin_creation_state[user_id] = {"step": True}
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="🔶 اسم ادمین جدید رو چی بزارم؟"
            )
        
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="فضولیت گل کرده ها😂\nاین دستورا برا بزرگتراس تو فقط میتونی با دستوراتی که بهت میدم کار کنی😁👌",
                reply_to_message_id=update.effective_message.id,
                reply_markup=inline_markup
            )
    
        return

    elif query.data == "del_admin":
        user_id = str(update.effective_user.id)

        with sqlite3.connect('data.db') as connection:
                cursor = connection.cursor()
                cursor.execute('SELECT user_id FROM admins WHERE user_id = ?', (user_id,))
                is_admin = cursor.fetchone()

        inline_keyboard = [[InlineKeyboardButton("کدوم دستورات❓", callback_data="back")]]
        inline_markup = InlineKeyboardMarkup(inline_keyboard)
        
        if is_admin:
            admin_del_state[user_id] = {"step": 1}
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="🔶 یوزر آیدی ادمین مورد نظر رو وارد کن:"
            )
        
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="فضولیت گل کرده ها😂\nاین دستورا برا بزرگتراس تو فقط میتونی با دستوراتی که بهت میدم کار کنی😁👌",
                reply_to_message_id=update.effective_message.id,
                reply_markup=inline_markup
            )

        return

    elif query.data == "show_homework":
        query = update.callback_query
        await query.answer()

        with sqlite3.connect('data.db') as connection:
            cursor = connection.cursor()

            cursor.execute('SELECT message FROM message')
            homework = cursor.fetchall()
            homework_text = "\n".join([row[0] for row in homework])
            
            if homework:
                inline_keyboard = [[InlineKeyboardButton("🔙 برگشتن", callback_data="back")]]
               
                inline_markup = InlineKeyboardMarkup(inline_keyboard)
                message = homework_text
            else:
                message = "انگار تکلیفی نداری🤔\nجهت اطمینان از بچه های گروه هم بپرس بعدا نندازی گردن من😬🙌"
                inline_markup = InlineKeyboardMarkup([])

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
                reply_to_message_id=update.effective_message.id,
                reply_markup=inline_markup
            )

        return

    elif query.data == "edit_homework":
            user_id = str(update.effective_user.id)

            with sqlite3.connect('data.db') as connection:
                    cursor = connection.cursor()
                    cursor.execute('SELECT user_id FROM admins WHERE user_id = ?', (user_id,))
                    is_admin = cursor.fetchone()

            inline_keyboard = [[InlineKeyboardButton("کدوم دستورات❓", callback_data="back")]]
            inline_markup = InlineKeyboardMarkup(inline_keyboard)
            
            if is_admin:    
                admin_edit_homework_state[user_id] = {"step": True}
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="🔶 متن تکالیف هارو بفرست:"
                )
            
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="فضولیت گل کرده ها😂\nاین دستورا برا بزرگتراس تو فقط میتونی با دستوراتی که بهت میدم کار کنی😁👌",
                    reply_to_message_id=update.effective_message.id,
                    reply_markup=inline_markup
                )
        
            return

    elif query.data == "talk_admins":
        user_id = str(update.effective_user.id)
        user_status[user_id] = {"step": True}
        await query.edit_message_text("هرچی میخوای بنویس من میفرستم برا ادمین😁:")

    elif query.data == "set_reminder":
        user_id = str(update.effective_user.id)
        reminder_state[user_id] = {"step": 1}

        await query.edit_message_text("یه تاریخ و زمان برای این یادآوری تنظیم کن:\nدقت کن باید تاریخ و زمان رو دقیقا به همین قالب بفرستی⬇\nYYYY-MM-DD HH:MM")
        return


async def check_reminders():
    while True:
        now = jdatetime.datetime.now(tehran_tz)
        now = now.strftime("%Y-%m-%d %H:%M")

        with sqlite3.connect('data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT chat_id, reminder_time, message FROM reminders')
            reminders = cursor.fetchall()

        for reminder in reminders:
            chat_id, reminder_time, message = reminder
            
            print(f"reminder= {reminder_time} && now= {now}")
            
            if reminder_time == now:
                print(f"Reminder sent to group {chat_id}: {message}")

                times = reminder_time.split(" ")
                await app.bot.send_message(
                    chat_id=chat_id,
                    text=f"🔴🔴 یادآوری 🔴🔴\n\n📅 تاریخ یادآوری: {times[0]}\n🕣 زمان یادآوری: {times[1]}\n\n💡 متن یادآوری: \n{message}\n\n🌟 موفق باشید! 🌟"
                )
                cursor.execute('DELETE FROM reminders WHERE reminder_time = ?', (reminder_time,))
                conn.commit()

    # زمان تا بررسی بعدی
        await asyncio.sleep(1)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = str(update.effective_message.text)

    #__ فرآیند ذخیره کردن یادآوری  __
    if user_id in reminder_state:

        inline_keyboard = [[InlineKeyboardButton("🔙 برگشتن", callback_data="back")]]
        inline_markup = InlineKeyboardMarkup(inline_keyboard)

        if reminder_state[user_id]["step"] == 1:
            reminder_state[user_id]["datetime"] = update.message.text  # ذخیره تاریخ و زمان
            try:
                datetime.strptime(reminder_state[user_id]["datetime"], '%Y-%m-%d %H:%M')

            except ValueError:
                await update.message.reply_text(
                    "❌ فرمت تاریخ/زمان نادرست است. لطفاً به صورت YYYY-MM-DD HH:MM وارد کنید!",
                    reply_to_message_id=update.effective_message.id,
                    reply_markup=inline_markup
                )
                
                del reminder_state[user_id]
                return

            reminder_state[user_id]["step"] = 2
            await update.message.reply_text("خیلی خب...\nحالا متن یادآوری رو بنویس:")
            return


        elif reminder_state[user_id]["step"] == 2:
            # دریافت متن یادآوری
            reminder_state[user_id]["message"] = update.message.text

            #ذخیره کردن یادآوری
            with sqlite3.connect('data.db') as connection:
                cursor = connection.cursor()
                cursor.execute('INSERT INTO reminders (chat_id, reminder_time, message) VALUES (?, ?, ?)', (update.effective_chat.id , reminder_state[user_id]["datetime"], reminder_state[user_id]["message"]))
                connection.commit()

            inline_keyboard = [
                [InlineKeyboardButton("🔙 برگشتن", callback_data="back")]
            ]
            inline_markup = InlineKeyboardMarkup(inline_keyboard)

            times = reminder_state[user_id]['datetime'].split(" ")

            await update.message.reply_text(
                f"یادآوری شما برای تاریخ {times[0]} و ساعت {times[1]} ثبت شد✅",
                reply_to_message_id=update.effective_message.id,
                reply_markup=inline_markup
            )

            del reminder_state[user_id]
            return

    #__ فرآیند پشتیبانی  __
    if user_id in user_status:
        start = user_status[user_id]

        if start["step"] == True:
            user_status.pop(user_id)
            sender_name = update.message.from_user.first_name
            username = update.message.from_user.username
            username_text = f"(@{username})" if username else "یوزرنیم نداره😬"
            message = update.message.text
            
            inline_keyboard = [
                [InlineKeyboardButton("🔙 برگشتن", callback_data="back")]
            ]
            inline_markup = InlineKeyboardMarkup(inline_keyboard)

            with sqlite3.connect('data.db') as connection:
                cursor = connection.cursor()
                
                cursor.execute("SELECT user_id FROM admins")
                admins = [row[0] for row in cursor.fetchall()]
                
                for admin_id in admins:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=f"پیامی از {sender_name} {username_text}:\n\n{message}"
                    )
                        
                await update.message.reply_text(
                    "پیامت رو فرستادم برا پشتیبانی✅\nاگه چیز مهمی بود بهت پیام  میدن",
                    reply_markup=inline_markup
                )
            
        connection.close()
        return

    #__ فرآیند حذف ادمین  __
    if user_id in admin_del_state:
        start = admin_del_state[user_id]

        if start["step"] == True:
            admin_del_state[user_id]["del_user_id"] = update.effective_message.text
            
            inline_keyboard = [
                [InlineKeyboardButton("🔙 برگشتن", callback_data="back")]
            ]
            inline_markup = InlineKeyboardMarkup(inline_keyboard)

            with sqlite3.connect('data.db') as connection:
                cursor = connection.cursor()
                try:
                    cursor.execute(
                        'DELETE FROM admins WHERE user_id = ?',
                        (admin_del_state[user_id]["del_user_id"],)
                    )
                    connection.commit()

                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"ادمین با یوزر آیدی {admin_del_state[user_id]['del_user_id']} با موفقیت حذف شد✅",
                        reply_to_message_id=update.effective_message.id,
                        reply_markup=inline_markup
                    )

                except sqlite3.IntegrityError:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"ادمین با یوزر آیدی {admin_del_state[user_id]['del_user_id']} وجود ندارد!! 😬",
                        reply_to_message_id=update.effective_message.id,
                        reply_markup=inline_markup
                    )
                    
        # پاک کردن وضعیت کاربر از دیکشنری
        del admin_del_state[user_id]
        return

    #__ فرآیند ادیت تکالیف __
    if user_id in admin_edit_homework_state:
        start = admin_edit_homework_state[user_id]

        if start["step"] == True:
            admin_edit_homework_state[user_id]["new_honework"] = update.effective_message.text
            
            inline_keyboard = [
                [InlineKeyboardButton("🔙 برگشتن", callback_data="back")]
            ]
            inline_markup = InlineKeyboardMarkup(inline_keyboard)

            with sqlite3.connect('data.db') as connection:
                cursor = connection.cursor()
                try:
                    cursor.execute('UPDATE message SET message = ? WHERE id = 1', (admin_edit_homework_state[user_id]["new_honework"],))
                    connection.commit()

                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"تکلیف جدید ذخیره شد✅",
                        reply_to_message_id=update.effective_message.id,
                        reply_markup=inline_markup
                    )

                except sqlite3.IntegrityError:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"یه مشکلی وجود داره باید کد هام بررسی بشه🤕\nبابا ببین چم شده @mheydari006🤒",
                        reply_to_message_id=update.effective_message.id,
                        reply_markup=inline_markup
                    )
                    
        # پاک کردن وضعیت کاربر از دیکشنری
        del admin_edit_homework_state[user_id]
        return

    #__ فرآیند افزودن ادمین  __
    if user_id in admin_creation_state:
        state = admin_creation_state[user_id]

       #__ مرحله 1 __
        if state["step"] == 1:
            admin_creation_state[user_id]["name"] = update.effective_message.text
            admin_creation_state[user_id]["step"] = 2

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="اسم ادمین با موفقیت ذخیره شد✅\nحالا یوزر آیدی ادمین جدید رو وارد کن:",
                reply_to_message_id=update.effective_message.id
            )
            return
        
        #__ مرحله 2 __
        elif state["step"] == 2:
            admin_creation_state[user_id]["user_id"] = update.effective_message.text
            admin_creation_state[user_id]["step"] = 3
            
            inline_keyboard=([
                [InlineKeyboardButton("🔙 برگشتن", callback_data="back")]
            ])
            inline_markup = InlineKeyboardMarkup(inline_keyboard)

            with sqlite3.connect('data.db') as connection:
                cursor = connection.cursor()
                try:
                    cursor.execute(
                        'INSERT INTO admins (user_id, name) VALUES (?, ?)',
                        (admin_creation_state[user_id]["user_id"], admin_creation_state[user_id]["name"])
                    )
                    connection.commit()

                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"ادمین با نام '{admin_creation_state[user_id]['name']}' و یوزر آیدی '{admin_creation_state[user_id]['user_id']}' ذخیره شد ✅",
                        reply_to_message_id=update.effective_message.id,
                        reply_markup=inline_markup
                    )

                except sqlite3.IntegrityError:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="این یوزر آیدی از قبل ادمین بوده!!😬",
                        reply_to_message_id=update.effective_message.id,
                        reply_markup=inline_markup
                    )

            # پاک کردن وضعیت کاربر از دیکشنری
            del admin_creation_state[user_id]
            return

    if waiting_for_message.get(user_id, False):
        with sqlite3.connect('data.db') as connection:
            cursor = connection.cursor()
            new_message = update.effective_message.text
            cursor.execute('UPDATE message SET message = ? WHERE id = 1', (new_message,))
            connection.commit()
        waiting_for_message[user_id] = False

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="پیامت با موفقیت ذخیره شد✅",
            reply_to_message_id=update.effective_message.id
        )

    if text == "ببعی" or text == "مهندس":
        random_num = random.randint(0, 2)
        
        inline_keyboard = [
            [InlineKeyboardButton("چی میخوای؟", callback_data="back")]
        ]
        inline_markup = InlineKeyboardMarkup(inline_keyboard)

        with sqlite3.connect('data.db') as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT text FROM awnser WHERE id = ?', (random_num,))
            anwser = cursor.fetchall()
            anwser_txt = "\n".join([row[0] for row in anwser])
            

            decoded_text = bytes(anwser_txt[0], 'utf-8').decode('unicode_escape')

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=anwser_txt,
                reply_to_message_id=update.effective_message.id,
                reply_markup=inline_markup
            )
            

    else:
        None
        
        # inline_keyboard = [
        #     [InlineKeyboardButton("🔙 برگشتن", callback_data="back")]
        # ]
        # inline_markup = InlineKeyboardMarkup(inline_keyboard)

        # await context.bot.send_message(
        #     chat_id=update.effective_chat.id,
        #     text="چی میگی نمیفهمم😶\nمن این چیزا سرم نمیشه با دستوراتی بهت دادم میتونی با من حرف بزنی😁",
        #     reply_to_message_id=update.effective_message.id,
        #     reply_markup=inline_markup
        # )



# async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await context.bot.send_message(
#         chat_id=update.effective_chat.id,
#         text="این بخش فعلاً در دسترس نیست.",
#         reply_to_message_id=update.effective_message.id
#     )


# async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = str(update.effective_user.id)
#     with sqlite3.connect('data.db') as connection:
#         cursor = connection.cursor()
#         cursor.execute('SELECT user_id FROM admins WHERE user_id = ?', (user_id,))
#         is_admin = cursor.fetchone()

#         if is_admin:  # کاربر مجاز است
#             args = context.args
            
#             if len(args) >= 2:
#                 new_user_id, new_user_name = args[0], " ".join(args[1:])

#                 try:
#                     cursor.execute('INSERT INTO admins (user_id, name) VALUES (?, ?)', (new_user_id, new_user_name))
#                     await context.bot.send_message(
#                         chat_id=update.effective_chat.id,
#                         text=f"ادمین جدید با اسم {new_user_name} و آیدی {new_user_id} به لیست ادمین های ربات اضافه شد✅\nبا دستور /showadmins میتونی اسم تمام ادمین هارو ببینی😀",
#                         reply_to_message_id=update.effective_message.id
#                     )

#                 except sqlite3.IntegrityError:
#                     await context.bot.send_message(
#                         chat_id=update.effective_chat.id,
#                         text=f"کاربری با یوزر آیدی {new_user_id} قبلا اضافه شده!😬",
#                         reply_to_message_id=update.effective_message.id
#                     )
#             else:
#                 await context.bot.send_message(
#                     chat_id=update.effective_chat.id,
#                     text="فرمت دستور درست نیست!\nباید به این صورت بنویسی⬇\n/addadmin [user-id] [name-admin]",
#                     reply_to_message_id=update.effective_message.id

#                 )

#         else:
#             await context.bot.send_message(
#                 chat_id=update.effective_chat.id,
#                 text="فضولیت گل کرده ها😂\nاین دستورا برا بزرگتراس تو فقط میتونی با دستوراتی که توی /help بهت گفتم کار کنی😁",
#                 reply_to_message_id=update.effective_message.id
#             )


# async def showadmins(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = str(update.effective_user.id)
#     with sqlite3.connect('data.db') as connection:
#         cursor = connection.cursor()
#         cursor.execute('SELECT user_id FROM admins WHERE user_id = ?', (user_id,))
#         is_admin = cursor.fetchone()

#         if is_admin:
#             cursor.execute('SELECT user_id, name FROM admins')
#             admins = cursor.fetchall()
            
#             if admins:
#                 message = "لیست ادمین‌ها:\n\n" + "\n".join(
#                     [f"{idx + 1}. {name} (USER-ID: {admin_id})" for idx, (admin_id, name) in enumerate(admins)]
#                 )
#             else:
#                 message = "چیز عجیبیه ولی ادمینی وجود نداره🤔"

#             await context.bot.send_message(
#                 chat_id=update.effective_chat.id,
#                 text=message,
#                 reply_to_message_id=update.effective_message.id
#             )

#         else:
#             await context.bot.send_message(
#                 chat_id=update.effective_chat.id,
#                 text="فضولیت گل کرده ها😂\nاین دستورا برا بزرگتراس تو فقط میتونی با دستوراتی که توی /help بهت گفتم کار کنی😁",
#                 reply_to_message_id=update.effective_message.id
#             )


# async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = str(update.effective_user.id)
#     with sqlite3.connect('data.db') as connection:
#         cursor = connection.cursor()
#         cursor.execute('SELECT user_id FROM admins WHERE user_id = ?', (user_id,))
#         is_admin = cursor.fetchone()

#         if is_admin:
#             waiting_for_message[user_id] = True
#             await update.message.reply_text("لطفاً پیامی که می‌خواهید تنظیم شود را ارسال کنید.")
#         else:
#             await context.bot.send_message(
#                 chat_id=update.effective_chat.id,
#                 text="شما دسترسی به این بخش ندارید."
#             )


# --- راه‌اندازی ---
async def run_telegram_bot():
    print("Telegram bot is initializing...")
    global app  # استفاده از متغیر گلوبال
    app = Application.builder().token(token).build()
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler('start', start))
    # app.add_handler(CommandHandler('help', help))
    # app.add_handler(CommandHandler('addadmin', addadmin))
    # app.add_handler(CommandHandler('showadmins', showadmins))
    # app.add_handler(CommandHandler('edit', edit))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))

    print("Telegram bot is starting polling...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("Telegram bot is running!")

async def main():
    await asyncio.gather(
        run_telegram_bot(),
        check_reminders()
    )

auth_db()
asyncio.run(main())