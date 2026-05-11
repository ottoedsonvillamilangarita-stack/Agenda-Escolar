import streamlit as st
from app import USUARIOS

def mostrar(data):
    st.title(f"⚙️ Administración")
    st.write(f"Bienvenido, {data['nombre']}")
    
    st.subheader("Usuarios del Sistema")
    for user, datos in USUARIOS.items():
        st.write(f"• **{user}** - {datos['rol']} - {datos['nombre']}")
