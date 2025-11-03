import discord
from discord.ext import commands
import datetime
from utils import ponto_manager # Importa nosso novo manager

# Classe auxiliar para guardar estado do ponto (será usada no bot.py)
class PontoState:
    def __init__(self):
        self.start_time = None # Hora que iniciou o ponto na sessão atual
        self.last_vc_join_time = None # Hora que entrou no último canal de voz

# --- View com Botões Iniciar/Finalizar ---
class PontoControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Persistente

    # --- FUNÇÃO ATUALIZADA ---
    async def handle_start_ponto(self, source: discord.Interaction | commands.Context):
        # source pode ser interaction (botão) ou ctx (comando)
        if isinstance(source, discord.Interaction):
            user = source.user
            bot = source.client
            guild = source.guild
            # Para interações, a resposta inicial deve ser rápida
            await source.response.defer(ephemeral=True, thinking=True)
            responder = source.followup.send # Usar followup após defer
        else: # É um commands.Context
            user = source.author
            bot = source.bot
            guild = source.guild
            responder = source.send # Comandos usam send direto


        if user.id in bot.active_pontos:
            await responder("⚠️ Você já está com o ponto iniciado!", ephemeral=True)
            return

        # Verifica estado de voz diretamente do membro no guild
        member = guild.get_member(user.id)
        if not member or not member.voice or not member.voice.channel:
             await responder("❌ Você precisa estar conectado a um canal de voz para iniciar o ponto.", ephemeral=True)
             return

        now = datetime.datetime.now(datetime.timezone.utc)
        bot.active_pontos[user.id] = PontoState()
        bot.active_pontos[user.id].start_time = now
        bot.active_pontos[user.id].last_vc_join_time = now # Começa a contar a partir de agora

        await responder("✅ Ponto iniciado! Seu tempo em canais de voz será contabilizado.", ephemeral=True)
        print(f"Ponto iniciado para {user.name} ({user.id})")

    # --- FUNÇÃO ATUALIZADA ---
    async def handle_end_ponto(self, source: discord.Interaction | commands.Context):
        if isinstance(source, discord.Interaction):
            user = source.user
            bot = source.client
            guild = source.guild
            await source.response.defer(ephemeral=True, thinking=True)
            responder = source.followup.send
        else: # commands.Context
            user = source.author
            bot = source.bot
            guild = source.guild
            responder = source.send

        if user.id not in bot.active_pontos:
            await responder("⚠️ Você não está com o ponto iniciado.", ephemeral=True)
            return

        now = datetime.datetime.now(datetime.timezone.utc)
        ponto_state = bot.active_pontos[user.id]

        seconds_added = 0
        # Se o usuário ainda está em um canal de voz ao finalizar, calcula o último trecho
        if ponto_state.last_vc_join_time:
             try:
                 time_in_current_vc = now - ponto_state.last_vc_join_time
                 seconds_added = time_in_current_vc.total_seconds()
                 ponto_manager.add_time(guild.id, user.id, seconds_added)
                 print(f"Adicionado {seconds_added:.2f}s para {user.name} ao finalizar ponto.")
             except Exception as e:
                 print(f"Erro ao calcular tempo final para {user.name}: {e}")
                 # Não impede de finalizar o ponto

        # Remove do estado ativo ANTES de enviar a mensagem final
        del bot.active_pontos[user.id]

        total_seconds, weekly_seconds = ponto_manager.get_user_times(guild.id, user.id)

        # --- INÍCIO DA CORREÇÃO (Formatação da Mensagem) ---
        session_time_formatted = ponto_manager.format_seconds(int(seconds_added))
        total_time_formatted = ponto_manager.format_seconds(total_seconds)
        weekly_time_formatted = ponto_manager.format_seconds(weekly_seconds)

        await responder(
            f"✅ Ponto finalizado!\n"
            f"**🕑 Tempo nesta sessão:** **{session_time_formatted}**\n"
            f"📅 Tempo nesta semana: **{weekly_time_formatted}**\n"
            f"⏱️ Tempo total registrado: **{total_time_formatted}**",
            ephemeral=True
        )
        # --- FIM DA CORREÇÃO ---
        print(f"Ponto finalizado para {user.name} ({user.id})")


    @discord.ui.button(label="Iniciar Ponto", style=discord.ButtonStyle.success, custom_id="ponto_iniciar")
    async def iniciar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_start_ponto(interaction) # Passa interaction

    @discord.ui.button(label="Finalizar Ponto", style=discord.ButtonStyle.danger, custom_id="ponto_finalizar")
    async def finalizar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_end_ponto(interaction) # Passa interaction