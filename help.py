import discord
import json
import asyncio
from discord import SelectOption
async def Help(ctx, client, arg=None):
    arg= "menu"if arg is None else arg

    with open("addons/prefixes.json", "r") as f:
        prefixes = json.load(f)
    if ctx.guild is not None:
        pre1 = prefixes[str(ctx.guild.id)]
    else:
        pre1 = "Zyablick, "
    helpmsg = await ctx.channel.send(ctx.author.mention)
    class CustomView(discord.ui.View):
            async def on_timeout(self):
                  try:
                     await helpmsg.delete()
                  except discord.errors.NotFound:
                    return
            async def interaction_check(self, interaction):
                  await interaction.response.defer()
                  if interaction.message.id == helpmsg.id:
                      iD=interaction.data["values"][0] if "values" in interaction.data.keys() else interaction.data["custom_id"]
                      await Choice(ctx,pre1,client,iD,self,helpmsg)
                  return
    help_view=CustomView(timeout=60)
    await Choice(ctx,pre1,client,arg,help_view,helpmsg)
    while True:
        help_view=CustomView(timeout=60)
        if await help_view.wait():
            break
        else:
            break
async def Choice(ctx,pre1,client,arg,view,msg):
    view.clear_items()
    if arg.lower() == "menu":
        em = discord.Embed(title="Помощь",
                           description=f':information_source: **Выберите категорию снизу, что-бы просмотреть комманды'
                                       f'** :information_source: ',
                           colour=discord.Color.dark_green())
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.insert_field_at(index=3, name=":gear:**Сервер**:gear:",
                           value=f"```Комманды которые улучшают ваш сервер и опыт работы с ботом```",
                           inline=False)
        em.insert_field_at(index=0, name=":musical_note:**Музыка**:musical_note:",
                           value=f"```Комманды для муз.бота и мэшапов```", inline=True)
        em.insert_field_at(index=0, name=":tools:**Инструменты**:tools:",
                           value=f"```Комманды которые могут быть полезны для чего-нибудь```", inline=True)
        em.insert_field_at(index=0, name=":video_game: **Веселье** :video_game:",
                           value=f"```Комманды для того чтоб повеселиться или поубивать время```", inline=True)
        view.add_item(discord.ui.Select(placeholder="Выберите категорию!",
                                                    options=[SelectOption(label="Сервер", value="Сервер"),
                                                             SelectOption(label="Музыка", value="Музыка"),
                                                             SelectOption(label="Инструменты", value="Инструменты"),
                                                             SelectOption(label="Веселье", value="Веселье"),
                                                             ],custom_id="cat_name"))
        view.add_item(discord.ui.Button(label="Закрыть", emoji="❌", custom_id="Помощь_close"))
        await msg.edit(embed=em, view=view)
        return
    elif arg.lower() == 'сервер':
        em = discord.Embed(title=":gear:**Сервер**:gear:",
                           description=f'**Выберите комманду снизу чтобы увидеть описание и как её использовать**',
                           colour=discord.Color.dark_green())
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name="_ _", value=f"```Канал, Префикс, Помощь, Настройки.```")
        view.add_item(discord.ui.Select(placeholder="Выберите комманду!",
                                                    options=[SelectOption(label="Канал", value="Канал"),
                                                                 SelectOption(label="Префикс", value="Префикс"),
                                                                 SelectOption(label="Помощь", value="Помощь"),
                                                                 SelectOption(label="Настройки", value="Настройки")
                                                                 ]))
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="menu"))
        await msg.edit(embed=em, view=view)
        return
    elif arg.lower() == 'музыка':
        em = discord.Embed(title=":musical_note:**Музыка**:musical_note:",
                           description=f':information_source: **Выберите комманду снизу чтобы увидеть описание и как её использовать** '
                                       f':information_source:',
                           colour=discord.Color.dark_green())
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name="_ _", value=f"```Сыграй, Пауза, Цикл, Повтор, Перемешать, Стоп, Некст, Громкость, Очередь, Мэшап.```")
        view.add_item(discord.ui.Select(placeholder="Выберите комманду!",
                                                    options=[SelectOption(label="Сыграй", value="Сыграй"),
                                                                 SelectOption(label="Пауза", value="Пауза"),
                                                                 SelectOption(label="Цикл", value="Цикл"),
                                                                 SelectOption(label="Повтор", value="Повтор"),
                                                                 SelectOption(label="Перемешать", value="Перемешать"),
                                                                 SelectOption(label="Стоп", value="Стоп"),
                                                                 SelectOption(label="Некст",
                                                                              value="Некст"),
                                                                 SelectOption(label="Громкость",
                                                                              value="Громкость"),
                                                                 SelectOption(label="Очередь",
                                                                              value="Очередь"),
                                                                 SelectOption(label="Мэшап",
                                                                              value="Мэшап"),
                                                                 ]))
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="menu"))
        await msg.edit(embed=em, view=view)
        return
    elif arg.lower() == 'инструменты':
        em = discord.Embed(title=":tools:**Инструменты**:tools:",
                           description=f':information_source: **Выберите комманду снизу чтобы увидеть описание и как её использовать** '
                                       f':information_source:',
                           colour=discord.Color.dark_green())
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name="_ _", value=f"```Очистка, Инфо, Глаз, Ascii```")
        view.add_item(discord.ui.Select(placeholder="Выберите комманду!",
                                                    options=[SelectOption(label="Очистка", value="Очистка"),
                                                                 SelectOption(label="Инфо", value="Инфо"),
                                                                 SelectOption(label="Глаз", value="Глаз"),
                                                                 SelectOption(label="Ascii", value="Ascii")
                                                                 ]))
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="menu"))
        await msg.edit(embed=em, view=view)
        return
    elif arg.lower() == 'веселье':
        em = discord.Embed(title=":video_game:**Веселье**:video_game:",
                           description=f':information_source: **Выберите комманду снизу чтобы увидеть описание и как её использовать** '
                                       f':information_source:',
                           colour=discord.Color.dark_green())
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name="_ _",
                     value=f"```Скажи, Демотиватор, Жмых, Нарисуй```")
        view.add_item(discord.ui.Select(placeholder="Выберите комманду!",
                                                    options=[SelectOption(label="Скажи", value="Скажи"),
                                                                 SelectOption(label="Демотиватор",
                                                                              value="Демотиватор"),
                                                                 SelectOption(label="Жмых", value="Жмых"),
                                                                 SelectOption(label="Нарисуй", value="Нарисуй")
                                                                 ]))
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="menu"))
        await msg.edit(embed=em, view=view)
        return
    elif arg.lower() == 'помощь':

        em = discord.Embed(title="Помощь", description="**Открывает меню с коммандами и информацией как их использовать**",
                           color=discord.
                           Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name="**Как использовать:**", value=f"```{pre1}Помощь [Комманда]```", inline=False)
        em.add_field(name="Пример:", value=f"```{pre1}Помощь Демотиватор```", inline=False)
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="сервер"))
        await msg.edit(embed=em, view=view)

    elif arg.lower() == 'глаз':

        em = discord.Embed(title="Глаз",
                           description="**Зяблик (попытается) описать данную вами картинку**",
                           color=discord.
                           Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name="**Как использовать:**", value=f"```{pre1}Глаз <Картинка или ссылка на неё>```", inline=False)
        em.add_field(name="Пример:",
                     value=f"```{pre1}Глаз https://bit.ly/3NJ7B27```",
                     inline=False)
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="инструменты"))
        await msg.edit(embed=em, view=view)
      
    elif arg.lower() == 'очистка':

        em = discord.Embed(title="Очистка", description="**Убирает сообщения (5 шт. по умолчанию)**",
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar_url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name="**Как использовать:**", value=f"```{pre1}Очистка [Значение]```", inline=False)
        em.add_field(name="Пример:", value=f"```{pre1}Очистка 10```", inline=False)
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="инструменты"))
        await msg.edit(embed=em, view=view)

    elif arg.lower() == 'нарисуй':

        em = discord.Embed(title="Нарисуй",
                           description="**Создаёт изображение на основе вашего описания и/или данного вами изображения**",
                           color=discord.
                           Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name="**Как использовать:**", value=f"```{pre1}Нарисуй <Запрос>```", inline=False)
        em.add_field(name="Пример:", value=f"```{pre1}Нарисуй Зяблика сидящего на дорожном знаке```", inline=False)
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="веселье"))
        await msg.edit(embed=em, view=view)

    elif arg.lower() == 'ascii':

        em = discord.Embed(title="ASCII", description="**Переделывает вашу картинку в текстовый файл**",
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name='**Как использовать:**', value=f'```{pre1}Ascii <Картинка или ссылка не неё> ```', inline=False)
        em.add_field(name="Пример:",
                     value=f'```{pre1}Ascii https://bit.ly/3OLHuZb```', inline=False)
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="инструменты"))
        await msg.edit(embed=em, view=view)
        
    elif arg.lower() == 'сыграй':

        em = discord.Embed(title="Сыграй", description="**Включает музыку в вашем голосовом канале**",
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name="**Как использовать:**", value=f"```{pre1}Сыграй <Ссылка на видео на ютубе или его название>```",
                     inline=False)
        em.add_field(name="Пример:", value=f"```{pre1}Сыграй https://www.youtube.com/watch?v=dQw4w9WgXcQ```",
                     inline=False)
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="музыка"))
        await msg.edit(embed=em, view=view)
      
    elif arg.lower() == 'пауза':

        em = discord.Embed(title="Пауза", description="**Ставит вашу музыку на паузу**",
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name="**Как использовать:**", value=f"```{pre1}Пауза```", inline=False)
        em.add_field(name="Пример:", value=f"```{pre1}Пауза```", inline=False)
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="музыка"))
        await msg.edit(embed=em, view=view)
      
    elif arg.lower() == 'стоп':

        em = discord.Embed(title="Стоп", description="**Останавливает музыку и сбрасывает всю очередь**",
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name="**Как использовать:**", value=f"```{pre1}Стоп```", inline=False)
        em.add_field(name="Пример:", value=f"```{pre1}Стоп```", inline=False)
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="музыка"))
        await msg.edit(embed=em, view=view)
      
    elif arg.lower() == 'некст':

        em = discord.Embed(title="Некст", description="**Переключает на следующий трек (Если он есть в очереди)**",
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name="**Как использовать:**", value=f"```{pre1}Некст```", inline=False)
        em.add_field(name="Пример:", value=f"```{pre1}Некст```", inline=False)
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="музыка"))
        await msg.edit(embed=em, view=view)
      
    elif arg.lower() == 'громкость':

        em = discord.Embed(title="Громкость", description="**Меняет громкость музыки**",
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name="**Как использовать:**", value=f"```{pre1}Громкость <Значение в процентах>```", inline=False)
        em.add_field(name="Пример:", value=f"```{pre1}Громкость 200```", inline=False)
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="музыка"))
        await msg.edit(embed=em, view=view)

    elif arg.lower() == 'очередь':

        em = discord.Embed(title="Очередь", description="**Показывает все треки стоящие в очереди**",
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name="**Как использовать:**", value=f"```{pre1}Очередь```", inline=False)
        em.add_field(name="Пример:", value=f"```{pre1}Очередь```", inline=False)
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="музыка"))
        await msg.edit(embed=em, view=view)

    elif arg.lower() == 'мэшап':

        em = discord.Embed(title="Мэшап", description="**Засовывает два трека в блендер, и выдаёт вам музыкальный коктейль**\n(РАБОТАЮТ ССЫЛКИ ТОЛЬКО С ЮТУБА)",
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name="**Как использовать:**", value=f'```{pre1}Мэшап <"Имя или ссылка"> <"Имя или ссылка">```',
                     inline=False)
        em.add_field(name="Пример:", value=f"```{pre1}Mэшап https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                                            f' "Rick Astley - Together Forever"```',
                     inline=False)
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="музыка"))
        await msg.edit(embed=em, view=view)

    elif arg.lower() == 'цикл':

        em = discord.Embed(title="Цикл", description="**Зацикливает текущий трек в очереди**",
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name="**Как использовать:**", value=f"```{pre1}Цикл```", inline=False)
        em.add_field(name="Пример:", value=f"```{pre1}Цикл```", inline=False)
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="музыка"))
        await msg.edit(embed=em, view=view)

    elif arg.lower() == 'повтор':

        em = discord.Embed(title="Повтор", description="**Ставит на повтор ВСЮ очередь**",
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name="**Как использовать:**", value=f"```{pre1}Повтор```", inline=False)
        em.add_field(name="Пример:", value=f"```{pre1}Повтор```", inline=False)
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="музыка"))
        await msg.edit(embed=em, view=view)

    elif arg.lower() == 'перемешать':

        em = discord.Embed(title="Перемешать", description="**Береёт треки из очереди в случайном порядке**",
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name="**Как использовать:**", value=f"```{pre1}Перемешать```", inline=False)
        em.add_field(name="Пример:", value=f"```{pre1}Перемешать```", inline=False)
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="музыка"))
        await msg.edit(embed=em, view=view)

    elif arg.lower() == 'скажи':

        em = discord.Embed(title="Скажи",
                           description='**Заставляет зяблика сказать всё что вы пожелаете.** \n(С озвучкой если включить её в комманде "Настройки")',
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name="**Как использовать:**", value=f"```{pre1}Скажи <Текст>```", inline=False)
        em.add_field(name="Пример:", value=f"```{pre1}Скажи Клей```", inline=False)
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="веселье"))
        await msg.edit(embed=em, view=view)

      
    elif arg.lower() == 'демотиватор':

        em = discord.Embed(title="Демотиватор", description="**Генерирует демотиватор из вашей картинки или текста**",
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name='**Как использовать:**',
                     value=f'```{pre1}Демотиватор "<Текст сверху>" "<Текст снизу>" [Вложенная картинка]```',
                     inline=False)
        em.add_field(name='Пример:',
                     value=f'```{pre1}Демотиватор'
                           f' "А где?" "а всё, нету" ```',
                     inline=False)
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="веселье"))
        await msg.edit(embed=em, view=view)

    elif arg.lower() == 'префикс':

        em = discord.Embed(title="Префикс", description="**Меняет префикс бота на вашем сервере**",
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name='**Как использовать:**', value=f'```{pre1}Префикс "<Новый префикс>" ```', inline=False)
        em.add_field(name="Пример:", value=f'```{pre1}Префикс "!" ```', inline=False)
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="сервер"))
        await msg.edit(embed=em, view=view)
    elif arg.lower() == 'жмых':

        em = discord.Embed(title="Жмых",
                           description="**Скукоживает данную вами картинку**",
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name='**Как использовать:**', value=f'```{pre1}Жмых [Картинка или ссылка не неё] ```', inline=False)
        em.add_field(name="Пример:",
                     value=f'```{pre1}Жмых https://bit.ly/3OLHuZb```', inline=False)
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="веселье"))
        await msg.edit(embed=em, view=view)
    elif arg.lower() == 'инфо':

        em = discord.Embed(title="Инфо",
                           description="**Показывает информацию о выбранном пользователе или роли**",
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name='**Как использовать:**', value=f'```{pre1}Инфо <Упоминание или id> ```', inline=False)
        em.add_field(name="Пример:", value=f'```{pre1}Инфо @Зяблик 3.0```', inline=False)
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="инструменты"))
        await msg.edit(embed=em, view=view)
    elif arg.lower() == 'канал':

        em = discord.Embed(title="Канал",
                           description="**Создаёт голосовой канал который создаёт ещё один голосовой канал в той же категории!**",
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name='**Как использовать:**', value=f'```{pre1}Канал <Имя канала> ```', inline=False)
        em.add_field(name="Пример:", value=f'```{pre1}Канал == Create voice channel ==```', inline=False)
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="сервер"))
        await msg.edit(embed=em, view=view)

    elif arg.lower() == 'настройки':

        em = discord.Embed(title="Настройки",
                           description=f"**Открывает меню настроек бота**",
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name='**Как использовать:**', value=f'```{pre1}Настройки```', inline=False)
        em.add_field(name="Пример:", value=f'```{pre1}Настройки```', inline=False)
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="сервер"))
        await msg.edit(embed=em, view=view)
      
    elif arg.lower() == "помощь_close":
            await msg.delete()
            return False
    else:
        em = discord.Embed(title="Ошибка",
                           description="**Такой комманды не существует!**",
                           color=discord.Color.dark_green())
        em.set_author(name=client.user.name, icon_url=client.user.avatar.url)
        em.set_footer(text=f'Запросил: {ctx.author.name}', icon_url=ctx.author.avatar.url)
        em.set_thumbnail(url='https://media.discordapp.net/attachments/702506535451885656/863973275960475648/6.jpg')
        em.add_field(name='Проверьте ещё раз:', value=f'```{pre1}Помощь```', inline=False)
        view.add_item(discord.ui.Button(label="Назад", emoji="⬅️", custom_id="menu"))
        await msg.edit(embed=em, view=view)
