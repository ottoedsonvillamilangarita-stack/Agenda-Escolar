import streamlit as st
from modulos import login, estudiante, docente, acudiente, director, admin

st.set_page_config(page_title="Plataforma Escolar", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login.mostrar()
else:
    # Barra lateral con información y cambio de perfil
    st.sidebar.title("📚 Plataforma Escolar")
    
    # Mostrar usuario actual
    st.sidebar.write(f"👤 {st.session_state.usuario}")
    
    # Si tiene múltiples roles, mostrar selector
    if len(st.session_state.roles_disponibles) > 1:
        st.sidebar.write("---")
        st.sidebar.write("🔄 **Cambiar perfil:**")
        
        # Crear botones para cada rol
        for rol in st.session_state.roles_disponibles:
            if st.sidebar.button(
                f"🔁 {rol.upper()}", 
                key=f"cambiar_{rol}",
                use_container_width=True,
                disabled=(rol == st.session_state.rol_actual)
            ):
                st.session_state.rol_actual = rol
                st.rerun()
        
        st.sidebar.write("---")
        st.sidebar.write(f"**Perfil actual:** {st.session_state.rol_actual.upper()}")
    else:
        st.sidebar.write(f"📌 Rol: {st.session_state.rol_actual.upper()}")
    
    st.sidebar.write("---")
    if st.sidebar.button("Cerrar sesión", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    
    # Redirigir según el rol actual
    rol = st.session_state.rol_actual
    
    if rol == 'estudiante':
        estudiante.mostrar(st.session_state.user_data)
    elif rol == 'docente':
        docente.mostrar(st.session_state.user_data)
    elif rol == 'acudiente':
        acudiente.mostrar(st.session_state.user_data)
    elif rol == 'director':
        director.mostrar(st.session_state.user_data)
    elif rol == 'admin':
        admin.mostrar(st.session_state.user_data)
    else:
        st.error("Rol no reconocido")
