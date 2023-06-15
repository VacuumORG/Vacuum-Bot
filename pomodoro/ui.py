from typing import List, Callable, Awaitable

from discord import Embed, Colour, ButtonStyle, Interaction
from discord.ui import View, Button

from pomodoro.session import PomodoroSettings, PomodoroSession, PomodoroState

COLOUR = Colour.red()


def __add_settings_fields(embed: Embed, settings: PomodoroSettings):
    embed.add_field(name="Tempo de trabalho",
                    value=f"{settings.work_time} minuto{'s' if settings.work_time > 1 else ''}")
    embed.add_field(name="Tempo de descanso",
                    value=f"{settings.break_time} minuto{'s' if settings.break_time > 1 else ''}")
    embed.add_field(name="Tempo de descanso longo",
                    value=f"{settings.long_break_time} minuto{'s' if settings.long_break_time > 1 else ''}")
    embed.add_field(name="Ciclos entre descansos longos",
                    value=f"{settings.n_breaks}")
    return embed


def __convert_session_state(state: PomodoroState):
    if state == PomodoroState.Working:
        return "Trabalhando"
    elif state == PomodoroState.Break:
        return "Descanso"
    elif state == PomodoroState.LongBreak:
        return "Descanso Longo"
    return ""


def session_start_view(settings: PomodoroSettings):
    embed = Embed(title=":tomato: PomoVacuum", description="Começando nova sessão de pomodoro com as configurações:",
                  colour=COLOUR)
    return {'embed': __add_settings_fields(embed, settings)}


def session_info_view(session: PomodoroSession):
    embed = Embed(title=":tomato: PomoVacuum",
                  description=f"Informações sobre a sessão do canal {session.channel.mention}:", colour=COLOUR)
    __add_settings_fields(embed, session.settings)
    embed.add_field(name="Estado", value=f"{__convert_session_state(session.state)}")
    remaining_minutes, remaining_seconds = session.get_remaining_time()
    embed.add_field(name="Tempo restante", value=f"{remaining_minutes}:{remaining_seconds}")
    embed.add_field(name="Ciclos completos", value=f"{session.cycles}")
    embed.add_field(name="Pausado?", value=f"{'Sim' if session.paused else 'Não'}")
    return {'embed': embed}


def __create_short_session_info(session: PomodoroSession):
    return f"Canal: {session.channel.mention}\n" \
           f"Iniciador: {session.user.mention}\n" \
           f"({session.settings.work_time}\{session.settings.break_time}\{session.settings.long_break_time})\n" \
           f"Estado: {__convert_session_state(session.state)}\n"


def all_sessions_info_view(sessions: List[PomodoroSession]):
    embed = Embed(title=":tomato: PomoVacuum", description=f"Sessões ativas:", colour=COLOUR)

    for i, session in enumerate(sessions):
        embed.add_field(name=f"{i + 1}", value=f"{__create_short_session_info(session)}")

    return {'embed': embed}


def help_view():
    description = f"Bem vindo ao PomoVacuum, o bot de pomodoro da Vacuum.\n\n " \
                  f"O pomodoro é uma técnica de gerenciamento de tempo que divide o trabalho em intervalos de 25 " \
                  f"minutos, chamados de 'pomodoros', seguidos por breves pausas. Essa abordagem ajuda a manter o foco " \
                  f"e aumentar a produtividade.\n Com nosso bot inicie sua sessão de pomodoro customizável " \
                  f"em um chat de voz e foque nos estudos/trabalhos, o bot notificará quando um 'pomodoro' acabar.\n\n" \
                  f"Aqui estão mais detalhes sobre como utilizar nossos comandos:\n"
    embed = Embed(title=":tomato: PomoVacuum", description=description, colour=COLOUR)
    embed.add_field(name=":arrow_forward:   /pomodoro start",
                    value="Cria uma sessão de pomodoro atrelada ao canal de voz em que você estiver conectado."
                          "O comando aceita parametros permitindo configurar seu pomodoro como quiser."
                          "Precisa estar conectado a um canal de voz para utilizar este comando.", inline=False)
    embed.add_field(name=":track_next:   /pomodoro pular",
                    value="Pula o estado do pomodoro. "
                          "Caso esteja em 'Trabalho' vai para 'Intervalo' ou 'Intervalo Longo' e vice versa. "
                          "O comando só é aceito dentro do chat de texto do canal de voz com uma sessão de pomodoro ativa.",
                    inline=False)
    embed.add_field(name=":information_source:   /pomodoro info",
                    value="Apresenta as informações da sessão de pomodoro. "
                          "O comando só é aceito dentro do chat de texto do canal de voz com uma sessão de pomodoro ativa.",
                    inline=False)
    embed.add_field(name=":koko:   /pomodoro sessões",
                    value="Apresenta todas as sessões de pomodoro ativas.", inline=False)

    return {'embed': embed}


def close_session_view(ok_callback: Callable[[dict], Awaitable], cancel_callback: Callable[[], Awaitable]):
    embed = Embed(title=":tomato: PomoVacuum", description="Deseja encerrar a sessão de pomodoro?", colour=COLOUR)
    view = View()
    ok_bt = Button(label="Sim", style=ButtonStyle.danger)
    cancel_bt = Button(label="Cancelar", style=ButtonStyle.secondary)

    async def __ok_callback(interaction: Interaction):
        await interaction.response.defer()
        closed_view = {'embed': None, 'view': None, 'content': ":tomato: Sessão encerrada!"}
        await ok_callback(closed_view)

    async def __cancel_callback(interaction: Interaction):
        await interaction.response.defer()
        await cancel_callback()

    ok_bt.callback = __ok_callback
    cancel_bt.callback = __cancel_callback
    view.add_item(ok_bt).add_item(cancel_bt)
    return {'embed': embed, 'view': view}
