import discord
from discord.ext import commands
import datetime
import requests
import wikipedia
import imdb
import random
from discord_components import DiscordComponents, Button, ButtonStyle



PREFIX = '#'
client = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())
wikipedia.set_lang('ru')
api_key = ''

@client.event
async def on_ready():
    print('Бот подключен')
    DiscordComponents(client)
    await client.change_presence(status=discord.Status.online, activity=discord.Game(f'в {PREFIX}help'))


@client.event
async def on_command_error(ctx, error):
    pass


###########################################################################################################
@client.command(pass_context = True)
async def all_commands(ctx):
    emb = discord.Embed(title='Навигация по командам')
    emb.add_field(name=f'{PREFIX}clear', value='Очистка чата по указанному количеству сообщений')
    emb.add_field(name=f'{PREFIX}mute', value='Запретить пользователю отправлять сообщение')
    emb.add_field(name=f'{PREFIX}unmute', value='Разрешить пользователю отправлять сообщение')
    emb.add_field(name=f'{PREFIX}kick', value='Исключение участника с возможностью самостоятельно вернуться')
    emb.add_field(name=f'{PREFIX}ban', value='Исключение участника без возможности самостоятельно вернуться')
    emb.add_field(name=f'{PREFIX}send', value='Отправить анонимное сообщение пользователю')
    emb.add_field(name=f'{PREFIX}weather', value='Показывает погоду в в введеном городе')
    emb.add_field(name=f'{PREFIX}find', value='Ищет введенную информацию')
    emb.add_field(name=f'{PREFIX}film', value='Ищет введенную информацию по названию фильма')
    emb.add_field(name=f'{PREFIX}bestfilm', value='Показывает случайный фильм из 250 лучших')
    emb.add_field(name=f'{PREFIX}translate', value='Переводит текст')


    await ctx.send(embed=emb)


@client.command(pass_context = True)
@commands.has_permissions(administrator=True)
async def clear(ctx, amount: int):
    """Очищает выбранное количество сообщений"""
    if isinstance(amount, int):
        await ctx.channel.purge(limit=amount + 1)



@client.command(pass_context = True)
@commands.has_permissions(administrator=True)
async def mute(ctx, member: discord.Member):
    """Не позволяет пользователю отправлять сообщения"""
    await ctx.channel.purge(limit=1)
    mute_role = discord.utils.get(ctx.message.guild.roles, name='mute')
    await member.add_roles(mute_role)
    emb = discord.Embed(title='Оповещение!', colour=discord.Colour.purple())
    emb.set_author(name=member.name, icon_url=member.avatar_url)
    emb.add_field(name=f'{member.name}', value=f'У пользователя {member.mention} ограничение чата за нарушение правил')
    await ctx.send(embed=emb)


@client.command(pass_context = True)
@commands.has_permissions(administrator=True)
async def unmute(ctx, member: discord.Member):
    """Разрешает пользователю отправлять сообщения"""
    await ctx.channel.purge(limit=1)
    mute_role = discord.utils.get(ctx.message.guild.roles, name='mute')
    await member.remove_roles(mute_role)
    emb = discord.Embed(title='Оповещение!', colour=discord.Colour.purple())
    emb.set_author(name=member.name, icon_url=member.avatar_url)
    emb.add_field(name=f'{member.name}', value=f'У пользователя {member.mention} снято ограничение чата')
    await ctx.send(embed=emb)


@client.command(pass_context = True)
@commands.has_permissions(administrator=True)
async def kick(ctx, member:discord.Member, *, reason = None):
    """Исключает пользователя с возможностью вернутся"""
    emb = discord.Embed(title='Оповещение об исключении!', colour=discord.Colour.dark_gold())
    await ctx.channel.purge(limit=1)
    await member.kick(reason=reason)

    emb.set_author(name=member.name, icon_url=member.avatar_url)
    emb.add_field(name=f'{member.name}', value=f'Исключен пользователь {member.mention}')
    emb.set_footer(text=f'Был исключен администратором {ctx.author.name}', icon_url=ctx.author.avatar_url)
    await ctx.send(embed=emb)


