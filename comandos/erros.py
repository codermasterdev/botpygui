import discord
from discord.ext import commands
import math

# Dicionário de exemplos para os comandos
COMMAND_EXAMPLES = {
    "ban": "r!ban @Usuario Mau comportamento",
    "mutar": "r!mutar @Usuario 30 Spam",
    "warn": "r!warn @Usuario spam",
    "anuncio": "r!anuncio #geral Nova atualização!",
    "sugestao": "r!sugestao Adicionar um bot de música",
    "divulgar": "r!divulgar Venha para o meu servidor!",
    "setlogs": "r!setlogs #logs-moderacao",
    "setbemvindo": "r!setbemvindo #bem-vindo",
    "setadeus": "r!setadeus #adeus",
    "setsugestoes": "r!setsugestoes #sugestoes",
    "setdivulgacao": "r!setdivulgacao #divulgacao",
    "setticketcategory": "r!setticketcategory Tickets",
    "unban": "r!unban 123456789012345678 Usuário perdoado",
    "setautorole": "r!setautorole @Membro (ou r!setautorole remover)",
    "setadminrole": "r!setadminrole @Admins",
    "setmodrole": "r!setmodrole @Moderadores",
    "setstaffrole": "r!setstaffrole @Equipe Support",
    "ticketsetup": "r!ticketsetup #abrir-ticket Suporte Denúncia Dúvida",
    "setuprecrutamento": "r!setuprecrutamento #logs-forms #canal-forms \"Descrição do formulário aqui\"",
    
    # --- NOVOS EXEMPLOS DE VENDAS ---
    "setupvendas": "r!setupvendas #loja",
    "adicionarproduto": "r!adicionarproduto \"Meu Produto Incrível\" 19,99",
    "addpagamento": "r!addpagamento PIX \"Chave aleatória: xyz...\"",
    "removerproduto": "r!removerproduto \"Nome Exato Do Produto\"",
    "removerpagamento": "r!removerpagamento PIX"
    # --------------------------------
}

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        
        # Ignora se o comando não existe
        if isinstance(error, commands.CommandNotFound):
            print(f"Comando não encontrado: {ctx.message.content}")
            return 

        # Erro de argumento faltando (ex: r!anuncio)
        if isinstance(error, commands.MissingRequiredArgument):
            
            # --- CORREÇÃO AQUI ---
            # Adicionamos {ctx.command.name} antes da assinatura
            uso_correto = f"`{ctx.prefix}{ctx.command.name} {ctx.command.signature}`"
            
            embed = discord.Embed(
                title="❌ Uso Incorreto!",
                description=f"Está faltando um argumento.\nO jeito certo de usar é: {uso_correto}",
                color=discord.Color.red()
            )
            
            command_name = ctx.command.name
            example = COMMAND_EXAMPLES.get(command_name)
            
            if example:
                embed.set_footer(text=f"Exemplo: {example}")
            else:
                embed.set_footer(text="Verifique os argumentos necessários.")
                        
            await ctx.send(embed=embed)
            
        # Erro de permissão
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="🚫 Sem Permissão",
                description="Você não tem permissão para usar este comando.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

        # Erro de Cooldown
        elif isinstance(error, commands.CommandOnCooldown):
            tempo_restante = math.ceil(error.retry_after)
            embed = discord.Embed(
                title="⏱️ Calma aí!",
                description=f"Você precisa esperar mais `{tempo_restante} segundos` para usar este comando novamente.",
                color=discord.Color.gold()
            )
            await ctx.send(embed=embed, delete_after=10)
        
        # Erro de Avatar (que corrigimos antes)
        elif isinstance(error, commands.CommandInvokeError) and isinstance(error.original, AttributeError) and "'NoneType' object has no attribute 'url'" in str(error.original):
            print("Erro de Avatar (NoneType) tratado. (Verifique comandos/utilidades.py)")
            # Não envia msg, pois já foi corrigido
            pass

        # Erro genérico
        else:
            print(f"Erro não tratado: {error}")
            try:
                embed = discord.Embed(
                    title="Ocorreu um Erro Inesperado",
                    description=f"Não foi possível executar o comando.\n```{error}```",
                    color=discord.Color.dark_red()
                )
                await ctx.send(embed=embed)
            except discord.errors.HTTPException:
                 await ctx.send(f"Ocorreu um erro inesperado: {error}")


async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))