import discord
from discord.ext import commands
from utils import settings_manager
from utils.checks import is_admin

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='setlogs', help='Define o canal para logs de moderação (ban, warn, etc).')
    @is_admin()
    async def setlogs(self, ctx, canal: discord.TextChannel):
        settings_manager.set_setting(ctx.guild.id, 'log_channel', canal.id)
        embed = discord.Embed(
            title="✅ Configuração Salva",
            description=f"O canal de logs de moderação foi definido para {canal.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name='setbemvindo', help='Define o canal de boas-vindas.')
    @is_admin()
    async def setbemvindo(self, ctx, canal: discord.TextChannel):
        settings_manager.set_setting(ctx.guild.id, 'welcome_channel', canal.id)
        embed = discord.Embed(
            title="✅ Configuração Salva",
            description=f"O canal de boas-vindas foi definido para {canal.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name='setadeus', help='Define o canal de saídas.')
    @is_admin()
    async def setadeus(self, ctx, canal: discord.TextChannel):
        settings_manager.set_setting(ctx.guild.id, 'goodbye_channel', canal.id)
        embed = discord.Embed(
            title="✅ Configuração Salva",
            description=f"O canal de saídas foi definido para {canal.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name='setsugestoes', help='Define o canal de sugestões.')
    @is_admin()
    async def setsugestoes(self, ctx, canal: discord.TextChannel):
        settings_manager.set_setting(ctx.guild.id, 'suggestions_channel', canal.id)
        embed = discord.Embed(
            title="✅ Configuração Salva",
            description=f"O canal de sugestões foi definido para {canal.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name='setdivulgacao', help='Define o canal para o comando /divulgar.')
    @is_admin()
    async def setdivulgacao(self, ctx, canal: discord.TextChannel):
        settings_manager.set_setting(ctx.guild.id, 'divulgacao_channel', canal.id)
        embed = discord.Embed(
            title="✅ Configuração Salva",
            description=f"O canal de divulgação foi definido para {canal.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name='setticketcategory', help='Define a categoria onde os tickets serão criados.')
    @is_admin()
    async def setticketcategory(self, ctx, categoria: discord.CategoryChannel):
        settings_manager.set_setting(ctx.guild.id, 'ticket_category', categoria.id)
        embed = discord.Embed(
            title="✅ Configuração Salva",
            description=f"A categoria de tickets foi definida para **{categoria.name}**",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Admin(bot))