import json
import os

DATA_DIR = "data"
SETTINGS_FILE = f"{DATA_DIR}/settings.json"

# Garante que a pasta 'data' e o arquivo .json existam
def setup_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'w') as f:
            json.dump({}, f)

# Carrega as configurações do JSON
def load_settings():
    setup_data() # Garante que existe antes de ler
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {} # Retorna dict vazio se o JSON estiver corrompido/vazio

# Salva as configurações no JSON
def save_settings(data):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Define uma configuração (canal, categoria, etc.)
def set_setting(guild_id, setting_key, value):
    data = load_settings()
    guild_id_str = str(guild_id)

    if guild_id_str not in data:
        data[guild_id_str] = {}

    data[guild_id_str][setting_key] = value
    save_settings(data)

# Pega uma configuração
def get_setting(guild_id, setting_key):
    data = load_settings()
    guild_id_str = str(guild_id)

    if guild_id_str not in data:
        return None
    
    return data[guild_id_str].get(setting_key) # Retorna None se a key não existir