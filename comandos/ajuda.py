import discord
from discord.ext import commands
from utils.checks import is_admin, is_mod

class AjudaView(discord.ui.View):
    def __init__(self, bot, author):
        super().__init__(timeout=120.0)
        self.bot = bot
        self.author = author
        self.add_item(AjudaCategoriaSelect(bot, author))

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        try:
            await self.message.edit(view=self)
        except discord.HTTPException:
            pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Garante que apenas o autor do comando possa interagir
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Este menu não é para você!", ephemeral=True)
            return False
        return True

class AjudaCategoriaSelect(discord.ui.Select):
    def __init__(self, bot, author):
        self.bot = bot
        self.author = author
        
        # Cria as opções do menu
        opcoes = [
            discord.SelectOption(label="Início", description="Voltar para a visão geral.", emoji="🏠"),
            # Adicionamos categorias manualmente para ter controle
            discord.SelectOption(label="Administração", description="Comandos de configuração.", emoji="⚙️"),
            discord.SelectOption(label="Moderação", description="Comandos para moderar o chat.", emoji="🔨"),
            discord.SelectOption(label="Tickets", description="Comandos do sistema de ticket.", emoji="🎟️"),
            discord.SelectOption(label="Utilidades", description="Comandos úteis para membros.", emoji="🛠️"),
            discord.SelectOption(label="Outros", description="Comandos gerais.", emoji="📦")
        ]
        
        super().__init__(placeholder="Escolha uma categoria...", min_values=1, max_values=1, options=opcoes)

    async def callback(self, interaction: discord.Interaction):
        # Pega o valor selecionado (ex: "Administração")
        categoria_selecionada = self.values[0]
        
        # Mapeia o valor para os Cogs reais
        cog_map = {
            "Administração": ["Admin", "Permissoes", "AutoRole"],
            "Moderação": ["Moderacao", "Kick", "Unban", "Limpar"],
            "Tickets": ["TicketSetup", "TicketRanking"], # Nomes dos novos cogs de ticket
            "Utilidades": ["Utilidades", "InfoUsuario", "ServerInfo", "Avatar", "Enquete"],
            "Outros": ["Ping", "Recarregar", "Ajuda"]
        }
        
        if categoria_selecionada == "Início":
            embed = self.get_initial_embed(interaction.client.user)
            await interaction.response.edit_message(embed=embed)
            return

        # Filtra os Cogs baseado na seleção
        cogs_para_mostrar = cog_map.get(categoria_selecionada)
        if not cogs_para_mostrar:
            await interaction.response.send_message("Categoria não encontrada.", ephemeral=True)
            return

        embed = discord.Embed(title=f"Categoria: {categoria_selecionada}", color=discord.Color.blue())
        prefix = await self.bot.get_prefix(interaction.message)
        prefix = prefix if isinstance(prefix, str) else prefix[0] # Lida com listas de prefixo

        # Verifica as permissões do autor
        ctx_mock = await self.bot.get_context(interaction.message)
        ctx_mock.author = self.author
        
        try:
            is_admin_check = await is_admin().predicate(ctx_mock)
        except commands.CheckFailure:
            is_admin_check = False
            
        try:
            is_mod_check = await is_mod().predicate(ctx_mock)
        except commands.CheckFailure:
            is_mod_check = False

        for cog_name in cogs_para_mostrar:
            cog = self.bot.get_cog(cog_name)
            if not cog:
                continue

            comandos_visiveis = []
            for cmd in cog.get_commands():
                if cmd.hidden:
                    continue
                
                # Checagem de Permissão
                if cog_name in cog_map["Administração"] and not is_admin_check:
                    continue
                if cog_name in cog_map["Moderação"] and not is_mod_check:
                    continue
                
                # Checagem de Dono (para r!recarregar)
                is_owner_command = any(check.__qualname__ == 'is_owner.<locals>.predicate' for check in cmd.checks)
                if is_owner_command and not await self.bot.is_owner(self.author):
                    continue

                help_text = cmd.help or "Sem descrição."
                comandos_visiveis.append(f"`{prefix}{cmd.name}` - {help_text}")
            
            if comandos_visiveis:
                embed.add_field(name=f"Comandos de {cog_name}", value="\n".join(comandos_visiveis), inline=False)
        
        if not embed.fields:
            embed.description = "Você não tem permissão para ver ou não há comandos nesta categoria."

        await interaction.response.edit_message(embed=embed)
    
    def get_initial_embed(self, bot_user):
        embed = discord.Embed(
            title=f"Painel de Ajuda de {bot_user.name}",
            description="Bem-vindo ao painel de ajuda interativo!\nUse o menu abaixo para selecionar uma categoria e ver os comandos.",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=bot_user.avatar.url if bot_user.avatar else bot_user.default_avatar.url)
        embed.set_footer(text="Este menu expira em 2 minutos.")
        return embed


class Ajuda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ajuda', help='Mostra o painel de ajuda interativo.')
    async def ajuda(self, ctx):
        view = AjudaView(self.bot, ctx.author)
        embed = view.children[0].get_initial_embed(self.bot.user) # Pega o embed inicial do Select
        view.message = await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Ajuda(bot))