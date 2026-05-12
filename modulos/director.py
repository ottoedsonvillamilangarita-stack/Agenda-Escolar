import streamlit as st
import requests
from utils import get_headers, SUPABASE_URL

def mostrar(data):
    st.title("🧭 Director de Grupo")
    
    headers = get_headers()
    
    # Obtener datos actualizados
    url = f"{SUPABASE_URL}/rest/v1/personas?id_persona=eq.{data['id_persona']}"
    response = requests.get(url, headers=headers)
    director = response.json()[0] if response.status_code == 200 else data
    
    # Obtener username
    url_user = f"{SUPABASE_URL}/rest/v1/usuarios_login?id_persona=eq.{data['id_persona']}"
    response_user = requests.get(url_user, headers=headers)
    username = response_user.json()[0]["username"] if response_user.json() else None
    
    usuario_completo = {
        "id_persona": director["id_persona"],
        "nombre": director["nombre"],
        "email": director.get("email"),
        "telefono": director.get("telefono"),
        "username": username
    }
    
    tab_perfil, tab_grupo = st.tabs(["👤 Mi Perfil", "🧭 Mi Grupo"])
    
    with tab_perfil:
        mostrar_perfil(usuario_completo)
    
    with tab_grupo:
        st.subheader("Estudiantes del Grupo")
        
        # Obtener grupo del director
        url_grupo = f"{SUPABASE_URL}/rest/v1/directores_grupo?id_docente=eq.{data['id_persona']}"
        response_grupo = requests.get(url_grupo, headers=headers)
        
        if response_grupo.status_code == 200 and response_grupo.json():
            grado_id = response_grupo.json()[0]["id_grado"]
            
            # Obtener estudiantes del grupo
            url_estudiantes = f"{SUPABASE_URL}/rest/v1/estudiantes_grados?id_grado=eq.{grado_id}"
            response_est = requests.get(url_estudiantes, headers=headers)
            
            if response_est.status_code == 200 and response_est.json():
                for est_rel in response_est.json():
                    id_estudiante = est_rel["id_estudiante"]
                    url_est = f"{SUPABASE_URL}/rest/v1/personas?id_persona=eq.{id_estudiante}"
                    resp_est = requests.get(url_est, headers=headers)
                    if resp_est.status_code == 200 and resp_est.json():
                        estudiante = resp_est.json()[0]
                        st.write(f"• {estudiante['nombre']}")
            else:
                st.info("No hay estudiantes en este grupo")
        else:
            st.warning("No tienes un grupo asignado")
