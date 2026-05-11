import streamlit as st

def mostrar(data):
    st.title(f"👁️ Supervisión")
    st.write(f"Bienvenido, {data['nombre']}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Estudiantes", "156")
        st.metric("Asistencia Promedio", "92%")
    with col2:
        st.metric("Total Docentes", "18")
        st.metric("Tareas Pendientes", "24")
