import json
import os
import datetime
from collections import defaultdict

DATA_DIR = "data"
PONTO_FILE = f"{DATA_DIR}/ponto_records.json"

# Garante que a pasta 'data' e o arquivo .json existam
def _setup_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(PONTO_FILE):
        with open(PONTO_FILE, 'w') as f:
            # Estrutura: {guild_id: {user_id: {'total_seconds': 0, 'week_start_iso': 'YYYY-MM-DD', 'current_week_seconds': 0}}}
            json.dump({}, f)

# Carrega os registros do JSON
def load_records():
    _setup_data()
    try:
        with open(PONTO_FILE, 'r') as f:
            # Usar defaultdict para facilitar a criação de novas entradas
            data = json.load(f)
            # Convertendo chaves de volta para int (JSON salva como string)
            return {int(gid): {int(uid): val for uid, val in udata.items()}
                    for gid, udata in data.items()}
    except (json.JSONDecodeError, ValueError):
        return {} # Retorna dict vazio se corrompido ou vazio

# Salva os registros no JSON
def save_records(data):
    with open(PONTO_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Função helper para obter o início da semana (Segunda-feira)
def get_week_start():
    today = datetime.date.today()
    # weekday() retorna 0 para segunda, 6 para domingo
    start_of_week = today - datetime.timedelta(days=today.weekday())
    return start_of_week.isoformat() # Salva como string YYYY-MM-DD

# Adiciona tempo a um usuário
def add_time(guild_id: int, user_id: int, seconds: float):
    if seconds <= 0:
        return

    records = load_records()
    current_week_iso = get_week_start()
    seconds_int = int(seconds) # Armazenar como inteiros

    if guild_id not in records:
        records[guild_id] = {}
    
    user_data = records[guild_id].get(user_id, {
        'total_seconds': 0,
        'week_start_iso': current_week_iso,
        'current_week_seconds': 0
    })

    # Verifica se a semana mudou
    if user_data.get('week_start_iso') != current_week_iso:
        user_data['week_start_iso'] = current_week_iso
        user_data['current_week_seconds'] = seconds_int # Começa a nova semana
    else:
        user_data['current_week_seconds'] = user_data.get('current_week_seconds', 0) + seconds_int

    user_data['total_seconds'] = user_data.get('total_seconds', 0) + seconds_int
    
    records[guild_id][user_id] = user_data
    save_records(records)

# Pega o tempo total e semanal de um usuário
def get_user_times(guild_id: int, user_id: int) -> tuple[int, int]:
    records = load_records()
    user_data = records.get(guild_id, {}).get(user_id, None)
    
    if not user_data:
        return 0, 0 # Total, Semanal

    current_week_iso = get_week_start()
    # Reseta a contagem semanal se a semana mudou desde a última leitura/escrita
    if user_data.get('week_start_iso') != current_week_iso:
         # Salva o reset para futuras chamadas (opcional, mas bom)
        user_data['week_start_iso'] = current_week_iso
        user_data['current_week_seconds'] = 0
        records[guild_id][user_id] = user_data
        save_records(records)
        weekly_seconds = 0
    else:
        weekly_seconds = user_data.get('current_week_seconds', 0)

    total_seconds = user_data.get('total_seconds', 0)
    return total_seconds, weekly_seconds

# Pega todos os registros semanais de um servidor para o ranking
def get_weekly_guild_records(guild_id: int) -> dict[int, int]:
    records = load_records()
    guild_records = records.get(guild_id, {})
    current_week_iso = get_week_start()
    
    weekly_data = {}
    needs_save = False
    for user_id, user_data in guild_records.items():
        if user_data.get('week_start_iso') != current_week_iso:
             # Reseta e não inclui no ranking desta semana ainda
            guild_records[user_id]['week_start_iso'] = current_week_iso
            guild_records[user_id]['current_week_seconds'] = 0
            needs_save = True
        else:
            weekly_data[user_id] = user_data.get('current_week_seconds', 0)

    if needs_save:
         save_records(records) # Salva os resets
         
    return weekly_data

# Função para formatar segundos em H:M:S
def format_seconds(seconds: int) -> str:
    if seconds < 0: seconds = 0
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"