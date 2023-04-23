import re
import numpy as np
import seam_carving
import time
import httpx
import os
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps
from discord.ext import commands
from discord import app_commands
from music import *
from help import *
from io import BytesIO
from polyglot.detect import Detector
from keep_alive import keep_alive
import deepl as dp0
import deepl_1 as dp1
import base64
import string
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

def get_slash_serv_list():
    with open("addons/prefixes.json", "r") as f:
        guild_list=[]
        for servers in json.load(f):
          guild_list.append(int(servers))
        return guild_list
init_servers=get_slash_serv_list()

def get_key():
    return dict(os.environ)


keys = get_key()

def get_prefix(client, message):
    if message.content.startswith(f'<@!{client.user.id}>') or message.content.startswith(f'<@{client.user.id}>'):
        if message.content.startswith(f'<@!{client.user.id}>'):
            return f'<@!{client.user.id}> '
        else:
            return f'<@{client.user.id}> '
    else:
        if message.guild is not None:
            with open("addons/prefixes.json", "r") as f:
                prefixes = json.load(f)
            return message.content[
                   :len(prefixes.get(str(message.guild.id), "Зяблик, "))] if message.content.lower().startswith(
                prefixes.get(str(message.guild.id), "Зяблик, ").lower()) else prefixes.get(str(message.guild.id),
                                                                                           "Зяблик, ")
        else:
            return message.content[:8] if message.content.lower().startswith("зяблик, ") else "Зяблик, "


client = commands.Bot(command_prefix=get_prefix, intents=discord.Intents.all())
client.remove_command("help")


def is_it_me(ctx):
    return (ctx.author.id == 334412601389875210) or (ctx.author.id == 663704850101567518)

@client.event
async def on_member_join(member):
    print(f"Welcome {member}")
    try:
        await member.send(
            f'Добро пожаловать {member.mention}!\nЧто-бы просмотреть комманды бота напиши `Зяблик, Помощь`\n'
            f'Если у тебя есть вопросы насчёт бота, пиши в ЛС сюда -> `КоТ с рыбкой#7316`\nЕщё можешь написать сюда и чатбот попробует ответить')
    except:
        print("Error, cant send msg to user")


@client.event
async def on_guild_join(guild):
    with open("addons/prefixes.json", "r") as f:
        prefixes = json.load(f)
    prefixes[str(guild.id)] = "Зяблик, "
    with open("addons/prefixes.json", "w") as f:
        json.dump(prefixes, f)
    with open(r"addons/vchannels.json", "r") as f:
        vchannels = json.load(f)
    vchannels[str(guild.id)] = ""
    with open(r"addons/vchannels.json", "w") as f:
        json.dump(vchannels, f)
    with open(r"addons/settings.json", "r") as f:
        settings = json.load(f)
    settings[str(guild.id)] = {"chatbot": 0, "tts": 0,
                               "draw_set": {"steps": 25, "sampler_name": "k_dpmpp_2s_a", "width": 512,
                                            "height": 512, "cfg_scale": 7, "seed_variation": 1000,
                                            "denoising_strength": 0.5, "use_gfpgan": True, "nsfw": False,
                                            "model_name": "stable_diffusion"}}
    with open(r"addons/settings.json", "w") as f:
        json.dump(settings, f)
    print(f"New server joined: {guild.name, guild.id}")


@client.event
async def on_voice_state_update(ctx, before, after):
    if after.channel is not None:
        afterchannelid = after.channel.id
    else:
        afterchannelid = None
    if before.channel is not None:
        beforechannelid = before.channel.id
    else:
        beforechannelid = None
    with open(r"addons/vchannels.json", "r") as f:
        voicechannels = json.load(f)
        Guildchannels = voicechannels[str(ctx.guild.id)]
        if Guildchannels == "":
            return
        else:
            Cid = Guildchannels[0]
            Mainid = Guildchannels[1]
        if afterchannelid == Mainid:
            chname = ctx.name
            channel = await ctx.guild.create_voice_channel(chname)

            voicechannels[str(ctx.guild.id)][0].append(channel.id)
            with open(r"addons/vchannels.json", "w") as f:
                json.dump(voicechannels, f)

            perm = channel.overwrites_for(ctx)
            perm.manage_channels = True
            perm.view_channel = True
            perm.use_voice_activation = True
            perm.stream = True
            perm.speak = True
            perm.priority_speaker = True
            perm.deafen_members = True
            perm.connect = True
            perm.mute_members = True
            perm.move_members = True

            if after.channel.category is not None:
                await channel.edit(category=after.channel.category, permissions_synced=True,
                                   position=after.channel.category.position, bitrate=96000)
            else:
                await channel.edit(category=after.channel.category, bitrate=96000)
            await channel.set_permissions(ctx, overwrite=perm)
            try:
                await ctx.move_to(channel)
            except:
                pass
        if beforechannelid in Cid:
            members = before.channel.members
            if members == []:
                voicechannels[str(ctx.guild.id)][0].remove(before.channel.id)
                with open(r"addons/vchannels.json", "w") as f:
                    json.dump(voicechannels, f)
                await before.channel.delete()


proxies = []
chat_buffer = {}
backslash = "\n"


async def chat_trans(args, lang, ctx, src="auto"):
    first_pass = True
    if all(char in set(string.punctuation) for char in args):
        return args
    if src == "auto":
        src = Detector(args).languages[0].code
    try:
        trans = dp0.translate(source_language=src, target_language=lang, text=args,
                             formality_tone="informal")
    except:
        print("=== backup translator in use ===")
        auth_key = keys["Translate"]
        translator = dp1.Translator(auth_key)
        lang= lang.replace("EN","EN-US")
        trans = str(translator.translate_text(args,source_lang=src, target_lang=lang))
    return trans


async def chat_loop(msg, clyde=False):
    global chat_buffer
    if msg.author.name == client.user.name:
        return
    message=msg.content
    print(f"{msg.author} - {message}")
    if not clyde:
        message= await chat_trans(message,"EN",msg,"RU")
        message= message.replace("booth","stand").replace("Booth","Stand")
        message= f"{msg.author.name}: "+message
    else:
        message=message.replace("[ChatGPT]:","")
        message= await chat_trans(message,"EN",msg,"RU")
        message= "Clyde [BOT]: "+message
    Client = httpx.AsyncClient(timeout=None)
    headers = {"sd-Authorization": f'Token {keys["character_api"]}'}
    token = keys["Scrape"]
    if (msg.guild.id not in chat_buffer.keys()) if msg.guild else (msg.author.id not in chat_buffer.keys()):
        #vX66TaB4zvJcZtJ1X7cvWlTUjsnQWR4Y47L4yo-0_Cg
        #5f4cd149-1f4a-4f26-9bd8-4f01b08dd6ed
        #iAh4fmAyZ21grPtuomVA1L3dIO_-TDPMetKZwQIrzZY
        url = f"https://api.scrape.do?token={token}&url=https://beta.character.ai/chat/history/create/&extraHeaders=true"
        await msg.channel.typing()
        resp = await Client.post(url, headers=headers, json={
            "character_external_id": "iAh4fmAyZ21grPtuomVA1L3dIO_-TDPMetKZwQIrzZY"
        })
        try:
            history = resp.json()["external_id"]
        except:
            print(resp.status_code)
            print(resp.text)
        print(history)
        chat_buffer[msg.guild.id if msg.guild else msg.author.id] = history
    url = f"https://api.scrape.do?token={token}&url=https://beta.character.ai/chat/streaming/&extraHeaders=true&retryTimeout=30000&sessionId={str(msg.guild.id if msg.guild else msg.author.id)[-5:]}"
    await msg.channel.typing()

    response = await Client.post(url, headers=headers, json={"history_external_id": chat_buffer[msg.guild.id if msg.guild else msg.author.id],
                                                       "character_external_id": "iAh4fmAyZ21grPtuomVA1L3dIO_-TDPMetKZwQIrzZY",
                                                       "text": message,
                                                       "tgt": "internal_id:232576:dba4599a-bf81-4efb-a3a2-4d95245a62ad"})
    reslist=(response.text).split(" "*20)
    try:
        answer1 = reslist[-1].split('", "uuid":')[0].split('{"replies": [{"text": "')[1]
    except:
        print(response.status_code)
        print(response.text)
    answer1=answer1.encode('utf-8').decode('unicode_escape')
    if answer1 is None:
        answer1 = "*ОТФИЛЬТРОВАНО* (попробуйте сменить тему)"
    else:
        answer1= await chat_trans(answer1,"RU",msg,"EN")
        answer1 = ' '.join(re.sub("(@[A-Za-z0-9]+)|(_[A-Za-z0-9]+)", " ", answer1).split())
        answer1 = ' '.join(re.sub("(\w+:\S+)", "*[HYPERLINK BLOCKED]*", answer1).split())
    print("bot - " + answer1)
    try:
        await msg.reply(answer1)
    except:
        print("Error, cant send msg to user")


