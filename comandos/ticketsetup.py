import discord
from discord.ext import commands
from utils import settings_manager
from utils.checks import is_admin
from comandos.ticket_system import TicketOpenView # Importa nossa View

class TicketSetup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ticketsetup', help='Configura o painel de tickets.')
    @is_admin()
    async def ticketsetup(self, ctx, canal: discord.TextChannel, *categorias: str):
        
        if not categorias:
            await ctx.send(f"Uso incorreto. Ex: `{ctx.prefix}ticketsetup #tickets Suporte Denúncia`")
            return
        
        if len(categorias) > 4:
            await ctx.send("Você pode definir no máximo 4 categorias.")
            return

        # Salva as categorias
        settings_manager.set_setting(ctx.guild.id, 'ticket_categories', list(categorias))
        
        # Cria a View de Abertura
        view = TicketOpenView()
        
        # Atualiza as opções do Select Menu dinamicamente
        select_menu = view.children[0] # Pega o Select Menu
        select_menu.options = [
            discord.SelectOption(label=cat.capitalize(), value=cat.lower(), emoji="🎟️")
            for cat in categorias
        ]
        
        # Envia o painel
        embed = discord.Embed(
            title="Central de Suporte",
            description="Para abrir um ticket, clique no menu abaixo e selecione a categoria apropriada.",
            color=discord.Color.dark_blue()
        )
        await canal.send(embed=embed, view=view)
        await ctx.send(f"✅ Painel de tickets configurado com sucesso em {canal.mention}!", delete_after=10)
        await ctx.message.delete()


async def setup(bot):
    await bot.add_cog(TicketSetup(bot))