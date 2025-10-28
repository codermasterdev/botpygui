import json
import os
import datetime

DATA_DIR = "data"
PUNISH_FILE = f"{DATA_DIR}/punishments.json"

# Garante que a pasta 'data' e o arquivo .json existam
def setup_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(PUNISH_FILE):
        with open(PUNISH_FILE, 'w') as f:
            json.dump({}, f)

# Carrega os dados do JSON
def load_data():
    setup_data() # Garante que existe antes de ler
    try:
        with open(PUNISH_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {} # Retorna dict vazio se o JSON estiver corrompido/vazio

# Salva os dados no JSON
def save_data(data):
    with open(PUNISH_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Adiciona uma nova punição
def add_punishment(guild_id, user_id, mod_id, p_type, reason):
    data = load_data()
    guild_id_str = str(guild_id)
    user_id_str = str(user_id)

    if guild_id_str not in data:
        data[guild_id_str] = {}
    if user_id_str not in data[guild_id_str]:
        data[guild_id_str][user_id_str] = []

    new_punishment = {
        "type": p_type,
        "reason": reason,
        "moderator": mod_id,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    
    data[guild_id_str][user_id_str].append(new_punishment)
    save_data(data)
    return new_punishment

# Pega todas as punições de um usuário
def get_punishments(guild_id, user_id, p_type=None):
    data = load_data()
    guild_id_str = str(guild_id)
    user_id_str = str(user_id)

    if guild_id_str not in data or user_id_str not in data[guild_id_str]:
        return []

    user_data = data[guild_id_str][user_id_str]

    if p_type:
        return [p for p in user_data if p['type'].lower() == p_type.lower()]
    
    return user_data

# Remove a última advertência (warn)
def remove_last_warn(guild_id, user_id):
    data = load_data()
    guild_id_str = str(guild_id)
    user_id_str = str(user_id)

    if guild_id_str not in data or user_id_str not in data[guild_id_str]:
        return False # Usuário não tem punições

    user_punishments = data[guild_id_str][user_id_str]
    
    # Encontra o último warn e remove
    for i in range(len(user_punishments) - 1, -1, -1):
        if user_punishments[i]['type'].lower() == 'warn':
            user_punishments.pop(i)
            save_data(data)
            return True # Warn removido
            
    return False # Nenhum warn encontrado