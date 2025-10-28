import discord
from discord.ext import commands

class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='avatar', help='Mostra o avatar de um usuário.')
    async def avatar(self, ctx, member: discord.Member = None):
        # Se nenhum membro for mencionado, usa o autor da mensagem
        if member is None:
            member = ctx.author

        icon_url = member.avatar.url if member.avatar else member.default_avatar.url

        embed = discord.Embed(
            title=f"Avatar de {member.name}",
            color=member.color
        )
        embed.set_image(url=icon_url)
        embed.set_footer(text=f"Solicitado por {ctx.author.name}")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Avatar(bot))