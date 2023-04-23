import asyncio
import discord
import yt_dlp
import threading
import random
from math import ceil
import datetime
from discord.utils import get
from multiprocessing.pool import ThreadPool

loop = False
repeat = False
shuffle = False
queue = {}

async def getinfo(song_search,youdl):
    global threads
    if song_search[0] != "h":
      song_search=song_search[0]
    def extract(song_search, results, i):
        results[i] = (youdl.extract_info(song_search, download=False) if "youtube.com" in song_search or "youtu.be" in song_search or "soundcloud.com" in song_search or "bilibili.com" in song_search else youdl.extract_info(f"ytsearch1:{song_search}", download=False))
    seed = random.random()
    threads = {}
    results = {}
    pool = ThreadPool()
    threads[seed] = pool.apply_async(extract, (song_search, results, seed))
    while True:
        await asyncio.sleep(1)
        try:
            threads[seed].successful()
        except:
            continue
        break
    return results[seed]

async def check_queue(ctx,client):
    voice = get(client.voice_clients, guild=ctx.guild)
    if ctx.guild.id not in queue.keys():
        queue[ctx.guild.id] = {"current": None, "current_progress": 0, "queue": [], "volume":0.5, "view":None}
    if len(queue[ctx.guild.id]["queue"]) == 0:
        if voice:
            await voice.disconnect()
        print("song over")
        return "song over"

async def Play(ctx, client, *url: str):
    voice = get(client.voice_clients, guild=ctx.guild)
    if not voice:
        channel = ctx.message.author.voice.channel
        voice = get(client.voice_clients, guild=ctx.guild)
        if voice is not None:
            return await voice.move_to(channel)
        try:
            await channel.connect()
            print("connected")
        except AttributeError:
            await ctx.reply("Сначала зайди В Голосовой канал")
    if ctx.guild.id not in queue.keys():
        queue[ctx.guild.id] = {"current": None, "current_progress": 0, "queue": [], "volume":0.5, "view":None}
    q = await Очередь(ctx, client, url)
    if q == "error":
        await ctx.reply("Извини, я не могу добавить этот трек в очередь")
    await queue_loop(ctx, client)
    await check_queue(ctx, client)

