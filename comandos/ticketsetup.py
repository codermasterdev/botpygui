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
            # --- CORREÇÃO: Sugere o uso de aspas para categorias compostas ---
            await ctx.send(f"Uso incorreto. Ex: `{ctx.prefix}ticketsetup #tickets Suporte \"Ajuda com Pagamento\" Denúncia`")
            return
        
        if len(categorias) > 4:
            await ctx.send("Você pode definir no máximo 4 categorias.")
            return

        # --- NOVO: VERIFICAÇÃO DE CATEGORIAS DUPLICADAS (Corrige o erro da imagem) ---
        valores_unicos = set()
        for cat in categorias:
            valor = cat.lower() # O 'value' do menu é o nome em minúsculas
            if valor in valores_unicos:
                await ctx.send(f"❌ Erro: A categoria **{cat}** (valor: `{valor}`) está duplicada ou tem o mesmo nome (ignorando maiúsculas/minúsculas) de outra. Por favor, forneça nomes de categorias únicos.")
                return
            valores_unicos.add(valor)
        # --- FIM DA VERIFICAÇÃO ---

        # Salva as categorias (o ticket_system.py vai ler isso agora)
        settings_manager.set_setting(ctx.guild.id, 'ticket_categories', list(categorias))
        
        # Cria a View de Abertura
        # Graças às nossas mudanças no Passo 2, ela já vai carregar as opções corretas
        # quando for registrada no 'bot.py'
        view = TicketOpenView()
        
        # --- MUDANÇA: ATUALIZAR AS OPÇÕES DO MENU INSTANTANEAMENTE ---
        # Embora o bot vá se lembrar das opções no restart, precisamos 
        # que este menu *novo* que estamos enviando já tenha as opções certas.
        
        # Pega o item Select (que é o primeiro item da view)
        select_menu = view.children[0] 
        
        # Carrega as opções que acabamos de salvar
        await select_menu._load_options(ctx.guild.id)
        # -----------------------------------------------------------------

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