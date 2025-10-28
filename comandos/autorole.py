import discord
from discord.ext import commands
from utils import settings_manager
from utils.checks import is_admin
import typing # <--- IMPORTANTE: Adicione esta linha no topo

class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 1. O Comando de Configuração (Atualizado)
    @commands.command(name='setautorole', help='Define ou remove o cargo automático para novos membros.')
    @is_admin()
    async def setautorole(self, ctx, cargo: typing.Union[discord.Role, str]):
        
        # Checa se o usuário digitou "remover"
        if isinstance(cargo, str) and cargo.lower() == 'remover':
            # Desativa o autorole
            settings_manager.set_setting(ctx.guild.id, 'autorole', None)
            embed = discord.Embed(
                title="⚙️ Autorole Desativado",
                description="O cargo automático para novos membros foi removido.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)

        # Checa se o usuário mencionou um Cargo
        elif isinstance(cargo, discord.Role):
            # Ativa o autorole
            settings_manager.set_setting(ctx.guild.id, 'autorole', cargo.id)
            embed = discord.Embed(
                title="✅ Autorole Configurado",
                description=f"Novos membros agora receberão o cargo {cargo.mention} automaticamente.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        
        # Se for uma string mas não for "remover" (ex: "r!setautorole batata")
        else:
            embed = discord.Embed(
                title="❌ Argumento Inválido",
                description=f"Você deve mencionar um cargo ou usar a palavra `remover`.",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Exemplo: {ctx.prefix}setautorole @Membro  (para definir)\n"
                                  f"Ou: {ctx.prefix}setautorole remover  (para desativar)")
            await ctx.send(embed=embed)

    # 2. O Listener (Evento) - Este não muda
    @commands.Cog.listener()
    async def on_member_join(self, member):
        role_id = settings_manager.get_setting(member.guild.id, 'autorole')
        
        if not role_id:
            return 
            
        role = member.guild.get_role(role_id)
        
        if role:
            try:
                await member.add_roles(role, reason="Autorole Automático")
                print(f"Cargo {role.name} dado para {member.name} no servidor {member.guild.name}")
            except discord.Forbidden:
                print(f"ERRO DE AUTOROLE: Sem permissão para dar o cargo {role.name} em {member.guild.name}")
            except Exception as e:
                print(f"ERRO DE AUTOROLE: {e}")

async def setup(bot):
    await bot.add_cog(AutoRole(bot))