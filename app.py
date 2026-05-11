import streamlit as st
from modulos import estudiante, docente, acudiente, director, coordinador, secretaria, supervisor, admin

st.set_page_config(page_title="Plataforma Escolar", page_icon="📚", layout="wide")

# ======================================================
# USUARIOS DE PRUEBA
# ======================================================
USUARIOS = {
    "estudiante.laura": {"password": "demo2026", "rol": "estudiante", "nombre": "Laura Méndez", "grado": "11°A"},
    "docente.herrera": {"password": "demo2026", "rol": "docente", "nombre": "Claudia Herrera"},
    "acudiente.mendez": {"password": "demo2026", "rol": "acudiente", "nombre": "Carlos Méndez"},
    "director.11a": {"password": "demo2026", "rol": "director", "nombre": "Claudia Herrera", "grupo": "11°A"},
    "coordinador.rincon": {"password": "demo2026", "rol": "coordinador", "nombre": "Ricardo Rincón"},
    "secretaria": {"password": "demo2026", "rol": "secretaria", "nombre": "Secretaria Académica"},
    "supervisor": {"password": "demo2026", "rol": "supervisor", "nombre": "Supervisor"},
    "admin": {"password": "demo2026", "rol": "admin", "nombre": "Administrador"}
}

# ======================================================
# LOGIN
# ======================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("📚 Plataforma Escolar")
    st.subheader("Iniciar Sesión")
    
    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar"):
        if usuario in USUARIOS and USUARIOS[usuario]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.usuario = usuario
            st.session_state.user_data = USUARIOS[usuario]
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos")
    
    st.divider()
    st.caption("Usuarios: estudiante.laura, docente.herrera, acudiente.mendez, director.11a, coordinador.rincon, secretaria, supervisor, admin")
    st.caption("Contraseña para todos: demo2026")

# ======================================================
# PANEL SEGÚN EL ROL (llama al módulo correspondiente)
# ======================================================

else:
    with st.sidebar:
        st.write(f"👤 {st.session_state.user_data['nombre']}")
        st.write(f"📌 Rol: {st.session_state.user_data['rol']}")
        st.divider()
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.logged_in = False
            st.rerun()
    
    rol = st.session_state.user_data["rol"]
    data = st.session_state.user_data
    
    if rol == "estudiante":
        estudiante.mostrar(data)
    elif rol == "docente":
        docente.mostrar(data)
    elif rol == "acudiente":
        acudiente.mostrar(data)
    elif rol == "director":
        director.mostrar(data)
    elif rol == "coordinador":
        coordinador.mostrar(data)
    elif rol == "secretaria":
        secretaria.mostrar(data)
    elif rol == "supervisor":
        supervisor.mostrar(data)
    elif rol == "admin":
        admin.mostrar(data)
    
    st.divider()
    st.caption("📚 Plataforma Escolar Demo - 2026")
