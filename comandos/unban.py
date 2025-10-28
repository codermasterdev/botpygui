import discord
from discord.ext import commands
from utils import settings_manager
from utils.checks import is_mod

class Unban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _get_log_channel(self, ctx):
        log_channel_id = settings_manager.get_setting(ctx.guild.id, 'log_channel')
        if not log_channel_id:
            await ctx.send(f"Canal de logs não configurado. Use `{ctx.prefix}setlogs #canal`")
            return None
        return self.bot.get_channel(log_channel_id)

    @commands.command(name='unban', help='Desbane um usuário do servidor (requer ID).')
    @is_mod()
    async def unban(self, ctx, user_id: int, *, reason: str = "Motivo não fornecido"):
        log_channel = await self._get_log_channel(ctx)
        if not log_channel:
            return 
        
        try:
            # Tenta encontrar o usuário pelo ID
            user = await self.bot.fetch_user(user_id)
        except discord.NotFound:
            await ctx.send(f"Usuário com ID `{user_id}` não encontrado.", delete_after=10)
            return
            
        try:
            # Tenta desbanir o usuário
            await ctx.guild.unban(user, reason=f"{reason} (Desbanido por: {ctx.author.name})")
            
            embed = discord.Embed(
                title="✅ Usuário Desbanido",
                color=discord.Color.green()
            )
            embed.add_field(name="Usuário", value=f"{user.name}#{user.discriminator} ({user.id})", inline=False)
            embed.add_field(name="Motivo", value=reason, inline=False)
            embed.add_field(name="Moderador", value=ctx.author.mention, inline=False)
            
            await log_channel.send(embed=embed)
            await ctx.send(f"✅ {user.name} foi desbanido. Log enviado para {log_channel.mention}", delete_after=5)

        except discord.Forbidden:
            await ctx.send("Eu não tenho permissão para desbanir usuários.", delete_after=10)
        except discord.HTTPException as e:
            await ctx.send(f"Ocorreu um erro ao tentar desbanir: {e}", delete_after=10)
        
        await ctx.message.delete()


async def setup(bot):
    await bot.add_cog(Unban(bot))