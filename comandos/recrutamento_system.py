import discord
import asyncio
from discord.ext import commands
from utils import settings_manager
from utils.checks import is_admin, is_mod # Usaremos is_mod para a revisão

# --- Lista das 14 Perguntas ---
# (Você pode editar as perguntas aqui se precisar)
QUESTIONS = [
    "1º • Qual é seu ID?",
    "2º • Qual apelido você usa?",
    "3º • Qual é sua idada?",
    "4º • O que é Surf?",
    "5º • O que é Meta Gaming?",
    "6º • O que é Roleplay?",
    "7º • O que é Amor a vida?",
    "8º • O que é Anti Roleplay?",
    "9º • O que é Combat Log?",
    "10º • O que é Car Jacking?",
    "11º • O que é duplo Roleplay?",
    "12º • O que é RP Delicado?",
    "13º • Qual a diferença de RDM para VDM?",
    "14º • O que é proibido fazer?"
]

# --- 1. Botão "Iniciar" (Painel de Setup) ---
class RecrutamentoStartView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Persistente

    @discord.ui.button(label="Iniciar", style=discord.ButtonStyle.success, custom_id="recrutamento_iniciar")
    async def iniciar(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        bot = interaction.client

        # Pega o canal de logs
        log_channel_id = settings_manager.get_setting(interaction.guild.id, 'recrutamento_logs_channel')
        if not log_channel_id:
            await interaction.response.send_message("❌ O sistema de recrutamento não está configurado. Contate um Staff.", ephemeral=True)
            return

        log_channel = bot.get_channel(log_channel_id)
        if not log_channel:
            await interaction.response.send_message("❌ O canal de logs de recrutamento não foi encontrado. Contate um Staff.", ephemeral=True)
            return

        # Verifica se o usuário já está em um recrutamento
        if user.id in bot.pending_recruitments:
            await interaction.response.send_message("⚠️ Você já tem um formulário de recrutamento em andamento. Verifique suas DMs!", ephemeral=True)
            return

        # Adiciona à lista de pendentes e avisa
        bot.pending_recruitments.add(user.id)
        await interaction.response.send_message(f"✅ Olá {user.mention}! Seu recrutamento foi iniciado em suas **Mensagens Diretas (DMs)**. Verifique lá!", ephemeral=True)

        try:
            # Inicia o processo de questionário na DM
            await self.start_questionnaire(bot, user, log_channel)
        except Exception as e:
            print(f"Erro ao iniciar questionário para {user.name}: {e}")
            # Use followup here since response was already sent
            try:
                await interaction.followup.send("❌ Ocorreu um erro ao tentar te enviar a primeira pergunta. Verifique se suas DMs estão abertas!", ephemeral=True)
            except discord.HTTPException: # Handle cases where the initial interaction expired before the error happened
                 print(f"Não foi possível enviar followup de erro para {user.name}")
        finally:
            # Remove o usuário da lista de pendentes, seja por concluir ou falhar
            bot.pending_recruitments.discard(user.id)


    async def start_questionnaire(self, bot: commands.Bot, user: discord.Member, log_channel: discord.TextChannel):
        """ Envia o questionário sequencial via DM """
        answers = []

        try:
            dm_channel = await user.create_dm()

            embed = discord.Embed(
                title=f"📝 Formulário de Recrutamento - {log_channel.guild.name}",
                description=f"Olá {user.name}! Vamos começar.\nResponda as {len(QUESTIONS)} perguntas a seguir, uma de cada vez.\n\nVocê tem **5 minutos** para responder cada pergunta.",
                color=discord.Color.blue()
            )
            await dm_channel.send(embed=embed)

            for i, question_text in enumerate(QUESTIONS):
                q_embed = discord.Embed(
                    title=f"Pergunta {i+1}/{len(QUESTIONS)}",
                    description=question_text,
                    color=discord.Color.gold()
                )
                await dm_channel.send(embed=q_embed)

                # Espera pela resposta do usuário na DM
                message = await bot.wait_for(
                    "message",
                    check=lambda m: m.author == user and m.channel == dm_channel,
                    timeout=300.0  # 5 minutos
                )
                answers.append((question_text, message.content))

            # Finalizado
            success_embed = discord.Embed(
                title="✅ Formulário Concluído!",
                description="Obrigado! Suas respostas foram enviadas para a equipe.\nVocê será notificado em breve.",
                color=discord.Color.green()
            )
            await dm_channel.send(embed=success_embed)

        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="❌ Tempo Esgotado",
                description="Você demorou muito para responder. O formulário foi cancelado.\nVocê pode tentar novamente clicando no botão 'Iniciar' no servidor.",
                color=discord.Color.red()
            )
            try: # Try sending timeout message, might fail if DMs closed later
                await dm_channel.send(embed=timeout_embed)
            except discord.Forbidden:
                 print(f"Erro ao enviar msg de timeout para {user.name}: DM fechada.")
            return # Para de executar

        except discord.Forbidden:
            # Usuário está com a DM fechada desde o início
            print(f"Erro: DM fechada para {user.name}")
            return # Para de executar

        # Envia as respostas para o canal de logs
        log_embed = discord.Embed(
            title=f"Novo Recrutamento - {user.name}",
            color=discord.Color.light_grey()
        )
        log_embed.set_author(name=f"{user.name} ({user.id})", icon_url=user.display_avatar.url)
        log_embed.set_footer(text=f"UserID:{user.id}") # Guarda o ID para os botões

        for q, a in answers:
            # Limita o tamanho da resposta para caber no embed
            answer_text = a if len(a) < 1020 else a[:1020] + "..."
            log_embed.add_field(name=f"❓ {q}", value=f"```{answer_text}```", inline=False)

        await log_channel.send(embed=log_embed, view=RecrutamentoReviewView())