@client.event
async def on_message(msg):
    if (msg.author.bot == True and msg.author.id==1081004946872352958):
      await msg.channel.typing()
      await chat_loop(msg,True)
      return
    if msg.guild and msg.reference is None:
        await client.process_commands(msg)
    elif (msg.reference is not None and msg.guild and msg.reference.message_id is not None):
        try:
          reference = await msg.channel.fetch_message(msg.reference.message_id)
        except discord.errors.NotFound:
            return
        except discord.errors.HTTPException as e:
            if "429" in str(e):
              print("rate limited, restarting")
              os.system("kill 1 && main.py")
              return
            else:
              print(e)
        with open(r"addons/settings.json", "r") as f:
            settings = json.load(f)
        if (msg.author.name != client.user.name and reference.author.name == client.user.name and settings[str(msg.guild.id)]['chatbot'] == 1):
            await msg.channel.typing()
            await chat_loop(msg)
            return
        await client.process_commands(msg)
    elif not msg.guild:
        if msg.content.startswith(f"Зяблик, ") or msg.content.startswith(
                f'<@!{client.user.id}>') or msg.content.startswith(f'<@{client.user.id}>'):
            await client.process_commands(msg)
            return
        if msg.author == client.user:
            return
        await msg.author.typing()
        await chat_loop(msg)


guild_ids = []


@client.event
async def on_ready():
    print('Зяблик готов')
    await client.change_presence(status=discord.Status.do_not_disturb,
                                 activity=discord.Activity(type=discord.ActivityType.listening,
                                                           name="звуки хруста жёсткого"))
    with open("addons/prefixes.json", "r") as f:
        guild_ids = []
        prefixes = json.load(f)
        servlist = prefixes
        for servers in servlist:
            try:
                guild = client.get_guild(int(servers))
                print(guild.name, guild.id)
                try:
                    await client.tree.sync(guild=guild)
                except discord.errors.Forbidden:
                    pass
                with open("addons/prefixes.json", "r") as f:
                    prefixes = json.load(f)
                if str(guild.id) not in prefixes.keys():
                    prefixes[str(guild.id)] = "Зяблик, "
                    with open("addons/prefixes.json", "w") as f:
                        json.dump(prefixes, f)
                with open(r"addons/vchannels.json", "r") as f:
                    vchannels = json.load(f)
                if str(guild.id) not in vchannels.keys():
                    vchannels[str(guild.id)] = ""
                    with open(r"addons/vchannels.json", "w") as f:
                        json.dump(vchannels, f)
                with open(r"addons/settings.json", "r") as f:
                    settings = json.load(f)
                if str(guild.id) not in settings.keys():
                    settings[str(guild.id)] = {"chatbot": 0, "tts": 0,
                                               "draw_set": {"steps": 25, "sampler_name": "k_dpmpp_2s_a", "width": 512,
                                                            "height": 512, "cfg_scale": 7, "seed_variation": 1000,
                                                            "denoising_strength": 0.5, "use_gfpgan": True,
                                                            "nsfw": False,
                                                            "model_name": "stable_diffusion"}}

                    with open(r"addons/settings.json", "w") as f:
                        json.dump(settings, f)
                guild_ids.append(int(guild.id))
            except AttributeError:
                if guild is None:
                    continue
    while True:
        await client.change_presence(status=discord.Status.do_not_disturb,activity=random.choice(activities))
        await asyncio.sleep(10)



activities = [discord.Activity(type=discord.ActivityType.watching, name="как растёт трава"),
              discord.Activity(type=discord.ActivityType.listening, name="голоса в своей голове"),
              discord.Game('Team Fortress 2')]
bad_batch = []


@client.hybrid_command(name="d100", description="Бросает кубик на котором выпадает число от 1 до 100.", guild_ids=guild_ids)
@app_commands.guilds(*init_servers)
async def d100(ctx: commands.Context):
    em = discord.Embed(title=f"D100",
                       color=discord.Color.dark_green())
    em.add_field(name="Вам выпало:", value=f"```{random.randint(0, 100)}```")
    em.set_image(url="https://cdn01.zipify.com/images/000/182/975/original/2179680_20171023T152722.png")
    em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
    em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
    msg1 = await ctx.send(embed=em)


@client.hybrid_command(name="бан", description="Банит пользователя (нет)", guild_ids=guild_ids)
@app_commands.guilds(*init_servers)
async def бан(ctx, user: discord.Member = None, reason: str="(Не указана)"):
    em = discord.Embed(title=f"БАН!!1!!",
                       color=discord.Color.red())
    em.add_field(name=f'`Причина: {reason}`', value=f"{'_ _' if user is None else f'```{user.name} Забанен (нет)```'}")
    em.set_image(
        url="https://media.discordapp.net/attachments/747037828936105994/918859379527266335/6dc7c13384f753f8.gif")
    em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
    em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
    msg1 = await ctx.send(embed=em)


@client.hybrid_command(aliases=['Помощь'],description="Открывает меню с коммандами и информацией как их использовать")
@app_commands.guilds(*init_servers)
async def помощь(ctx, комманда=None):
    if ctx.interaction is not None and not ctx.interaction.response.is_done():
          await ctx.interaction.response.defer(ephemeral=True)
          orig=await ctx.interaction.original_response()
          await orig.delete()
    await Help(ctx, client, комманда)

