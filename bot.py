import os
from PIL import Image
from pyrogram import Client,filters 
from pyrogram.types import (InlineKeyboardButton,  InlineKeyboardMarkup)

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

@app.on_message(filters.command(['start']))
async def start(client, message):
 await message.reply_text(text =f"""Hello {message.from_user.first_name }image to pdf bot 

i can convert image to pdf

This bot created by @mrlokaman""",reply_to_message_id = message.message_id ,  reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Support 🇮🇳" ,url="https://t.me/lntechnical") ],
                 [InlineKeyboardButton("Subscribe 🧐", url="https://youtube.com/c/LNtechnical") ]       ]        ) )




@app.on_message(filters.private & filters.photo)
async def pdf(client,message):
 
 if not isinstance(LIST.get(message.from_user.id), list):
   LIST[message.from_user.id] = []

  
 
 file_id = str(message.photo.file_id)
 if UPDATE_CHANNEL:
  try:
   user = await client.get_chat_member(UPDATE_CHANNEL, message.chat.id)
   if user.status == "kicked":
    await message.reply_text(" Sorry, You are **B A N N E D**")
    return
  except UserNotParticipant:
   #await message.reply_text(f"Join @{UPDATE_CHANNEL} To Use Me")
   await message.reply_text(
    text="**Please Join My Update Channel Before Using Me..**",
    reply_markup=InlineKeyboardMarkup([
    [ InlineKeyboardButton(text="Join Updates Channel", url=f"https:/
    ])
   )
   return
  else:
   ms = await message.reply_text("Converting to PDF ......")
 file = await client.download_media(file_id)

 trace_msg = None
 if LOG_CHANNEL:
  try:
   file = await photo.forward(LOG_CHANNEL)
   trace_msg = await file.reply_text(f'**User Name:** {message.from_user.mention(style="md")}\n\n**User Id:** `{message.from_user.id}`)
 
 image = Image.open(file)
 img = image.convert('RGB')
 LIST[message.from_user.id].append(img)
 await ms.edit(f"{len(LIST[message.from_user.id])} image   Successful created PDF if you want add more image Send me One by one\n\n **if done click here 👉 /convert** ")
 

@app.on_message(filters.command(['convert']))
async def done(client,message):
 images = LIST.get(message.from_user.id)

 if isinstance(images, list):
  del LIST[message.from_user.id]
 if not images:
  await message.reply_text( "No image !!")
  return

 path = f"{message.from_user.id}" + ".pdf"
 images[0].save(path, save_all = True, append_images = images[1:])
 
 await client.send_document(message.from_user.id, open(path, "rb"), caption = "Here your pdf !!")
 os.remove(path)
 
 
 
 
app.run()
