import streamlit as st
import requests
from utils import get_headers, SUPABASE_URL


def mostrar(data):
    st.title("🍎 Panel del Docente")
    
    headers = get_headers()
    
    # Obtener datos actualizados
    url = f"{SUPABASE_URL}/rest/v1/personas?id_persona=eq.{data['id_persona']}"
    response = requests.get(url, headers=headers)
    docente = response.json()[0] if response.status_code == 200 else data
    
    # Obtener username
    url_user = f"{SUPABASE_URL}/rest/v1/usuarios_login?id_persona=eq.{data['id_persona']}"
    response_user = requests.get(url_user, headers=headers)
    username = response_user.json()[0]["username"] if response_user.json() else None
    
    usuario_completo = {
        "id_persona": docente["id_persona"],
        "nombre": docente["nombre"],
        "email": docente.get("email"),
        "telefono": docente.get("telefono"),
        "username": username
    }
    
    tab_perfil, tab_cursos = st.tabs(["👤 Mi Perfil", "📚 Mis Cursos"])
    
    with tab_perfil:
        mostrar_perfil(usuario_completo)
    
    with tab_cursos:
        st.subheader("Mis Cursos")
        st.write("Próximamente: lista de cursos asignados")
