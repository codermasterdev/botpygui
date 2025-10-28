import discord
from discord.ext import commands
from utils import data_manager, settings_manager
from utils.checks import is_mod

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _get_log_channel(self, ctx):
        log_channel_id = settings_manager.get_setting(ctx.guild.id, 'log_channel')
        if not log_channel_id:
            await ctx.send(f"Canal de logs não configurado. Use `{ctx.prefix}setlogs #canal`")
            return None
        return self.bot.get_channel(log_channel_id)

    @commands.command(name='kick', help='Expulsa um usuário do servidor.')
    @is_mod()
    async def kick(self, ctx, member: discord.Member, *, reason: str):
        log_channel = await self._get_log_channel(ctx)
        if not log_channel:
            return 

        embed = discord.Embed(
            title="👢 Usuário Expulso",
            color=discord.Color.orange()
        )
        embed.add_field(name="Usuário", value=member.mention, inline=False)
        embed.add_field(name="Motivo", value=reason, inline=False)
        embed.add_field(name="Moderador", value=ctx.author.mention, inline=False)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

        try:
            await member.send(f"Você foi expulso do servidor **{ctx.guild.name}** pelo motivo: {reason}")
        except discord.Forbidden:
            embed.set_footer(text="Não foi possível enviar DM para o usuário.")
        
        await member.kick(reason=f"{reason} (Expulso por: {ctx.author.name})")
        data_manager.add_punishment(ctx.guild.id, member.id, ctx.author.id, 'kick', reason)
        
        await log_channel.send(embed=embed)
        await ctx.send(f"✅ {member.name} foi expulso. Log enviado para {log_channel.mention}", delete_after=5)
        await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(Kick(bot))