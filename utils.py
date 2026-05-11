import requests

# ======================================================
# CONFIGURACIÓN DE SUPABASE (CAMBIA ESTOS VALORES)
# ======================================================
SUPABASE_URL = "https://qiiozstdvpohoxtxggim.supabase.co"  # <-- Pega tu URL aquí
SUPABASE_KEY = "sb_publishable_MeqREZhTFQ54Ex4ajoQ_Rw_KaqTd_o6"  # <-- Pega tu anon key aquí
# ======================================================

def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

def consultar_supabase(tabla, filtros=None):
    url = f"{SUPABASE_URL}/rest/v1/{tabla}"
    headers = get_headers()
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return []
