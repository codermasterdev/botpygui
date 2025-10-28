import discord
import random
import string
from utils import settings_manager, ticket_stats
from utils.checks import get_staff_roles # Para checar permissão nos botões

# --- View de Gerenciamento (Botões dentro do ticket) ---
class TicketManageView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Botões persistentes

    async def _check_perms(self, interaction: discord.Interaction):
        # Verifica se o usuário é Dono, Admin do Discord ou tem Cargo Staff
        user = interaction.user
        if user == interaction.guild.owner or user.guild_permissions.administrator:
            return True
        
        staff_roles = get_staff_roles(interaction.guild.id)
        if not staff_roles:
            await interaction.response.send_message("Os cargos de Staff não estão configurados.", ephemeral=True)
            return False

        for role_id in staff_roles:
            if discord.utils.get(user.roles, id=role_id):
                return True
        
        await interaction.response.send_message("Você não tem permissão para usar este botão.", ephemeral=True)
        return False

    @discord.ui.button(label="Concluir", style=discord.ButtonStyle.success, emoji="✅", custom_id="ticket_concluir")
    async def concluir(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_perms(interaction):
            return

        await interaction.response.send_message("Ticket marcado como concluído. Fechando em 5 segundos...", ephemeral=True)
        ticket_stats.add_stat(interaction.guild.id, interaction.user.id, 'resolvidos')
        
        # Aqui você pode adicionar lógica de transcript, se desejar
        await asyncio.sleep(5)
        await interaction.channel.delete(reason="Ticket Concluído")

    @discord.ui.button(label="Bloquear", style=discord.ButtonStyle.secondary, emoji="🔒", custom_id="ticket_bloquear")
    async def bloquear(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_perms(interaction):
            return

        # Pega o usuário que abriu o ticket (pelo nome do canal)
        user_id_str = interaction.channel.name.split('-')[-1]
        member = interaction.guild.get_member(int(user_id_str))

        if member:
            await interaction.channel.set_permissions(member, send_messages=False)
            await interaction.response.send_message(f"🔒 Ticket bloqueado por {interaction.user.mention}. O usuário não pode mais enviar mensagens.", ephemeral=False)
        else:
            await interaction.response.send_message("Não foi possível encontrar o usuário do ticket.", ephemeral=True)

    @discord.ui.button(label="Deletar", style=discord.ButtonStyle.danger, emoji="🗑️", custom_id="ticket_deletar")
    async def deletar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_perms(interaction):
            return

        await interaction.response.send_message("Ticket cancelado. Deletando em 5 segundos...", ephemeral=True)
        ticket_stats.add_stat(interaction.guild.id, interaction.user.id, 'cancelados')
        
        await asyncio.sleep(5)
        await interaction.channel.delete(reason="Ticket Deletado/Cancelado")

# --- View de Abertura (Menu de Categorias) ---
class TicketOpenView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # View persistente
        self.add_item(TicketCategorySelect()) # Adiciona o menu

class TicketCategorySelect(discord.ui.Select):
    def __init__(self):
        # As opções são carregadas dinamicamente
        super().__init__(custom_id="ticket_open_select", placeholder="Clique aqui para abrir um ticket...", min_values=1, max_values=1)
        self._load_options()

    def _load_options(self):
        # Esta é uma gambiarra, pois não temos acesso fácil
        # ao settings_manager de forma dinâmica aqui.
        # As opções serão (re)carregadas quando o comando setup for usado.
        # No setup, vamos popular isso.
        
        # Placeholder
        self.options = [discord.SelectOption(label="Configuração Pendente", value="none", description="Peça a um admin para usar r!ticketsetup")]

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True) # "Pensando..."
        
        categoria_selecionada = self.values[0]
        if categoria_selecionada == "none":
            await interaction.followup.send("O sistema de tickets ainda não foi configurado.", ephemeral=True)
            return

        # Gera nome do ticket
        rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        user = interaction.user
        channel_name = f"ticket-{categoria_selecionada}-{rand_str}-{user.id}"

        # Pega a categoria de tickets
        category_id = settings_manager.get_setting(interaction.guild.id, 'ticket_main_category')
        category = interaction.guild.get_channel(category_id)
        
        if not category or not isinstance(category, discord.CategoryChannel):
            # Tenta criar a categoria se não existir
            try:
                category = await interaction.guild.create_category("Tickets")
                settings_manager.set_setting(interaction.guild.id, 'ticket_main_category', category.id)
            except discord.Forbidden:
                await interaction.followup.send("Erro: Não tenho permissão para criar a categoria 'Tickets'.", ephemeral=True)
                return

        # Pega cargos de staff
        staff_roles = get_staff_roles(interaction.guild.id)
        staff_objects = [interaction.guild.get_role(role_id) for role_id in staff_roles if interaction.guild.get_role(role_id)]

        # Permissões do novo canal
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        # Adiciona permissão para os cargos de staff
        for role in staff_objects:
            overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        try:
            new_channel = await interaction.guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites
            )
        except discord.Forbidden:
            await interaction.followup.send("Erro: Não tenho permissão para criar canais na categoria 'Tickets'.", ephemeral=True)
            return
        
        # Envia a mensagem de gerenciamento no novo canal
        embed = discord.Embed(
            title=f"Ticket: {categoria_selecionada.capitalize()}",
            description=f"Bem-vindo, {user.mention}! \n"
                        f"Um membro da staff virá ajudar em breve. "
                        f"Por favor, descreva seu problema detalhadamente.",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Use os botões abaixo para gerenciar o ticket (Apenas Staff).")
        
        await new_channel.send(content=user.mention, embed=embed, view=TicketManageView())
        await interaction.followup.send(f"✅ Ticket criado com sucesso! Acesse: {new_channel.mention}", ephemeral=True)

# Precisamos do asyncio para o sleep
import asyncio