@client.hybrid_command(aliases=['Настройки'],description="Открывает меню настроек бота")
@app_commands.guilds(*init_servers)
async def настройки(ctx):
    if ctx.interaction is not None and not ctx.interaction.response.is_done():
          await ctx.interaction.response.defer(ephemeral=True)
          orig=await ctx.interaction.original_response()
          await orig.delete()
    Options = [discord.SelectOption(label=f"stable_diffusion (Оригинал)", value="stable_diffusion"),
               discord.SelectOption(label=f"Poison (Аниме фоны)", value="Poison"),
               discord.SelectOption(label=f"Anything Diffusion (Аниме портреты)", value="Anything Diffusion"),
               discord.SelectOption(label=f"Realistic Vision (Реалистичные портреты)", value="Realistic Vision"),
               discord.SelectOption(label=f"Cyberpunk Anime Diffusion (Сериал Cyberpunk: Edgerunners)",
                            value="Cyberpunk Anime Diffusion"),
               discord.SelectOption(label=f"mo-di-diffusion (3D анимациz Disney)", value="mo-di-diffusion"),
               discord.SelectOption(label=f"Project Unreal Engine 5 (3D рендеры)", value="Project Unreal Engine 5"),
               discord.SelectOption(label=f"Arcane Diffusion (Сериал Arcane)", value="Arcane Diffusion"),
               discord.SelectOption(label=f"Anygen (Реализм/Аниме)", value="Anygen"),
               discord.SelectOption(label=f"Deliberate (Реализм)", value="Deliberate"),
               discord.SelectOption(label=f"Dreamlike Photoreal (Реализм)", value="Dreamlike Photoreal")]
  
    msg = await ctx.channel.send(ctx.author.mention)
  
    while True:
        if (ctx.guild.id not in chat_buffer.keys()) if ctx.guild else (ctx.author.id not in chat_buffer.keys()):
            answer1=0
        else:
            Client = httpx.AsyncClient(timeout=None)
            headers = {
                "sd-Authorization": f"Token {keys['character_api']}"
            }
            token = keys["Scrape"]
            url = f"https://api.scrape.do?token={token}&url=https://beta.character.ai/chat/history/msgs/user/?history_external_id={chat_buffer[ctx.guild.id if ctx.guild else ctx.author.id]}&extraHeaders=true"
            response = await Client.get(url, headers=headers)
            answer1 = len(response.json()["messages"])-1
        with open(r"addons/settings.json", "r") as f:
            settings = json.load(f)
        em = discord.Embed(title="Настройки",
                           description=f'Кликай на кнопки внизу сообщения что-бы переключать значения',
                           colour=discord.Color.dark_green())
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.add_field(name=f"`Очистить память чатбота` [{answer1} сообщений]",
                     value=f"```\nУдаляет все сообщения используемые как контекст для чат бота\n```",
                     inline=True)
        class CustomView(discord.ui.View):
            async def on_timeout(self):
                  return
            async def interaction_check(self, interaction):
                  await interaction.response.defer()
                  if interaction.message.id == msg.id:
                      iD=interaction.data["custom_id"]
                      print(iD)
                      if iD == "chatbot":
                          if settings[str(ctx.guild.id)]["chatbot"] == 1:
                              settings[str(ctx.guild.id)]["chatbot"] = 0
                          else:
                              settings[str(ctx.guild.id)]["chatbot"] = 1
                          with open(r"addons/settings.json", "w") as f:
                              json.dump(settings, f)
                      elif iD == "clear_chat":
                          chat_buffer.pop(ctx.guild.id if ctx.guild else ctx.author.id)
                      elif iD == "tts":
                          if settings[str(ctx.guild.id)]["tts"] == 1:
                              settings[str(ctx.guild.id)]["tts"] = 0
                          else:
                              settings[str(ctx.guild.id)]["tts"] = 1
                          with open(r"addons/settings.json", "w") as f:
                              json.dump(settings, f)
                      elif iD == "model_name":
                          settings[str(ctx.guild.id)]['draw_set']['model_name'] = interaction.data["values"][0]
                          with open(r"addons/settings.json", "w") as f:
                              json.dump(settings, f)
                      elif iD == "Settings_Close":
                          await msg.delete()
                  self.stop()
                  return
        set_view=CustomView(timeout=60)
        if ctx.guild is not None:
            em.add_field(
                name=f"`Чатбот на сервере` {'[ON]' if settings[str(ctx.guild.id)]['chatbot'] == 1 else '[OFF]'}",
                value=f"```ansi\nВключает чат-бота на сервере\n(Ответьте на любое сообщение бота для ответа) {backslash + '[2;31m[Нужны права на управление сообщениями][0m' if not ctx.author.guild_permissions.manage_messages else ''}```",
                inline=True)
            em.add_field(name=f"`Озвучка сообщений` {'[ON]' if settings[str(ctx.guild.id)]['tts'] == 1 else '[OFF]'}",
                         value=f'```ansi\nОзвучивает текст в комманде "Скажи" {(backslash + "[2;31m[Нужны права на отправку tts сообщений][0m") if not ctx.author.guild_permissions.send_tts_messages else ""}```',
                         inline=True)
            em.add_field(name=f"`Стиль рисовки` [{settings[str(ctx.guild.id)]['draw_set']['model_name']}]",
                         value=f'```Меняет стиль нарисованного нейросетью используемой в комманде "Нарисуй" (Может замедлить генерацию)```')
            set_view.add_item(discord.ui.Button(label=f"Очистить память чатбота", custom_id="clear_chat", style=discord.ButtonStyle.gray, disabled=False if (ctx.guild.id in chat_buffer.keys()) else True))
            set_view.add_item(discord.ui.Button(label="Чатбот на сервере", custom_id="chatbot",style=discord.ButtonStyle.green if settings[str(ctx.guild.id)]["chatbot"] == 1 else discord.ButtonStyle.gray ,disabled=False if ctx.author.guild_permissions.manage_messages else True))
            set_view.add_item(discord.ui.Button(label="Озвучка сообщений", custom_id="tts",style=discord.ButtonStyle.green if settings[str(ctx.guild.id)]["tts"] == 1 else discord.ButtonStyle.gray,
                    disabled=False if ctx.author.guild_permissions.send_tts_messages else True))
            set_view.add_item(discord.ui.Button(emoji="❌", custom_id="Settings_Close", style=discord.ButtonStyle.gray))
            set_view.add_item(discord.ui.Select(placeholder=f"Стиль рисовки ({settings[str(ctx.guild.id)]['draw_set']['model_name']})",
                       options=Options, custom_id="model_name"))
        else:

            set_view.add_item(discord.ui.Button(label=f"Очистить память чатбота", custom_id="clear_chat", style=discord.ButtonStyle.gray, disabled=False if ctx.author.id in chat_buffer.keys() else True))
            set_view.add_item(discord.ui.Button(emoji="❌", custom_id="Settings_Close", style=discord.ButtonStyle.gray))
        try:
            await msg.edit(content=ctx.author.mention,embed=em,view=set_view)
        except discord.errors.NotFound:
              return
        if await set_view.wait():
            await msg.delete()
            break
        else:
            try:
              await msg.edit(content="i am error")
              print("i am error")
            except discord.errors.NotFound:
              return