async def queue_loop(ctx,client):
    global loop, repeat, shuffle
    voice = get(client.voice_clients, guild=ctx.guild)
    r_count = 0
    while len(queue[ctx.guild.id]["queue"]) != 0 or loop or repeat:
        if voice.is_playing() or voice.is_paused():
            return
        queue[ctx.guild.id]["current_progress"] = 0
        if ctx.guild.id not in queue.keys():
            queue[ctx.guild.id] = {"current": None, "current_progress": 0, "queue": [],
                                   "buttons": [], "volume":0.5, "view":None}
        if not repeat and r_count > 0:
            r_count = 0
        if repeat:
            if r_count >= len(queue[ctx.guild.id]["queue"])-1:
                r_count = 0
            else:
                r_count += 1
            if len(queue[ctx.guild.id]["queue"])!=0:
                if shuffle:
                    r_count = random.randint(0, len(queue[ctx.guild.id]["queue"])-1)
                queue[ctx.guild.id]["current"] = queue[ctx.guild.id]["queue"][r_count]
            song_search = queue[ctx.guild.id]["current"]["url"]
        else:
            if queue[ctx.guild.id]["current"] is None and len(queue[ctx.guild.id]["queue"]) == 0:
                if await check_queue(ctx, client) == "song over":
                    return
            elif len(queue[ctx.guild.id]["queue"]) != 0 and not loop:
                if shuffle:
                    ran = random.randint(0,len(queue[ctx.guild.id]["queue"])-1)
                queue[ctx.guild.id]["current"] = queue[ctx.guild.id]["queue"][ran if shuffle else 0]
                queue[ctx.guild.id]["queue"].pop(ran if shuffle else 0)
            song_search = queue[ctx.guild.id]["current"]["url"]
        if voice and not voice.is_playing():
            youdl_opts = {
                'quiet': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': 320}],
                "ignoreerrors": True
            }
            with yt_dlp.YoutubeDL(youdl_opts) as youdl:
                try:
                    if "http" in song_search:
                        info = await getinfo(song_search, youdl)
                        if "soundcloud" in song_search:
                            URL = info['formats'][-1]['url']
                        elif 'format_note' in info.keys():
                            for format in info['formats']:
                                if format.get('format_note', None) != "medium":
                                    continue
                                else:
                                    URL = format['url']
                                    break
                        try:
                            aboba = URL
                        except UnboundLocalError:
                            URL = info['formats'][0]['url']
                except yt_dlp.DownloadError:
                    await ctx.channel.send("An unknown error happened")
                    await voice.disconnect()
                    return

                info_dict = info

            FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                              'options': '-vn'}
            if not voice.is_connected():
                loop = False
                repeat = False
                queue[ctx.guild.id] = {"current": None, "current_progress": 0, "queue": [], "volume":0.5, "view":None}
                break
            discord.opus.load_opus("./libopus.so.0.8.0")
            if not discord.opus.is_loaded():
                print("opus failed, lmao")
            voice.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = queue[ctx.guild.id]["volume"]
            voice.is_playing()
            def counter():
                while voice.is_playing() or voice.is_paused():
                    p.wait(1)
                    if not voice.is_paused():
                        queue[ctx.guild.id]["current_progress"] += 1
                queue[ctx.guild.id]["current_progress"] = 0

            p = threading.Event()
            t = threading.Thread(name='counter', target=counter)
            t.start()
            duration = int(info_dict.get('duration', 0))
            new_embed = discord.Embed(title="Сейчас играет:",
                                      description=f'[{info_dict["title"]}]({info_dict["original_url"]})',
                                      color=discord.Color.dark_green())
            new_embed.set_thumbnail(url=info_dict["thumbnail"])
            new_embed.add_field(name="\u200b",value=f"\u200b")
            new_embed.set_footer(
                text=f'Запросил: {client.get_user(int(queue[ctx.guild.id]["current"]["author_id"])).name}, Треков в очереди: {len(queue[ctx.guild.id]["queue"])}',
                icon_url=client.get_user(int(queue[ctx.guild.id]["current"]["author_id"])).avatar.url)
          
            msg = await ctx.channel.send("\u200b", embed=new_embed)
          
            queue[ctx.guild.id]["msg"]=msg
            class Button_tab(discord.ui.View):
                async def on_timeout(self):
                      self.children[0].disabled=True
                      await msg.edit(content=ctx.author.mention,view=self)
                      return
                async def interaction_check(self, interaction):
                      if interaction.message.id == msg.id:
                          iD=interaction.data["custom_id"]
                          if iD == 'Pause':
                              await Pause(ctx, client, interaction.user)
                          elif iD == 'Next':
                              await Next(ctx, client, interaction.user)
                          elif iD == 'Stop':
                              await Stop(ctx, client, interaction.user)
                          elif iD == 'Loop':
                              if not loop and not repeat:
                                  await Repeat(ctx, client, interaction.user)
                              elif repeat:
                                  await Loop(ctx, client, interaction.user)
                              elif loop:
                                  await Loop(ctx, client, interaction.user)
                          elif iD == 'Shuffle':
                              await Shuffle(ctx, client, interaction.user)
                          if not interaction.response.is_done():
                              await interaction.response.defer()
            but_view=Button_tab(timeout=None)
            queue[ctx.guild.id]["view"]=but_view
            but_view.add_item(discord.ui.Button(label="", emoji="⏸️", style=discord.ButtonStyle.gray, custom_id="Pause", disabled=False))
            but_view.add_item(discord.ui.Button(label="", emoji="⏭️", style=discord.ButtonStyle.gray, custom_id="Next", disabled=False))
            but_view.add_item(discord.ui.Button(label="", emoji="⏹️", style=discord.ButtonStyle.gray, custom_id="Stop", disabled=False))
            but_view.add_item(discord.ui.Button(label="", emoji="🔁", style=discord.ButtonStyle.gray, custom_id="Loop", disabled=False))
            but_view.add_item(discord.ui.Button(label="", emoji="🔀", style=discord.ButtonStyle.gray, custom_id="Shuffle", disabled=False))
            print()
            await msg.edit(content="\u200b",embed=new_embed,
                         view=but_view)
            refresh=3600
            print("playing music")
            while voice and voice.is_playing() or voice.is_paused():
                x = str(datetime.timedelta(seconds=queue[ctx.guild.id]["current_progress"])).split(':')
                mm, ss = divmod(queue[ctx.guild.id]["current_progress"], 60)
                hh, mm = divmod(mm, 60)
                if duration != 0:
                    new_embed.set_field_at(0,
                                           name=f'[{("▬" * (ceil(queue[ctx.guild.id]["current_progress"] / duration * 15)))[:-1]+"⦾"}{("▬" * ((15 - ceil(queue[ctx.guild.id]["current_progress"] / duration * 15))-(1 if (ceil(queue[ctx.guild.id]["current_progress"] / duration * 15))==0 else 0)))}]',
                                           value=f"`[{(str(hh) + ':') if x[0] != '0' else ''}{x[1][1:] if x[1][0] == '0' else x[1]}:{x[2]}/{info_dict.get('duration_string', '00:00')}] 🔉{str(queue[ctx.guild.id]['volume']*100)[:-2]}%`")
                    new_embed.set_footer(
                        text=f'Запросил: {client.get_user(int(queue[ctx.guild.id]["current"]["author_id"])).name}, Треков в очереди: {len(queue[ctx.guild.id]["queue"])}',
                        icon_url=client.get_user(int(queue[ctx.guild.id]["current"]["author_id"])).avatar.url)
                    if not voice:
                        but_view.stop()
                        return
                else:
                    new_embed.set_field_at(0,
                                           name=f'[{("▬" * 15) + "⦾"}]',
                                           value=f"`[{(str(hh) + ':') if x[0] != '0' else ''}{x[1][1:] if x[1][0] == '0' else x[1]}:{x[2]}/{info_dict.get('duration_string', '00:00')}]`")
                if queue[ctx.guild.id]["current_progress"] >= refresh:
                    await msg.delete()
                    msg = await ctx.channel.send("\u200b", embed=new_embed, view=but_view)
                    queue[ctx.guild.id]["msg"]=msg
                    refresh+=3600
                await msg.edit(content="\u200b", embed=new_embed, view=but_view)
                await asyncio.sleep(3)
            if not voice.is_playing() and not voice.is_paused():
                await msg.delete()

