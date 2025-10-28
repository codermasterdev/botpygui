import discord
from discord.ext import commands
import os
import asyncio

# Configurações do bot
TOKEN=seu_token_aqui
PREFIX=r!

# Intents necessários
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Inicializar o bot
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# Evento quando o bot estiver pronto
@bot.event
async def on_ready():
    print(f'{bot.user} está online!')
    print(f'ID: {bot.user.id}')
    print('------')

    # Definir status/atividade
    await bot.change_presence(
        activity=discord.Game(name="Em desenvolvimento"),
        status=discord.Status.online
    )

# Evento de mensagens
@bot.event
async def on_message(message):
    # Ignorar mensagens do próprio bot
    if message.author == bot.user:
        return

    # Não responder em DM/privado
    if isinstance(message.channel, discord.DMChannel):
        return

    # Responder quando mencionado
    if bot.user in message.mentions:
        await message.channel.send(f'{message.author.mention} Em que posso te ajudar?')

    # Processar comandos
    await bot.process_commands(message)

# Carregar comandos da pasta comandos
async def load_commands():
    for filename in os.listdir('./comandos'):
        if filename.endswith('.py') and not filename.startswith('__'):
            try:
                await bot.load_extension(f'comandos.{filename[:-3]}')
                print(f'Comando {filename} carregado com sucesso!')
            except Exception as e:
                print(f'Erro ao carregar {filename}: {e}')

# Função principal
async def main():
    async with bot:
        await load_commands()
        await bot.start(TOKEN)

# Executar o bot
if __name__ == "__main__":
    asyncio.run(main())
