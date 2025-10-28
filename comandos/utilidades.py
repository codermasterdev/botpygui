import discord
from discord.ext import commands
from utils import settings_manager

class Utilidades(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='anuncio', help='Envia um anúncio em um canal específico.')
    @commands.has_permissions(administrator=True)
    async def anuncio(self, ctx, canal: discord.TextChannel, *, mensagem: str):
        # CORREÇÃO AQUI: Adicionado 'if ctx.author.avatar else ctx.author.default_avatar.url'
        author_icon_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
        
        embed = discord.Embed(title="📢 Anúncio", description=mensagem, color=discord.Color.blue())
        embed.set_footer(text=f"Anúncio feito por {ctx.author.name}", icon_url=author_icon_url)
        
        await canal.send(embed=embed)
        await ctx.send(f"✅ Anúncio enviado com sucesso para {canal.mention}!", delete_after=5)
        await ctx.message.delete()

    @commands.command(name='sugestao', help='Envia uma sugestão para o canal de sugestões.')
    async def sugestao(self, ctx, *, sugestao_texto: str):
        channel_id = settings_manager.get_setting(ctx.guild.id, 'suggestions_channel')
        if not channel_id:
            embed = discord.Embed(
                title="⚠️ Canal de Sugestões Não Configurado",
                description=f"Peça a um administrador para definir o canal de sugestões.",
                color=discord.Color.gold()
            )
            embed.set_footer(text=f"Use: {ctx.prefix}setsugestoes #canal-sugestoes")
            await ctx.send(embed=embed, delete_after=10)
            await ctx.message.delete()
            return

        channel = self.bot.get_channel(channel_id)
        if not channel:
            await ctx.send("Canal de sugestões não encontrado. Avise um admin.", delete_after=10)
            return

        # CORREÇÃO AQUI: Adicionado 'if ctx.author.avatar else ctx.author.default_avatar.url'
        author_icon_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url

        embed = discord.Embed(title="💡 Nova Sugestão", description=sugestao_texto, color=discord.Color.yellow())
        embed.set_author(name=ctx.author.name, icon_url=author_icon_url)
        
        try:
            msg = await channel.send(embed=embed)
            await msg.add_reaction("👍")
            await msg.add_reaction("👎")
            
            await ctx.send(f"✅ Sugestão enviada com sucesso para {channel.mention}!", delete_after=10)
        except Exception as e:
            await ctx.send(f"Ocorreu um erro ao enviar a sugestão: {e}")
            
        await ctx.message.delete()
        
    @commands.command(name='divulgar', help='Divulga algo no canal de divulgação.')
    @commands.cooldown(1, 3600, commands.BucketType.user) # Cooldown de 1 hora por usuário
    async def divulgar(self, ctx, *, mensagem: str):
        channel_id = settings_manager.get_setting(ctx.guild.id, 'divulgacao_channel')
        if not channel_id:
            embed = discord.Embed(
                title="⚠️ Canal de Divulgação Não Configurado",
                description=f"Peça a um administrador para definir o canal de divulgação.",
                color=discord.Color.gold()
            )
            embed.set_footer(text=f"Use: {ctx.prefix}setdivulgacao #canal-divulgacao")
            await ctx.send(embed=embed, delete_after=10)
            ctx.command.reset_cooldown(ctx)
            await ctx.message.delete()
            return
            
        if ctx.channel.id != channel_id:
            await ctx.send(f"Este comando só pode ser usado no canal <#{channel_id}>.", delete_after=10)
            ctx.command.reset_cooldown(ctx)
            await ctx.message.delete()
            return

        # CORREÇÃO AQUI: Adicionado 'if ctx.author.avatar else ctx.author.default_avatar.url'
        author_icon_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            
        embed = discord.Embed(title="📣 Nova Divulgação", description=mensagem, color=discord.Color.purple())
        embed.set_author(name=ctx.author.name, icon_url=author_icon_url)
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Utilidades(bot))