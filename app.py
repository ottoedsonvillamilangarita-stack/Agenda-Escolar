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
    # Barra lateral
    st.sidebar.title("📚 Plataforma Escolar")
    st.sidebar.write(f"👤 {st.session_state.usuario}")
    
    # Mostrar rol actual
    rol_actual = st.session_state.user_data.get('rol', '')
    st.sidebar.write(f"📌 Rol: {rol_actual.upper()}")
    
    st.sidebar.write("---")
    if st.sidebar.button("Cerrar sesión", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    
    # ============================================
    # REDIRECCIÓN CORRECTA POR ROL
    # ============================================
    
    # Depuración: ver qué rol está llegando
    st.write(f"🔍 Debug - Rol detectado: '{rol_actual}'")
    
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
        st.success("✅ Redirigiendo a panel de Secretaria")
        secretaria.mostrar(st.session_state.user_data)
    elif rol_actual == 'supervisor':
        supervisor.mostrar(st.session_state.user_data)
    elif rol_actual == 'admin':
        admin.mostrar(st.session_state.user_data)
    else:
        st.error(f"❌ Rol no reconocido: '{rol_actual}'")
        st.write("Contacta al administrador del sistema")
