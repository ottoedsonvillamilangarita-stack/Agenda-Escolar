import streamlit as st

def mostrar():
    st.title("📚 Plataforma Escolar")
    st.subheader("Iniciar Sesión")
    
    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar"):
        # Datos de prueba (después conectaremos a Supabase)
        usuarios_validos = {
            "estudiante.laura": {"password": "demo2026", "rol": "estudiante", "nombre": "Laura Méndez", "grado": "11°A"},
            "docente.herrera": {"password": "demo2026", "rol": "docente", "nombre": "Claudia Herrera"},
            "acudiente.mendez": {"password": "demo2026", "rol": "acudiente", "nombre": "Carlos Méndez"},
            "director.11a": {"password": "demo2026", "rol": "director", "nombre": "Claudia Herrera", "grupo": "11°A"},
            "coordinador.rincon": {"password": "demo2026", "rol": "coordinador", "nombre": "Ricardo Rincón"},
            "secretaria": {"password": "demo2026", "rol": "secretaria", "nombre": "Secretaria Académica"},
            "supervisor": {"password": "demo2026", "rol": "supervisor", "nombre": "Supervisor"},
            "admin": {"password": "demo2026", "rol": "admin", "nombre": "Administrador"}
        }
        
        if usuario in usuarios_validos and usuarios_validos[usuario]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.usuario = usuario
            st.session_state.user_data = usuarios_validos[usuario]
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos")
    
    st.divider()
    st.caption("Usuarios de prueba:")
    st.caption("• estudiante.laura / demo2026")
    st.caption("• docente.herrera / demo2026")
    st.caption("• acudiente.mendez / demo2026")
    st.caption("• director.11a / demo2026")
    st.caption("• coordinador.rincon / demo2026")
    st.caption("• secretaria / demo2026")
    st.caption("• supervisor / demo2026")
    st.caption("• admin / demo2026")
