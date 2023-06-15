import discord
from discord import Interaction, VoiceChannel


def is_guild():
    async def predicate(interaction: Interaction):
        if not interaction.guild:
            await interaction.response.send_message(
                content="Você precisa estar dentro de um servidor para utilizar este comando!",
                delete_after=8)
        return bool(interaction.guild)

    return discord.app_commands.check(predicate)


def is_in_voice_channel():
    async def predicate(interaction: Interaction):
        user_voice = interaction.user.voice
        if user_voice and isinstance(user_voice.channel, VoiceChannel):
            return True
        await interaction.response.send_message(
            content="Você precisa estar em um canal de voz para utilizar este comando!",
            delete_after=8)
        return False

    return discord.app_commands.check(predicate)


def is_in_voice_channel_chat():
    async def predicate(interaction: Interaction):
        it_channel = interaction.channel
        if isinstance(it_channel, VoiceChannel):
            return True
        await interaction.response.send_message(
            content="Você precisa estar em um chat de canal de voz para utilizar este comando",
            delete_after=8)
        return False

    return discord.app_commands.check(predicate)


def has_session(sessions):
    async def predicate(interaction: Interaction):
        channel = interaction.channel
        if channel in sessions:
            return True
        await interaction.response.send_message(
            content="Não há sessão de pomodoro ativa para este canal!",
            delete_after=8)
        return False

    return discord.app_commands.check(predicate)


def user_channel_do_not_have_session(sessions):
    async def predicate(interaction: Interaction):
        user_vc = interaction.user.voice
        if user_vc:
            if user_vc.channel not in sessions:
                return True
        await interaction.response.send_message(
            content="Esse canal já possui uma sessão de pomodoro ativa!",
            delete_after=8)
        return False

    return discord.app_commands.check(predicate)


def is_session_owner(sessions):
    async def predicate(interaction: Interaction):
        user_vc = interaction.user.voice
        if user_vc:
            if user_vc.channel in sessions:
                session = sessions[user_vc.channel]
                if interaction.user.id == session.user.id:
                    return True
        await interaction.response.send_message(
            content="Você precisa ser o iniciador da sessão para utilizar este comando.",
            delete_after=8)
        return False

    return discord.app_commands.check(predicate)
