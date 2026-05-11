import requests

# ======================================================
# CONFIGURACIÓN DE SUPABASE (CAMBIA ESTOS VALORES)
# ======================================================
SUPABASE_URL = "https://gpprggvygfempevfzjhi.supabase.co/rest/v1/"  # <-- Pega tu URL aquí
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpaW96c3RkdnBvaG94dHhnZ2ltIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY4MjY3NzQsImV4cCI6MjA5MjQwMjc3NH0.0GznsyzaH3D211z7qm_1lNHVNVM0X0KvklCrF4z1BCE"  # <-- Pega tu anon key aquí
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
