import streamlit as st

def mostrar_perfil(usuario_data):
    st.subheader("👤 Mi Perfil")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Nombre:**")
        st.write(usuario_data.get("nombre", "No registrado"))
        st.write("**Usuario:**")
        st.write(usuario_data.get("username", "No registrado"))
    with col2:
        st.write("**Email:**")
        st.write(usuario_data.get("email", "No registrado"))
        st.write("**Teléfono:**")
        st.write(usuario_data.get("telefono", "No registrado"))
    
    st.info("🔧 Próximamente: editar perfil")
