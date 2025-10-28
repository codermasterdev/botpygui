import discord
from discord.ext import commands
import asyncio
from utils.checks import is_mod

class Limpar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='limpar', aliases=['purge'], help='Apaga uma quantidade de mensagens do chat.')
    @is_mod()
    async def limpar(self, ctx, quantidade: int):
        
        if quantidade > 100 or quantidade < 1:
            await ctx.send("Você só pode limpar entre 1 e 100 mensagens por vez.", delete_after=10)
            return
            
        try:
            # Adicionamos +1 para incluir a própria mensagem do comando
            deleted_messages = await ctx.channel.purge(limit=quantidade + 1)
            
            embed = discord.Embed(
                title="🧹 Limpeza Concluída",
                description=f"**{len(deleted_messages) - 1}** mensagens foram apagadas por {ctx.author.mention}.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed, delete_after=5) # Envia uma confirmação que se apaga
            
        except discord.Forbidden:
            await ctx.send("Eu não tenho permissão para apagar mensagens neste canal.", delete_after=10)
        except Exception as e:
            await ctx.send(f"Ocorreu um erro: {e}", delete_after=10)

async def setup(bot):
    await bot.add_cog(Limpar(bot))