import discord
from discord.ext import commands
from utils import settings_manager
from utils.checks import is_admin

# Função helper para gerenciar listas de cargos
async def _manage_role_list(ctx, cargo, setting_key):
    guild_id = ctx.guild.id
    # Pega a lista de cargos, ou cria uma nova se não existir
    roles = settings_manager.get_setting(guild_id, setting_key) or []
    
    if cargo.id in roles:
        # Remove o cargo se ele já estiver na lista
        roles.remove(cargo.id)
        action = "removido de"
    else:
        # Adiciona o cargo se ele não estiver na lista
        roles.append(cargo.id)
        action = "adicionado a"
        
    settings_manager.set_setting(guild_id, setting_key, roles)
    return action

class Permissoes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='setadminrole', help='Adiciona/Remove um cargo de Admin do bot.')
    @is_admin()
    async def setadminrole(self, ctx, cargo: discord.Role):
        # Usa a chave no plural: "admin_roles"
        action = await _manage_role_list(ctx, cargo, 'admin_roles')
        embed = discord.Embed(
            title="Permissão de Admin Atualizada",
            description=f"O cargo {cargo.mention} foi {action} lista de Admins do bot.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name='setmodrole', help='Adiciona/Remove um cargo de Moderação.')
    @is_admin()
    async def setmodrole(self, ctx, cargo: discord.Role):
        # Usa a chave no plural: "mod_roles"
        action = await _manage_role_list(ctx, cargo, 'mod_roles')
        embed = discord.Embed(
            title="Permissão de Moderação Atualizada",
            description=f"O cargo {cargo.mention} foi {action} lista de Moderadores.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name='setstaffrole', help='Adiciona/Remove um cargo de Staff (Tickets).')
    @is_admin()
    async def setstaffrole(self, ctx, cargo: discord.Role):
        # Usa a chave no plural: "staff_roles"
        action = await _manage_role_list(ctx, cargo, 'staff_roles')
        embed = discord.Embed(
            title="Permissão de Staff Atualizada",
            description=f"O cargo {cargo.mention} foi {action} lista de Staff (Tickets).",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Permissoes(bot))