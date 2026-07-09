import streamlit as st
import requests
from utils import SUPABASE_URL, get_headers
from modulos import login, estudiante, docente, acudiente, director, coordinador, secretaria, supervisor, admin
from modulos.mobile_utils import es_movil, aplicar_css_movil

# Configuración según dispositivo
ES_MOVIL = es_movil()

if ES_MOVIL:
    st.set_page_config(page_title="Plataforma Escolar", layout="centered", initial_sidebar_state="collapsed")
    aplicar_css_movil()
else:
    st.set_page_config(page_title="Plataforma Escolar", layout="wide")

# Inicializar session_state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login.mostrar()
else:
    # =============================================
    # ACTUALIZAR ROLES DESDE LA BASE DE DATOS
    # =============================================
    username = st.session_state.usuario
    headers = get_headers()
    
    url = f"{SUPABASE_URL}/rest/v1/usuarios_login?username=eq.{username}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200 and response.json():
        user_data = response.json()[0]
        st.session_state.user_data['roles'] = user_data.get('roles', [])
        st.session_state.user_data['rol'] = user_data.get('rol', '')
        
        if st.session_state.get('rol_actual') not in st.session_state.user_data['roles']:
            st.session_state.rol_actual = st.session_state.user_data['roles'][0] if st.session_state.user_data['roles'] else ''
    
    # Barra lateral
    st.sidebar.title("📚 Plataforma Escolar")
    st.sidebar.write(f"👤 {st.session_state.usuario}")
    
    user_roles = st.session_state.user_data.get('roles', [])
    user_roles = [r for r in user_roles if r]
    
    rol_actual = st.session_state.get('rol_actual', st.session_state.user_data.get('rol'))
    
    if len(user_roles) > 1:
        st.sidebar.write("---")
        st.sidebar.write("🔄 **Cambiar perfil:**")
        for rol in user_roles:
            # Mostrar el rol con un nombre más amigable
            nombre_mostrar = rol.replace('_grupo', '')
            if st.sidebar.button(f"🔁 {nombre_mostrar.upper()}", key=f"cambiar_{rol}", 
                                 disabled=(rol == rol_actual),
                                 use_container_width=True):
                st.session_state.rol_actual = rol
                st.rerun()
        st.sidebar.write("---")
        st.sidebar.write(f"**Perfil actual:** {rol_actual.replace('_grupo', '').upper()}")
    else:
        st.sidebar.write(f"📌 Rol: {rol_actual.replace('_grupo', '').upper()}")
    
    st.sidebar.write("---")
    if st.sidebar.button("Cerrar sesión", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    
    # Redirección por rol (CONVERSIÓN DE NOMBRES)
    ROLES_VALIDOS = ['estudiante', 'docente', 'acudiente', 'director', 'coordinador', 'secretaria', 'supervisor', 'admin']
    
    # Convertir director_grupo a director para el módulo
    if rol_actual == 'director_grupo':
        rol_actual = 'director'
        st.session_state.rol_actual = 'director'
    
    if rol_actual in ROLES_VALIDOS:
        if rol_actual == 'estudiante':
            estudiante.mostrar(st.session_state.user_data)
        elif rol_actual == 'docente':
            docente.mostrar(st.session_state.user_data)
        elif rol_actual == 'acudiente':
            acudiente.mostrar(st.session_state.user_data)
        elif rol_actual == 'director':
            director.mostrar(st.session_state.user_data)
        elif rol_actual == 'coordinador':
            coordinador.mostrar(st.session_state.user_data)
        elif rol_actual == 'secretaria':
            secretaria.mostrar(st.session_state.user_data)
        elif rol_actual == 'supervisor':
            supervisor.mostrar(st.session_state.user_data)
        elif rol_actual == 'admin':
            admin.mostrar(st.session_state.user_data)
    else:
        st.error(f"⚠️ Rol no reconocido: {rol_actual}")
        st.info("📌 Roles disponibles: " + ", ".join(ROLES_VALIDOS))
        if st.button("Volver a login"):
            st.session_state.logged_in = False
            st.rerun()
