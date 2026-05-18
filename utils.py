import requests
import streamlit as st

# ======================================================
# CONFIGURACIÓN DE SUPABASE (CAMBIA ESTOS VALORES)
# ======================================================
SUPABASE_URL = "https://qiiozstdvpohoxtxggim.supabase.co"  # <-- Pega tu URL aquí
SUPABASE_KEY = "sb_publishable_MeqREZhTFQ54Ex4ajoQ_Rw_KaqTd_o6"  # <-- Pega tu anon key aquí
# ======================================================

def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
         "Content-Type": "application/json"
    }