@client.command(pass_context = True)
@commands.has_permissions(administrator=True)
async def ban(ctx, member:discord.Member, *, reason = None):
    """Банит пользователя, без разбана невозможно зайти обратно"""
    emb = discord.Embed(title='Оповещение о бане!', colour=discord.Colour.dark_red())
    await ctx.channel.purge(limit=1)
    await member.ban(reason=reason)
    emb.set_author(name=member.name, icon_url=member.avatar_url)
    emb.add_field(name=f'{member.name}', value=f'Забанен пользователь {member.mention}')
    emb.set_footer(text=f'Был забанен администратором {ctx.author.name}', icon_url=ctx.author.avatar_url)
    await ctx.send(embed=emb)


@client.command(pass_context = True)
async def send(ctx, member: discord.Member, *message):
    """Отправляет анонимное сообщение пользователю"""
    await ctx.channel.purge(limit=1)
    message = ' '.join(message)
    await member.send(message)





###########################################################################################################
@client.command(pass_context = True)
async def weather(ctx, town='Москва'):
    """Показывает погоду и фото местности"""
    key = '3d600cbfdcd737b14ae03adfe8105dc3'
    url = f'https://api.openweathermap.org/data/2.5/weather?q={town}&appid={key}'
    response = requests.get(url)
    json_response = response.json()

    loc = pos(town)
    map_request = f"http://static-maps.yandex.ru/1.x/?ll={loc[0]},{loc[1]}&spn=0.2,0.002&l=sat"

    weather = f'Погода: {json_response["weather"][0]["main"]},' \
              f' {json_response["weather"][0]["description"].capitalize()}'
    temperature = f'Температура: {str(json_response["main"]["temp"] - 273)[:5]} °С, ' \
                  f'чувствуется как: {str(json_response["main"]["feels_like"] - 273)[:5]} °С'
    other = f'Влажность: {json_response["main"]["humidity"]}%, Pressure: {json_response["main"]["pressure"]}'
    sun = f'Восход: {norm_time(json_response["sys"]["sunrise"] + 10800)}, ' \
          f'Закат: {norm_time(json_response["sys"]["sunset"] + 10800)}'

    emb = discord.Embed(title=f'Погода в городе {town}', colour=discord.Colour.green())
    emb.set_author(name=client.user.name, icon_url=client.user.avatar_url)
    emb.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
    emb.set_image(url=map_request)
    emb.add_field(name='Погода:', value=f'{weather}')
    emb.add_field(name='Температура:', value=f'{temperature}')
    emb.add_field(name='Другое:', value=f'{other}')
    emb.add_field(name='Солнце:', value=f'{sun}')

    await ctx.send(embed=emb)


@client.command(pass_context = True)
async def find(ctx, *info):
    """Ищет в википедии введеную информацию"""
    info = ' '.join(info)
    print(info)
    message = f'{wikipedia.summary(info, sentences=4)}'
    print(message)
    emb = discord.Embed(title=f'Результат поиска по запросу "{info.capitalize()}"', colour=discord.Colour.blue())
    emb.add_field(name=f'{info.capitalize()}', value=message)
    await ctx.send(embed=emb)


@client.command(pass_context = True)
async def film(ctx, *movie):
    """Показывают информацию о введеном фильме"""
    movie = ' '.join(movie)
    moviesDb = imdb.IMDb()
    movies = moviesDb.search_movie(movie)
    id = movies[0].getID()
    ans = moviesDb.get_movie(id)
    title = ans['title']
    type = ans['kind']
    year = ans['year']
    thumbnail = ans['cover url']
    image = ans['full-size cover url']
    rating = ans['rating']
    box_office = ans['box office']
    budget = box_office['Budget']
    money = box_office['Cumulative Worldwide Gross']
    try:
        directors = ans['directors']
    except KeyError:
        directors = ['Не найдено']
    casting = ans['cast']
    actors = casting[:4]
    directors = ' '.join(map(str, directors))
    casting = ', '.join(map(str, casting[:4]))
    emb = discord.Embed(title=f'Результат поиска по запросу "{movie.capitalize()}"', colour=discord.Colour.green())
    emb.add_field(name='Название:', value=title)
    emb.add_field(name='Год выпуска:', value=year)
    emb.add_field(name='Тип:', value=f'{type}')
    emb.add_field(name='Рейтинг:', value=f'{rating}')
    emb.add_field(name='Режиссер:', value=f'{directors}')
    emb.add_field(name='Актеры:', value=f'{casting}')
    emb.add_field(name='Бюджет:', value=f'{budget}')
    emb.add_field(name='Сборы:', value=f'{money}')
    emb.set_thumbnail(url=thumbnail)
    emb.set_image(url=image)
    embs = []
    for i in range(0, 4):
        person = actors[i]
        id = person.getID()
        person = moviesDb.get_person(id)
        thumbnail = person['headshot']
        image = person['full-size headshot']
        ember = discord.Embed(title=f'{actors[0]}')
        ember.set_image(url=image)
        ember.set_thumbnail(url=thumbnail)
        embs.append(ember)
    await ctx.send(embed=emb, components=[[
                       Button(style=ButtonStyle.green, label=f'{actors[0]}', emoji='✔'),
                       Button(style=ButtonStyle.green, label=f'{actors[1]}', emoji='✔'),
                       Button(style=ButtonStyle.green, label=f'{actors[2]}', emoji='✔'),
                       Button(style=ButtonStyle.green, label=f'{actors[3]}', emoji='✔')]])
    while True:
        response = await client.wait_for('button_click')
        if response.channel == ctx.channel:
            if response.component.label == f'{actors[0]}':
                await response.respond(embed=embs[0])
            elif response.component.label == f'{actors[1]}':
                await response.respond(embed=embs[1])
            elif response.component.label == f'{actors[2]}':
                await response.respond(embed=embs[2])
            elif response.component.label == f'{actors[3]}':
                await response.respond(embed=embs[3])



