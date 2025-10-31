import discord
from discord.ext import commands
# Importa as novas funções de verificação
from utils.checks import check_admin, check_mod, check_staff

class AjudaView(discord.ui.View):
    def __init__(self, bot, author):
        super().__init__(timeout=120.0)
        self.bot = bot
        self.author = author
        # Adiciona o Select atualizado
        self.add_item(AjudaCategoriaSelect(bot, author))

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        try:
            await self.message.edit(view=self)
        except discord.HTTPException:
            pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Este menu não é para você!", ephemeral=True)
            return False
        return True

class AjudaCategoriaSelect(discord.ui.Select):
    def __init__(self, bot, author):
        self.bot = bot
        self.author = author
        
        # --- OPÇÕES ATUALIZADAS ---
        opcoes = [
            discord.SelectOption(label="Início", description="Voltar para a visão geral.", emoji="🏠"),
            discord.SelectOption(label="Administração", description="Comandos de configuração do bot.", emoji="⚙️"),
            discord.SelectOption(label="Moderação", description="Comandos para moderar o servidor.", emoji="🔨"),
            discord.SelectOption(label="Tickets", description="Comandos do sistema de ticket.", emoji="🎟️"),
            discord.SelectOption(label="Bate-Ponto", description="Comandos do sistema de ponto.", emoji="🕒"),
            discord.SelectOption(label="Recrutamento", description="Comandos do formulário de recrutamento.", emoji="📝"),
            discord.SelectOption(label="Vendas", description="Comandos do sistema de loja.", emoji="🛒"),
            discord.SelectOption(label="Ausência", description="Comandos para registrar ausência.", emoji="📅"),
            discord.SelectOption(label="Utilidades", description="Comandos úteis para membros.", emoji="🛠️"),
            discord.SelectOption(label="Outros", description="Comandos gerais e de ajuda.", emoji="📦")
        ]
        
        super().__init__(placeholder="Escolha uma categoria...", min_values=1, max_values=1, options=opcoes)

    async def callback(self, interaction: discord.Interaction):
        categoria_selecionada = self.values[0]
        
        # --- MAPA DE COGS ATUALIZADO ---
        cog_map = {
            "Administração": [
                "Admin", "Permissoes", "AutoRole", "TicketSetup", 
                "SetupBatePonto", "SetupRecrutamento", "SetupVendasCog", "SetupAusencia"
            ],
            "Moderação": ["Moderacao", "Kick", "Unban", "Limpar"],
            "Tickets": ["TicketRanking"], 
            "Bate-Ponto": ["BatePontoCog"],
            "Recrutamento": [], 
            "Vendas": [], 
            "Ausência": ["Ausencia"],
            "Utilidades": ["Utilidades", "InfoUsuario", "ServerInfo", "Avatar", "Enquete"],
            "Outros": ["Ping", "Recarregar", "Ajuda", "PrimeirosPassos", "Creditos"]
        }
        
        if categoria_selecionada == "Início":
            embed = self.get_initial_embed(interaction.client.user)
            await interaction.response.edit_message(embed=embed)
            return

        cogs_para_mostrar = cog_map.get(categoria_selecionada)
        if cogs_para_mostrar is None:
            await interaction.response.send_message("Categoria não encontrada.", ephemeral=True)
            return

        embed = discord.Embed(title=f"Categoria: {categoria_selecionada}", color=discord.Color.blue())
        prefix = await self.bot.get_prefix(interaction.message)
        prefix = prefix if isinstance(prefix, str) else prefix[0] 

        # --- VERIFICAÇÃO DE PERMISSÃO CORRIGIDA ---
        ctx_mock = await self.bot.get_context(interaction.message)
        ctx_mock.author = interaction.user
        
        # Lógica para categorias que não têm cogs, mas sim descrições
        if categoria_selecionada == "Recrutamento":
            embed.description = "Este sistema funciona por botões.\nUse `r!setuprecrutamento` (Admin) para criar o painel."
        elif categoria_selecionada == "Vendas":
            embed.description = "Este sistema funciona por botões.\nUse `r!setupvendas` (Admin) para criar o painel da loja."
            
        comandos_na_categoria = 0

        for cog_name in cogs_para_mostrar:
            cog = self.bot.get_cog(cog_name)
            if not cog:
                continue

            comandos_visiveis = []
            for cmd in cog.get_commands():
                if cmd.hidden:
                    continue
                
                try:
                    # Simula a checagem de permissão do comando
                    await cmd.can_run(ctx_mock)
                except commands.CheckFailure:
                    continue # Usuário não pode ver este comando, pula
                
                is_owner_command = any(check.__qualname__ == 'is_owner.<locals>.predicate' for check in cmd.checks)
                if is_owner_command and not await self.bot.is_owner(self.author):
                    continue

                help_text = cmd.help or "Sem descrição."
                comandos_visiveis.append(f"`{prefix}{cmd.name}` - {help_text}")
                comandos_na_categoria += 1
            
            if comandos_visiveis:
                embed.add_field(name=f"Comandos de {cog_name}", value="\n".join(comandos_visiveis), inline=False)
        
        if comandos_na_categoria == 0 and not embed.description:
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
        embed = view.children[0].get_initial_embed(self.bot.user) 
        view.message = await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Ajuda(bot))