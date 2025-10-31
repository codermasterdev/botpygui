import discord
from discord.ext import commands

class Creditos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='creditos', help='Mostra os créditos do desenvolvedor do bot.')
    async def creditos(self, ctx):
        
        embed = discord.Embed(
            title="Créditos do Bot",
            description="Este bot foi desenvolvido pela **Coder Master**.",
            color=0x0066cc # Um tom de azul
        )
        
        embed.set_author(name="Coder Master", url="https://codermaster.com.br")
        
        embed.add_field(
            name="Site", 
            value="[codermaster.com.br](https://codermaster.com.br)", 
            inline=True
        )
        
        embed.add_field(
            name="WhatsApp", 
            value="[Clique aqui para conversar](https://api.whatsapp.com/send/?phone=5519995476892&text=Ol%C3%A1,%20vim%20pelo%20bot%20do%20discord%20e%20tenho%20interesse%20em%20seu%20servi%C3%A7o.&type=phone_number&app_absent=0)", 
            inline=True
        )
        
        embed.set_footer(text="Coder Master - Soluções em Desenvolvimento")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Creditos(bot))