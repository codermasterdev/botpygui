import json
import os
import locale

DATA_DIR = "data"
VENDAS_FILE = f"{DATA_DIR}/vendas_data.json"

# Configura o locale para formatar moeda (opcional, mas recomendado)
try:
    # Tenta configurar para Português do Brasil no Windows/Linux
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252') # Windows fallback
    except locale.Error:
        print("Aviso: Locale 'pt_BR.UTF-8' ou 'Portuguese_Brazil.1252' não encontrado. Usando formatação de preço padrão.")
        # Fallback manual simples se locale falhar
        def format_price_manual(price_float: float) -> str:
             return f"R$ {price_float:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
        format_price_locale = format_price_manual
else:
    # Usa a formatação do locale se funcionou
    def format_price_locale(price_float: float) -> str:
        # currency() adiciona R$ e formata corretamente
        return locale.currency(price_float, grouping=True, symbol='R$ ')

# Garante que a pasta 'data' e o arquivo .json existam
def _setup_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(VENDAS_FILE):
        with open(VENDAS_FILE, 'w') as f:
            # Estrutura: {guild_id: {'products': [], 'payments': []}}
            json.dump({}, f)

# Carrega os dados do JSON
def load_data():
    _setup_data()
    try:
        with open(VENDAS_FILE, 'r') as f:
            data = json.load(f)
            # Converte chaves de guild_id para int
            return {int(gid): gdata for gid, gdata in data.items()}
    except (json.JSONDecodeError, ValueError):
        return {}

# Salva os dados no JSON
def save_data(data):
    with open(VENDAS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- Funções de Produto ---

def add_product(guild_id: int, name: str, price_float: float):
    data = load_data()
    if guild_id not in data:
        data[guild_id] = {'products': [], 'payments': []}
    
    # Verifica se o produto já existe (pelo nome, case-insensitive)
    for i, prod in enumerate(data[guild_id].get('products', [])):
        if prod['name'].lower() == name.lower():
            # Atualiza o preço se já existe
            data[guild_id]['products'][i]['price'] = price_float
            save_data(data)
            return False # Indica que atualizou

    # Adiciona novo produto
    data[guild_id].setdefault('products', []).append({'name': name, 'price': price_float})
    save_data(data)
    return True # Indica que adicionou

def remove_product(guild_id: int, name: str) -> bool:
     data = load_data()
     if guild_id not in data or 'products' not in data[guild_id]:
         return False

     initial_len = len(data[guild_id]['products'])
     data[guild_id]['products'] = [p for p in data[guild_id]['products'] if p['name'].lower() != name.lower()]

     if len(data[guild_id]['products']) < initial_len:
          save_data(data)
          return True # Removeu
     return False # Não encontrou

def get_products(guild_id: int) -> list[dict]:
    data = load_data()
    return data.get(guild_id, {}).get('products', [])

# --- Funções de Pagamento ---

def add_payment(guild_id: int, type: str, description: str):
    data = load_data()
    if guild_id not in data:
        data[guild_id] = {'products': [], 'payments': []}

    # Verifica se o tipo já existe (case-insensitive)
    for i, pay in enumerate(data[guild_id].get('payments', [])):
        if pay['type'].lower() == type.lower():
            # Atualiza a descrição
            data[guild_id]['payments'][i]['description'] = description
            save_data(data)
            return False # Indica que atualizou

    # Adiciona novo método
    data[guild_id].setdefault('payments', []).append({'type': type, 'description': description})
    save_data(data)
    return True # Indica que adicionou

def remove_payment(guild_id: int, type: str) -> bool:
     data = load_data()
     if guild_id not in data or 'payments' not in data[guild_id]:
         return False

     initial_len = len(data[guild_id]['payments'])
     data[guild_id]['payments'] = [p for p in data[guild_id]['payments'] if p['type'].lower() != type.lower()]

     if len(data[guild_id]['payments']) < initial_len:
          save_data(data)
          return True # Removeu
     return False # Não encontrou

def get_payments(guild_id: int) -> list[dict]:
    data = load_data()
    return data.get(guild_id, {}).get('payments', [])

# --- Função de Formatação de Preço ---
def format_price(price_float: float) -> str:
    """ Formata um float para a string de moeda BRL (ex: R$ 1.234,50) """
    return format_price_locale(price_float)

def parse_price(price_str: str) -> float | None:
    """ Tenta converter uma string (ex: '10,50', '1.000', 'R$ 10.5') para float. """
    try:
        # Remove R$, espaços e troca vírgula por ponto
        cleaned_price = price_str.replace("R$", "").strip().replace(".", "").replace(",", ".")
        return float(cleaned_price)
    except ValueError:
        return None