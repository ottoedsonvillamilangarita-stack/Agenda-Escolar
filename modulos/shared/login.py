# modulos/compartido/auth.py
import streamlit as st
import requests
from utils import SUPABASE_URL, get_headers

def mostrar_login():
    st.title("📚 Plataforma Escolar")
    st.subheader("Iniciar Sesión")
    
    if "recover_mode" not in st.session_state:
        st.session_state.recover_mode = False
    
    if not st.session_state.recover_mode:
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Ingresar", use_container_width=True):
                # Lógica de autenticación (sin cambios)
                url = f"{SUPABASE_URL}/rest/v1/usuarios_login?username=eq.{usuario}"
                headers = get_headers()
                try:
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        datos = response.json()
                        if datos and len(datos) > 0:
                            user_data = datos[0]
                            if user_data.get("password_hash") == password:
                                roles_disponibles = user_data.get('roles', [user_data.get('rol')])
                                st.session_state.logged_in = True
                                st.session_state.usuario = usuario
                                st.session_state.user_data = user_data
                                st.session_state.roles_disponibles = roles_disponibles
                                st.session_state.rol_actual = user_data.get('rol', roles_disponibles[0])
                                st.success("✅ Login exitoso. Redirigiendo...")
                                st.rerun()
                            else:
                                st.error("❌ Contraseña incorrecta")
                        else:
                            st.error("❌ Usuario no encontrado")
                    else:
                        st.error(f"❌ Error de conexión: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ Error al conectar: {str(e)}")
        
        with col2:
            if st.button("¿Olvidaste tu contraseña?", use_container_width=True):
                st.session_state.recover_mode = True
                st.rerun()
        
        st.divider()
        st.caption("Usuarios de prueba: admin, secretaria, docente_1, estudiante_1, acudiente_1")
        st.caption("Contraseña: demo2026")
    else:
        st.subheader("🔐 Recuperar Contraseña")
        usuario_rec = st.text_input("Usuario")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Enviar instrucciones", use_container_width=True):
                # Lógica de recuperación (sin cambios)
                pass
        with col2:
            if st.button("Volver al inicio", use_container_width=True):
                st.session_state.recover_mode = False
                st.rerun()
