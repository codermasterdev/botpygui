# Bot Discord Modular - RPG Bot (Nome Sugerido)

Bem-vindo ao RPG Bot, um bot modular para Discord desenvolvido em Python usando a biblioteca `discord.py` \[cite: requirements.txt\]. Este bot oferece uma ampla gama de funcionalidades de moderação, administração, utilidade e um sistema avançado de tickets, tudo configurável por servidor e com um sistema de permissões baseado em cargos.

## 📁 Estrutura do Projeto

```
.
├── bot.py              # Arquivo principal (inicializador)
├── comandos/           # Pasta com os comandos modulares (Cogs)
│   ├── __init__.py     # Marcador Python (ignorado pelo bot)
│   ├── admin.py        # Comandos de configuração de canais
│   ├── ajuda.py        # Comando de ajuda interativo
│   ├── autorole.py     # Sistema de cargo automático para novos membros
│   ├── avatar.py       # Comando para exibir avatar
│   ├── enquete.py      # Comando para criar enquetes
│   ├── erros.py        # Gerenciador global de erros de comando
│   ├── eventos.py      # Listeners para entrada/saída de membros
│   ├── infousuario.py  # Comando para exibir informações do usuário
│   ├── kick.py         # Comando para expulsar membros
│   ├── limpar.py       # Comando para apagar mensagens
│   ├── moderacao.py    # Comandos principais de moderação (ban, warn, mutar, etc.)
│   ├── permissoes.py   # Comandos para definir cargos (Admin, Mod, Staff)
│   ├── recarregar.py   # Comando para recarregar módulos (apenas dono do bot)
│   ├── serverinfo.py   # Comando para exibir informações do servidor
│   ├── ticket_system.py # Lógica interna do sistema de tickets (Views e Botões)
│   ├── ticketranking.py # Comando para exibir ranking de tickets da staff
│   ├── ticketsetup.py  # Comando para configurar o painel de tickets
│   ├── unban.py        # Comando para desbanir membros
│   └── utilidades.py   # Comandos diversos (anuncio, sugestao, divulgar)
├── utils/              # Pasta com módulos de utilidade interna
│   ├── checks.py       # Funções de verificação de permissão (is_admin, is_mod, is_staff)
│   ├── data_manager.py # Gerenciador do histórico de punições (data/punishments.json)
│   ├── settings_manager.py # Gerenciador das configurações do servidor (data/settings.json)
│   └── ticket_stats.py # Gerenciador das estatísticas de ticket (data/ticket_stats.json)
├── data/               # Pasta onde os dados JSON são armazenados (criada automaticamente)
│   ├── punishments.json # Histórico de punições
│   ├── settings.json   # Configurações dos servidores
│   └── ticket_stats.json # Estatísticas de tickets
├── requirements.txt    # Dependências do projeto
└── .env                # Arquivo para configurar o token e prefixo

```

## ✨ Funcionalidades Principais

* **Prefix Padrão**: `r!` (Configurável no arquivo `.env`) \[cite: .env\].

* **Modularidade (Cogs)**: Comandos organizados em arquivos `.py` na pasta `comandos/`, facilitando a manutenção e adição de novas funcionalidades \[cite: bot.py\].

* **Configuração por Servidor**: A maioria das funcionalidades precisa ser configurada individualmente para cada servidor via comandos administrativos. As configurações são salvas em `data/settings.json` \[cite: utils/settings_manager.py\].

* **Sistema de Permissões Flexível**:

  * **Admin Roles**: Cargos definidos com `r!setadminrole` têm acesso aos comandos de configuração \[cite: comandos/permissoes.py, utils/checks.py\].

  * **Mod Roles**: Cargos definidos com `r!setmodrole` têm acesso aos comandos de moderação \[cite: comandos/permissoes.py, utils/checks.py\].

  * **Staff Roles**: Cargos definidos com `r!setstaffrole` podem gerenciar o sistema de tickets \[cite: comandos/permissoes.py, utils/checks.py\].

  * **Padrão**: Donos do Servidor e membros com a permissão "Administrador" do Discord sempre podem usar *todos* os comandos do bot \[cite: utils/checks.py\].

