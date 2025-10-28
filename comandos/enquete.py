import discord
from discord.ext import commands

class Enquete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='enquete', help='Cria uma enquete simples (Sim/Não).')
    async def enquete(self, ctx, *, pergunta: str):
        
        embed = discord.Embed(
            title="📊 Nova Enquete",
            description=pergunta,
            color=discord.Color.yellow()
        )
        
        icon_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
        embed.set_author(name=f"Iniciada por {ctx.author.name}", icon_url=icon_url)
        
        try:
            # Envia a enquete
            msg = await ctx.send(embed=embed)
            
            # Adiciona as reações
            await msg.add_reaction("👍") # SIM
            await msg.add_reaction("👎") # NÃO
            
            # Apaga a mensagem de comando original
            await ctx.message.delete()
            
        except Exception as e:
            await ctx.send(f"Ocorreu um erro ao criar a enquete: {e}")

async def setup(bot):
    await bot.add_cog(Enquete(bot))