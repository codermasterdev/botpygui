import discord
from discord.ext import commands
import datetime
from utils import data_manager, settings_manager # Importamos os dois managers
from utils.checks import is_mod

# Classe principal do Cog
class Moderacao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- Função Helper ---
    # Verifica e retorna o canal de logs. Se não estiver setado, avisa o usuário.
    async def _get_log_channel(self, ctx):
        log_channel_id = settings_manager.get_setting(ctx.guild.id, 'log_channel')
        
        if not log_channel_id:
            embed = discord.Embed(
                title="⚠️ Canal de Logs Não Configurado",
                description=f"Por favor, peça a um administrador para definir o canal de logs de moderação primeiro.",
                color=discord.Color.gold()
            )
            embed.set_footer(text=f"Use: {ctx.prefix}setlogs #canal-de-logs")
            await ctx.send(embed=embed)
            return None
            
        log_channel = self.bot.get_channel(log_channel_id)
        
        if not log_channel:
            # O canal foi setado mas talvez deletado
            await ctx.send(f"Canal de logs (`{log_channel_id}`) não encontrado. Configure-o novamente.", delete_after=10)
            return None
            
        return log_channel
    # --- Fim da Função Helper ---


    @commands.command(name='ban', help='Bane um usuário do servidor.')
    @is_mod()
    async def ban(self, ctx, member: discord.Member, *, reason: str):
        log_channel = await self._get_log_channel(ctx)
        if not log_channel:
            return # Para a execução se o canal não estiver configurado

        embed = discord.Embed(title="🔨 Usuário Banido", color=discord.Color.dark_red())
        embed.add_field(name="Usuário", value=member.mention, inline=False)
        embed.add_field(name="Motivo", value=reason, inline=False)
        embed.add_field(name="Moderador", value=ctx.author.mention, inline=False)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

        try:
            await member.send(f"Você foi banido do servidor **{ctx.guild.name}** pelo motivo: {reason}")
        except discord.Forbidden:
            embed.set_footer(text="Não foi possível enviar DM para o usuário.")
        
        await member.ban(reason=f"{reason} (Banido por: {ctx.author.name})")
        data_manager.add_punishment(ctx.guild.id, member.id, ctx.author.id, 'ban', reason)
        
        await log_channel.send(embed=embed) # Envia para o canal de LOG
        await ctx.send(f"✅ {member.name} foi banido. Log enviado para {log_channel.mention}", delete_after=5)
        await ctx.message.delete()


    @commands.command(name='mutar', help='Silencia um usuário por X minutos.')
    @is_mod()
    async def mutar(self, ctx, member: discord.Member, minutos: int, *, reason: str):
        log_channel = await self._get_log_channel(ctx)
        if not log_channel:
            return

        duration = datetime.timedelta(minutes=minutos)
        
        try:
            await member.timeout(duration, reason=f"{reason} (Mutado por: {ctx.author.name})")
            
            embed = discord.Embed(title="🔇 Usuário Silenciado (Timeout)", color=discord.Color.orange())
            embed.add_field(name="Usuário", value=member.mention, inline=False)
            embed.add_field(name="Duração", value=f"{minutos} minutos", inline=False)
            embed.add_field(name="Motivo", value=reason, inline=False)
            embed.add_field(name="Moderador", value=ctx.author.mention, inline=False)
            
            data_manager.add_punishment(ctx.guild.id, member.id, ctx.author.id, 'timeout', f"{reason} ({minutos} min)")
            
            await log_channel.send(embed=embed) # Envia para o canal de LOG
            await ctx.send(f"✅ {member.name} foi silenciado. Log enviado para {log_channel.mention}", delete_after=5)
            await ctx.message.delete()
            
        except discord.Forbidden:
            await ctx.send("Eu não tenho permissão para aplicar timeout neste usuário.")
        except Exception as e:
            await ctx.send(f"Ocorreu um erro: {e}")


    @commands.command(name='warn', help='Adverte um usuário.')
    @is_mod()
    async def warn(self, ctx, member: discord.Member, *, reason: str):
        log_channel = await self._get_log_channel(ctx)
        if not log_channel:
            return

        data_manager.add_punishment(ctx.guild.id, member.id, ctx.author.id, 'warn', reason)
        warns = data_manager.get_punishments(ctx.guild.id, member.id, p_type='warn')
        warn_count = len(warns)

        embed = discord.Embed(title="⚠️ Usuário Advertido", color=discord.Color.gold())
        embed.add_field(name="Usuário", value=member.mention, inline=False)
        embed.add_field(name="Motivo", value=reason, inline=False)
        embed.add_field(name="Moderador", value=ctx.author.mention, inline=False)
        embed.set_footer(text=f"Este usuário agora tem {warn_count} advertência(s).")
        
        await log_channel.send(embed=embed) # Envia para o canal de LOG
        await ctx.send(f"✅ {member.name} foi advertido. Log enviado para {log_channel.mention}", delete_after=5)
        await ctx.message.delete()

        # Lógica dos 3 warns = ban
        if warn_count >= 3:
            ban_reason = f"Acúmulo de 3 advertências. (Último motivo: {reason})"
            ban_embed = discord.Embed(title="🔨 Usuário Automaticamente Banido", color=discord.Color.dark_red())
            ban_embed.add_field(name="Usuário", value=member.mention, inline=False)
            ban_embed.add_field(name="Motivo", value=ban_reason, inline=False)
            
            try:
                await member.send(f"Você foi banido do servidor **{ctx.guild.name}** pelo motivo: {ban_reason}")
            except discord.Forbidden:
                pass
            
            await member.ban(reason=ban_reason)
            data_manager.add_punishment(ctx.guild.id, member.id, self.bot.user.id, 'ban', ban_reason)
            await log_channel.send(embed=ban_embed) # Envia o ban automático para o LOG


    @commands.command(name='unwarn', help='Remove a última advertência de um usuário.')
    @is_mod()
    async def unwarn(self, ctx, member: discord.Member):
        log_channel = await self._get_log_channel(ctx)
        if not log_channel:
            return

        success = data_manager.remove_last_warn(ctx.guild.id, member.id)
        
        if success:
            warns = data_manager.get_punishments(ctx.guild.id, member.id, p_type='warn')
            embed = discord.Embed(title="✅ Advertência Removida", color=discord.Color.green())
            embed.add_field(name="Usuário", value=member.mention, inline=False)
            embed.add_field(name="Moderador", value=ctx.author.mention, inline=False)
            embed.set_footer(text=f"Este usuário agora tem {len(warns)} advertência(s).")
        else:
            embed = discord.Embed(
                title="ℹ️ Nenhuma Advertência",
                description=f"{member.mention} não possui nenhuma advertência para remover.",
                color=discord.Color.blue()
            )
            
        await log_channel.send(embed=embed) # Envia para o canal de LOG
        await ctx.send(f"✅ Ação concluída. Log enviado para {log_channel.mention}", delete_after=5)
        await ctx.message.delete()


    @commands.command(name='listarpunicoes', aliases=['hist', 'punicoes'], help='Lista o histórico de punições de um usuário.')
    @is_mod()
    async def listarpunicoes(self, ctx, member: discord.Member):
        # Este comando é informativo, pode ser exibido no canal de logs OU no canal atual.
        # Vamos mantê-lo no canal atual para facilidade do moderador.
        punishments = data_manager.get_punishments(ctx.guild.id, member.id)
        
        if not punishments:
            embed = discord.Embed(title=f"Histórico de {member.name}", description="Este usuário não possui punições.", color=discord.Color.blue())
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(title=f"Histórico de {member.name}", color=discord.Color.light_grey())
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        description = ""
        for p in punishments:
            timestamp_dt = datetime.datetime.fromisoformat(p['timestamp'])
            data_formatada = timestamp_dt.strftime("%d/%m/%Y às %H:%M")
            description += f"**Tipo:** {p['type'].upper()}\n"
            description += f"**Motivo:** {p['reason']}\n"
            description += f"**Moderador:** <@{p['moderator']}>\n"
            description += f"**Data:** {data_formatada}\n---\n"
        
        embed.description = description
        await ctx.send(embed=embed)

    # Comandos de Lock/Unlock enviam a msg no próprio canal que está sendo afetado.
    # Não precisam de um canal de log.
    @commands.command(name='bloquearchat', aliases=['lock'], help='Bloqueia o canal atual.')
    @is_mod()
    async def bloquearchat(self, ctx):
        role = ctx.guild.default_role
        overwrites = ctx.channel.overwrites_for(role)
        overwrites.send_messages = False
        
        await ctx.channel.set_permissions(role, overwrite=overwrites)
        embed = discord.Embed(title="🔒 Canal Bloqueado", description=f"{ctx.channel.mention} foi bloqueado por {ctx.author.mention}.", color=discord.Color.red())
        await ctx.send(embed=embed)

    @commands.command(name='desbloquearchat', aliases=['unlock'], help='Desbloqueia o canal atual.')
    @is_mod()
    async def desbloquearchat(self, ctx):
        role = ctx.guild.default_role
        overwrites = ctx.channel.overwrites_for(role)
        overwrites.send_messages = True 
        
        await ctx.channel.set_permissions(role, overwrite=overwrites)
        embed = discord.Embed(title="🔓 Canal Desbloqueado", description=f"{ctx.channel.mention} foi desbloqueado por {ctx.author.mention}.", color=discord.Color.green())
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Moderacao(bot))