* **Sistema de Tickets Avançado**:

  * Painel de abertura interativo com categorias personalizáveis (`r!ticketsetup`) \[cite: comandos/ticketsetup.py\].

  * Criação de canais privados para cada ticket, com permissões para o usuário e a Staff \[cite: comandos/ticket_system.py\].

  * Botões ("Concluir", "Bloquear", "Deletar") para gerenciamento pela Staff dentro do canal do ticket \[cite: comandos/ticket_system.py\].

  * Ranking de Staff (`r!ticketranking`) baseado em tickets resolvidos/cancelados \[cite: comandos/ticketranking.py, utils/ticket_stats.py\].

* **Moderação Completa**: Comandos `ban`, `unban`, `kick`, `mutar` (timeout), `warn` (com sistema de 3 avisos = ban), `unwarn`, `listarpunicoes`, `bloquearchat`, `desbloquearchat`, `limpar` \[cite: comandos/moderacao.py, comandos/kick.py, comandos/unban.py, comandos/limpar.py\]. Histórico de punições salvo em `data/punishments.json` \[cite: utils/data_manager.py\].

* **Automatização**:

  * Mensagens automáticas de boas-vindas e saída (`r!setbemvindo`, `r!setadeus`) \[cite: comandos/eventos.py, comandos/admin.py\].

  * Sistema de Autorole para dar um cargo automaticamente a novos membros (`r!setautorole`) \[cite: comandos/autorole.py\].

* **Utilidades**: Comandos `anuncio`, `sugestao` (com reações 👍/👎), `divulgar` (com cooldown), `ping`, `infousuario`, `serverinfo`, `avatar`, `enquete` \[cite: comandos/utilidades.py, comandos/infousuario.py, comandos/serverinfo.py, comandos/avatar.py, comandos/enquete.py\].

* **Ajuda Interativa**: Comando `r!ajuda` com menu dropdown para navegar pelas categorias de comandos \[cite: comandos/ajuda.py\].

* **Tratamento de Erros**: Mensagens claras para uso incorreto, falta de permissão ou cooldowns, com exemplos de uso correto \[cite: comandos/erros.py\].

* **Persistência**: Dados importantes (configurações, punições, stats) são salvos em JSON, sobrevivendo a reinicializações \[cite: utils/settings_manager.py, utils/data_manager.py, utils/ticket_stats.py\].

* **Desenvolvimento**: Comando `r!recarregar` (apenas para o dono do bot) permite atualizar os comandos sem reiniciar o bot \[cite: comandos/recarregar.py\].

## 🚀 Instalação e Execução

1. **Pré-requisitos**: Python 3.8+ instalado.

2. **Clone o Repositório**: Baixe ou clone todos os arquivos do projeto.

3. **Instale as Dependências**: Abra um terminal na pasta do projeto e execute:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o `.env`**:

   * Renomeie (ou crie) o arquivo `.env.example` para `.env`.

   * Abra o arquivo `.env` e substitua `seu_token_aqui` pelo token do seu bot \[cite: .env\].

   * (Opcional) Altere o `PREFIX` se desejar \[cite: .env\].

   * **NUNCA COMPARTILHE SEU TOKEN!**

5. **Execute o Bot**: No mesmo terminal, execute:

   ```bash
   python bot.py
   ```

6. **Primeira Execução**: A pasta `data/` e os arquivos `.json` serão criados automaticamente se não existirem.

## ⚙️ Configuração Inicial Obrigatória (por Servidor)

**IMPORTANTE**: Para que o bot funcione corretamente, um **Administrador** (Dono do Servidor ou alguém com a permissão "Administrador" do Discord) precisa configurar os seguintes itens **em cada servidor** onde o bot for adicionado:

1.  **Cargos de Permissão (Recomendado)**:
    * `r!setadminrole @CargoAdmin`: Define quem pode usar os comandos de configuração. Pode adicionar vários cargos.
    * `r!setmodrole @CargoMod`: Define quem pode usar os comandos de moderação. Pode adicionar vários cargos. Admins também podem usar.
    * `r!setstaffrole @CargoStaff`: Define quem pode gerenciar tickets. Pode adicionar vários cargos. Admins também podem usar.
