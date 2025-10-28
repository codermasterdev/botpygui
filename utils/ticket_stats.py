import json
import os

DATA_DIR = "data"
STATS_FILE = f"{DATA_DIR}/ticket_stats.json"

def setup_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'w') as f:
            json.dump({}, f)

def load_stats():
    setup_data()
    try:
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_stats(data):
    with open(STATS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def add_stat(guild_id, staff_id, stat_type):
    """ stat_type pode ser 'resolvidos' ou 'cancelados' """
    stats = load_stats()
    guild_id_str = str(guild_id)
    staff_id_str = str(staff_id)

    if guild_id_str not in stats:
        stats[guild_id_str] = {}
    if staff_id_str not in stats[guild_id_str]:
        stats[guild_id_str][staff_id_str] = {"resolvidos": 0, "cancelados": 0}
    
    if stat_type in stats[guild_id_str][staff_id_str]:
        stats[guild_id_str][staff_id_str][stat_type] += 1
    
    save_stats(stats)

def get_guild_stats(guild_id):
    stats = load_stats()
    guild_id_str = str(guild_id)
    return stats.get(guild_id_str, {})