import streamlit as st

def mostrar(data):
    st.title(f"🧭 Director de Grupo")
    st.write(f"Bienvenido, {data['nombre']}")
    st.success(f"📖 Grupo a cargo: {data.get('grupo', 'No asignado')}")
    
    st.subheader("👥 Estudiantes del grupo")
    estudiantes = ["Laura Méndez", "Sofía Méndez", "Tomás Herrera"]
    for est in estudiantes:
        st.write(f"• {est}")
    st.metric("Total Estudiantes", len(estudiantes))
