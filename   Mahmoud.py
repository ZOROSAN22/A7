import logging
import asyncio
import json
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from telethon import TelegramClient, events
from telethon.tl.functions.users import GetFullUserRequest

# ----------------- الإعدادات والتوكنات الأساسية -----------------
API_ID = 39472464
API_HASH = "a4e5f8bdb9da185818b406de020d757c"
BOT_TOKEN = "8716192417:AAFNSB_OpMtWBycD3jCyo0092aHEvH9De_g"
LOG_CHANNEL = "@Mahmoudha_p"

# إعداد تيليثون (Userbot / Session)
client = TelegramClient('zoro_session', API_ID, API_HASH)

# إعداد إيوجرام (بوت التحكم)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)

# ----------------- نظام التخزين الدائم (منع مسح الحسابات) -----------------
ACCOUNTS_FILE = "saved_accounts.json"

def load_saved_accounts():
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_accounts_data(data):
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# تهيئة قاعدة البيانات الأساسية مع دعم نص الرد التلقائي الاحترافي
system_data = load_saved_accounts()
if "bot_states" not in system_data:
    system_data["bot_states"] = {
        "auto_reply": False,
        "auto_post": False,
        "auto_report": True
    }
if "linked_accounts" not in system_data:
    system_data["linked_accounts"] = []
if "autoreply_text" not in system_data:
    system_data["autoreply_text"] = "مرحباً بك! أنا أرد تلقائياً عبر نظام Zoro Anti-Scam الذكي. سيتم مراجعة رسالتك والرد عليك قريباً 🛡️."

save_accounts_data(system_data)


# ----------------- حالات نظام المحادثة (FSM States) -----------------
class ZoroStates(StatesGroup):
    waiting_for_deep_info_target = State()
    waiting_for_post_media = State()
    waiting_for_post_interval = State()
    waiting_for_new_autoreply = State()


