import streamlit as st
from modulos import login, estudiante, docente, acudiente, director, coordinador, secretaria, supervisor, admin

st.set_page_config(page_title="Plataforma Escolar", layout="wide")

# Inicializar session_state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login
if not st.session_state.logged_in:
    login.mostrar()
else:
    # Mostrar información del usuario (corregido)
    st.sidebar.title("Menú")
    st.sidebar.write(f"👤 {st.session_state.user_data.get('username', 'Usuario')}")
    st.sidebar.write(f"📌 Rol: {st.session_state.user_data.get('rol', 'Sin rol')}")
    
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.logged_in = False
        st.rerun()
    
    # Redirigir según el rol
    rol = st.session_state.user_data.get('rol')
    
    if rol == 'estudiante':
        estudiante.mostrar(st.session_state.user_data)
    elif rol == 'docente':
        docente.mostrar(st.session_state.user_data)
    elif rol == 'acudiente':
        acudiente.mostrar(st.session_state.user_data)
    elif rol == 'director':
        director.mostrar(st.session_state.user_data)
    elif rol == 'coordinador':
        coordinador.mostrar(st.session_state.user_data)
    elif rol == 'secretaria':
        secretaria.mostrar(st.session_state.user_data)
    elif rol == 'supervisor':
        supervisor.mostrar(st.session_state.user_data)
    elif rol == 'admin':
        admin.mostrar(st.session_state.user_data)
    else:
        st.error("Rol no reconocido")
