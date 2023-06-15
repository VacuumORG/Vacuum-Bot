import importlib
from typing import Optional

import discord
from discord import Interaction, VoiceChannel
from discord.ext import commands

import pomodoro.models
import pomodoro.session
import pomodoro.ui

importlib.reload(pomodoro.models)
importlib.reload(pomodoro.session)
importlib.reload(pomodoro.ui)

from pomodoro.ui import session_start_view, session_info_view, all_sessions_info_view, help_view
from pomodoro.session import PomodoroSettings, PomodoroSession
from pomodoro.models import AlarmOptions


class Pomodoro(commands.GroupCog, group_name='pomodoro', group_description='Pomodoro'):
    """Pomodoro bot"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sessions = dict()
        self.vc = None

    async def finish_session_callback(self, channel):
        if channel in self.sessions:
            self.sessions.pop(channel)

    @discord.app_commands.command(name='start',
                                  description='Inicia uma nova sessão de pomodoro. Deve ser utilizado estando em um chat de voz.')
    @discord.app_commands.describe(work_time='Tempo de trabalho em minutos (padrão 25)',
                                   break_time='Tempo do intervalo em minutos (padrão 5)',
                                   long_break_time='Tempo do intervalo longo em minutos (padrão 15)',
                                   n_breaks='Número de intervalos até intervalo longo (padrão 3)',
                                   alarm_sound='Tipo de alarme',
                                   use_voices='Utilizar voz nas notificações (padrão False)')
    async def _start(self, interaction: Interaction, work_time: Optional[int] = 25,
                     break_time: Optional[int] = 5, long_break_time: Optional[int] = 15,
                     n_breaks: Optional[int] = 3, alarm_sound: Optional[AlarmOptions] = AlarmOptions.Digital,
                     use_voices: Optional[bool] = False):
        settings = PomodoroSettings(work_time=work_time, break_time=break_time, long_break_time=long_break_time,
                                    n_breaks=n_breaks, alarm_sound=alarm_sound, use_voices=use_voices)
        if isinstance(interaction.user, discord.Member):
            user_voice = interaction.user.voice
            if not user_voice or not isinstance(user_voice.channel, VoiceChannel):
                return await interaction.response.send_message(
                    "Você precisa estar em um canal de voz para criar uma sessão de pomodoro")
            if user_voice.channel in self.sessions:
                return await interaction.response.send_message("Esse canal já possui uma sessão de pomodoro ativa!")
            session = PomodoroSession(self.bot, interaction, settings)
            session.finish_session_callback = self.finish_session_callback
            self.sessions[user_voice.channel] = session
            await session.start()

            await interaction.response.send_message(**session_start_view(settings))

    @discord.app_commands.command(name='pular',
                                  description='Pula o estado atual do pomodoro. Deve ser utilizado no canal de voz da sessão.')
    async def skip(self, interaction: Interaction):
        if isinstance(interaction.user, discord.Member):
            user_channel = interaction.user.voice.channel
            if interaction.channel_id != user_channel.id:
                return await interaction.response.send_message(content="Comando exclusivo para chats de canais de voz",
                                                               delete_after=5)
            if user_channel not in self.sessions:
                return await interaction.response.send_message("Não há sessão de pomodoro ativa para este canal!")
            session = self.sessions[user_channel]
            return await session.skip(interaction)

    @discord.app_commands.command(
        description='Exibe as informações do pomodoro. Deve ser utilizado no canal de voz da sessão.')
    async def info(self, interaction: Interaction):
        if isinstance(interaction.user, discord.Member):
            user_channel = interaction.user.voice.channel
            if not isinstance(interaction.channel, VoiceChannel):
                return await interaction.response.send_message(content="Comando exclusivo para chats de canais de voz",
                                                               delete_after=5)
            if interaction.channel not in self.sessions:
                return await interaction.response.send_message(
                    content="Não há sessão de pomodoro ativa para este canal!",
                    delete_after=5)
            session = self.sessions[user_channel]
            await interaction.response.send_message(**session_info_view(session))

    @discord.app_commands.command(name='sessões', description='Exibe todas as sessões ativas de pomodoro.')
    async def sessions(self, interaction: Interaction):
        if isinstance(interaction.user, discord.Member):
            await interaction.response.send_message(**all_sessions_info_view(list(self.sessions.values())))

    @discord.app_commands.command(name='ajuda', description='Mais detalhes sobre os comandos.')
    async def help(self, interaction: Interaction):
        if isinstance(interaction.user, discord.Member):
            await interaction.response.send_message(**help_view())

    def get_helper(self):
        return ["Pomovacuum", help_view()['embed']]


async def setup(bot):
    await bot.add_cog(Pomodoro(bot))
