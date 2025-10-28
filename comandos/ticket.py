import discord
from discord.ext import commands
from utils import settings_manager
import asyncio # Adicionado aqui para o fecharticket

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='abrirticket', help='Abre um novo ticket de suporte.')
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def abrirticket(self, ctx):
        category_id = settings_manager.get_setting(ctx.guild.id, 'ticket_category')
        if not category_id:
            embed = discord.Embed(
                title="⚠️ Categoria de Tickets Não Configurada",
                description=f"Peça a um administrador para definir a categoria de tickets.",
                color=discord.Color.gold()
            )
            embed.set_footer(text=f"Use: {ctx.prefix}setticketcategory <nome-da-categoria>")
            await ctx.send(embed=embed)
            ctx.command.reset_cooldown(ctx)
            return

        category = self.bot.get_channel(category_id)
        if not category or not isinstance(category, discord.CategoryChannel):
            await ctx.send("A categoria de tickets configurada não foi encontrada ou é inválida. Avise um admin.")
            ctx.command.reset_cooldown(ctx)
            return

        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        try:
            channel = await ctx.guild.create_text_channel(
                name=f'ticket-{ctx.author.name}',
                category=category,
                overwrites=overwrites
            )
            
            await ctx.send(f"✅ Ticket criado com sucesso! Acesse: {channel.mention}", delete_after=10)
            
            embed = discord.Embed(
                title=f"Ticket de {ctx.author.name}",
                description="Por favor, descreva seu problema ou dúvida em detalhes.\nUm moderador virá ajudar assim que possível.",
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Para fechar este ticket, use {ctx.prefix}fecharticket")
            
            await channel.send(f"Bem-vindo, {ctx.author.mention}!", embed=embed)

        except Exception as e:
            await ctx.send(f"Ocorreu um erro ao criar o ticket: {e}")

    @commands.command(name='fecharticket', help='Fecha o ticket atual.')
    async def fecharticket(self, ctx):
        # Verifica se está numa categoria de ticket (melhor do que checar nome)
        category_id = settings_manager.get_setting(ctx.guild.id, 'ticket_category')
        if not ctx.channel.category_id or ctx.channel.category_id != category_id:
            await ctx.send("Este comando só pode ser usado em um canal de ticket.")
            return

        embed = discord.Embed(
            title="Ticket Fechado",
            description="Este ticket será deletado em 5 segundos...",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        
        await asyncio.sleep(5)
        await ctx.channel.delete(reason="Ticket fechado")


async def setup(bot):
    await bot.add_cog(Ticket(bot))