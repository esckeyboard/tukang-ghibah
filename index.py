import discord
import os
import openai
from discord.ext import commands
from discord import app_commands
from config import server_id, channel_id_ai, channel_id_curhat, author_id, token, openai_key


openai.api_key = openai_key
bot = commands.Bot(command_prefix="tg!", intents=discord.Intents.all()) # you can also change to intents=discord.Intents.default()


@bot.event
async def on_ready():
    print("Bot is Up and ready!")
    activity = discord.Activity(type=discord.ActivityType.listening, name="Curhatan penghuni Kost Hady") # Change name= to anything to your desire
    await bot.change_presence(activity=activity) 
    print(f"Bot {bot.user.name} is ready!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

#Start of slash command section
@bot.tree.command(name="reveal", description="Show your username/Memperlihatkan username mu")
@commands.dm_only() # idk if this thing still work or not (when i test it it still working to use on channel)
async def reveal(interaction: discord.Interaction, messages: str):
    server = bot.get_guild(server_id) 
    channel_curhat = server.get_channel(channel_id_curhat)

    try:
        await interaction.response.send_message(f"Messages has been relayed with your username revealed! <#{channel_id_curhat}>", ephemeral=True)
        await channel_curhat.send(f"Pesan dari **{interaction.user.mention}**: {messages}\n\n############################")
        print("Revealed DM has been relayed")
        
    except Exception as e:
        await interaction.response.send_message(e, ephemeral=True)        

@bot.tree.command(name="reply", description="Reply to existing messages in #curhat-anonymous")
@commands.dm_only()
async def reply(interaction: discord.Interaction, msgid:str, messages: str):
    server = bot.get_guild(server_id) 
    channel_curhat = server.get_channel(channel_id_curhat)

    try:
        msgid = await channel_curhat.fetch_message(int(msgid))
        await interaction.response.send_message(f"Messages has been relayed! <#{channel_id_curhat}>", ephemeral=True)
        await channel_curhat.send(f"Pesan dari **Seseorang**: {messages}\n\n############################", reference=msgid)
        print("Reply has been relayed")

    except Exception as e:
        await interaction.response.send_message(e, ephemeral=True)

@bot.event
async def on_message(message):

    # ignore messages sent by the bot itself to avoid infinite loops
    if message.author == bot.user:
        return

    if message.content == "":
        return
     
    if isinstance(message.channel, discord.DMChannel):
            print("BOT got DM") 
            await relay_dm(message)

    else:
        if bot.user in message.mentions and message.channel.id == channel_id_ai:
            print("BOT got some questions")
            await respond_prompt(message)
            
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
    await channel_curhat.send(f"Pesan dari **Seseorang**: {message.content}\n\n############################")
    print("DM relayed") 
    for attachment in message.attachments:
        await channel_curhat.send(attachment.url)
        print("Attachment from DM relayed")    

async def respond_prompt(message):
    server = bot.get_guild(server_id) 
    channel = server.get_channel(channel_id_ai)   
    prompt = message.content.replace(bot.user.mention, "")
    try:
        response = openai.Completion.create(
            engine="text-babbage-001",
            prompt=prompt,
            temperature=.5,
            top_p=0.3,
            max_tokens=60,
            stop=["You:"],
            frequency_penalty=0.5,
            presence_penalty=0
        )
        text_response = response.choices[0].text.strip()
        await message.channel.send(f"*babbage-001* : {text_response}\n\n*Respon dari bot ini terlimit sekitar 200 token per jawaban. Jadi ada beberapa respon yang tidak terselesaikan karena melebihi limit token.\nMau membantu meringankan biaya edukasi bot ini? <https://bit.ly/helpnoru>\nSource Code: <https://bit.ly/tgcode>*", reference=message)
        print("Answer to the Prompt Sent")
    except Exception as e:
        await channel.send(f"**ERROR**: {e}", reference=message)
        print(f"**ERROR**: {e}")

#TOKEN TO RUN THE BOT
bot.run(token)
