import asyncio

import discord
from discord.ext import tasks, commands


class SoundController:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.__setup_instance(*args, **kwargs)
        return cls._instance

    def __setup_instance(self, *args, **kwargs):
        bot = None
        if args:
            bot = args[0]
        elif kwargs:
            bot = kwargs['bot']
        if not bot:
            raise AttributeError("The first initialization of Sound Controller must receive the bot as argument!")
        if not isinstance(bot, commands.Bot):
            raise TypeError(
                "The first initialization of Sound Controller must receive a discord.py Bot instance as argument")
        self.bot = bot
        self.queue = asyncio.Queue()
        self.lock = asyncio.Lock()

    async def play(self, sound_path, channel):
        await self.queue.put((sound_path, channel))

    async def _connect_to_channel(self, channel):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=channel.guild)
        if not voice_client:
            return await channel.connect()
        if not voice_client.is_connected():
            await voice_client.disconnect(force=True)
            return await channel.connect()
        if voice_client.channel != channel:
            await voice_client.move_to(channel)
            while not voice_client.is_connected():
                await asyncio.sleep(0.05)
            await asyncio.sleep(0.1)

        return voice_client

    async def _play_sound(self, voice_client, sound_path):
        voice_client.play(discord.FFmpegPCMAudio(sound_path), after=lambda x: ...)
        while voice_client.is_playing():
            await asyncio.sleep(0.2)

    @tasks.loop(seconds=0.2)
    async def task_loop(self):
        while not self.queue.empty():
            sound_path, channel = await self.queue.get()
            async with self.lock:
                voice_client = await self._connect_to_channel(channel)
                await self._play_sound(voice_client, sound_path)

            await asyncio.sleep(0.1)  # Delay between playing sounds

    def start(self):
        self.task_loop.start()

    def stop(self):
        self.task_loop.stop()

    def disconnect(self):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=self.bot.guilds[0])
        if voice_client:
            asyncio.create_task(voice_client.disconnect(force=True))