# Не спрашивайте почему тут стоят точки с запятой
@client.hybrid_command(aliases=["Ascii", "ASCII"], with_app_command=True, description="Переделывает вашу картинку в текстовый файл")
@app_commands.guilds(*init_servers)
async def ascii(ctx, *,ссылка_на_картинку=None, картинка:discord.Attachment = None):
    url=ссылка_на_картинку
    if ctx.interaction is not None and not ctx.interaction.response.is_done():
          await ctx.interaction.response.defer(ephemeral=True)
          orig=await ctx.interaction.original_response()
          await orig.delete()
    Client = httpx.AsyncClient(timeout=3600, follow_redirects=True);
    if url is not None:
        r = await Client.get(url)
        if (r.status_code != 200 and r.status_code != 301):
            await ctx.channel.send("**Ошибка, Ссылка на изображение не работает**", delete_after=15)
            return
    else:
        if len(ctx.message.attachments) != 0:
            url = ctx.message.attachments[0].url
        else:
            raise discord.ext.commands.errors.MissingRequiredArgument
    UNICODE = [' ', '┈', '┈', '░', '░', '▒', '▒', '▓', '▓', '█', '█'];
    r = await Client.get(url);
    try:
        image = Image.open(BytesIO(r.content));
    except:
        await ctx.channel.send("**Ошибка, Ссылка на изображение не работает**", delete_after=15)
        return
    width, height = image.size;
    new_width = 159 if width > 159 else width;
    ratio = height / width / 1.65;
    new_height = int(new_width * ratio);
    image = image.resize((new_width, new_height));
    pixels = image.convert("L").getdata();
    new_image_data = "".join([UNICODE[pixel // 25] for pixel in pixels]);
    pixel_count = len(new_image_data);
    ascii_image = "\n".join(new_image_data[i:(i + new_width)] for i in range(0, pixel_count, new_width));
    buf = BytesIO(bytes(ascii_image, "UTF-8"));
    await ctx.channel.send(ctx.author.mention, file=discord.File(buf, filename='ascii.txt'))


@client.hybrid_command(aliases=["Глаз"], with_app_command=True,
                           description="Зяблик (попытается) описать данную вами картинку")
@app_commands.guilds(*init_servers)
async def глаз(ctx,*, ссылка_на_картинку=None, картинка:discord.Attachment = None):
    if ctx.interaction is not None and not ctx.interaction.response.is_done():
          await ctx.interaction.response.defer(ephemeral=True)
          orig=await ctx.interaction.original_response()
          await orig.delete()
    Url=ссылка_на_картинку
    msg=None
    Client = httpx.AsyncClient(timeout=None, follow_redirects=True)
    if Url is not None and Url != ctx.author:
        r = await Client.get(Url)
        if (r.status_code != 200 and r.status_code != 301):
            await ctx.channel.send("**Ошибка, Ссылка на изображение не работает**", delete_after=15)
            return
        url = Url
    else:
        if len(ctx.message.attachments) != 0:
            url = ctx.message.attachments[0].url
        else:
            raise discord.ext.commands.errors.MissingRequiredArgument
    image_binary = BytesIO()
    i = await Client.get(url)
    try:
        img = Image.open(BytesIO(i.content));
    except:
        await ctx.channel.send("**Ошибка, Ссылка на изображение не работает**", delete_after=15)
        return
    img.save(image_binary, "PNG")
    image_binary.seek(0)
    base = base64.b64encode(image_binary.getvalue()).decode('ascii')
  
    emoji = discord.utils.get(client.emojis, name=f'zagruzka')
    msg = await ctx.channel.send(f"**Читаю вашу картинку...** {emoji}")
    
    data = {"source_image":base,"forms":[{"name":"nsfw"},{"name":"caption"},{"name":"interrogation"}]}
    api_key = keys["horde"]
    res = await Client.post(
        "https://stablehorde.net/api/v2/interrogate/async",
        headers={"Content-Type": "application/json", "Apikey": api_key}, json=data)
    
    first_time = True
    try:
        uid=res.json()["id"]
    except:
        print(res.json())
        return
    while first_time or res.json()["state"] != "done":
        first_time = False
        res = await Client.get(
            "https://stablehorde.net/api/v2/interrogate/status/" + uid)
        await asyncio.sleep(3)
    for form in res.json()["forms"]:
      if form["form"]=="caption":
          prompt = form["result"]['caption']
      elif form["form"]=="interrogation":
          inter = form["result"]["interrogation"]
          tags=[]
          for type,taglist in inter.items():
              for tag in taglist:
                tags.append(tag["text"])
    if msg is not None:
        await msg.delete()
    if Url == ctx.author:
      return (prompt + ", " + ", ".join(tags))
    trans = await chat_trans(f"{prompt}", "RU", ctx,"EN")
    await Client.aclose()
    if trans is None:
        return
    em = discord.Embed(title="Я вижу на этой картинке:", description=f"```{trans}```",
                       color=discord.Color.dark_green())
    em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
    em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
    em.set_image(url=url)
    await ctx.channel.send(ctx.author.mention,embed=em)


@client.hybrid_command(aliases=["Мэшап", "mashup"], with_app_command=True, description="Засовывает два трека в блендер, и выдаёт вам музыкальный коктейль (РАБОТАЮТ ССЫЛКИ ТОЛЬКО С ЮТУБА)")
@app_commands.guilds(*init_servers)
async def мэшап(ctx, ссылка1, ссылка2):
    link1, link2=ссылка1, ссылка2
    if ctx.interaction is not None and not ctx.interaction.response.is_done():
          await ctx.interaction.response.defer(ephemeral=True)
          orig=await ctx.interaction.original_response()
          await orig.delete()
    youdl_opts = {
        'quiet': True,
        'noplaylist': True}
    with yt_dlp.YoutubeDL(youdl_opts) as youdl:
        try:
            song1 = (youdl.extract_info(link1,
                                        download=False) if "youtube.com" in link1 or "youtu.be" in link1 else youdl.extract_info(
                f"ytsearch1:{link1}", download=False))
            song2 = (youdl.extract_info(link2,
                                        download=False) if "youtube.com" in link2 or "youtu.be" in link2 else youdl.extract_info(
                f"ytsearch1:{link2}", download=False))
            if 'entries' in song1.keys():
                song1 = song1.get('entries', None)[0]
            if 'entries' in song2.keys():
                song2 = song2.get('entries', None)[0]
        except:
            await ctx.reply("Ошибка: Один из отправленных видео, ограничено по возрасту", delete_after=15)
            return
        if song1["playable_in_embed"] is False:
            await ctx.reply("Ошибка: я не могу сыграть (№1) видео которое вы отправили", delete_after=15)
            return
        if song2["playable_in_embed"] is False:
            await ctx.reply("Ошибка: я не могу сыграть (№2) видео которое вы отправили", delete_after=15)
            return
        if song1['duration'] > 500 or song2['duration'] > 500 or (song1['duration'] * song2['duration']) == 0:
            await ctx.reply("Ошибка: Видео не может быть длиннее 8 минут 20 секунд", delete_after=15)
            return
    header = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/json',
        'X-Client-Version': 'Firefox/Js Core/6.0.4/FirebaseUI-web',
        'Origin': 'https://rave.dj',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Referer': 'https://rave.dj/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'TE': 'trailers'
    }
    data = {"return Secure Token": True}
    url = f'https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key={keys["mashup"]}'
    Client = httpx.AsyncClient(timeout=3600)
    response = await Client.post(url, headers=header, json=data)
    header = {
        'Host': 'api.red.wemesh.ca',
        'Wemesh-Platform': 'Android',
        'Client-Version': '5.0',
        'Authorization': f'bearer {response.json()["idToken"]}',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0',
        'Wemesh-Api-Version': '5.0',
        'Accept': '*/*',
        'Origin': 'https://rave.dj',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://rave.dj/',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'

    }
    url = 'https://api.red.wemesh.ca/ravedj/dj/self/content'
    data = {"style": "MASHUP", "title": "zyablick", "media": [{"providerId": song1["id"], "provider": "YOUTUBE"},
                                                              {"providerId": song2["id"], "provider": "YOUTUBE"}]}
    first_time = True
    emoji = discord.utils.get(client.emojis, name=f'zagruzka')
    perc = 0.0
    while first_time or perc != 100.0:
        if first_time:
            response = await Client.post(url, headers=header, json=data)
            if response.status_code != 200:
                if response.status_code == 400:
                    if msg is not None:
                        await msg.delete()
                    await ctx.reply(f"Сорян, {ctx.author.mention}, я не могу смешать эти два трека :(", delete_after=30)
                    return
                print("mashup err " + str(response.status_code), str(response.text))
                await asyncio.sleep(1)
                continue
            Url = response.json()["data"]["id"]
            print("https://rave.dj/" + Url)
            msg = await ctx.channel.send(f"Ваш мэшап ожидает своей очереди... (Это может занять немного времени) {str(emoji)}")
            first_time = False
        response = await Client.post(url, headers=header, json=data)
        if response.status_code != 200:
            print("mashup err " + str(response.status_code), str(response.text))
            await asyncio.sleep(1)
            continue
        if Url != response.json()["data"]["id"] and response.json()["data"]["percentageComplete"] == 0.0:
            if msg is not None:
                await msg.delete()
            await ctx.reply(f"Сорян, {ctx.author.mention}, я не могу смешать эти два трека :(", delete_after=30)
            return
        if response.json()["data"]["percentageComplete"] != 0.0:
            if perc != response.json()['data']['percentageComplete']:
                await msg.delete()
                msg = await ctx.channel.send(
                    f"Ваш мэшап готов на **{response.json()['data']['percentageComplete']}%** ({response.json()['data']['stage'].replace('DOWNLOAD', 'Загрузка').replace('ANALYZE', 'Анализация').replace('GENERATE', 'Генерация').replace('BUILD', 'Постройка').replace('RENDER', 'Рендеринг').replace('UPLOAD', 'Отправка').replace('COMPLETE', 'Готово')}) {str(emoji)}")
        perc = response.json()["data"]["percentageComplete"]
        await asyncio.sleep(1)
    await Client.aclose()
    await msg.delete()
    await ctx.channel.send(
        f"{ctx.author.mention} \n ||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​|| _ _ _ _ _ _ {('https://rave.dj/' + str(response.json()['data']['id']))}")
#Небольшие манипуляции с рендером сообщений дискорда

@client.hybrid_command(aliases=["draw", "Нарисуй"], with_app_command=True,
                           description="Создаёт изображение на основе вашего описания и/или данного вами изображения")
@app_commands.guilds(*init_servers)
async def нарисуй(ctx, *, запрос=None, референс_картинка:discord.Attachment = None):
    a=запрос
    if ctx.interaction is not None and not ctx.interaction.response.is_done():
          await ctx.interaction.response.defer(ephemeral=True)
          orig=await ctx.interaction.original_response()
          await orig.delete()
    global retry
    if a is not None:
        if len(a) >= 1024:
            a = a[:1024]
        a = await chat_trans(a, "EN", ctx, "RU")
        if a is None:
            return
    elif len(ctx.message.attachments) != 0:
        a = await глаз(ctx, ссылка_на_картинку=ctx.author)
    else:
        raise discord.ext.commands.errors.MissingRequiredArgument
    emoji = discord.utils.get(client.emojis, name=f'zagruzka')
    #a=re.sub(r'(?i)young', ' ', re.sub(r'(?i)child', ' ', re.sub(r'(?i)girl', 'woman', re.sub(r'(?i)boy', 'man', a))))
    msg = await ctx.channel.send(f"**Рисую {a}...** {emoji}")
    Client = httpx.AsyncClient(timeout=3600, follow_redirects=True)
    with open(r"addons/settings.json", "r") as f:
        settings = json.load(f)
    if ctx.guild is not None:
        if settings[str(ctx.guild.id)]['draw_set']['model_name'] in ["Arcane Diffusion", "mo-di-diffusion",
                                                                     "Cyberpunk Anime Diffusion"]:
            if settings[str(ctx.guild.id)]['draw_set']['model_name'] == "Arcane Diffusion":
                booth = "arcane style, "
            elif settings[str(ctx.guild.id)]['draw_set']['model_name'] == "Cyberpunk Anime Diffusion":
                booth = "dgs illustration style, "
            else:
                booth = "modern disney style, "
        else:
            booth = ""
        Json = {"prompt": booth + a,
                "params": {"steps": 35, "n": 1, "sampler_name": "k_dpm_2_a", "width": 512, "height": 512,
                           "cfg_scale": 10,
                           "seed_variation": 1000, "seed": "", "denoising_strength": 0.5, "prompt": booth + a,
                            "karras": True,
                           "post_processing":["GFPGAN"]}, "nsfw": True, "karras": True,"slow_workers": False,"censor_nsfw": False, "replacement_filter": True, "trusted_workers": False,
                "models": [settings[str(ctx.guild.id)]['draw_set']['model_name']],"r2":True,"shared":True}
    else:
        Json = {"prompt": a,
                "params": {"steps": 35, "n": 1, "sampler_name": "k_dpm_2_a", "width": 512, "height": 512,
                           "cfg_scale": 10,
                           "seed_variation": 1000, "seed": "", "denoising_strength": 0.5, "prompt": a, "karras": True}, "karras": True, "replacement_filter": True, "nsfw": True,
                "censor_nsfw": False,"slow_workers": False, "trusted_workers": False,
                "models": ["stable_diffusion"],"r2":True,"shared":True}
    if len(ctx.message.attachments) != 0:
        image = await Client.get(ctx.message.attachments[0].url)
        img = Image.open(BytesIO(image.content))
        bite = BytesIO()
        bg = Image.new("RGB", (512, 512), (0, 0, 0))
        img.thumbnail((512, 512), Image.Resampling.LANCZOS)
        cr = ((512 - img.size[0]) // 2, (512 - img.size[1]) // 2)
        bg.paste(img, (cr), img.convert('RGBA'))
        img = bg
        img.save(bite, "PNG", quality=10)
        Json["source_image"] = base64.b64encode(bite.getvalue()).decode('ascii')
        Json["params"]["control_type"]="depth"
    # soup = httpx.Client().post("https://stablehorde.net/register", data={"username": "spamtong"})
    # api_key = soup.text.split('<p style="background-color:darkorange;">')[1].split('</p>')[0]
    api_key = keys["horde"]
    try:
        id = await Client.post(r'https://stablehorde.net/api/v2/generate/async', json=Json,
                               headers={"Content-Type": "application/json", "Apikey": api_key})
        await Client.aclose()
        id = id.json()
    except:
        id = {'message': "9999 seconds"}
    while "id" not in id.keys():
        count = int(re.search(r'\d+', id['message']).group() if re.search(r'\d+', id['message']) is not None else "0")
        await msg.edit(content=
        f"**Рисую {a}...** {emoji} (Расчётное время: {count} секунд) {'[происходят технические шоколадки, оставайтесь спокойны]' if count > 1000 else ''}")
        Client = httpx.AsyncClient(timeout=3600)
        id = await Client.post(r'https://stablehorde.net/api/v2/generate/async', json=Json,
                               headers={"Content-Type": "application/json", "Apikey": api_key})
        await Client.aclose()
        id = id.json()
        await asyncio.sleep(3)
    result = {"finished": 0}
    fIrst_pass = True
    while fIrst_pass or result['finished'] == 0:
        fIrst_pass=False
        Client = httpx.AsyncClient(timeout=3600)
        result = await Client.get(r'https://stablehorde.net/api/v2/generate/check/' + id["id"])
        if result.status_code == 429:
            result = result.json()
            await Client.aclose()
            continue
        result = result.json()
        await Client.aclose()
        try:
            await msg.edit( content=f"**Рисую {a}...** {emoji} (Расчётное время: {result['wait_time']} секунд)")
        except:
              return

        await asyncio.sleep(3)
    result = await httpx.AsyncClient(timeout=3600).get(
        r'https://stablehorde.net/api/v2/generate/status/' + id["id"])
    Client = httpx.AsyncClient(timeout=3600)
    i=await Client.get(result.json()['generations'][0]["img"])
    image_binary = BytesIO()
    try:
        img = Image.open(BytesIO(i.content));
    except:
        await ctx.channel.send("**Ошибка, Ссылка на изображение не работает**", delete_after=15)
        return
    if len(ctx.message.attachments) != 0:
        img = ImageOps.crop(img, (cr[0], cr[1], cr[0], cr[1]))
    img.save(image_binary, "PNG")
    image_binary.seek(0)
    em = discord.Embed(title=f"Вот что у меня получилось!", description=f"Запрос: ```{a}```\n",
                       color=discord.Color.dark_green())
    em.set_image(url="attachment://image.png")
    em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
    em.set_footer(
        text=f'Запросил: {ctx.author.name} \nМодель: {settings[str(ctx.guild.id)]["draw_set"]["model_name"] if ctx.guild is not None else "stable_diffusion"}',
        icon_url=ctx.author.avatar.url)
    await msg.delete()
    msg = await ctx.channel.send(ctx.author.mention, file=discord.File(fp=image_binary, filename='image.png'), embed=em)
  
    class CustomView(discord.ui.View):
      async def on_timeout(self):
            self.children[0].disabled=True
            self.children[0].style=discord.ButtonStyle.gray
            await msg.edit(content=ctx.author.mention, embed=em,view=self)
            return
      async def interaction_check(self, interaction):
            await interaction.response.defer()
            if interaction.message.id == msg.id:
                self.stop()
            return
  
    view=CustomView(timeout=30)
    view.add_item(discord.ui.Button(label="Сгенерировать ещё", emoji="♻️", style=discord.ButtonStyle.green, custom_id="Again"))
    await msg.edit(content=ctx.author.mention,embed=em,
                         view=view)
    if not await view.wait():
        view.children[0].disabled=True
        await msg.edit(content=ctx.author.mention, embed=em,view=view)
        await нарисуй(ctx, запрос=a, референс_картинка=референс_картинка)


@client.hybrid_command(aliases=['Жмых'],description="Скукоживает данную вами картинку")
@commands.max_concurrency(1, per=commands.BucketType.default, wait=True)
@app_commands.guilds(*init_servers)
async def жмых(ctx,*, ссылка_на_картинку=None, картинка:discord.Attachment = None):
    if ctx.interaction is not None and not ctx.interaction.response.is_done():
        await ctx.interaction.response.defer(ephemeral=True)
        orig=await ctx.interaction.original_response()
        await orig.delete()
    url=ссылка_на_картинку
    Client = httpx.AsyncClient(timeout=3600, follow_redirects=True)
    if url is not None:
        r = await Client.get(url)
        if (r.status_code != 200 and r.status_code != 301):
            await ctx.channel.send("**Ошибка, Ссылка на изображение не работает**", delete_after=15)
            return
    else:
        if len(ctx.message.attachments) != 0:
            url = ctx.message.attachments[0].url
        else:
            url = f'https://d2ph5fj80uercy.cloudfront.net/04/cat{random.randint(0,4999)}.jpg'
    i = await Client.get(url)
    try:
        im0 = Image.open(BytesIO(i.content));
    except:
        await ctx.channel.send("**Ошибка, Ссылка на изображение не работает**", delete_after=15)
        return
    bite = BytesIO()
    bg = Image.new("RGB", im0.size, (47, 49, 54))
    bg.paste(im0, (0, 0), im0.convert('RGBA'))
    im0 = bg
    wid, hgt = im0.size
    size = 800, 600
    if wid + hgt > 1400:
        print(f"image is big ({wid}x{hgt}), transforming...")
        im0 = im0.resize(size, Image.Resampling.LANCZOS)
        im0.save(bite, "JPEG", quality=25)
    else:
        print(f"image is small ({wid}x{hgt}), don't transform")
        im0 = im0.resize(im0.size, Image.Resampling.LANCZOS)
        im0.save(bite, "JPEG", quality=25)
    emoji = discord.utils.get(client.emojis, name=f'zagruzka')
    msg = await ctx.channel.send(f"**Ваш жмых обрабатывается...** {emoji}")

    tic = time.perf_counter()
    src = np.array(Image.open(bite))

    h, w, c = src.shape
    pool = ThreadPool()
    thread = pool.apply_async(seam_carving.resize, (src, (w / 2, h / 2)))
    while True:
        await asyncio.sleep(3)
        try:
            thread.successful()
        except:
            continue
        break
    image_binary = BytesIO()
    Image.fromarray(thread.get()).save(image_binary, 'PNG')
    image_binary.seek(0)
    toc = time.perf_counter()
    await msg.delete()
    em = discord.Embed(title="Вот ваш жмых:", description=f'Обработал за {toc - tic:0.4f} Секунд',
                       color=discord.Color.dark_green())
    em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
    em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
    em.set_image(url="attachment://image.png")
    await ctx.channel.send(ctx.message.author.mention, file=discord.File(fp=image_binary, filename='image.png'), embed=em)


@client.hybrid_command(aliases=['Инфо'],
                           description="Показывает информацию о выбранном пользователе или роли")
@app_commands.guilds(*init_servers)
async def инфо(ctx, *, пользователь_или_роль=None):
    user=пользователь_или_роль
    if ctx.interaction is not None and not ctx.interaction.response.is_done():
        await ctx.interaction.response.defer(ephemeral=True)
        orig=await ctx.interaction.original_response()
        await orig.delete()
    if user is None:
        user = ctx.author.mention
    elif user.isdigit():
        if ctx.guild.get_member(int(user)) is not None:
            user = f"<@{user}>"
        elif ctx.guild.get_role(int(user)) is not None:
            user = f"<@&{user}>"
        else:
            await ctx.channel.send("Сорян, не помню такого, может быть ты ID не правильный указал?")
            return
    elif not user.startswith("<"):
        await ctx.channel.send("Мне нужно ID или Упоминание роли или пользователя")
        return
    if user[2] == "&":
        role = user.replace("<@&", "")
        role = role.replace(">", "")
        role = ctx.guild.get_role(int(role))
        cr = str(role.created_at.timestamp())[:-4]
        embed = discord.Embed(title="Информация о роли:", color=role.color,
                              description=f"{role.mention} , {role.color}")
        embed.set_thumbnail(url=role.guild.icon.url)
        embed.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        embed.add_field(name="Была создана:", value=f"<t:{cr}:F>", inline=False)
        embed.insert_field_at(index=4, name="Позиция:", value=f"```{role.position}```")
        embed.insert_field_at(index=4, name="Показывается отдельно?",
                              value=f"```{'Да' if role.hoist else 'Нет'}```")
        embed.add_field(name='ID: ', value=f"```{str(role.id)}```")
        if len(role.members) > 0:
            role_list = []
            for i in range(len(role.members)):
                role_list.append(role.members[i].mention)
                if i >= 47:
                    break
            role_string = ' '.join(role_list)
            if i >= 47:
                role_string = f"{role_string[0:1000]} И ещё {len(role.members) - i} человек"
            embed.add_field(name="Люди имеющие роль: [{}]".format(len(role.members)), value=role_string)
        perm_string = '- '.join([str(p[0]).replace("_", " ").title() for p in role.permissions if p[1]])
        perm_string = perm_string.replace("Create Instant Invite", "Создавать моментальные приглашения,\n") \
            .replace("Kick Members", "Выгонять Участников,\n") \
            .replace("Ban Members", "Банить Участников,\n") \
            .replace("Manage Channels", "Управлять каналами,\n") \
            .replace("Manage Guild", "Управлять настройками сервера,\n") \
            .replace("Add Reactions", "Добавлять реакции,\n") \
            .replace("View Audit Log", "Просматривать журнал аудита,\n") \
            .replace("Priority Speaker", "Приоритет в голосовом канале,\n") \
            .replace("Stream", "Стримить в канале,\n") \
            .replace("Read Messages", "Читать сообщения,\n") \
            .replace("Send Messages", "Отправлять сообщения,\n") \
            .replace("Send Tts Messages", "Отправлять TTS сообщения,\n") \
            .replace("Manage Messages", "Управлять сообщениями,\n") \
            .replace("Embed Links", "Вставлять ссылки,\n") \
            .replace("Attach Files", "Прикреплять файлы,\n") \
            .replace("Read Message History", "Читать историю сообщений,\n") \
            .replace("Mention Everyone", "Упоминать всех,\n") \
            .replace("External Emojis", "Использовать сторонние эмодзи,\n") \
            .replace("View Guild Insights", "Просматривать статистику сервера,\n") \
            .replace("Connect", "Подсоединятся к голосовому каналу,\n") \
            .replace("Request To Speak", "Поднимать руку на трибуне,\n") \
            .replace("Speak", "Разговаривать,\n") \
            .replace("Mute Members", "Мутить участников в голосовом канале,\n") \
            .replace("Deafen Members", "Заглушать участников в голосовом канале,\n") \
            .replace("Move Members", "Перемещать участников в голосовом канале,\n") \
            .replace("Use Voice Activation", "Использовать Push to talk,\n") \
            .replace("Change Nickname", "Менять свой никнейм,\n") \
            .replace("Manage Nicknames", "Менять никнейм других участников,\n") \
            .replace("Manage Roles", "Управление ролями,\n") \
            .replace("Manage Webhooks", "Управлять вебхуками,\n") \
            .replace("Manage Emojis", "Управлять Эмодзи,\n") \
            .replace("Use Slash Commands", "Использовать Слэш-кломманды,\n")
        if perm_string == "":
            perm_string = "Прав нет ¯\_(ツ)_/¯"
        elif "Administrator" in perm_string:
            perm_string = "Администратор (Имеет абсолютно все права)"
        embed.add_field(name=f"Права [{len(list(role.permissions)) if 'Админ' not in perm_string else '∞'}]",
                        value=f"```- {perm_string}```")
        embed.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        await ctx.channel.send(embed=embed)
    else:
        user = user.replace("<@", "")
        user = user.replace("!", "")
        user = user.replace(">", "")
        user = ctx.guild.get_member(int(user))


        jo = str(user.joined_at.timestamp())[:-4]
        cr = str(user.created_at.timestamp())[:-4]
        if "online" in user.status:
            status = "Онлайн :green_circle:"
        elif "idle" in user.status:
            status = "Неактивен :yellow_circle:"
        elif "offline" in user.status:
            status = "Оффлайн :black_circle:"
        elif "dnd" in user.status:
            status = "Не беспокоить :no_entry_sign:"
        else:
            status = user.status
        embed = discord.Embed(title="Информация о пользователе:", color=discord.Color.dark_green(),
                              description=f"`{str(user)}` А.К.А {user.mention}  {status}")
        embed.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        embed.set_thumbnail(url=user.avatar.url)
        embed.add_field(name="Последний раз присоеденился на этот сервер:", value=f"<t:{jo}:F>", inline=False)
        embed.add_field(name="Зарегистрировался в дискорде:", value=f"<t:{cr}:F> ", inline=False)
        members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
        embed.insert_field_at(index=4, name="Индекс:", value=f"```{str(members.index(user) + 1)}```")
        embed.insert_field_at(index=4, name="Активность:",
                              value=f"```{user.activity.name if user.activity is not None else 'Никакая'}```")
        embed.add_field(name='ID: ', value=f"```{str(user.id)}```")
        if len(user.roles) > 1:
            role_string = ' '.join([r.mention for r in user.roles][1:])
            embed.add_field(name="Роли: [{}]".format(len(user.roles) - 1), value=role_string)
        
        perm_string = '- '.join([str(p[0]).replace("_", " ").title() for p in user.guild_permissions if p[1]])
        perm_string = perm_string.replace("Create Instant Invite", "Создавать моментальные приглашения,\n") \
            .replace("Kick Members", "Выгонять Участников,\n") \
            .replace("Ban Members", "Банить Участников,\n") \
            .replace("Manage Channels", "Управлять каналами,\n") \
            .replace("Manage Guild", "Управлять настройками сервера,\n") \
            .replace("Add Reactions", "Добавлять реакции,\n") \
            .replace("View Audit Log", "Просматривать журнал аудита,\n") \
            .replace("Priority Speaker", "Приоритет в голосовом канале,\n") \
            .replace("Stream", "Стримить в канале,\n") \
            .replace("Read Messages", "Читать сообщения,\n") \
            .replace("Send Messages", "Отправлять сообщения,\n") \
            .replace("Send Tts Messages", "Отправлять TTS сообщения,\n") \
            .replace("Manage Messages", "Управлять сообщениями,\n") \
            .replace("Embed Links", "Вставлять ссылки,\n") \
            .replace("Attach Files", "Прикреплять файлы,\n") \
            .replace("Read Message History", "Читать историю сообщений,\n") \
            .replace("Mention Everyone", "Упоминать всех,\n") \
            .replace("External Emojis", "Использовать сторонние эмодзи,\n") \
            .replace("View Guild Insights", "Просматривать статистику сервера,\n") \
            .replace("Connect", "Подсоединятся к голосовому каналу,\n") \
            .replace("Request To Speak", "Поднимать руку на трибуне,\n") \
            .replace("Speak", "Разговаривать,\n") \
            .replace("Mute Members", "Мутить участников в голосовом канале,\n") \
            .replace("Deafen Members", "Заглушать участников в голосовом канале,\n") \
            .replace("Move Members", "Перемещать участников в голосовом канале,\n") \
            .replace("Use Voice Activation", "Использовать Push to talk,\n") \
            .replace("Change Nickname", "Менять свой никнейм,\n") \
            .replace("Manage Nicknames", "Менять никнейм других участников,\n") \
            .replace("Manage Roles", "Управление ролями,\n") \
            .replace("Manage Webhooks", "Управлять вебхуками,\n") \
            .replace("Manage Emojis", "Управлять Эмодзи,\n") \
            .replace("Use Slash Commands", "Использовать Слэш-кломманды,\n")
        if perm_string == "":
            perm_string = "Прав нет ¯\_(ツ)_/¯"
            pass
        elif "Administrator" in perm_string:
            perm_string = "Администратор (Имеет абсолютно все права)"
        embed.add_field(name=f"Права [{len(list(user.guild_permissions)) if 'Админ' not in perm_string else '∞'}] :",
                        value=f"```- {perm_string}```")
        embed.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        await ctx.channel.send(embed=embed)


@client.hybrid_command(aliases=['Канал'],
                           description="Создаёт голосовой канал который создаёт ещё один голосовой канал в той же категории!")
@commands.cooldown(1, 10, commands.BucketType.guild)
@commands.has_permissions(administrator=True)
@app_commands.guilds(*init_servers)
async def канал(ctx, *, название_канала=None):
    if название_канала is None:
        await ctx.send("Нужно название для голосового канала")
        return
    else:
        with open("addons/vchannels.json", "r") as f:
            vchannels = json.load(f)

        Guildchannels = vchannels[str(ctx.guild.id)]
        if "" not in Guildchannels:
            channel = client.get_channel(Guildchannels[1])
            try:
                await channel.delete()
            except AttributeError:
                pass
        ch = await ctx.guild.create_voice_channel(название_канала)
        vchannels[str(ctx.guild.id)] = [], ch.id

        with open("addons/vchannels.json", "w") as f:
            json.dump(vchannels, f)
        await ctx.send(f"Успешно создал голосовой канал ({название_канала})")


@client.hybrid_command(aliases=['Префикс'], description="Меняет префикс бота на вашем сервере")
@commands.has_permissions(administrator=True)
@app_commands.guilds(*init_servers)
async def префикс(ctx, префикс):
    if len(префикс) > 25:
        префикс = префикс[:25]
    with open("addons/prefixes.json", "r") as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = префикс

    with open("addons/prefixes.json", "w") as f:
        json.dump(prefixes, f)
    await ctx.send(f'Префикс изменён на "{префикс}" ')


@client.hybrid_command(aliases=['Скажи'],
                           description='Заставляет зяблика сказать всё что вы пожелаете.')
@app_commands.guilds(*init_servers)
async def скажи(ctx, *, текст="_ _", картинка:discord.Attachment = None):
    arg=текст
    if ctx.interaction is not None and not ctx.interaction.response.is_done():
        await ctx.interaction.response.defer(ephemeral=True)
        orig=await ctx.interaction.original_response()
        await orig.delete()
    try:
        await ctx.message.delete()
    except:
        pass

    with open(r"addons/settings.json", "r") as f:
        settings = json.load(f)
    tts = True if settings[str(ctx.guild.id)]['tts'] == 1 else False
    if "@" in arg and ctx.author.id == 334412601389875210:
        print(arg)
        arg = arg.replace("@everyone", "\u200b")
        arg = arg.replace("@here", "\u200b")

    if ctx.message.reference is not None:
        reference = await ctx.fetch_message(ctx.message.reference.message_id)
        if len(ctx.message.attachments) == 0:
            await reference.reply(arg, tts=tts, mention_author=True)
        else:
            image_url = ctx.message.attachments[0].url
            Client = httpx.AsyncClient(timeout=3600, follow_redirects=True)
            r = await Client.get(image_url)
            await reference.reply(arg, tts=tts, mention_author=True, file=discord.File(fp=BytesIO(r.content),
                                                                                       filename=ctx.message.attachments[
                                                                                           0].filename))
    else:
        if len(ctx.message.attachments) == 0:
            await ctx.channel.send(arg, tts=tts)
        else:
            image_url = ctx.message.attachments[0].url
            Client = httpx.AsyncClient(timeout=3600, follow_redirects=True)
            r = await Client.get(image_url)
            await ctx.channel.send(arg, tts=tts,
                           file=discord.File(fp=BytesIO(r.content), filename=ctx.message.attachments[0].filename))


@client.hybrid_command()
@app_commands.guilds(*init_servers)
async def пинг(ctx):
    await ctx.send(f'понг ({round(client.latency * 1000)} мс)')


"""@client.command(aliases=['анекдот'])

async def Анекдот(ctx):
    with open(r"addons/settings.json", "r") as f:
          settings = json.load(f)
    tts = True if settings[str(ctx.guild.id)]['tts'] == 1 else False
    url = 'http://rzhunemogu.ru/RandJSON.aspx?CType=11'
    r = await httpx.AsyncClient(timeout=3600).get(url)
    data = r.json(strict=False)["content"]
    await ctx.channel.send("Внимание, Анекдот:\n" + data, tts=tts)"""


regex = re.compile('[+*/^:<>]')


@client.hybrid_command(aliases=['play', 'Сыграй'], description="Включает музыку в вашем голосовом канале")
@commands.cooldown(1, 3, commands.BucketType.guild)
@app_commands.guilds(*init_servers)
async def сыграй(ctx, *,ссылка_или_запрос: str):
    if "()" in str(ссылка_или_запрос):
        await ctx.channel.send("Я не могу играть без ссылки или запроса")
        return
    elif not ctx.author.voice:
        await ctx.channel.send("Сначала зайди в голосовой канал")
        return
    elif get(client.voice_clients, guild=ctx.guild) and get(client.voice_clients,
                                                            guild=ctx.guild).channel.id != ctx.author.voice.channel.id:
        await ctx.reply("Ошибка: МузБота уже используют на этом сервере")
        return
    if ctx.interaction is not None:
          await ctx.interaction.response.defer(ephemeral=True)
          orig=await ctx.interaction.original_response()
          await orig.delete()
    await Play(ctx, client, ссылка_или_запрос)


@client.hybrid_command(aliases=['loop', 'Цикл'], description="Зацикливает текущий трек в очереди")
@app_commands.guilds(*init_servers)
async def цикл(ctx):
    if ctx.interaction is not None:
          await ctx.interaction.response.defer(ephemeral=True)
          orig=await ctx.interaction.original_response()
          await orig.delete()
    await Loop(ctx, client)


@client.hybrid_command(aliases=['repeat', 'Повтор'], description="Ставит на повтор ВСЮ очередь")
@app_commands.guilds(*init_servers)
async def повтор(ctx):
    if ctx.interaction is not None:
          await ctx.interaction.response.defer(ephemeral=True)
          orig=await ctx.interaction.original_response()
          await orig.delete()
    await Repeat(ctx, client)


@client.hybrid_command(aliases=['shuffle', 'Перемешать'], description="Береёт треки из очереди в случайном порядке")
@app_commands.guilds(*init_servers)
async def перемешать(ctx):
    if ctx.interaction is not None:
          await ctx.interaction.response.defer(ephemeral=True)
          orig=await ctx.interaction.original_response()
          await orig.delete()
    await Shuffle(ctx, client)


@client.hybrid_command(aliases=['pause', 'Пауза'], description="Ставит вашу музыку на паузу")
@app_commands.guilds(*init_servers)
async def пауза(ctx):
    if ctx.interaction is not None:
          await ctx.interaction.response.defer(ephemeral=True)
          orig=await ctx.interaction.original_response()
          await orig.delete()
    await Pause(ctx, client)


@client.hybrid_command(aliases=['stop', 'Стоп'], description="Останавливает музыку и сбрасывает очередь")
@app_commands.guilds(*init_servers)
async def стоп(ctx):
    if ctx.interaction is not None:
          await ctx.interaction.response.defer(ephemeral=True)
          orig=await ctx.interaction.original_response()
          await orig.delete()
    await Stop(ctx, client)


@client.hybrid_command(aliases=['next', 'Некст', "Следующая", "следующая"], description="Переключает на следующий трек (Если он есть в очереди)")
@app_commands.guilds(*init_servers)
async def некст(ctx):
    if ctx.interaction is not None:
          await ctx.interaction.response.defer(ephemeral=True)
          orig=await ctx.interaction.original_response()
          await orig.delete()
    await Next(ctx, client)


@client.hybrid_command(aliases=['volume', 'Громкость'], description="Меняет громкость музыки")
@app_commands.guilds(*init_servers)
async def громкость(ctx, громкость: int):
    if ctx.interaction is not None:
        await ctx.interaction.response.defer(ephemeral=True)
        orig=await ctx.interaction.original_response()
        await orig.delete()
    await Volume(ctx, client, громкость)


@client.hybrid_command(aliases=['queue', 'Очередь'], description="Показывает все треки стоящие в очереди")
@app_commands.guilds(*init_servers)
async def очередь(ctx):
    if ctx.interaction is not None:
        await ctx.interaction.response.defer(ephemeral=True)
        orig=await ctx.interaction.original_response()
        await orig.delete()
    await View(ctx, client)


@client.hybrid_command(aliases=['Демотиватор'], description="Генерирует демотиватор из вашей картинки или текста")
@app_commands.guilds(*init_servers)
async def демотиватор(ctx, текст_сверху="", текст_снизу="", *,lol=None, картинка:discord.Attachment=None):
    arg,arg1,arg2=текст_сверху,текст_снизу,картинка
    if ctx.interaction is not None and not ctx.interaction.response.is_done():
        await ctx.interaction.response.defer(ephemeral=True)
        orig=await ctx.interaction.original_response()
        await orig.delete()
    if arg2 is None and картинка is None and len(ctx.message.attachments) ==0:
        url="https://images.squarespace-cdn.com/content/v1/55fc0004e4b069a519961e2d/1442590746571-RPGKIXWGOO671REUNMCB/image-asset.gif?format=300w"
    else:
        url = ctx.message.attachments[0].url
    Client = httpx.AsyncClient(timeout=3600, follow_redirects=True)
    r = await Client.get(url)
    if (r.status_code != 200 and r.status_code != 301):
        await ctx.channel.send("**Ошибка, Ссылка на изображение не работает**", delete_after=15)
        return
    top_size = 80
    bottom_size = 60
    img = Image.new('RGB', (1280, 1024), color='black')
    img_border = Image.new('RGB', (1060, 720), color='#000000')
    border = ImageOps.expand(img_border, border=2, fill='#ffffff')
    user_img = Image.open(BytesIO(r.content)).convert("RGBA").resize((1050, 710))
    (width, height) = user_img.size
    img.paste(border, (111, 96))
    img.paste(user_img, (118, 103))
    drawer = ImageDraw.Draw(img)
    font_1 = ImageFont.truetype(font='times.ttf', size=top_size, encoding='UTF-8')
    text_width = font_1.getsize(arg)[0]
    while text_width >= (width + 250) - 20:
        font_1 = ImageFont.truetype(font='times.ttf', size=top_size, encoding='UTF-8')
        text_width = font_1.getsize(arg)[0]
        top_size -= 1
    font_2 = ImageFont.truetype(font='times.ttf', size=bottom_size, encoding='UTF-8')
    text_width = font_2.getsize(arg1)[0]
    while text_width >= (width + 250) - 20:
        font_2 = ImageFont.truetype(font='times.ttf', size=bottom_size, encoding='UTF-8')
        text_width = font_2.getsize(arg1)[0]
        bottom_size -= 1
    size_1 = drawer.textsize(arg, font=font_1)
    size_2 = drawer.textsize(arg1, font=font_2)
    drawer.text(((1280 - size_1[0]) / 2, 840), arg, fill='white', font=font_1)
    drawer.text(((1280 - size_2[0]) / 2, 930), arg1, fill='white', font=font_2)
    image_binary = BytesIO()
    img.save(image_binary, 'PNG')
    image_binary.seek(0)
    em = discord.Embed(title=f"Вот ваш демотиватор:",
                       color=discord.Color.dark_green())
    em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
    em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
    em.set_image(url="attachment://image.png")
    await ctx.channel.send(ctx.author.mention, file=discord.File(fp=image_binary, filename='image.png'), embed=em)
    return


@client.hybrid_command(aliases=['Очисти', 'Очистка'], description="Убирает сообщения (5 шт. по умолчанию)")
@app_commands.guilds(*init_servers)
@commands.has_permissions(manage_messages=True)
async def очистка(ctx, количество=5):
    if ctx.interaction is not None and not ctx.interaction.response.is_done():
        await ctx.interaction.response.defer(ephemeral=True)
        orig=await ctx.interaction.original_response()
        await orig.delete()
    await ctx.channel.purge(limit=1)
    await ctx.channel.purge(limit=количество)
    await ctx.channel.send(f"Успешно очищено {количество} сообщений", delete_after=10)


@client.command(aliases=['Фас'])
@commands.check(is_it_me)
async def фас(ctx, user: discord.Member = None):
    try:
        await ctx.message.delete()
    except:
        pass
    i = 1
    while i < 5001:
        await asyncio.sleep(1)
        try:
            await user.send("https://media.discordapp.net/attachments/747037828936105994/892644974582173746/8.jpg")
        except:
            print("Сообщение заблокировано")
            return
        print(f"\rАтака на {user.display_name}: {i}", sep=' ', end='', flush=True)
        i += 1


showerror = True
if showerror:
    @client.event
    async def on_command_error(ctx, error):
        with open("addons/prefixes.json", "r") as f:
            prefixes = json.load(f)
        if ctx.guild is not None:
            pre1 = prefixes[str(ctx.guild.id)]
        else:
            pre1 = "Зяблик, "
        print(error)
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.MissingRequiredAttachment) or error == "missing arg":
            await ctx.reply(
                f'Мне кажется ты кое-что забыл добавить к команде (Посмотрите `{pre1}Помощь {ctx.command}`) ')
        elif isinstance(error, commands.CommandNotFound) or error == "missing command":
            await ctx.reply(f'Да нет такой комманды! (Посмотрите `{pre1}Помощь`)')
        elif isinstance(error, commands.MissingPermissions) or error == "no perm user":
            await ctx.reply(f'Похоже что у тебя нет прав для этой комманды')
        elif isinstance(error, commands.CommandOnCooldown) or error == "cooldown":
            await ctx.reply('**Успокойся**, попробуй ещё раз через {:.2f} секунд'.format(error.retry_after))
        elif isinstance(error, NotImplementedError) or error == "not impl":
            await ctx.reply(f'Сорян, ты не можешь использовать эту комманду в ЛС')
        elif isinstance(error, discord.errors.Forbidden) or error == "no perm bot":
            await ctx.reply(f'Похоже что у меня нет прав для этой комманды')
        elif isinstance(error, commands.MemberNotFound) or error == "missing user":
            await ctx.reply(f'Я не нашёл такого пользователя, попробуй ещё раз')
        elif isinstance(error, discord.ext.commands.errors.MaxConcurrencyReached):
            await ctx.reply('*Ваша комманда в очереди, подождите*')
        
keep_alive()
try:
    print("attempting run")
    client.run(keys["rus_key"])
except:
    print("ERROR, restarting")
    time.sleep(1)
    os.system("kill 1 && main.py")