# Bot Discord - Python

Bot de Discord desenvolvido em Python com sistema modular de comandos.

## 📁 Estrutura do Projeto

```
.
├── bot.py              # Arquivo principal (inicializador)
├── comandos/           # Pasta com os comandos do bot
│   ├── __init__.py
│   ├── ping.py        # Comando de ping
│   ├── ajuda.py       # Comando de ajuda
│   └── info.py        # Informações do bot
├── requirements.txt    # Dependências do projeto
├── .env.example       # Exemplo de arquivo de configuração
└── README.md          # Este arquivo
```

## 🚀 Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure o token no arquivo `bot.py` (já configurado) ou use variáveis de ambiente

## ▶️ Executar o Bot

```bash
python bot.py
```

## 🎮 Comandos Disponíveis

- `r!ping` - Mostra a latência do bot
- `r!ajuda` - Lista todos os comandos disponíveis
- `r!info` - Mostra informações sobre o bot

## ✨ Funcionalidades

- **Prefix**: `r!`
- **Status**: "Em desenvolvimento"
- **Responde a menções**: Quando mencionado, responde "Em que posso te ajudar?"
- **Não responde em privado**: O bot ignora mensagens diretas
- **Sistema modular**: Comandos organizados na pasta `comandos/`

## 📝 Como Adicionar Novos Comandos

1. Crie um novo arquivo `.py` na pasta `comandos/`
2. Use a estrutura de Cog do discord.py:

```python
from discord.ext import commands
import discord

class MeuComando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='meucomando', help='Descrição do comando')
    async def meu_comando(self, ctx):
        await ctx.send("Olá!")

async def setup(bot):
    await bot.add_cog(MeuComando(bot))
```

3. O bot carregará automaticamente o novo comando ao iniciar

## ⚠️ Segurança

**IMPORTANTE**: Nunca compartilhe seu token publicamente! Para maior segurança, use variáveis de ambiente.

## 📚 Requisitos

- Python 3.8+
- discord.py 2.3.0+