# --- 2. Modal para "Negar" ---
class RecrutamentoNegarModal(discord.ui.Modal, title="Negar Recrutamento"):
    motivo = discord.ui.TextInput(
        label="Motivo da Negação",
        style=discord.TextStyle.paragraph,
        placeholder="Explique por que o usuário foi negado...",
        required=True
    )

    def __init__(self, original_embed: discord.Embed, applicant_id: int):
        super().__init__()
        self.original_embed = original_embed
        self.applicant_id = applicant_id

    async def on_submit(self, interaction: discord.Interaction):
        # --- CORREÇÃO: Adicionado defer() e followup.send() ---
        await interaction.response.defer(ephemeral=True)
        # ---------------------------------------------------

        # Atualiza o embed original
        self.original_embed.title = f"Recrutamento NEGADO - {self.original_embed.author.name}"
        self.original_embed.color = discord.Color.red()
        self.original_embed.add_field(name="Revisado por", value=interaction.user.mention, inline=True)
        self.original_embed.add_field(name="Motivo", value=self.motivo.value, inline=False)

        # Desativa os botões da mensagem original
        await interaction.message.edit(embed=self.original_embed, view=None)

        # --- CORREÇÃO: Usar followup.send() ---
        await interaction.followup.send("Formulário negado.", ephemeral=True)
        # ------------------------------------

        # Tenta avisar o usuário na DM
        try:
            applicant = await interaction.guild.fetch_member(self.applicant_id)
            if applicant: # Verifica se o membro foi encontrado
                 dm_embed = discord.Embed(
                     title="❌ Recrutamento Negado",
                     description=f"Seu formulário para `{interaction.guild.name}` foi negado.\n**Motivo:** {self.motivo.value}",
                     color=discord.Color.red()
                 )
                 await applicant.send(embed=dm_embed)
        except discord.NotFound:
             print(f"Usuário {self.applicant_id} não encontrado no servidor para DM de negação.")
        except discord.Forbidden:
             print(f"Não foi possível enviar DM de negação para {self.applicant_id} (DM fechada ou bot bloqueado).")
        except Exception as e:
            print(f"Falha ao enviar DM de negação para {self.applicant_id}: {e}")


