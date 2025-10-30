import discord
import asyncio
from discord.ext import commands
from utils import settings_manager, vendas_manager, checks

# --- 1. View de Fechar Canal de Venda ---
class VendasCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Fechar Venda", style=discord.ButtonStyle.danger, custom_id="vendas_fechar")
    async def fechar(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Verifica permissão (Staff ou Admin)
        is_staff = False
        staff_roles_ids = settings_manager.get_setting(interaction.guild.id, 'staff_roles') or []
        user_role_ids = {role.id for role in interaction.user.roles}
        if any(role_id in user_role_ids for role_id in staff_roles_ids) or interaction.user.guild_permissions.administrator:
            is_staff = True

        if not is_staff and not interaction.channel.permissions_for(interaction.user).manage_channels:
             # Se não for staff E não tiver permissão de gerenciar canais, nega
             # (Permite que o criador do canal o feche se tiver perm, mas foca em staff)
            await interaction.response.send_message("❌ Apenas membros da Staff podem fechar este canal.", ephemeral=True)
            return

        await interaction.response.send_message("✅ Canal será fechado em 5 segundos...")
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete(reason=f"Venda fechada por {interaction.user.name}")
        except discord.Forbidden:
            # Fallback se não conseguir deletar
            await interaction.followup.send("❌ Erro de permissão ao tentar deletar o canal.", ephemeral=True)
        except Exception as e:
            print(f"Erro ao fechar canal de venda: {e}")
            await interaction.followup.send(f"❌ Erro inesperado ao fechar canal: {e}", ephemeral=True)


# --- 2. Select de Produtos ---
class VendasProductSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(
            custom_id="vendas_product_select",
            placeholder="Escolha um produto para comprar...",
            min_values=1,
            max_values=1,
            options=[discord.SelectOption(label="Nenhum produto cadastrado", value="disabled")] # Placeholder inicial
        )

    async def _load_options(self, guild_id):
        products = vendas_manager.get_products(guild_id)
        if not products:
            self.options = [discord.SelectOption(label="Nenhum produto cadastrado", value="disabled")]
            self.disabled = True
        else:
            self.options = [
                discord.SelectOption(
                    label=f"{prod['name']} - {vendas_manager.format_price(prod['price'])}",
                    value=prod['name'] # Usar o nome como identificador único
                )
                for prod in products[:25] # Limite de 25 opções no Select
            ]
            self.disabled = False
        # Atualiza o placeholder se necessário
        self.placeholder = "Escolha um produto para comprar..." if not self.disabled else "Nenhum produto disponível"


    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "disabled":
            await interaction.response.send_message("Não há produtos disponíveis no momento.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True, thinking=True)

        selected_product_name = self.values[0]
        guild = interaction.guild
        user = interaction.user

        # Encontra os detalhes do produto selecionado
        product_info = None
        products = vendas_manager.get_products(guild.id)
        for prod in products:
            if prod['name'] == selected_product_name:
                product_info = prod
                break

        if not product_info:
            await interaction.followup.send("❌ Erro: Produto selecionado não encontrado.", ephemeral=True)
            return

        # Pega/Cria a categoria de vendas (similar ao ticket)
        category_id = settings_manager.get_setting(guild.id, 'vendas_category_id')
        category = guild.get_channel(category_id) if category_id else None

        if not category or not isinstance(category, discord.CategoryChannel):
             # Tenta criar a categoria se não existir
             try:
                 # Permissões básicas: @everyone não vê, bot vê
                 overwrites = {
                     guild.default_role: discord.PermissionOverwrite(read_messages=False),
                     guild.me: discord.PermissionOverwrite(read_messages=True)
                 }
                 category = await guild.create_category("🛒 Vendas", overwrites=overwrites, reason="Categoria para canais de vendas")
                 settings_manager.set_setting(guild.id, 'vendas_category_id', category.id)
                 print(f"Categoria de Vendas criada em {guild.name}")
             except discord.Forbidden:
                 await interaction.followup.send("❌ Erro: Não tenho permissão para criar a categoria 'Vendas'. Peça a um admin.", ephemeral=True)
                 return
             except Exception as e:
                 await interaction.followup.send(f"❌ Erro ao criar categoria: {e}", ephemeral=True)
                 return


        # Pega cargos de staff (para permissão no canal)
        staff_roles_ids = settings_manager.get_setting(guild.id, 'staff_roles') or []
        staff_objects = [guild.get_role(role_id) for role_id in staff_roles_ids if guild.get_role(role_id)]

        # Permissões do novo canal de venda
        channel_overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        # Adiciona permissão para cargos Staff
        for role in staff_objects:
            channel_overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        # Adiciona permissão para Admins (redundante se já for staff, mas garante)
        admin_roles_ids = settings_manager.get_setting(guild.id, 'admin_roles') or []
        for role_id in admin_roles_ids:
             role = guild.get_role(role_id)
             if role:
                 channel_overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)


        # Cria o nome do canal (limitado em tamanho)
        safe_prod_name = ''.join(c for c in selected_product_name if c.isalnum() or c in ['-', '_'])[:20]
        channel_name = f"venda-{safe_prod_name}-{user.name}"[:100] # Limite de 100 caracteres

        try:
            new_channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=channel_overwrites,
                topic=f"Canal de venda para {user.name} - Produto: {selected_product_name}"
            )
        except discord.Forbidden:
            await interaction.followup.send("❌ Erro: Não tenho permissão para criar canais na categoria 'Vendas'.", ephemeral=True)
            return
        except Exception as e:
            await interaction.followup.send(f"❌ Erro ao criar canal: {e}", ephemeral=True)
            return

        # Prepara o Embed de Pagamentos
        payments = vendas_manager.get_payments(guild.id)
        payment_embed = discord.Embed(title="💲 Métodos de Pagamento Disponíveis", color=discord.Color.green())
        if payments:
            for pay in payments:
                payment_embed.add_field(name=f"Tipo: {pay['type']}", value=f"```{pay['description']}```", inline=False)
        else:
            payment_embed.description = "Nenhum método de pagamento configurado. Contate um Staff."

        # Envia a mensagem inicial no canal de venda
        product_price_formatted = vendas_manager.format_price(product_info['price'])
        initial_message = (
            f"Olá {user.mention}! Bem-vindo ao seu canal de compra.\n\n"
            f"**Produto Selecionado:** {product_info['name']}\n"
            f"**Preço:** {product_price_formatted}\n\n"
            f"Um membro da Staff virá atendê-lo em breve. Abaixo estão os métodos de pagamento:"
        )

        await new_channel.send(content=initial_message, embed=payment_embed, view=VendasCloseView())
        await interaction.followup.send(f"✅ Canal de venda criado! Acesse: {new_channel.mention}", ephemeral=True)


# --- 3. View Principal (Contém o Select) ---
class VendasProductSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Persistente
        self.add_item(VendasProductSelect())