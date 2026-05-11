import streamlit as st

def mostrar(data):
    st.title(f"📋 Secretaría Académica")
    st.write(f"Bienvenido, {data['nombre']}")
    
    tab1, tab2 = st.tabs(["📚 Cursos", "👥 Usuarios"])
    with tab1:
        st.write("• 9°A, 9°B, 10°A, 10°B, 11°A, 11°B")
    with tab2:
        st.write("• 156 Estudiantes, 18 Docentes, 45 Acudientes")
