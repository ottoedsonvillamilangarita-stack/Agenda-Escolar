# utils.py (ESTE ARCHIVO DEBE ESTAR EN LA RAÍZ, JUNTO A app.py)
import streamlit as st
import requests

# TUS CLAVES CORRECTAS
SUPABASE_URL = "https://qiiozstdvpohoxtxggim.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpaW96c3RkdnBvaG94dHhnZ2ltIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY4MjY3NzQsImV4cCI6MjA5MjQwMjc3NH0.0GznsyzaH3D211z7qm_1lNHVNVM0X0KvklCrF4z1BCE"

def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
