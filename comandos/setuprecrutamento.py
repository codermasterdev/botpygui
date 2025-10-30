import discord
from discord.ext import commands
from utils import settings_manager
from utils.checks import is_admin
from .recrutamento_system import RecrutamentoStartView # Importa a View do botão "Iniciar"

class SetupRecrutamento(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='setuprecrutamento', help='Configura o painel de recrutamento.')
    @is_admin()
    async def setuprecrutamento(self, ctx, canal_logs: discord.TextChannel, canal_setup: discord.TextChannel, *, descricao: str):
        
        # Salva as configurações
        settings_manager.set_setting(ctx.guild.id, 'recrutamento_logs_channel', canal_logs.id)
        settings_manager.set_setting(ctx.guild.id, 'recrutamento_setup_channel', canal_setup.id)

        # Cria o Embed
        embed = discord.Embed(
            title="Formulário de Recrutamento",
            description=descricao, # Descrição definida pelo Staff
            color=discord.Color.dark_blue()
        )
        embed.set_footer(text="Clique no botão abaixo para iniciar seu formulário.")
        
        try:
            # Envia o painel com o botão "Iniciar"
            await canal_setup.send(embed=embed, view=RecrutamentoStartView())
            await ctx.send(f"✅ Painel de recrutamento configurado com sucesso em {canal_setup.mention}!", delete_after=10)
        except discord.Forbidden:
            await ctx.send(f"❌ Erro de Permissão: Não consigo enviar mensagens em {canal_setup.mention}.")
        
        await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(SetupRecrutamento(bot))