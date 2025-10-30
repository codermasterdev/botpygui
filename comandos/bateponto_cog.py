import discord
from discord.ext import commands
import datetime
from utils import ponto_manager
from .ponto_system import PontoControlView, PontoState # Importa a View e o State

class BatePontoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Listener para eventos de voz (Entrar/Sair/Mudar de canal)
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        # Ignora se o usuário não está com o ponto ativo
        if member.id not in self.bot.active_pontos:
            return

        now = datetime.datetime.now(datetime.timezone.utc)
        ponto_state = self.bot.active_pontos[member.id]
        guild_id = member.guild.id

        # CASO 1: Usuário ENTROU em um canal de voz (vindo de NENHUM canal)
        if before.channel is None and after.channel is not None:
            ponto_state.last_vc_join_time = now
            print(f"{member.name} entrou em VC ({after.channel.name}), iniciando contagem.")

        # CASO 2: Usuário SAIU de um canal de voz (indo para NENHUM canal)
        elif before.channel is not None and after.channel is None:
            if ponto_state.last_vc_join_time: # Só calcula se ele estava sendo contado
                 try:
                     duration = now - ponto_state.last_vc_join_time
                     seconds_added = duration.total_seconds()
                     ponto_manager.add_time(guild_id, member.id, seconds_added)
                     print(f"{member.name} saiu de VC ({before.channel.name}), adicionado {seconds_added:.2f}s.")
                 except Exception as e:
                     print(f"Erro ao calcular tempo de {member.name} ao sair de VC: {e}")
            ponto_state.last_vc_join_time = None # Para de contar até ele entrar em outro

        # CASO 3: Usuário MUDOU de canal de voz
        elif before.channel is not None and after.channel is not None and before.channel != after.channel:
            if ponto_state.last_vc_join_time: # Só calcula se ele estava sendo contado
                 try:
                     duration = now - ponto_state.last_vc_join_time
                     seconds_added = duration.total_seconds()
                     ponto_manager.add_time(guild_id, member.id, seconds_added)
                     print(f"{member.name} mudou de VC ({before.channel.name} -> {after.channel.name}), adicionado {seconds_added:.2f}s.")
                 except Exception as e:
                      print(f"Erro ao calcular tempo de {member.name} ao mudar de VC: {e}")
            ponto_state.last_vc_join_time = now # Começa a contar no novo canal

    # --- Comandos Manuais (ATUALIZADOS) ---
    @commands.command(name='iniciarponto', help='Inicia manualmente o bate-ponto (requer estar em VC).')
    async def iniciar_ponto(self, ctx):
        # Chama a função handle diretamente com ctx
        view = PontoControlView() # Apenas para acessar o método
        await view.handle_start_ponto(ctx)

    @commands.command(name='finalizarponto', help='Finaliza manualmente o bate-ponto.')
    async def finalizar_ponto(self, ctx):
        # Chama a função handle diretamente com ctx
        view = PontoControlView() # Apenas para acessar o método
        await view.handle_end_ponto(ctx)

    # --- Comandos de Visualização (Não precisam mudar) ---
    @commands.command(name='registroponto', help='Mostra seu tempo total e semanal de bate-ponto.')
    async def registro_ponto(self, ctx, usuario: discord.Member = None):
        if usuario is None:
            usuario = ctx.author # Mostra o próprio registro se nenhum usuário for mencionado

        total_seconds, weekly_seconds = ponto_manager.get_user_times(ctx.guild.id, usuario.id)

        embed = discord.Embed(
            title=f"Registro de Ponto - {usuario.display_name}",
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=usuario.display_avatar.url)
        embed.add_field(name="⏱️ Tempo Total", value=ponto_manager.format_seconds(total_seconds), inline=False)
        embed.add_field(name="📅 Tempo nesta Semana", value=ponto_manager.format_seconds(weekly_seconds), inline=False)
        embed.set_footer(text=f"ID: {usuario.id}")

        await ctx.send(embed=embed)

    @commands.command(name='rankingponto', help='Mostra o ranking semanal de tempo em ponto.')
    async def ranking_ponto(self, ctx):
        guild_records = ponto_manager.get_weekly_guild_records(ctx.guild.id)

        if not guild_records:
            await ctx.send("Ninguém registrou ponto nesta semana ainda.")
            return

        # Ordena por tempo (maior primeiro) e pega os top 10
        sorted_ranking = sorted(guild_records.items(), key=lambda item: item[1], reverse=True)[:10]

        embed = discord.Embed(
            title="🏆 Ranking Semanal de Ponto",
            description="Top 10 usuários com mais tempo registrado nesta semana:",
            color=discord.Color.gold()
        )

        rank_text = ""
        for i, (user_id, seconds) in enumerate(sorted_ranking):
            member = ctx.guild.get_member(user_id)
            name = member.display_name if member else f"ID: {user_id}"
            emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"**{i+1}.**"
            rank_text += f"{emoji} {name} - {ponto_manager.format_seconds(seconds)}\n"

        if not rank_text:
             rank_text = "Nenhum registro encontrado para esta semana."

        embed.description = rank_text
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(BatePontoCog(bot))