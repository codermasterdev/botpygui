import discord
from discord.ext import commands
from utils.checks import is_admin, is_mod, is_staff

class PrimeirosPassos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='primeirospassos', help='Guia rápido de configuração para a staff.')
    @commands.check_any(is_admin(), is_mod(), is_staff())
    async def primeirospassos(self, ctx):
        prefix = ctx.prefix

        embed = discord.Embed(
            title="🚀 Guia de Configuração Rápida (Primeiros Passos)",
            description="Este guia ajuda Administradores a configurar as funções essenciais do bot.",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="1. Permissões (Obrigatório)",
            value=f"Defina quem pode fazer o quê. Admins do Discord já têm acesso a tudo.\n"
                  f"`{prefix}setadminrole @CargoAdmin` (Gerencia o bot)\n"
                  f"`{prefix}setmodrole @CargoMod` (Modera o servidor)\n"
                  f"`{prefix}setstaffrole @CargoStaff` (Gerencia tickets, vendas, etc.)",
            inline=False
        )

        embed.add_field(
            name="2. Canais Essenciais (Obrigatório)",
            value=f"Defina os canais onde o bot registrará as ações.\n"
                  f"**`{prefix}setlogs #canal-logs`** (Crítico! Moderação depende disso)\n"
                  f"`{prefix}setsugestoes #canal-sugestoes` (Para o `r!sugestao`)",
            inline=False
        )

        embed.add_field(
            name="3. Canais Opcionais (Boas-vindas)",
            value=f"`{prefix}setbemvindo #boas-vindas`\n"
                  f"`{prefix}setadeus #saidas`\n"
                  f"`{prefix}setautorole @CargoInicial`",
            inline=False
        )
        
        embed.add_field(
            name="4. Setup de Sistemas (Conforme o uso)",
            value=f"**Tickets**:\n"
                  f"`{prefix}setticketcategory NomeDaCategoria` (Cria/Define a Categoria de tickets)\n"
                  f"`{prefix}ticketsetup #canal-abertura Categoria1 Categoria2 ...`\n\n"
                  f"**Bate-Ponto**:\n"
                  f"`{prefix}setupbateponto #canal-ponto`\n\n"
                  f"**Recrutamento**:\n"
                  f"`{prefix}setuprecrutamento #logs-forms #canal-forms \"Descrição aqui\"`\n\n"
                  f"**Vendas/Loja**:\n"
                  f"`{prefix}addpagamento PIX \"Chave: 123...\"`\n"
                  f"`{prefix}adicionarproduto \"Produto Exemplo\" 10,50`\n"
                  f"`{prefix}setupvendas #loja`",
            inline=False
        )
        
        embed.set_footer(text="Após configurar, use r!ajuda para ver todos os comandos.")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PrimeirosPassos(bot))