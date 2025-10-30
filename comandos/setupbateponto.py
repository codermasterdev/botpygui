import discord
from discord.ext import commands
from utils import settings_manager
from utils.checks import is_admin
from .ponto_system import PontoControlView # Importa a View dos botões

class SetupBatePonto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='setupbateponto', help='Configura o painel de bate-ponto em um canal.')
    @is_admin()
    async def setupbateponto(self, ctx, canal: discord.TextChannel):
        
        # Salva o ID do canal nas configurações
        settings_manager.set_setting(ctx.guild.id, 'ponto_channel_id', canal.id)

        # Cria o Embed com a descrição
        embed = discord.Embed(
            title="🕒 Sistema de Bate-Ponto",
            # Descrição da imagem
            description="Bem-vindo ao sistema de bate-ponto! Aqui você pode registrar sua entrada e saída de forma prática e eficiente. Certifique-se de seguir as instruções fornecidas para garantir que seu registro seja feito corretamente. Estamos aqui para facilitar sua rotina!",
            color=discord.Color.blue()
        )
        embed.add_field(name="Instruções", value="1. Conecte-se a um canal de voz.\n2. Clique em 'Iniciar Ponto'.\n3. Seu tempo será contado enquanto estiver em um canal de voz.\n4. Ao terminar, clique em 'Finalizar Ponto'.", inline=False)
        embed.set_footer(text="Desenvolvido por gordimxx8") #

        try:
            # Envia o painel com os botões
            await canal.send(embed=embed, view=PontoControlView())
            await ctx.send(f"✅ Painel de bate-ponto configurado com sucesso em {canal.mention}!", delete_after=10)
        except discord.Forbidden:
            await ctx.send(f"❌ Erro de Permissão: Não consigo enviar mensagens em {canal.mention}.")
        
        await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(SetupBatePonto(bot))