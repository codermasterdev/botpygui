import discord
from discord.ext import commands
from utils import settings_manager
from utils.checks import is_admin

class SetupAusencia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='setupausencia', help='Define o canal para logs de ausência.')
    @is_admin()
    async def setupausencia(self, ctx, canal: discord.TextChannel):
        settings_manager.set_setting(ctx.guild.id, 'ausencia_channel_id', canal.id)
        embed = discord.Embed(
            title="✅ Configuração Salva",
            description=f"O canal de logs de ausência foi definido para {canal.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SetupAusencia(bot))