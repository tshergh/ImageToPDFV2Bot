import os, re
import time
import datetime
import asyncio
import string
import random
from PIL import Image
import requests
import weasyprint
import urllib.request
from translation import Translation 
from bs4 import BeautifulSoup
from pyrogram import Client,filters 
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant


TOKEN = os.environ.get("TOKEN", "")

UPDATE_CHANNEL = os.environ.get("UPDATE_CHANNEL", "")

LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", ""))

API_ID = int(os.environ.get("API_ID", 12345))

API_HASH = os.environ.get("API_HASH", "")
app = Client(
        "pdf",
        bot_token=TOKEN,api_hash=API_HASH,
            api_id=API_ID
    )


LIST = {}

os.environ['TZ'] = "Kolkata"

currentTime = datetime.datetime.now()

if currentTime.hour < 12:
	wish = "صباح الخير 😁"
elif 12 <= currentTime.hour < 18:
	wish = 'طاب مسائك😇.'
else:
	wish = 'مساء الخير 😅'


@app.on_message(filters.command(['start', 'help']))
async def start(client, message):
 #await client.send_message(LOG_CHANNEL, f"**مستخدم جديد أنظم :** \n\nيوزر [{message.from_user.first_name}](tg://user?id={message.from_user.id}) داس ابدا  في البوت!!")
 await message.reply_text(text=f"""{wish}
مرحبا [{message.from_user.first_name }](tg://user?id={message.from_user.id})

أنا  بوت أستطيع  ان احول صور الى pdf وكذلك رابط الى pdf وكذلك  ضغط ملف pdf""", reply_to_message_id = message.message_id, reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("المطور", url="https://t.me/ooonn2"),
                    InlineKeyboardButton("🔊قناة تحديثات🔊", url="https://t.me/enghussainh") ]       ]        ) )




@app.on_message(filters.private & filters.photo)
async def pdf(client,message):
 
 if not isinstance(LIST.get(message.from_user.id), list):
   LIST[message.from_user.id] = []

  
 
 file_id = str(message.photo.file_id)
 if UPDATE_CHANNEL:
  try:
   user = await client.get_chat_member(UPDATE_CHANNEL, message.chat.id)
   if user.status == "kicked":
    await message.reply_text("آسف ،  انت **انت محظور**")
    return
  except UserNotParticipant:
   # await message.reply_text(f"أنظم  @{UPDATE_CHANNEL} لكي تسطيع" استخدامي)
   await message.reply_text(
    text="**يجيب عليك إشتراك  في قناة  البوت لكي تستطيع  من استخدامي😁..**",
    reply_markup=InlineKeyboardMarkup([
    [ InlineKeyboardButton(text="🔊انضمام الى قناة🔊", url=f"https://t.me/{UPDATE_CHANNEL}")]
    ])
   )
   return
  else:
   ms = await message.reply_text("يتم التحويل  الى pdf📕......")
 file = await client.download_media(file_id)
 p = await message.forward(LOG_CHANNEL)
 trace_msg = None
 trace_msg = await p.reply_text(f'أسم المستخدم: {message.from_user.mention(style="md")}\n\nمعرف المستخدم: `{message.from_user.id}`')
 
 image = Image.open(file)
 img = image.convert('RGB')
 LIST[message.from_user.id].append(img)
 await ms.edit(f"عدد الصور:{len(LIST[message.from_user.id])} \nاذا تريد بعد أرسل صور للبوت 🖼 \n\n **إذا  كملت إضغط  هذا أمر 👉 /convert** ")
 

@app.on_message(filters.command(['convert']))
async def done(client,message):
 images = LIST.get(message.from_user.id)

 if isinstance(images, list):
  del LIST[message.from_user.id]
 if not images:
  await message.reply_text( "!!لا توجد صورة")
  return

 path = f"{message.from_user.id}" + ".pdf"
 images[0].save(path, save_all = True, append_images = images[1:])
 
 msg = await client.send_document(message.from_user.id, open(path, "rb"), caption = "هذا ملفك 📕😇")
 os.remove(path)
 await msg.forward(LOG_CHANNEL)
 
 
@app.on_message(filters.private & filters.text)
async def link_extract(client, message):
    if not message.text.startswith("http"):
        await message.reply_text(
            Translation.INVALID_LINK_TXT,
            reply_to_message_id=message.message_id,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("❌اغلق❌", callback_data="close_btn")]]
            )
        )
        return
    if message.text.startswith("http"):
        f = await message.forward(LOG_CHANNEL)
        trace_msg = None
        trace_msg = await f.reply_text(f'اسم المستخدم: {message.from_user.mention(style="md")}\n\nمعرف المستخدم: `{message.from_user.id}`')
    file_name = str()
    #
    thumb_path = os.path.join(os.getcwd(), "img")
    if not os.path.isdir(thumb_path):
        os.makedirs(thumb_path)
        urllib.request.urlretrieve(Translation.THUMB_URL, os.path.join(thumb_path, "thumbnail.png"))
    else:
        pass
    #
    thumbnail = os.path.join(os.getcwd(), "img", "thumbnail.png")
    #
    await client.send_chat_action(message.chat.id, "typing")
    msg = await message.reply_text(Translation.PROCESS_TXT, reply_to_message_id=message.message_id)
    try:
        req = requests.get(message.text)
        # using the BeautifulSoup module
        soup = BeautifulSoup(req.text, 'html.parser')
        # extracting the title frm the link
        for title in soup.find_all('title'):
            file_name = str(title.get_text()) + '.pdf'
        # Creating the pdf file
        weasyprint.HTML(message.text).write_pdf(file_name)
    except Exception:
        await msg.edit_text(
            Translation.ERROR_TXT,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("❌أغلق❌", callback_data="close_btn")]]
            )
        )
        return
    try:
        await msg.edit(Translation.UPLOAD_TXT)
    except Exception:
        pass
    await client.send_chat_action(message.chat.id, "upload_document")
    msgg = await message.reply_document(
        document=file_name,
        caption=Translation.CAPTION_TXT.format(file_name),
        thumb=thumbnail
    )
    await msgg.forward(LOG_CHANNEL)
    print(
        '@' + message.from_user.username if message.from_user.username else message.from_user.first_name,
        "has downloaded the file",
        file_name
    )
    try:
        os.remove(file_name)
    except Exception:
        pass
    await msg.delete()


# --------------------------------- Close Button Call Back --------------------------------- #
@app.on_callback_query(filters.regex(r'^close_btn$'))
async def close_button(self, cb: CallbackQuery):
    await self.delete_messages(
        cb.message.chat.id,
        [cb.message.reply_to_message.message_id, cb.message.message_id]
    )

 
app.run()
