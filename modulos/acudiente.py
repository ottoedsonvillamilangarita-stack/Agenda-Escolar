import streamlit as st
import requests
from utils import get_headers, SUPABASE_URL
from perfil import mostrar_perfil

def mostrar(data):
    st.title("👨‍👩‍👧 Panel del Acudiente")
    
    headers = get_headers()
    
    # Obtener datos actualizados
    url = f"{SUPABASE_URL}/rest/v1/personas?id_persona=eq.{data['id_persona']}"
    response = requests.get(url, headers=headers)
    acudiente = response.json()[0] if response.status_code == 200 else data
    
    # Obtener username
    url_user = f"{SUPABASE_URL}/rest/v1/usuarios_login?id_persona=eq.{data['id_persona']}"
    response_user = requests.get(url_user, headers=headers)
    username = response_user.json()[0]["username"] if response_user.json() else None
    
    usuario_completo = {
        "id_persona": acudiente["id_persona"],
        "nombre": acudiente["nombre"],
        "email": acudiente.get("email"),
        "telefono": acudiente.get("telefono"),
        "username": username
    }
    
    tab_perfil, tab_hijos = st.tabs(["👤 Mi Perfil", "👨‍👩‍👧 Mis Hijos"])
    
    with tab_perfil:
        mostrar_perfil(usuario_completo)
    
    with tab_hijos:
        st.subheader("Mis Hijos")
        
        # Obtener hijos del acudiente
        url_hijos = f"{SUPABASE_URL}/rest/v1/estudiantes_acudientes?id_acudiente=eq.{data['id_persona']}"
        response_hijos = requests.get(url_hijos, headers=headers)
        
        if response_hijos.status_code == 200 and response_hijos.json():
            for hijo_rel in response_hijos.json():
                id_estudiante = hijo_rel["id_estudiante"]
                url_est = f"{SUPABASE_URL}/rest/v1/personas?id_persona=eq.{id_estudiante}"
                resp_est = requests.get(url_est, headers=headers)
                if resp_est.status_code == 200 and resp_est.json():
                    estudiante = resp_est.json()[0]
                    st.write(f"• **{estudiante['nombre']}** (Documento: {estudiante.get('documento', 'N/A')})")
        else:
            st.info("No hay hijos registrados")
