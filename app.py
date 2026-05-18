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
    # Barra lateral con información y cambio de perfil
    st.sidebar.title("📚 Plataforma Escolar")
    st.sidebar.write(f"👤 {st.session_state.usuario}")
    
    # Si tiene múltiples roles, mostrar selector
    if len(st.session_state.get('roles_disponibles', [st.session_state.user_data.get('rol', '')])) > 1:
        st.sidebar.write("---")
        st.sidebar.write("🔄 **Cambiar perfil:**")
        
        for rol in st.session_state.roles_disponibles:
            if st.sidebar.button(f"🔁 {rol.upper()}", key=f"cambiar_{rol}"):
                st.session_state.rol_actual = rol
                st.rerun()
        
        st.sidebar.write("---")
        st.sidebar.write(f"**Perfil actual:** {st.session_state.rol_actual.upper()}")
    else:
        rol_mostrar = st.session_state.user_data.get('rol', '')
        st.sidebar.write(f"📌 Rol: {rol_mostrar.upper()}")
    
    st.sidebar.write("---")
    if st.sidebar.button("Cerrar sesión", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    
    # ============================================
    # REDIRECCIÓN CORRECTA POR ROL
    # ============================================
    
    # Obtener el rol actual (podría venir de cambio de perfil)
    rol_actual = st.session_state.get('rol_actual', st.session_state.user_data.get('rol', ''))
    
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
        secretaria.mostrar(st.session_state.user_data)  # ← IMPORTANTE
    elif rol_actual == 'supervisor':
        supervisor.mostrar(st.session_state.user_data)
    elif rol_actual == 'admin':
        admin.mostrar(st.session_state.user_data)
    else:
        st.error(f"❌ Rol no reconocido: {rol_actual}")
        st.write("Contacta al administrador del sistema")
