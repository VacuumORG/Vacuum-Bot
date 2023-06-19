import importlib
from typing import Optional

import discord
from discord import Interaction
from discord.ext import commands, tasks

import pomodoro.checkers
import pomodoro.models
import pomodoro.session
import pomodoro.ui
from shared.sound_controller import SoundController

importlib.reload(pomodoro.models)
importlib.reload(pomodoro.session)
importlib.reload(pomodoro.ui)
importlib.reload(pomodoro.checkers)

from pomodoro.ui import session_start_view, session_info_view, all_sessions_info_view, help_view, close_session_view
from pomodoro.session import PomodoroSettings, PomodoroSession
from pomodoro.models import AlarmOptions
from pomodoro.checkers import has_session, is_guild, is_in_voice_channel, user_channel_do_not_have_session, \
    is_session_owner, is_in_voice_channel_chat


class Pomodoro(commands.GroupCog, group_name='pomodoro', group_description='Pomodoro'):
    """Pomodoro bot"""
    sessions = dict()

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        SoundController(self.bot).start()
        self.disconnect_if_no_session.start()

    def close_session(self, channel):
        if channel in self.sessions:
            session = self.sessions.pop(channel)
            session.close()

    @tasks.loop(seconds=1)
    async def disconnect_if_no_session(self):
        if not self.sessions:
            SoundController().disconnect()

    @discord.app_commands.command(name='start',
                                  description='Inicia uma nova sessão de pomodoro. Deve ser utilizado estando em um chat de voz.')
    @discord.app_commands.describe(work_time='Tempo de trabalho em minutos (padrão 25)',
                                   break_time='Tempo do intervalo em minutos (padrão 5)',
                                   long_break_time='Tempo do intervalo longo em minutos (padrão 15)',
                                   n_breaks='Número de intervalos até intervalo longo (padrão 3)',
                                   alarm_sound='Tipo de alarme',
                                   use_voices='Utilizar voz nas notificações (padrão False)')
    @user_channel_do_not_have_session(sessions=sessions)
    @is_in_voice_channel()
    @is_guild()
    async def _start(self, interaction: Interaction, work_time: Optional[int] = 25,
                     break_time: Optional[int] = 5, long_break_time: Optional[int] = 15,
                     n_breaks: Optional[int] = 3, alarm_sound: Optional[AlarmOptions] = AlarmOptions.Digital,
                     use_voices: Optional[bool] = False):
        settings = PomodoroSettings(work_time=work_time, break_time=break_time, long_break_time=long_break_time,
                                    n_breaks=n_breaks, alarm_sound=alarm_sound, use_voices=use_voices)
        channel = interaction.user.voice.channel
        session = PomodoroSession(self.bot, interaction, settings)
        session.on_empty_channel = self.close_session
        self.sessions[channel] = session
        await session.start()

        await interaction.response.send_message(**session_start_view(settings))

    @discord.app_commands.command(name='pular',
                                  description='Pula o estado atual do pomodoro. Deve ser utilizado no canal de voz da sessão.')
    @is_session_owner(sessions=sessions)
    @has_session(sessions=sessions)
    @is_in_voice_channel_chat()
    @is_guild()
    async def skip(self, interaction: Interaction):
        user_channel = interaction.user.voice.channel
        session = self.sessions[user_channel]
        return await session.skip(interaction)

    @discord.app_commands.command(
        description='Exibe as informações do pomodoro. Deve ser utilizado no canal de voz da sessão.')
    @has_session(sessions=sessions)
    @is_in_voice_channel_chat()
    @is_guild()
    async def info(self, interaction: Interaction):
        user_channel = interaction.user.voice.channel
        session = self.sessions[user_channel]
        await interaction.response.send_message(**session_info_view(session))

    @discord.app_commands.command(name='sessões', description='Exibe todas as sessões ativas de pomodoro.')
    @is_guild()
    async def _sessions(self, interaction: Interaction):
        await interaction.response.send_message(**all_sessions_info_view(list(self.sessions.values())))

    @discord.app_commands.command(name='ajuda', description='Mais detalhes sobre os comandos.')
    @is_guild()
    async def help(self, interaction: Interaction):
        await interaction.response.send_message(**help_view())

    @discord.app_commands.command(name='encerrar',
                                  description='Encerra a sessão de pomodoro. Deve ser utilizado no canal de voz da sessão.')
    @is_session_owner(sessions=sessions)
    @has_session(sessions=sessions)
    @is_in_voice_channel_chat()
    @is_guild()
    async def end(self, interaction: Interaction):
        async def ok_callback(new_view):
            self.close_session(interaction.channel)
            await interaction.edit_original_response(**new_view)

        async def cancel_callback():
            await interaction.delete_original_response()

        await interaction.response.send_message(**close_session_view(ok_callback, cancel_callback))

    def get_helper(self):
        return ["Pomovacuum", help_view()['embed']]


async def setup(bot):
    await bot.add_cog(Pomodoro(bot))
