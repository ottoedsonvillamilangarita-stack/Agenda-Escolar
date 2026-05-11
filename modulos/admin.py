import streamlit as st

def mostrar(data):
    st.title(f"⚙️ Administración")
    st.write(f"Bienvenido, {data['nombre']}")
    
    st.subheader("👥 Usuarios del Sistema")
    st.write("• estudiante.laura - Estudiante")
    st.write("• docente.herrera - Docente")
    st.write("• secretaria - Secretaria")
    st.write("• supervisor - Supervisor")
    st.write("• admin - Administrador")
