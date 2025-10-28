import discord
from discord.ext import commands
import os
import asyncio
from utils.checks import is_admin

class Recarregar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='recarregar', aliases=['reload'], help='Recarrega todos os módulos (cogs) do bot.')
    @is_admin()
    async def recarregar(self, ctx):
        """
        Recarrega, carrega novos e descarrega cogs removidos da pasta 'comandos'.
        """
        embed = discord.Embed(
            title="🔄 Recarregando Módulos...",
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at
        )
        logs = ""

        # Usar sets para facilitar a comparação
        try:
            # Pega todos os arquivos .py na pasta 'comandos'
            cogs_in_folder = {f'comandos.{f[:-3]}' for f in os.listdir('./comandos') if f.endswith('.py')}
        except FileNotFoundError:
            await ctx.send("ERRO: Pasta `comandos/` não encontrada.")
            return

        # Pega todos os cogs que começam com 'comandos.' já carregados no bot
        loaded_cogs = {cog for cog in self.bot.extensions.keys() if cog.startswith('comandos.')}

        # Compara os sets para ver o que fazer
        to_load = cogs_in_folder - loaded_cogs     # Cogs no HD mas não no bot (Novos)
        to_unload = loaded_cogs - cogs_in_folder  # Cogs no bot mas não no HD (Deletados)
        to_reload = cogs_in_folder & loaded_cogs  # Cogs em ambos (Modificados)

        # 1. Recarrega cogs existentes (modificados)
        for cog_name in to_reload:
            try:
                await self.bot.reload_extension(cog_name)
                logs += f"✅ Recarregado: `{cog_name}`\n"
            except Exception as e:
                logs += f"❌ Falha (Reload) `{cog_name}`:\n```py\n{e}\n```\n"
        
        # 2. Carrega cogs novos
        for cog_name in to_load:
            try:
                await self.bot.load_extension(cog_name)
                logs += f"➕ Carregado (Novo): `{cog_name}`\n"
            except Exception as e:
                logs += f"❌ Falha (Load) `{cog_name}`:\n```py\n{e}\n```\n"

        # 3. Descarrega cogs deletados
        for cog_name in to_unload:
            try:
                await self.bot.unload_extension(cog_name)
                logs += f"➖ Descarregado (Deletado): `{cog_name}`\n"
            except Exception as e:
                logs += f"❌ Falha (Unload) `{cog_name}`:\n```py\n{e}\n```\n"

        if not logs:
            logs = "Nenhuma alteração encontrada nos cogs."

        embed.description = logs
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Recarregar(bot))