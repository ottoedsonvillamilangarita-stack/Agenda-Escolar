# modulos/paneles/admin.py
import streamlit as st

def mostrar(data):
    st.title("🛡️ Panel de Administrador")
    st.write(f"Bienvenido, {data.get('username', 'Admin')}")
    
    # =============================================
    # CONTENIDO PRINCIPAL DEL PANEL
    # =============================================
    st.subheader("📊 Panel de control")
    st.info("🔐 Selecciona una opción del menú lateral para comenzar.")
    
    # Mostrar algunas métricas rápidas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👨‍🎓 Estudiantes", "251")
    col2.metric("👨‍🏫 Docentes", "11")
    col3.metric("📚 Cursos", "7")
    col4.metric("📅 Año Lectivo", "2024")
    
    st.divider()
    st.caption("📌 Panel de control del Administrador")
