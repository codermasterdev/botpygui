from discord.ext import commands
from utils import settings_manager
import discord

# --- FUNÇÕES HELPER CORRIGIDAS ---
# Estas funções agora leem as listas de cargos corretamente

async def check_admin(ctx):
    """ Verifica se o usuário é Admin (Perm ou Cargo) """
    if ctx.author.guild_permissions.administrator:
        return True
    
    # CORREÇÃO: Lê 'admin_roles' (plural)
    admin_roles_ids = settings_manager.get_setting(ctx.guild.id, 'admin_roles') or []
    if not admin_roles_ids:
        return False
        
    author_role_ids = {role.id for role in ctx.author.roles}
    return any(role_id in author_role_ids for role_id in admin_roles_ids)

async def check_mod(ctx):
    """ Verifica se o usuário é Mod (Admin ou Cargo Mod) """
    if await check_admin(ctx):
        return True

    # CORREÇÃO: Lê 'mod_roles' (plural)
    mod_roles_ids = settings_manager.get_setting(ctx.guild.id, 'mod_roles') or []
    if not mod_roles_ids:
        return False
        
    author_role_ids = {role.id for role in ctx.author.roles}
    return any(role_id in author_role_ids for role_id in mod_roles_ids)

async def check_staff(ctx):
    """ Verifica se o usuário é Staff (Admin ou Cargo Staff) """
    if await check_admin(ctx):
        return True

    # CORREÇÃO: Lê 'staff_roles' (plural)
    staff_roles_ids = settings_manager.get_setting(ctx.guild.id, 'staff_roles') or []
    if not staff_roles_ids:
        return False
        
    author_role_ids = {role.id for role in ctx.author.roles}
    return any(role_id in author_role_ids for role_id in staff_roles_ids)

# --- DECORATORS ---

def is_admin():
    """ Decorator @is_admin() """
    async def predicate(ctx_or_interaction):
        # Lida com Comandos (ctx) e Interações (interaction)
        ctx = await _get_context(ctx_or_interaction)
        if not await check_admin(ctx):
            raise commands.CheckFailure("Você não tem permissão de Admin do Bot.")
        return True
    return commands.check(predicate)

def is_mod():
    """ Decorator @is_mod() """
    async def predicate(ctx_or_interaction):
        ctx = await _get_context(ctx_or_interaction)
        if not await check_mod(ctx):
            raise commands.CheckFailure("Você não tem permissão de Moderação do Bot.")
        return True
    return commands.check(predicate)

def is_staff():
    """ Decorator @is_staff() """
    async def predicate(ctx_or_interaction):
        ctx = await _get_context(ctx_or_interaction)
        if not await check_staff(ctx):
            raise commands.CheckFailure("Você não tem permissão de Staff do Bot.")
        return True
    return commands.check(predicate)

async def _get_context(ctx_or_interaction):
    """ Helper para extrair 'ctx' de um comando ou interação de componente """
    if isinstance(ctx_or_interaction, discord.Interaction):
        # Se for uma interação, recria um 'Context' simples
        # Precisamos pegar o 'ctx' do bot para checar permissões de comando
        ctx = await ctx_or_interaction.client.get_context(ctx_or_interaction.message, cls=commands.Context)
        # Sobrescreve o autor para ser o usuário que clicou
        ctx.author = ctx_or_interaction.user
        return ctx
    return ctx_or_interaction # Já é um Context