# --- 3. Botões "Aceitar" / "Negar" (Painel de Logs) ---
class RecrutamentoReviewView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Persistente

    async def _check_perms(self, interaction: discord.Interaction):
        # Apenas Admins ou Mods podem revisar
        # Verifica Admin
        is_admin_check = False
        try:
             # is_admin() retorna um decorator, precisamos pegar a função predicate
             # Nota: Isso assume que seu is_admin() em checks.py retorna commands.check(predicate)
             # Se for diferente, ajuste esta parte para chamar a função de verificação corretamente.
            if await commands.check(is_admin().predicate).predicate(interaction):
                 is_admin_check = True
        except Exception: # Captura ampla caso a estrutura de predicate mude
             # Se a checagem is_admin falhar por qualquer motivo (ex: cargo não configurado),
             # verifica as permissões nativas do Discord
             if interaction.user.guild_permissions.administrator:
                 is_admin_check = True

        if is_admin_check:
             return True

        # Verifica Mod
        is_mod_check = False
        try:
             # Mesmo raciocínio para is_mod()
             if await commands.check(is_mod().predicate).predicate(interaction):
                 is_mod_check = True
        except Exception:
             pass # Falha na checagem do Mod, não faz nada, pois pode ser admin

        if is_mod_check:
            return True

        # Se não for Admin nem Mod, envia a mensagem de erro
        # Só envie a mensagem se a interação não foi respondida ainda (evita erro)
        if not interaction.response.is_done():
            await interaction.response.send_message("Você não tem permissão (Admin/Mod) para revisar este formulário.", ephemeral=True)
        return False


    @discord.ui.button(label="Aceitar", style=discord.ButtonStyle.success, custom_id="recrutamento_aceitar")
    async def aceitar(self, interaction: discord.Interaction, button: discord.ui.Button):
        # --- CORREÇÃO: Adicionado defer() e followup.send() ---
        await interaction.response.defer(ephemeral=True)
        # ---------------------------------------------------

        # A checagem de permissão agora é mais robusta
        if not await self._check_perms(interaction):
            # A mensagem de erro já foi enviada em _check_perms se necessário
            return

        original_embed = interaction.message.embeds[0]

        # Pega o ID do usuário guardado no footer
        try:
            applicant_id = int(original_embed.footer.text.split(":")[-1])
        except:
            # --- CORREÇÃO: Usar followup.send() ---
            await interaction.followup.send("❌ Erro: Não foi possível extrair o ID do usuário do formulário.", ephemeral=True)
            return

        applicant = interaction.guild.get_member(applicant_id)
        if not applicant:
            # --- CORREÇÃO: Usar followup.send() ---
            await interaction.followup.send("❌ Erro: O usuário não está mais no servidor.", ephemeral=True)
            return

        # Pega a resposta da Pergunta 1 ("Qual é seu ID?")
        id_resposta = "ID não encontrado"
        for field in original_embed.fields:
            if field.name.startswith("❓ 1º"):
                # Remove os ``` do texto e limita o tamanho
                id_resposta = field.value.strip("`")[:30] # Limita ID a 30 chars no nick
                break

        # Tenta alterar o nick
        # Tenta pegar o nome original, se possível, para evitar nick acumulado
        nome_base = applicant.nick if applicant.nick else applicant.global_name if applicant.global_name else applicant.name
        nome_base = nome_base.split(" | ")[0] # Remove parte antiga se existir
        
        novo_nick = f"{nome_base} | {id_resposta}"
        # Limita o nick total a 32 caracteres (limite do Discord)
        if len(novo_nick) > 32:
             novo_nick = novo_nick[:32]
             
        try:
            await applicant.edit(nick=novo_nick)
        except discord.Forbidden:
            # --- CORREÇÃO: Usar followup.send() ---
            await interaction.followup.send(f"❌ Erro de Permissão: Não consegui alterar o nick de {applicant.mention}. Meu cargo é muito baixo.", ephemeral=True)
            return
        except Exception as e:
            # --- CORREÇÃO: Usar followup.send() ---
            await interaction.followup.send(f"❌ Erro ao alterar nick: {e}", ephemeral=True)
            return

        # Atualiza o embed original
        original_embed.title = f"Recrutamento APROVADO - {original_embed.author.name}"
        original_embed.color = discord.Color.green()
        original_embed.add_field(name="Revisado por", value=interaction.user.mention, inline=True)
        original_embed.add_field(name="Novo Nick", value=novo_nick, inline=True)

        await interaction.message.edit(embed=original_embed, view=None)

        # --- CORREÇÃO: Usar followup.send() ---
        await interaction.followup.send(f"Usuário {applicant.mention} aprovado e renomeado!", ephemeral=True)
        # ------------------------------------

        # Tenta avisar o usuário na DM
        try:
            dm_embed = discord.Embed(
                title="✅ Recrutamento Aprovado!",
                description=f"Parabéns! Seu formulário para `{interaction.guild.name}` foi aprovado.",
                color=discord.Color.green()
            )
            await applicant.send(embed=dm_embed)
        except Exception as e:
            print(f"Falha ao enviar DM de aprovação para {applicant_id}: {e}")

    @discord.ui.button(label="Negar", style=discord.ButtonStyle.danger, custom_id="recrutamento_negar")
    async def negar(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Não precisa de defer aqui, pois a resposta será o Modal
        
        # A checagem de permissão agora é mais robusta
        if not await self._check_perms(interaction):
            return

        original_embed = interaction.message.embeds[0]
        try:
            applicant_id = int(original_embed.footer.text.split(":")[-1])
        except:
             # Só envie a mensagem se a interação não foi respondida ainda
            if not interaction.response.is_done():
                await interaction.response.send_message("❌ Erro: Não foi possível extrair o ID do usuário do formulário.", ephemeral=True)
            return

        # Abre o Modal para pedir o motivo
        modal = RecrutamentoNegarModal(original_embed, applicant_id)
        await interaction.response.send_modal(modal)