2.  **Canal de Logs**:
    * `r!setlogs #canal-de-logs`: Define onde as ações de moderação (ban, kick, warn, etc.) serão registradas. **Necessário para os comandos de moderação funcionarem.**
3.  **Sistema de Tickets (Opcional, mas recomendado)**:
    * `r!setticketcategory NomeDaCategoria`: **(Opcional, mas recomendado)** Cria ou define a *Categoria* do Discord onde os canais de ticket serão criados. Se não definida, tentará criar uma "Tickets".
    * `r!ticketsetup #canal-abertura Categoria1 Categoria2 ...`: Cria o painel interativo no canal especificado, com até 4 categorias para os usuários escolherem ao abrir um ticket.
4.  **Outros Canais (Opcional)**:
    * `r!setbemvindo #canal-boasvindas`: Para mensagens de entrada.
    * `r!setadeus #canal-saidas`: Para mensagens de saída.
    * `r!setsugestoes #canal-sugestoes`: Para o comando `r!sugestao`.
    * `r!setdivulgacao #canal-divulgacao`: Para o comando `r!divulgar`.
5.  **Autorole (Opcional)**:
    * `r!setautorole @CargoInicial`: Define um cargo a ser dado automaticamente a novos membros.
    * `r!setautorole remover`: Desativa o cargo automático.

## 🎮 Comandos Disponíveis

Use `r!ajuda` no Discord para ver a lista interativa e atualizada.

**Categorias Principais:**

* **Administração (`@is_admin()` ou Permissão Discord)**:
    * `setlogs`, `setbemvindo`, `setadeus`, `setsugestoes`, `setdivulgacao`, `setticketcategory`, `ticketsetup`, `setautorole`, `setadminrole`, `setmodrole`, `setstaffrole`.
* **Moderação (`@is_mod()` ou superior)**:
    * `ban`, `unban`, `kick`, `mutar`, `warn`, `unwarn`, `listarpunicoes`, `bloquearchat`, `desbloquearchat`, `limpar`.
* **Tickets (Abertura: Todos / Gerenciamento: `@is_staff()` ou superior)**:
    * *Abertura*: Interação via painel criado pelo `ticketsetup`.
    * *Gerenciamento*: Botões "Concluir", "Bloquear", "Deletar" dentro do canal do ticket.
    * `ticketranking`: Mostra o ranking da staff (acessível por todos, mas útil para staff/admins).
* **Utilidades (Acessível por Todos, exceto `anuncio`)**:
    * `anuncio` (`@is_admin()` ou Permissão Discord): Envia anúncio em canal específico.
    * `sugestao`: Envia sugestão para o canal configurado.
    * `divulgar`: Envia divulgação no canal configurado (com cooldown).
    * `infousuario`: Mostra informações sobre um membro.
    * `serverinfo`: Mostra informações sobre o servidor.
    * `avatar`: Mostra o avatar de um membro.
    * `enquete`: Cria uma enquete Sim/Não.
* **Outros**:
    * `ping`: Mostra a latência do bot (Todos).
    * `recarregar` (**Apenas Dono do Bot**): Recarrega os módulos de comando.
    * `ajuda`: Mostra o painel de ajuda interativo (Todos).

## 📝 Como Adicionar Novos Comandos

1.  Crie um novo arquivo `.py` na pasta `comandos/`.
2.  Use a estrutura de Cog do `discord.py`, similar aos arquivos existentes (ex: `comandos/ping.py`).
3.  Defina as permissões usando os decorators `@is_admin()`, `@is_mod()`, `@is_staff()` (importados de `utils.checks`) ou deixe sem decorator para acesso público.
4.  Use `async def setup(bot): await bot.add_cog(NomeDaSuaClasse(bot))` no final do arquivo.
5.  O bot carregará o novo comando automaticamente na próxima inicialização ou ao usar `r!recarregar`.

## ⚠️ Segurança

* **NUNCA** compartilhe o seu `TOKEN` (do arquivo `.env` ou `bot.py`).
* Configure os cargos de Admin, Mod e Staff (`r!setadminrole`, etc.) cuidadosamente.
