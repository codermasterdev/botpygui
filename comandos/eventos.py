import discord
from discord.ext import commands
from utils import settings_manager

class Eventos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Evento de entrada
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel_id = settings_manager.get_setting(member.guild.id, 'welcome_channel')
        if not channel_id:
            print(f"Servidor {member.guild.name}: Canal 'welcome_channel' não configurado.")
            return

        channel = self.bot.get_channel(channel_id)
        if not channel:
            print(f"Servidor {member.guild.name}: Canal 'welcome_channel' (ID: {channel_id}) não encontrado.")
            return

        embed = discord.Embed(
            title=f"👋 Bem-vindo(a), {member.name}!",
            description=f"{member.mention} acabou de entrar no servidor.\nSeja bem-vindo(a) e divirta-se!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text=f"ID do usuário: {member.id}")
        
        await channel.send(embed=embed)

    # Evento de saída
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel_id = settings_manager.get_setting(member.guild.id, 'goodbye_channel')
        if not channel_id:
            print(f"Servidor {member.guild.name}: Canal 'goodbye_channel' não configurado.")
            return
            
        channel = self.bot.get_channel(channel_id)
        if not channel:
            print(f"Servidor {member.guild.name}: Canal 'goodbye_channel' (ID: {channel_id}) não encontrado.")
            return
            
        embed = discord.Embed(
            title=f"😢 Adeus, {member.name}!",
            description=f"{member.mention} (ou {member.name}#{member.discriminator}) saiu do servidor.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text=f"ID do usuário: {member.id}")
        
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Eventos(bot))