import discord
from discord.ext import commands

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='serverinfo', aliases=['infoserver'], help='Mostra informações sobre o servidor.')
    async def serverinfo(self, ctx):
        guild = ctx.guild
        
        embed = discord.Embed(
            title=f"Informações de {guild.name}",
            color=ctx.guild.owner.color if ctx.guild.owner.color != discord.Color.default() else discord.Color.blue()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="👑 Dono", value=guild.owner.mention, inline=True)
        embed.add_field(name="🆔 ID do Servidor", value=guild.id, inline=True)
        
        # Contagens
        total_members = guild.member_count
        human_members = sum(1 for member in guild.members if not member.bot)
        bot_members = sum(1 for member in guild.members if member.bot)

        embed.add_field(name="👥 Membros", 
                        value=f"**Total:** {total_members}\n"
                              f"**Pessoas:** {human_members}\n"
                              f"**Bots:** {bot_members}", 
                        inline=True)
        
        embed.add_field(name="Canais",
                        value=f"**Texto:** {len(guild.text_channels)}\n"
                              f"**Voz:** {len(guild.voice_channels)}\n"
                              f"**Categorias:** {len(guild.categories)}",
                        inline=True)

        embed.add_field(name="📅 Criado em", value=discord.utils.format_dt(guild.created_at, style='D'), inline=True)
        embed.add_field(name="Cargos", value=f"{len(guild.roles)} cargos", inline=True)
        
        embed.set_footer(text=f"Solicitado por {ctx.author.name}")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerInfo(bot))