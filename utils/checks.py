from discord.ext import commands
from utils import settings_manager
def is_staff():
    async def predicate(ctx):
        settings = settings_manager.load_settings()
        staff_role_id = settings.get(ctx.guild.id, {}).get("staff_role")
        if not staff_role_id:
            return False
        staff_role = ctx.guild.get_role(staff_role_id)
        return staff_role and (ctx.author.guild_permissions.administrator or staff_role in ctx.author.roles)
    return commands.check(predicate)

def is_mod():
    async def predicate(ctx):
        settings = settings_manager.load_settings()
        mod_role_id = settings.get(ctx.guild.id, {}).get("mod_role")
        if not mod_role_id:
            return False
        mod_role = ctx.guild.get_role(mod_role_id)
        return mod_role and (ctx.author.guild_permissions.administrator or mod_role in ctx.author.roles or is_staff_check(ctx))
    return commands.check(predicate)

def is_admin():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator or is_staff_check(ctx)
    return commands.check(predicate)

def is_staff_check(ctx):
    settings = settings_manager.load_settings()
    staff_role_id = settings.get(ctx.guild.id, {}).get("staff_role")
    if not staff_role_id:
        return False
    staff_role = ctx.guild.get_role(staff_role_id)
    return staff_role and staff_role in ctx.author.roles
