import discord
from discord.ext import commands
from utils import ticket_stats

class TicketRanking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ticketranking', aliases=['tstats'], help='Mostra o ranking da staff de tickets.')
    async def ticketranking(self, ctx):
        stats = ticket_stats.get_guild_stats(ctx.guild.id)
        
        if not stats:
            embed = discord.Embed(title="Ranking de Tickets", description="Nenhum ticket foi processado ainda.", color=discord.Color.blue())
            await ctx.send(embed=embed)
            return
            
        # Classifica os stats por tickets resolvidos (do maior para o menor)
        sorted_stats = sorted(stats.items(), key=lambda item: item[1]['resolvidos'], reverse=True)
        
        embed = discord.Embed(title="🏆 Ranking de Staff (Tickets)", color=discord.Color.gold())
        
        description = ""
        rank = 1
        for staff_id, data in sorted_stats:
            try:
                member = ctx.guild.get_member(int(staff_id)) or f"ID: {staff_id}"
                name = member.display_name if isinstance(member, discord.Member) else member
            except:
                name = f"ID: {staff_id}"

            emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"**{rank}.**"
            description += f"{emoji} {name}\n"
            description += f"   > **Resolvidos:** {data['resolvidos']} | **Cancelados:** {data['cancelados']}\n"
            rank += 1
            
        embed.description = description
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TicketRanking(bot))