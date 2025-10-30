import discord
from discord.ext import commands
from utils import settings_manager  # Corrigido: SEM '..'
from utils.checks import is_admin      # Corrigido: SEM '..'
from .ticket_system import TicketOpenView  # O '.' aqui está correto

class TicketSetup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ticketsetup', help='Configura o painel de tickets.')
    @is_admin()
    async def ticketsetup(self, ctx, canal: discord.TextChannel, *categorias: str):
        
        # --- CORREÇÃO: Mensagem de erro em Embed ---
        if not categorias:
            embed = discord.Embed(
                title="❌ Uso Incorreto!",
                description=f"Você precisa fornecer um canal e pelo menos uma categoria.\nUso: `{ctx.prefix}ticketsetup <#canal> <categoria1> [categoria2] ...`",
                color=discord.Color.red()
            )
            embed.add_field(
                name="Situação 1: Categorias com uma palavra",
                value=f"Basta digitar os nomes separados por espaço.\n"
                      f"`{ctx.prefix}ticketsetup #{canal.name} Suporte Denúncia Dúvida`",
                inline=False
            )
            embed.add_field(
                name="Situação 2: Categorias com várias palavras",
                value=f"Use aspas (\"\") ao redor do nome com espaços.\n"
                      f"`{ctx.prefix}ticketsetup #{canal.name} \"Fale conosco\" \"Ajuda com Pagamento\"`",
                inline=False
            )
            await ctx.send(embed=embed)
            return
        # --- FIM DA CORREÇÃO ---
        
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
        view = TicketOpenView()
        
        # --- MUDANÇA: ATUALIZAR AS OPÇÕES DO MENU INSTANTANEAMENTE ---
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