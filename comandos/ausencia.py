import discord
from discord.ext import commands
from utils import settings_manager
import datetime
import asyncio

class Ausencia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ausencia', help='Inicia o registro interativo de ausência no seu privado.')
    async def ausencia(self, ctx, *, args: str = None):
        
        log_channel_id = settings_manager.get_setting(ctx.guild.id, 'ausencia_channel_id')
        log_channel = self.bot.get_channel(log_channel_id) if log_channel_id else None

        if not log_channel:
            embed_err = discord.Embed(
                title="❌ Sistema Desconfigurado",
                description=f"O sistema de ausência não está configurado.\nPeça a um Admin para usar `{ctx.prefix}setupausencia #canal`.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed_err, delete_after=10)
            await ctx.message.delete()
            return

        # --- Tratamento de Erro (Digitou r!ausencia <texto>) ---
        if args:
            embed_warn = discord.Embed(
                title="⚠️ Aviso: Comando Incorreto",
                description=f"O uso correto é apenas `{ctx.prefix}ausencia`.\n\nEstou iniciando o processo no seu privado mesmo assim...",
                color=discord.Color.gold()
            )
            await ctx.send(embed=embed_warn, delete_after=10)
        else:
            embed_info = discord.Embed(
                description=f"✅ {ctx.author.mention}, verifique seu privado (DM) para continuar o registro.",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed_info, delete_after=10)
        
        try:
            # Deleta o comando (r!ausencia ...)
            await ctx.message.delete() 
        except:
            pass # Ignora se não puder deletar

        # --- Início do Processo Interativo via DM ---
        try:
            dm_channel = await ctx.author.create_dm()
        except discord.Forbidden:
            embed_dm_err = discord.Embed(
                title="❌ DM Fechada",
                description=f"{ctx.author.mention}, não consigo enviar mensagens no seu privado. Por favor, habilite suas DMs e tente novamente.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed_dm_err, delete_after=15)
            return

        # --- Pergunta 1: Data (Embed) ---
        try:
            embed_q1 = discord.Embed(
                title="📅 Registro de Ausência (Passo 1/2)",
                description="Até qual data (inclusive) você ficará ausente?\n\nFormato: **dd/mm/aaaa**",
                color=discord.Color.blue()
            )
            await dm_channel.send(embed=embed_q1)
            
            def check(m):
                return m.author == ctx.author and m.channel == dm_channel

            # Timeout de 2 minutos para responder
            date_msg = await self.bot.wait_for('message', check=check, timeout=120.0)
            date_str = date_msg.content
            
            # Validação da data
            try:
                data_fim = datetime.datetime.strptime(date_str, '%d/%m/%Y')
                data_hoje = datetime.date.today()
                
                if data_fim.date() < data_hoje:
                    embed_err = discord.Embed(title="❌ Data Inválida", description=f"A data `{date_str}` já passou. Tente novamente no servidor.", color=discord.Color.red())
                    await dm_channel.send(embed=embed_err)
                    return
            except ValueError:
                embed_err = discord.Embed(title="❌ Formato Inválido", description=f"Formato de data inválido. Use **dd/mm/aaaa**. Tente novamente no servidor.", color=discord.Color.red())
                await dm_channel.send(embed=embed_err)
                return

        except asyncio.TimeoutError:
            embed_err = discord.Embed(title="⏰ Tempo Esgotado", description="Você demorou muito para responder. Tente novamente no servidor.", color=discord.Color.red())
            await dm_channel.send(embed=embed_err)
            return

        # --- Pergunta 2: Motivo (Embed) ---
        try:
            embed_q2 = discord.Embed(
                title="📝 Registro de Ausência (Passo 2/2)",
                description="Qual o motivo da sua ausência?",
                color=discord.Color.blue()
            )
            await dm_channel.send(embed=embed_q2)
            # Timeout de 3 minutos para o motivo
            reason_msg = await self.bot.wait_for('message', check=check, timeout=180.0) 
            motivo = reason_msg.content

        except asyncio.TimeoutError:
            embed_err = discord.Embed(title="⏰ Tempo Esgotado", description="Você demorou muito para responder. Tente novamente no servidor.", color=discord.Color.red())
            await dm_channel.send(embed=embed_err)
            return

        # --- Sucesso ---
        data_hoje = datetime.date.today()
        # +1 para incluir o dia final
        dias_ausente = (data_fim.date() - data_hoje).days + 1 

        # (1) Envia no Canal de Log (Embed)
        embed_log = discord.Embed(
            title="📅 Novo Registro de Ausência",
            color=discord.Color.light_grey()
        )
        embed_log.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed_log.add_field(name="Usuário", value=ctx.author.mention, inline=False)
        embed_log.add_field(name="Data Final", value=data_fim.strftime('%d/%m/%Y'), inline=True)
        embed_log.add_field(name="Total de Dias", value=f"{dias_ausente} dia(s)", inline=True)
        embed_log.add_field(name="Motivo", value=f"```{motivo}```", inline=False)
        embed_log.set_footer(text=f"Registrado em: {data_hoje.strftime('%d/%m/%Y')}")

        await log_channel.send(embed=embed_log)

        # (2) Envia Confirmação na DM (Embed)
        embed_success_dm = discord.Embed(
            title="✅ Ausência Registrada!",
            description="Sua ausência foi registrada com sucesso no servidor.",
            color=discord.Color.green()
        )
        await dm_channel.send(embed=embed_success_dm)

async def setup(bot):
    await bot.add_cog(Ausencia(bot))