@client.command(pass_context = True)
async def bestfilm(ctx):
    """Показывает случайный фильм из 250 IMDb"""
    moviesDb = imdb.IMDb()
    top = moviesDb.get_top250_movies()
    ans = random.choice(top)
    id = ans.getID()
    ans = moviesDb.get_movie(id)
    title = ans['title']
    type = ans['kind']
    year = ans['year']
    thumbnail = ans['cover url']
    image = ans['full-size cover url']
    rating = ans['rating']
    directors = ans['directors']
    casting = ans['cast']
    box_office = ans['box office']
    budget = box_office['Budget']
    money = box_office['Cumulative Worldwide Gross']
    directors = ' '.join(map(str, directors))
    casting = ', '.join(map(str, casting[:4]))
    emb = discord.Embed(title=f'Случайный фильм из топ 250 IMDb', colour=discord.Colour.green())
    emb.add_field(name='Название:', value=title)
    emb.add_field(name='Год выпуска:', value=year)
    emb.add_field(name='Тип:', value=f'{type}')
    emb.add_field(name='Рейтинг:', value=f'{rating}')
    emb.add_field(name='Режиссер:', value=f'{directors}')
    emb.add_field(name='Актеры:', value=f'{casting}')
    emb.add_field(name='Бюджет:', value=f'{budget}')
    emb.add_field(name='Сборы:', value=f'{money}')
    emb.set_thumbnail(url=thumbnail)
    emb.set_image(url=image)
    await ctx.send(embed=emb)


@client.command(pass_context = True)
async def translate(ctx, fromlang, tolang, *translating_text):
    """Переводит текст (с какого на какой)
    Возможные языки:
    ru - Русский
    en - Английский
    it - Итальянский
    de - Немецкий
    es - Испанский
    uk - Украинский
    остальные языки можно посмотреть по этой ссылке (ISO-639-1):
    https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes"""
    translating_text = ' '.join(translating_text)
    url = "https://translated-mymemory---translation-memory.p.rapidapi.com/api/get"
    querystring = {"langpair": f"{fromlang}|{tolang}", "q": f"{translating_text}", "mt": "1", "onlyprivate": "0",
                   "de": "a@b.c"}

    headers = {
        "X-RapidAPI-Host": "translated-mymemory---translation-memory.p.rapidapi.com",
        "X-RapidAPI-Key": "80acf4f38dmsh2642f2ed7e61192p165421jsnabed824d9403"
    }

    response = requests.request("GET", url, headers=headers, params=querystring).json()
    result = response['responseData']['translatedText']
    await ctx.send(result)


###########################################################################################################
@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.mention} Обязательно укажите аргумент!')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.mention} У вас недостаточно прав!')


###########################################################################################################
def norm_time(unix: int):
    return datetime.datetime.utcfromtimestamp(unix).strftime('%H:%M:%S')


def pos(town):
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={town}&format=json"
    response = requests.get(geocoder_request)
    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]['Point']['pos']
    return list(map(float, toponym.split()))



###########################################################################################################

TOKEN = 'Your Token'
client.run(TOKEN)
