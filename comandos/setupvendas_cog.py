import discord
from discord.ext import commands
from utils import settings_manager, vendas_manager, checks
from .vendas_system import VendasProductSelectView # Importa a View principal

class SetupVendasCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='setupvendas', help='Configura o painel de seleção de produtos.')
    @checks.is_admin()
    async def setupvendas(self, ctx, canal: discord.TextChannel):
        """ Cria a mensagem com o dropdown de produtos no canal especificado. """

        # Salva o ID do canal onde a mensagem ficará
        settings_manager.set_setting(ctx.guild.id, 'vendas_setup_channel', canal.id)

        # Garante que a categoria de vendas existe (ou cria)
        category_id = settings_manager.get_setting(ctx.guild.id, 'vendas_category_id')
        category = ctx.guild.get_channel(category_id) if category_id else None
        if not category or not isinstance(category, discord.CategoryChannel):
             try:
                 overwrites = {
                     ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                     ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
                 }
                 category = await ctx.guild.create_category("🛒 Vendas", overwrites=overwrites, reason="Categoria para canais de vendas")
                 settings_manager.set_setting(ctx.guild.id, 'vendas_category_id', category.id)
                 await ctx.send(f"ℹ️ Categoria '🛒 Vendas' criada.", delete_after=10)
             except discord.Forbidden:
                 await ctx.send("⚠️ Não tenho permissão para criar a categoria 'Vendas'. Os canais serão criados sem categoria.", delete_after=15)
                 settings_manager.set_setting(ctx.guild.id, 'vendas_category_id', None) # Garante que não use ID inválido
             except Exception as e:
                 await ctx.send(f"⚠️ Erro ao tentar criar categoria 'Vendas': {e}", delete_after=15)
                 settings_manager.set_setting(ctx.guild.id, 'vendas_category_id', None)

        # Cria a View e carrega as opções ATUAIS
        view = VendasProductSelectView()
        select_menu: discord.ui.Select = view.children[0] # Pega o Select dentro da View
        await select_menu._load_options(ctx.guild.id) # Carrega produtos no menu

        # Cria o Embed inicial
        embed = discord.Embed(
            title="🛒 Loja de Produtos",
            description="Selecione um produto abaixo para iniciar o processo de compra.",
            color=discord.Color.dark_purple()
        )
        embed.set_footer(text="Ao selecionar, um canal privado será criado para você.")

        try:
            # Envia a mensagem com o select (e a view persistente)
            setup_message = await canal.send(embed=embed, view=view)
            # Salva o ID da mensagem para poder atualizá-la depois (opcional, mas útil)
            settings_manager.set_setting(ctx.guild.id, 'vendas_setup_message_id', setup_message.id)
            await ctx.send(f"✅ Painel de vendas configurado com sucesso em {canal.mention}!", delete_after=10)
        except discord.Forbidden:
            await ctx.send(f"❌ Erro de Permissão: Não consigo enviar mensagens em {canal.mention}.")

        await ctx.message.delete()


    @commands.command(name='adicionarproduto', help='Adiciona ou atualiza um produto na loja.')
    @checks.is_admin()
    async def adicionar_produto(self, ctx, nome: str, preco_str: str):
        """ Adiciona um produto. Uso: r!adicionarproduto "Nome do Produto" 10,50 """
        
        price_float = vendas_manager.parse_price(preco_str)
        if price_float is None or price_float < 0:
            embed = discord.Embed(
                title="❌ Preço Inválido",
                description=f"O preço '{preco_str}' não é válido. Use números, vírgula ou ponto.\n**Não** use 'R$'.",
                color=discord.Color.red()
            )
            embed.add_field(name="Exemplos Válidos", value="`10`\n`10,50`\n`10.50`\n`1500,00`\n`1.500`", inline=False)
            await ctx.send(embed=embed)
            return

        is_new = vendas_manager.add_product(ctx.guild.id, nome, price_float)
        action_text = "adicionado" if is_new else "atualizado"
        
        embed = discord.Embed(
            title=f"✅ Produto {action_text.capitalize()}!",
            description=f"**Nome:** {nome}\n**Preço:** {vendas_manager.format_price(price_float)}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

        # Opcional: Tentar atualizar a mensagem do setup
        await self._try_update_setup_message(ctx.guild)


    @commands.command(name='addpagamento', help='Adiciona ou atualiza um método de pagamento.')
    @checks.is_admin()
    async def add_pagamento(self, ctx, tipo: str, *, descricao: str):
        """ Adiciona método de pagamento. Uso: r!addpagamento PIX "Chave: 1234..." """
        is_new = vendas_manager.add_payment(ctx.guild.id, tipo, descricao)
        action_text = "adicionado" if is_new else "atualizado"
        
        embed = discord.Embed(
            title=f"✅ Pagamento {action_text.capitalize()}!",
            description=f"**Tipo:** {tipo}\n**Descrição:** {descricao}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    # --- Comandos Opcionais de Remoção ---

    @commands.command(name='removerproduto', help='Remove um produto da loja.')
    @checks.is_admin()
    async def remover_produto(self, ctx, *, nome: str):
         """ Remove um produto pelo nome. Uso: r!removerproduto "Nome Exato" """
         removed = vendas_manager.remove_product(ctx.guild.id, nome)
         if removed:
             embed = discord.Embed(title="✅ Produto Removido", description=f"O produto '{nome}' foi removido.", color=discord.Color.orange())
             await ctx.send(embed=embed)
             await self._try_update_setup_message(ctx.guild) # Tenta atualizar
         else:
             embed = discord.Embed(title="❌ Produto Não Encontrado", description=f"Não encontrei um produto com o nome '{nome}'.", color=discord.Color.red())
             await ctx.send(embed=embed)

    @commands.command(name='removerpagamento', help='Remove um método de pagamento.')
    @checks.is_admin()
    async def remover_pagamento(self, ctx, *, tipo: str):
         """ Remove um método de pagamento pelo tipo. Uso: r!removerpagamento PIX """
         removed = vendas_manager.remove_payment(ctx.guild.id, tipo)
         if removed:
             embed = discord.Embed(title="✅ Pagamento Removido", description=f"O método de pagamento '{tipo}' foi removido.", color=discord.Color.orange())
             await ctx.send(embed=embed)
         else:
             embed = discord.Embed(title="❌ Pagamento Não Encontrado", description=f"Não encontrei um método de pagamento do tipo '{tipo}'.", color=discord.Color.red())
             await ctx.send(embed=embed)


    async def _try_update_setup_message(self, guild: discord.Guild):
        """ Tenta encontrar e atualizar a mensagem de setup com a nova lista de produtos. """
        channel_id = settings_manager.get_setting(guild.id, 'vendas_setup_channel')
        message_id = settings_manager.get_setting(guild.id, 'vendas_setup_message_id')

        if not channel_id or not message_id:
            print(f"Update Vendas: Canal ou Mensagem de Setup não configurados para guild {guild.id}")
            return

        try:
            channel = await self.bot.fetch_channel(channel_id)
            if not isinstance(channel, discord.TextChannel): return

            message = await channel.fetch_message(message_id)
            if not message or not message.components: return

            # Encontra a View e o Select Menu
            view = discord.ui.View.from_message(message) # Recria a view a partir da mensagem
            select_menu = discord.utils.get(view.children, custom_id="vendas_product_select")

            if isinstance(select_menu, discord.ui.Select):
                await select_menu._load_options(guild.id) # Carrega as novas opções
                await message.edit(view=view) # Edita a mensagem com a view atualizada
                print(f"Mensagem de setup de vendas atualizada em {guild.name}")
            else:
                 print(f"Select menu não encontrado na mensagem de setup de vendas em {guild.name}")

        except discord.NotFound:
            print(f"Update Vendas: Canal ({channel_id}) ou Mensagem ({message_id}) não encontrados.")
        except discord.Forbidden:
            print(f"Update Vendas: Sem permissão para editar a mensagem em {channel_id}.")
        except Exception as e:
            print(f"Erro inesperado ao atualizar mensagem de vendas: {e}")


async def setup(bot):
    await bot.add_cog(SetupVendasCog(bot))