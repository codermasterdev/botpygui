import discord
from discord.ext import commands

class InfoUsuario(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='infousuario', aliases=['userinfo'], help='Mostra informações de um usuário.')
    async def infousuario(self, ctx, member: discord.Member = None):
        # Se nenhum membro for mencionado, usa o autor da mensagem
        if member is None:
            member = ctx.author

        # Pega os cargos do membro (exceto o @everyone)
        roles = [role.mention for role in member.roles[1:]]
        roles.reverse() # Inverte para mostrar o cargo mais alto primeiro
        if not roles:
            roles = ["Nenhum"]

        embed = discord.Embed(
            title=f"Informações de {member.name}",
            color=member.color # Usa a cor do cargo mais alto do usuário
        )
        
        icon_url = member.avatar.url if member.avatar else member.default_avatar.url
        embed.set_thumbnail(url=icon_url)

        embed.add_field(name="🏷️ Nome", value=member.mention, inline=True)
        embed.add_field(name="🆔 ID", value=member.id, inline=True)
        
        # Formata as datas
        created_at = discord.utils.format_dt(member.created_at, style='R')
        joined_at = discord.utils.format_dt(member.joined_at, style='R')
        
        embed.add_field(name="📅 Conta Criada", value=created_at, inline=True)
        embed.add_field(name="📥 Entrou no Servidor", value=joined_at, inline=True)
        
        embed.add_field(name=f"Cargos ({len(roles)})", value=" ".join(roles), inline=False)
        
        embed.set_footer(text=f"Solicitado por {ctx.author.name}")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(InfoUsuario(bot))