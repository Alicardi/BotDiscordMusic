import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from discord.ui import Button, View
from collections import deque



intents = discord.Intents.default()
intents.guilds = True  
intents.members = True  
intents.messages = True  
intents.message_content = True  

bot = commands.Bot(command_prefix='!', intents=intents)

# Добавить треки как в примере
tracks = {
    # 1: "tracks/Gringo - Пропавший Дух v2.mp3",
}

class MusicPlayer:
    def __init__(self):
        self.queue = deque()
        self.current = None
        self.is_looping = False

    def add_to_queue(self, track):
        self.queue.append(track)

    def next_track(self):
        if self.is_looping and self.current:
            self.queue.appendleft(self.current)  
        if self.queue:
            self.current = self.queue.popleft()
        else:
            self.current = None
        return self.current

    def toggle_loop(self):
        self.is_looping = not self.is_looping

player = MusicPlayer()

@bot.command(name='playtrack', help='Воспроизводит указанный локальный трек по номеру. Использование: !playtrack <номер трека>')
async def playtrack(ctx, track_number: int = None):
    if track_number is None:
        await ctx.send("Вы не указали номер трека. Используйте команду так: `!playtrack <номер трека>`. Используйте `!listtracks` для списка треков.")
        return
    
    track_path = tracks.get(track_number)
    if not track_path:
        await ctx.send("Трек с таким номером не найден. Пожалуйста, проверьте список доступных треков с помощью `!listtracks`.")
        return

    if ctx.voice_client is None:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("Вы не подключены к голосовому каналу.")
            return

    source = FFmpegPCMAudio(track_path)
    ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
    await ctx.send(f'Воспроизведение: {track_path.split("/")[-1]}')

async def start_playback(ctx):
    track_path = player.next_track()
    if track_path:
        source = FFmpegPCMAudio(track_path)
        ctx.voice_client.play(source, after=lambda e: start_playback(ctx) if not e else print('Player error:', e))
    else:
        print("Очередь пуста или треки закончились.")

@bot.command(name='listtracks', help='Отображает список всех доступных треков')
async def listtracks(ctx):
    message = "Доступные треки:\n"
    for number, path in tracks.items():
        track_name = path.split("/")[-1] 
        message += f"{number}: {track_name}\n"
    await ctx.send(message)

@bot.command(name='skip', help='Пропускает текущий трек')
async def skip(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Трек пропущен.")
    start_playback(ctx)

@bot.command(name='loop', help='Переключает режим повтора текущего трека')
async def loop(ctx):
    player.toggle_loop()
    await ctx.send("Режим повтора " + ("включен" if player.is_looping else "выключен"))

@bot.command(name='clear', help='Очищает очередь треков')
async def clear(ctx):
    player.clear_queue()
    await ctx.send("Очередь очищена.")

@bot.command(name='playyoutube', help='Воспроизводит указанное YouTube видео по URL')
async def playyoutube(ctx, *, url):
    if ctx.voice_client is None:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("Вы не подключены к голосовому каналу.")
            return

    source = FFmpegPCMAudio(url)
    ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
    await ctx.send(f'Воспроизведение YouTube видео: {url}')

@bot.command(name='join', help='Присоединяется к голосовому каналу')
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("Вы не подключены к голосовому каналу.")

@bot.command(name='leave', help='Покидает голосовой канал')
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("Бот не подключен к голосовому каналу.")

class CustomHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Помощь по командам бота", description="Список всех команд:", color=discord.Color.blue())
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "Без категории")
                embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)
        channel = self.get_destination()
        await channel.send(embed=embed)
        print(f"Sent help to {channel}")

    async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(command),
                              description=command.help or "Описание отсутствует...",
                              color=discord.Color.green())
        channel = self.get_destination()
        await channel.send(embed=embed)
        print(f"Sent command help for {command.name} to {channel}")

    def get_command_signature(self, command):
        return f'{self.clean_prefix}{command.qualified_name} {command.signature}'

bot.help_command = commands.DefaultHelpCommand()

@bot.event
async def on_ready():
    print(f'Залогинен как {bot.user.name}')

# TOKEN 
bot.run('') 