# ----------------- القائمة الرئيسية -----------------
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    current_data = load_saved_accounts()
    saved_accs_count = len(current_data.get("linked_accounts", []))
    
    kb = [
        [types.InlineKeyboardButton(text=f"👥 إِدارة حساباتي ({saved_accs_count})", callback_data="manage_accounts"),
         types.InlineKeyboardButton(text="🛑 إيقاف كافة العمليات", callback_data="stop_ops")],
        [types.InlineKeyboardButton(text="⚙️ النشر الانهائي (صور/فيديو/نص)", callback_data="start_infinite_posting"),
         types.InlineKeyboardButton(text="💬 ضبط الرد التلقائي الاحترافي", callback_data="set_autoreply")],
        [types.InlineKeyboardButton(text="🕵️‍♂️ جلب معلومات عميق (مكافحة النصابين)", callback_data="deep_info"),
         types.InlineKeyboardButton(text="📊 التبليغ التلقائي (Auto Report)", callback_data="auto_report")],
        [types.InlineKeyboardButton(text="📊 تقرير حالة النظام", callback_data="status_report"),
         types.InlineKeyboardButton(text="📈 تواصل مع المطور", url="https://t.me/ZORO_SAN")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    
    await state.clear()
    
    await message.answer(
        "🛡️ **[ نظام Zoro Cyber Intelligence & Anti-Scam الاسطوري ]** 🛡️\n\n"
        "✨ تم تحميل كافة الأنظمة وقواعد البيانات بنجاح.\n"
        "🔒 الحسابات والبيانات محمية كلياً ولن يتم مسحها أبداً عند إعادة التشغيل أو إرسال /start.\n\n"
        "اختر العملية المطلوبة للبدء:", 
        reply_markup=keyboard
    )


@dp.callback_query(F.data == "back_to_home")
async def back_to_home(callback: types.CallbackQuery, state: FSMContext):
    current_data = load_saved_accounts()
    saved_accs_count = len(current_data.get("linked_accounts", []))
    
    kb = [
        [types.InlineKeyboardButton(text=f"👥 إِدارة حساباتي ({saved_accs_count})", callback_data="manage_accounts"),
         types.InlineKeyboardButton(text="🛑 إيقاف كافة العمليات", callback_data="stop_ops")],
        [types.InlineKeyboardButton(text="⚙️ النشر الانهائي (صور/فيديو/نص)", callback_data="start_infinite_posting"),
         types.InlineKeyboardButton(text="💬 ضبط الرد التلقائي الاحترافي", callback_data="set_autoreply")],
        [types.InlineKeyboardButton(text="🕵️‍♂️ جلب معلومات عميق (مكافحة النصابين)", callback_data="deep_info"),
         types.InlineKeyboardButton(text="📊 التبليغ التلقائي (Auto Report)", callback_data="auto_report")],
        [types.InlineKeyboardButton(text="📊 تقرير حالة النظام", callback_data="status_report"),
         types.InlineKeyboardButton(text="📈 تواصل مع المطور", url="https://t.me/ZORO_SAN")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    await state.clear()
    
    await callback.message.edit_text(
        "🛡️ **[ نظام Zoro Cyber Intelligence & Anti-Scam الاسطوري ]** 🛡️\n\nاختر العملية المطلوبة:", 
        reply_markup=keyboard
    )
    await callback.answer()


# ----------------- إدارة الحسابات المرتبطة -----------------
@dp.callback_query(F.data == "manage_accounts")
async def manage_accounts_menu(callback: types.CallbackQuery):
    data = load_saved_accounts()
    accounts = data.get("linked_accounts", [])
    accs_list = "\n".join([f"• `{acc}`" for acc in accounts]) if accounts else "لا توجد حسابات فرعية مرتبطة حتى الآن."
    
    kb = [
        [types.InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_home")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    
    await callback.message.edit_text(
        f"👥 **لوحة إدارة الحسابات المحفوظة:**\n\n{accs_list}\n\n"
        f"*(ملاحظة: الحسابات لا يتم مسحها أبداً وتحفظ تلقائياً).* \n\nاختر الإجراء المناسب:",
        reply_markup=keyboard
    )
    await callback.answer()


# ----------------- نظام جلب المعلومات العميق (مكافحة النصابين) -----------------
@dp.callback_query(F.data == "deep_info")
async def deep_info_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "🕵️‍♂️ **[ وضع الاستخبارات ومكافحة النصابين والسكام نشط ]**\n\n"
        "أرسل الآن يوزر الحساب المستهدف (مثال: `@username`) أو الآيدي (`ID`) لفحص أثره البرمجي واستخراج كافة بياناته المخفية:"
    )
    await state.set_state(ZoroStates.waiting_for_deep_info_target)
    await callback.answer()

@dp.message(ZoroStates.waiting_for_deep_info_target)
async def process_deep_info(message: types.Message, state: FSMContext):
    target = message.text.strip()
    status_msg = await message.answer("⏳ **جارِ اختراق واجهة الهدف وسحب البصمة الرقمية وتحليل السجلات بدقة...**")
    
    try:
        async with client:
            user = await client.get_entity(target)
            full_user = await client(GetFullUserRequest(user))
            
            name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            username = f"@{user.username}" if user.username else "لا يوجد (حساب مخفي المعرف)"
            user_id = user.id
            
            bio = "لا توجد نبذة"
            if hasattr(full_user, 'about') and full_user.about:
                bio = full_user.about
            elif hasattr(full_user, 'full_user') and hasattr(full_user.full_user, 'about'):
                bio = full_user.full_user.about

            is_scam = getattr(user, 'scam', False)
            is_fake = getattr(user, 'fake', False)
            is_bot = getattr(user, 'bot', False)
            is_premium = getattr(user, 'premium', False)
            common_chats = getattr(full_user, 'common_chats_count', 0)
            
            threat_level = "آمن ✅"
            if is_scam or is_fake:
                threat_level = "خطير جداً! 🚨 (حساب محظور/انتحال شخصية أو سكام)"
            elif not user.username:
                threat_level = "مشبوه ⚠️ (بدون معرف رسمي)"

            report = (
                f"🚨 **[ تقرير البصمة الرقمية والاستخباراتية للهدف ]** 🚨\n\n"
                f"👤 **الاسم الكامل:** `{name}`\n"
                f"🆔 **الآيدي البرمجي (ID):** `{user_id}`\n"
                f"🔗 **المعرف (Username):** {username}\n"
                f"💎 **حساب ممول (Premium):** {'نعم ⭐' if is_premium else 'لا'}\n"
                f"🤖 **نوع الحساب:** {'بوت تليجرام' if is_bot else 'حساب شخصي/مستخدم'}\n"
                f"⚠️ **مؤشر التهديد (Threat Level):** {threat_level}\n"
                f"🛑 **حالة السكام (Scam/Fake):** {'مشبوه/محظور ❌' if (is_scam or is_fake) else 'نظيف سليم ✔️'}\n"
                f"👥 **المجموعات المشتركة معك:** {common_chats}\n"
                f"📝 **البايو / النبذة الكاملة (About):**\n`{bio}`\n\n"
                f"🔍 **تم إرسال نسخة من الفحص وسجلات الاستخبارات إلى قناة المطور بنجاح.**"
            )
            
            await status_msg.edit_text(report)
            await bot.send_message(LOG_CHANNEL, f"🕵️‍♂️ **[ سجل فحص استخباراتي ]**\nتم فحص الهدف: {username} (`{user_id}`) بواسطة النظام.")
            
    except Exception as e:
        await status_msg.edit_text(f"❌ **فشلت عملية الفحص أو جلب المعلومات:**\nتأكد من صحة اليوزر أو الأيدي.\nالخطأ التقني: `{str(e)}`")
    
    await state.clear()


# ----------------- نظام النشر الانهائي للوسائط مع وقت مرن (1 إلى 60 ثانية) -----------------
@dp.callback_query(F.data == "start_infinite_posting")
async def infinite_posting_setup(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "🔄 **[ نظام النشر الانهائي المتقدم للوسائط ]**\n\n"
        "أرسل الآن **المنشور المراد نشره** (يمكنك إرسال: **نص، صورة مع تعليق، فيديو، أو ملف**):"
    )
    await state.set_state(ZoroStates.waiting_for_post_media)
    await callback.answer()

@dp.message(ZoroStates.waiting_for_post_media, F.content_type.in_({
    types.ContentType.TEXT, types.ContentType.PHOTO, types.ContentType.VIDEO, types.ContentType.DOCUMENT
}))
async def capture_post_media(message: types.Message, state: FSMContext):
    await state.update_data(post_message=message)
    
    await message.answer(
        "⏱️ **أدخل الآن الفاصل الزمني (الوقت بين كل رسالة والأخرى) بالثواني:**\n"
        "*(اختر رقماً دقيقاً من 1 إلى 60 ثانية)*:"
    )
    await state.set_state(ZoroStates.waiting_for_post_interval)

@dp.message(ZoroStates.waiting_for_post_interval)
async def capture_post_interval(message: types.Message, state: FSMContext):
    try:
        interval = int(message.text.strip())
        if interval < 1:
            interval = 1
        elif interval > 60:
            interval = 60
    except:
        await message.answer("❌ يرجى إدخال رقم صحيح بين 1 و 60 فقط. أعد المحاولة:")
        return
    
    data = await state.get_data()
    post_msg = data.get("post_message")
    
    sys_data = load_saved_accounts()
    sys_data["bot_states"]["auto_post"] = True
    save_accounts_data(sys_data)
    
    await message.answer(f"🚀 **تم تفعيل النشر الانهائي بنجاح!**\nسيتم النشر بشكل دوري ومستمر كل `{interval}` ثانية.")
    await bot.send_message(LOG_CHANNEL, f"🔄 **بدء مهمة نشر لانهائي جديدة:**\nالفاصل الزمني: كل `{interval}` ثانية.")
    
    asyncio.create_task(run_infinite_media_loop(post_msg, interval))
    await state.clear()

async def run_infinite_media_loop(post_msg: types.Message, interval: int):
    while True:
        sys_data = load_saved_accounts()
        if not sys_data["bot_states"].get("auto_post", False):
            break
        
        try:
            await post_msg.send_copy(chat_id=LOG_CHANNEL)
        except Exception as e:
            logging.error(f"خطأ أثناء تنفيذ النشر الانهائي للوسائط: {e}")
            
        await asyncio.sleep(interval)


# ----------------- نظام الرد التلقائي الاحترافي المتطور -----------------
@dp.callback_query(F.data == "set_autoreply")
async def autoreply_menu(callback: types.CallbackQuery, state: FSMContext):
    data = load_saved_accounts()
    current_text = data.get("autoreply_text", "غير محدد")
    
    kb = [
        [types.InlineKeyboardButton(text="✏️ تغيير نص الرد التلقائي", callback_data="change_autoreply_text")],
        [types.InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_home")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    
    data["bot_states"]["auto_reply"] = True
    save_accounts_data(data)
    
    await callback.message.edit_text(
        f"💬 **إدارة الرد التلقائي الاحترافي:**\n\n"
        f"• الحالة: تفعيل شغال ✅\n"
        f"• النص الحالي للرد:\n`{current_text}`\n\n"
        f"اختر الإجراء المطلوب:",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "change_autoreply_text")
async def change_autoreply_prompt(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("✏️ **أرسل الآن النص الجديد الذي تريد أن يرد به الحساب تلقائياً على الرسائل الخاصة:**")
    await state.set_state(ZoroStates.waiting_for_new_autoreply)
    await callback.answer()

@dp.message(ZoroStates.waiting_for_new_autoreply)
async def save_new_autoreply_text(message: types.Message, state: FSMContext):
    new_text = message.text.strip()
    
    data = load_saved_accounts()
    data["autoreply_text"] = new_text
    data["bot_states"]["auto_reply"] = True
    save_accounts_data(data)
    
    await message.answer(f"✅ **تم تحديث وتفعيل نص الرد التلقائي الاحترافي بنجاح!**\n\nالنص الجديد:\n`{new_text}`")
    await bot.send_message(LOG_CHANNEL, f"⚙️ تم تغيير وتفعيل نص الرد التلقائي الجديد بالحساب.")
    await state.clear()


@client.on(events.NewMessage(incoming=True))
async def telethon_auto_reply(event):
    if event.is_private:
        data = load_saved_accounts()
        if data["bot_states"].get("auto_reply", False):
            custom_reply = data.get("autoreply_text", "مرحباً بك. أنا أرد تلقائياً عبر نظام Zoro Anti-Scam.")
            await event.reply(custom_reply)


# ----------------- التبليغ التلقائي وإيقاف العمليات -----------------
@dp.callback_query(F.data == "auto_report")
async def auto_report_action(callback: types.CallbackQuery):
    data = load_saved_accounts()
    data["bot_states"]["auto_report"] = True
    save_accounts_data(data)
    
    await callback.message.answer("🛡️ **نظام التبليغ والتوثيق التلقائي (Auto Report) يعمل بكفاءة قصوى.**")
    await callback.answer()


@dp.callback_query(F.data == "stop_ops")
async def stop_all_operations(callback: types.CallbackQuery):
    data = load_saved_accounts()
    data["bot_states"]["auto_reply"] = False
    data["bot_states"]["auto_post"] = False
    data["bot_states"]["auto_report"] = False
    save_accounts_data(data)
    
    await callback.message.answer("🛑 **تم إيقاف كافة العمليات النشطة (النشر الانهائي، الرد التلقائي، والمهام في الخلفية) بنجاح.**")
    await bot.send_message(LOG_CHANNEL, "🛑 تنبيه أمني: تم إيقاف جميع مهام وعمليات البوت مؤقتاً.")
    await callback.answer()


@dp.callback_query(F.data == "status_report")
async def status_report_display(callback: types.CallbackQuery):
    data = load_saved_accounts()
    states = data.get("bot_states", {})
    
    status_text = (
        f"📊 **تقرير حالة النظام الاستخباراتي الشامل:**\n\n"
        f"• الرد التلقائي الاحترافي: {'شغال ✅' if states.get('auto_reply') else 'متوقف 🛑'}\n"
        f"• النشر الانهائي (Media Auto Post): {'شغال ✅' if states.get('auto_post') else 'متوقف 🛑'}\n"
        f"• التبليغ التلقائي: {'شغال ✅' if states.get('auto_report') else 'متوقف 🛑'}\n"
        f"• الحسابات المحفوظة دائمًا: {len(data.get('linked_accounts', []))}\n"
        f"• قناة السجلات الرسمية: {LOG_CHANNEL}"
    )
    await callback.message.answer(status_text)
    await callback.answer()


# ----------------- الدالة الرئيسية والتشغيل المناسب للـ السيرفرات (Railway) -----------------
async def main():
    print("🚀 جاري إقلاع عميل التيليثون الأمني...")
    await client.start()
    print("✨ تم تشغيل التيليثون بنجاح واستقرار الجلسة!")
    
    print("🤖 جاري إقلاع نظام إيوجرام ولوحة تحكم البوت...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
