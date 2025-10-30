import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv # <-- Adicionada esta linha

# --- ADICIONADO: Importa as Views do sistema de tickets ---
from comandos.ticket_system import TicketOpenView, TicketManageView
# --------------------------------------------------------

# --- ADICIONADO: Importa as Views do sistema de recrutamento ---
from comandos.recrutamento_system import RecrutamentoStartView, RecrutamentoReviewView
# -----------------------------------------------------------

# --- ADICIONADO: Importa as Views do sistema de bate-ponto ---
from comandos.ponto_system import PontoControlView, PontoState # Adicionado PontoState
# ---------------------------------------------------------

# --- ADICIONADO: Importa as Views do sistema de Vendas ---
from comandos.vendas_system import VendasProductSelectView, VendasCloseView
# ------------------------------------------------------

load_dotenv() # <-- Adicionada esta linha para carregar o .env

# Configurações do bot carregadas do .env
TOKEN = os.getenv("TOKEN") # <-- Modificada esta linha
PREFIX = os.getenv("PREFIX") or "r!" # <-- Modificada esta linha (com valor padrão "r!")

# Verifica se o TOKEN foi carregado
if TOKEN is None:
    print("ERRO CRÍTICO: O TOKEN do bot não foi encontrado no arquivo .env!")
    exit() # Impede o bot de iniciar sem token

# Intents necessários
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.dm_messages = True # Necessário para ler DMs do recrutamento
intents.voice_states = True # <-- ADICIONADO PARA O BATE-PONTO

# Inicializar o bot
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# --- ADICIONADO: Dicionários para estados ativos ---
bot.pending_recruitments = set()
bot.active_pontos = {} # <-- ADICIONADO PARA O BATE-PONTO {user_id: PontoState}
# ----------------------------------------------------

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

    # NÃO ignorar mais em DM, pois o questionário precisa
    # (O bot.wait_for cuidará de ler a DM correta)

    # Responder quando mencionado (apenas em guilds)
    if not isinstance(message.channel, discord.DMChannel) and bot.user in message.mentions:
        await message.channel.send(f'{message.author.mention} Em que posso te ajudar?')

    # Processar comandos (apenas em guilds)
    if not isinstance(message.channel, discord.DMChannel):
        await bot.process_commands(message)

# Carregar comandos da pasta comandos
async def load_commands():
    # --- ATUALIZADO: Lista de arquivos a serem ignorados ---
    ignore_files = [
        '__init__.py', 
        'ticket_system.py', 
        'recrutamento_system.py', 
        'ponto_system.py',
        'vendas_system.py' # <-- Adicionado
    ]
    # -----------------------------------------------------
    
    for filename in os.listdir('./comandos'):
        if filename.endswith('.py') and filename not in ignore_files: # <-- Verifica se NÃO está na lista
            try:
                await bot.load_extension(f'comandos.{filename[:-3]}')
                print(f'Comando {filename} carregado com sucesso!')
            except Exception as e:
                print(f'Erro ao carregar {filename}: {e}')

# Função principal
async def main():
    
    # --- ADICIONADO: Registra as Views persistentes ANTES do bot iniciar ---
    # Sistema de Tickets
    bot.add_view(TicketOpenView())
    bot.add_view(TicketManageView())
    
    # Sistema de Recrutamento
    bot.add_view(RecrutamentoStartView())
    bot.add_view(RecrutamentoReviewView())

    # Sistema de Bate-Ponto
    bot.add_view(PontoControlView())
    
    # Sistema de Vendas (NOVO)
    bot.add_view(VendasProductSelectView())
    bot.add_view(VendasCloseView())
    # --------------------------------------------------------------------

    async with bot:
        await load_commands()
        await bot.start(TOKEN)

# Executar o bot
if __name__ == "__main__":
    asyncio.run(main())