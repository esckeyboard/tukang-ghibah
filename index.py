import discord
import os
import openai
from discord.ext import commands

#setup openAI client
openai.api_key = 'YOUR-OPENAI-API'

# create a new bot client
bot = discord.Client(intents=discord.Intents.default())

server_id = 1234567890 #
channel_id_curhat = 1234567890
channel_id_ai = 1234567890
token = "your_bot_token_here"

#change activity
@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.listening, name="Curhatan penghuni Kost Hady")
    await bot.change_presence(activity=activity)
    print("BOT IS READY!")

# listen for new messages
@bot.event
async def on_message(message):
    # ignore messages sent by the bot itself to avoid infinite loops
    if message.author == bot.user:
        print("messages is from bot itself")
        return
    # ignore if the messages empty
    if message.content == "":
        print("Messages is empty")
        return

     
    if isinstance(message.channel, discord.DMChannel): 
        await relay_dm(message)
        print("BOT got DM")

    else:
        if bot.user in message.mentions and message.channel.id == channel_id_ai:
            await respond_prompt(message)
            print("BOT got some questions")
        else:
            print("Messages is outside selected channel")

async def relay_dm(message):
    server = bot.get_guild(server_id) 
    channel_curhat = server.get_channel(channel_id_curhat) 
    # check if the channel exists
    if channel_curhat is None:
        print(f"Channel with ID {channel_id_curhat} not found.")
        return
    
    # send the message to the channel
    await channel_curhat.send(f"Pesan dari **Seseorang**: {message.content}")
    for attachment in message.attachments:
        await channel_curhat.send(attachment.url)    

async def respond_prompt(message):
    server = bot.get_guild(server_id) 
    channel = server.get_channel(channel_id_ai)   
    prompt = message.content.replace(bot.user.mention, "")
    try:
        response = openai.Completion.create(
            engine="text-babbage-001",
            prompt=prompt,
            temperature=.8,
            max_tokens=150,
            n=7,
            stop=None,
            frequency_penalty=0.5,
            presence_penalty=0.5
        )
        text_response = response.choices[0].text.strip()
        await message.channel.send(f"*babbage-001* : {text_response}\n\n*Respon dari bot ini terlimit sekitar 200 token per jawaban. Jadi ada beberapa respon yang tidak terselesaikan karena melebihi limit token.\nMau membantu meringankan biaya edukasi bot ini? https://bit.ly/helpnoru*", reference=message)
        print("Answer to the Prompt Sent")
    except Exception as e:
        await channel.send(f"**ERROR**: {e}", reference=message)
        print(f"**ERROR**: {e}")



        # run the bot with your bot token
bot.run(token)