async def Loop(ctx, client, alt=None):
    global loop
    voice = get(client.voice_clients, guild=ctx.guild)
    if alt is None:
        alt = ctx.message.author
    if alt.voice and alt.voice.channel.id != voice.channel.id:
        await ctx.reply("Сначала зайди в голосовой канал со мной",delete_after=5)
        return
    if loop:
        view=queue[ctx.guild.id]["view"]
        msg=queue[ctx.guild.id]["msg"]
        em = discord.Embed(title="Цикл", description=f'Цикл текущего трека  :repeat_one: **ВЫКЛ**', color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {alt.name}', icon_url=alt.avatar.url)
        #await ctx.channel.send(embed=em, delete_after=5)
        view.children[3].style = discord.ButtonStyle.gray
        view.children[3].emoji = "🔁"
        loop = False
        await msg.edit(view=view)

    else:
        if repeat:
            await Repeat(ctx, client, alt)
        view=queue[ctx.guild.id]["view"]
        msg=queue[ctx.guild.id]["msg"]
        em = discord.Embed(title="Цикл", description=f'Цикл текущего трека :repeat_one: **ВКЛ**', color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {alt.name}', icon_url=alt.avatar.url)
        #await ctx.channel.send(embed=em, delete_after=5)
        view.children[3].style = discord.ButtonStyle.green
        view.children[3].emoji = "🔂"
        loop = True
        await msg.edit(view=view)

async def Repeat(ctx, client, alt=None):
    global repeat
    voice = get(client.voice_clients, guild=ctx.guild)
    if alt is None:
        alt = ctx.message.author
    if alt.voice and alt.voice.channel.id != voice.channel.id:
        await ctx.reply("Сначала зайди в голосовой канал со мной",delete_after=5)
        return
    if repeat:
        view=queue[ctx.guild.id]["view"]
        msg=queue[ctx.guild.id]["msg"]
        em = discord.Embed(title="Повтор", description=f'Повтор всей очереди :repeat: **ВЫКЛ**', color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {alt.name}', icon_url=alt.avatar.url)
        #await ctx.channel.send(embed=em, delete_after=5)
        view.children[3].style = discord.ButtonStyle.gray
        view.children[3].emoji = "🔁"
        repeat = False
        await msg.edit(view=view)

    else:
        if loop:
            await Loop(ctx, client, alt)
        view=queue[ctx.guild.id]["view"]
        msg=queue[ctx.guild.id]["msg"]
        em = discord.Embed(title="Повтор", description=f'Повтор всей очереди :repeat: **ВКЛ**', color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {alt.name}', icon_url=alt.avatar.url)
        #await ctx.channel.send(embed=em, delete_after=5)
        view.children[3].style = discord.ButtonStyle.green
        view.children[3].emoji = "🔁"
        repeat = True
        await msg.edit(view=view)

async def Shuffle(ctx, client, alt=None):
    global shuffle
    voice = get(client.voice_clients, guild=ctx.guild)
    if alt is None:
        alt = ctx.message.author
    if alt.voice and alt.voice.channel.id != voice.channel.id:
        await ctx.reply("Сначала зайди в голосовой канал со мной",delete_after=5)
        return
    if shuffle:
        view=queue[ctx.guild.id]["view"]
        msg=queue[ctx.guild.id]["msg"]
        em = discord.Embed(title="Перемешать", description=f'Перемешка Очереди :twisted_rightwards_arrows: **ВЫКЛ**', color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {alt.name}', icon_url=alt.avatar.url)
        #await ctx.channel.send(embed=em, delete_after=5)
        view.children[4].style = discord.ButtonStyle.gray
        shuffle = False
        await msg.edit(view=view)

    else:
        view=queue[ctx.guild.id]["view"]
        msg=queue[ctx.guild.id]["msg"]
        em = discord.Embed(title="Перемешать", description=f'Перемешка Очереди :twisted_rightwards_arrows: **ВКЛ**', color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {alt.name}', icon_url=alt.avatar.url)
        #await ctx.channel.send(embed=em, delete_after=5)
        view.children[4].style = discord.ButtonStyle.green
        shuffle = True
        await msg.edit(view=view)

async def Pause(ctx, client, alt=None):
    voice = get(client.voice_clients, guild=ctx.guild)
    if alt is None:
        alt = ctx.message.author
    if alt.voice and alt.voice.channel.id != voice.channel.id:
        await ctx.reply("Сначала зайди в голосовой канал со мной", delete_after=5)
        return
    if voice and voice.is_playing():
        view=queue[ctx.guild.id]["view"]
        msg=queue[ctx.guild.id]["msg"]
        print("Music paused")
        voice.pause()
        em = discord.Embed(title="Пауза", description=f':pause_button:', color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {alt.name}', icon_url=alt.avatar.url)
        view.children[0].style = discord.ButtonStyle.green
        #await ctx.channel.send(embed=em, delete_after=5)
        await msg.edit(view=view)
    elif voice and voice.is_paused():
        await Resume(ctx, client, alt)
    else:
        print("Music not playing failed pause")
        em = discord.Embed(title="Ошибка", description=f'**Музыка сейчас не играет**',
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {alt.name}', icon_url=alt.avatar.url)
        await ctx.channel.send(embed=em, delete_after=5)


async def Resume(ctx, client, alt=None):
    voice = get(client.voice_clients, guild=ctx.guild)
    if alt is None:
        alt = ctx.message.author
    if alt.voice and alt.voice.channel.id != voice.channel.id:
        await ctx.reply("Сначала зайди в голосовой канал со мной", delete_after=5)
        return
    if voice and voice.is_paused():
        view=queue[ctx.guild.id]["view"]
        msg=queue[ctx.guild.id]["msg"]
        print("Resumed music")
        voice.resume()
        view.children[0].style = discord.ButtonStyle.gray
        await msg.edit(view=view)
        em = discord.Embed(title="Возобновление", description=f':arrow_forward:', color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {alt.name}', icon_url=alt.avatar.url)
        #await ctx.channel.send(embed=em, delete_after=5)
    else:
        print("Music is not paused")
        em = discord.Embed(title="Ошибка", description=f'**Music is not paused**',
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {alt.name}', icon_url=alt.avatar.url)
        await ctx.channel.send(embed=em, delete_after=5)


async def Stop(ctx, client, alt=None):
    global loop, repeat
    voice = get(client.voice_clients, guild=ctx.guild)
    if alt is None:
        alt = ctx.message.author
    if voice and voice.is_playing() or voice and voice.is_paused():
        if alt.voice and alt.voice.channel.id != voice.channel.id:
            await ctx.reply("Сначала зайди в голосовой канал со мной", delete_after=5)
            return
        queue[ctx.guild.id] = {"current": None, "current_progress": 0, "queue": [], "volume":0.5, "view":None}
        if voice and voice.is_paused():
            voice.resume()
        print("Music stopped")
        loop = False
        repeat = False
        voice.stop()
        em = discord.Embed(title="Стоп", description=f':stop_button:', color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {alt.name}', icon_url=alt.avatar.url)
        #await ctx.channel.send(embed=em, delete_after=5)
    else:
        print("No music playing failed to stop")
        em = discord.Embed(title="Ошибка", description=f'**Музыка сейчас не играет**', color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {alt.name}', icon_url=alt.avatar.url)
        await ctx.channel.send(embed=em, delete_after=5)

async def Next(ctx, client, alt=None):
    voice = get(client.voice_clients, guild=ctx.guild)
    if alt is None:
        alt = ctx.message.author
    if voice and voice.is_playing():
        if alt.voice and alt.voice.channel.id != voice.channel.id:
            await ctx.reply("Сначала зайди в голосовой канал со мной", delete_after=5)
            return
        print("Playing Next Song")
        em = discord.Embed(title="Следующий трек", description=f':track_next:',
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {alt.name}', icon_url=alt.avatar.url)
        #await ctx.channel.send(embed=em, delete_after=5)
        voice.stop()
    else:
        print("No music playing")
        em = discord.Embed(title="Ошибка", description=f'**Музыка сейчас не играет**:',
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {alt.name}', icon_url=alt.avatar.url)
        #await ctx.channel.send(embed=em, delete_after=5)


async def Volume(ctx, client, Volume: int):
    if ctx.voice_client is None:
        em = discord.Embed(title="Ошибка", description=f'**Я не в Голосовм Канале**',
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        await ctx.channel.send(embed=em, delete_after=5)
        return 

    print(queue[ctx.guild.id]["volume"] / 100)
    queue[ctx.guild.id]["volume"]=Volume /100
    ctx.voice_client.source.volume = Volume /100
    em = discord.Embed(title="Громкость", description=f"Громкость установлена на {str(queue[ctx.guild.id]['volume'])[:-2]}%",
                       color=discord.Color.dark_green())
    em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
    em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
    #await ctx.channel.send(embed=em, delete_after=5)

async def View(ctx, client):
    queue_view = list(queue[ctx.guild.id]["queue"])
    queue_str = "\u200b"
    for i in range(len(queue_view)):
        track = queue_view[i]
        author = client.get_user(int(track['author_id']))
        queue_str+=f"{i+1}. [{track['name']}]({track['url']}) ({author.name})\n"
        if len(queue_str) > 750:
            queue_str+="..."
            break
    current = queue[ctx.guild.id]['current']
    em = discord.Embed(title=f"Длина очереди: `{len(queue[ctx.guild.id]['queue'])}` {'🔂' if loop else ''}{'🔁' if repeat else ''}",
                       color=discord.Color.dark_green())
    em.add_field(name=f"Сейчас играет:", value=f"**--> [{current['name']}]({current['url']}) ({client.get_user(int(current['author_id'])).name}**)\n\n{queue_str}")
    em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
    em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
    return await ctx.channel.send(embed=em,delete_after=15)

async def Очередь(ctx, client, song_search):
    global queue
    youdl_opts = {
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': 320}],
            "ignoreerrors": True,
            "playlistend":64,
    }
    with yt_dlp.YoutubeDL(youdl_opts) as youdl:
        r_msg = await ctx.channel.send(f"Добавляем ваш трек/плейлист в очередь {discord.utils.get(client.emojis, name=f'zagruzka')}")
        info_dict = await getinfo(song_search, youdl)
        if info_dict is None:
            await r_msg.delete()
            return "error"
        if "_type" in info_dict.keys() and len(info_dict["entries"])>1:
            song_count = 0
            for song in info_dict['entries']:
                if song is None:
                    continue
                queue[ctx.guild.id]["queue"].append(
                    {"name": song['title'], "url": song['original_url'], "author_id": ctx.author.id})
                song_count += 1
            Thumb = song['thumbnail']
            new_embed = discord.Embed(title="Плейлист поставлен в очередь:",
                                      description=f'[{info_dict["title"]}]({info_dict["original_url"]})',
                                      color=discord.Color.dark_green())
            new_embed.set_thumbnail(url=Thumb)
            new_embed.add_field(name="Треков добавлено в очередь:", value=f"{song_count}")
            new_embed.set_author(name=client.user.name, icon_url=client.user.avatar.url)
            new_embed.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
            await r_msg.delete()
            await ctx.channel.send(embed=new_embed, delete_after=15)
        else:
            try:
                info_dict = info_dict.get('entries', [info_dict])[0]
            except:
                await ctx.reply("Извини, по этому запросу ничего не найдено")
                return
            queue[ctx.guild.id]["queue"].append({"name":info_dict["title"],"url":info_dict['original_url'],"author_id":ctx.author.id})
            if len(queue[ctx.guild.id]["queue"])>0:
                new_embed = discord.Embed(title="Трек поставлен в очередь:",
                                          description=f'[{info_dict["title"]}]({info_dict["original_url"]}) ({info_dict.get("duration_string", 0)})',
                                          color=discord.Color.dark_green())
                new_embed.set_thumbnail(url=info_dict['thumbnail'])
                new_embed.add_field(name="Место в очереди", value=f"{len(queue[ctx.guild.id]['queue'])}")
                new_embed.set_author(name=client.user.name, icon_url=client.user.avatar.url)
                new_embed.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
                await r_msg.delete()
                await ctx.channel.send(embed=new_embed, delete_after=15)
