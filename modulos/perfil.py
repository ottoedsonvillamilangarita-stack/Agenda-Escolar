import streamlit as st
import requests
from utils import get_headers, SUPABASE_URL

def mostrar_editar_perfil(id_persona, nombre_actual, email_actual, telefono_actual):
    """Muestra el formulario para editar perfil"""
    st.subheader("✏️ Editar mi información")
    
    nuevo_email = st.text_input("Correo electrónico", value=email_actual if email_actual else "")
    nuevo_telefono = st.text_input("Teléfono", value=telefono_actual if telefono_actual else "")
    
    if st.button("💾 Actualizar datos"):
        headers = get_headers()
        datos_actualizar = {}
        
        if nuevo_email and nuevo_email != email_actual:
            datos_actualizar["email"] = nuevo_email
        if nuevo_telefono and nuevo_telefono != telefono_actual:
            datos_actualizar["telefono"] = nuevo_telefono
        
        if datos_actualizar:
            url_update = f"{SUPABASE_URL}/rest/v1/personas?id_persona=eq.{id_persona}"
            response = requests.patch(
                url_update,
                headers={**headers, "Content-Type": "application/json"},
                json=datos_actualizar
            )
            if response.status_code == 200:
                st.success("✅ Datos actualizados correctamente")
                st.rerun()
            else:
                st.error("❌ Error al actualizar")
        else:
            st.warning("No se realizaron cambios")

def mostrar_cambiar_password(username):
    """Muestra el formulario para cambiar contraseña"""
    st.subheader("🔐 Cambiar mi contraseña")
    
    if not username:
        st.error("No se pudo identificar el usuario")
        return
    
    st.write(f"**Usuario:** {username}")
    
    password_actual = st.text_input("Contraseña actual", type="password")
    nueva_password = st.text_input("Nueva contraseña", type="password")
    confirmar_password = st.text_input("Confirmar nueva contraseña", type="password")
    
    if st.button("🔐 Cambiar contraseña"):
        if not password_actual:
            st.error("❌ Ingresa tu contraseña actual")
        elif not nueva_password:
            st.error("❌ La nueva contraseña no puede estar vacía")
        elif nueva_password != confirmar_password:
            st.error("❌ Las contraseñas nuevas no coinciden")
        elif len(nueva_password) < 4:
            st.error("❌ La contraseña debe tener al menos 4 caracteres")
        else:
            headers = get_headers()
            
            # Verificar contraseña actual
            url_verificar = f"{SUPABASE_URL}/rest/v1/usuarios_login?username=eq.{username}&password_hash=eq.{password_actual}"
            response = requests.get(url_verificar, headers=headers)
            
            if response.status_code == 200 and response.json():
                # Actualizar contraseña
                url_update = f"{SUPABASE_URL}/rest/v1/usuarios_login?username=eq.{username}"
                response_update = requests.patch(
                    url_update,
                    headers={**headers, "Content-Type": "application/json"},
                    json={"password_hash": nueva_password}
                )
                if response_update.status_code == 200:
                    st.success("✅ Contraseña cambiada exitosamente")
                    st.info("🔐 A partir de ahora usa tu nueva contraseña")
                else:
                    st.error("❌ Error al cambiar la contraseña")
            else:
                st.error("❌ Contraseña actual incorrecta")

def mostrar_perfil(usuario_data):
    """Muestra el perfil completo con pestañas"""
    tab1, tab2 = st.tabs(["👤 Mi Perfil", "🔐 Seguridad"])
    
    with tab1:
        st.subheader("Información Personal")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Nombre:**")
            st.write(usuario_data.get("nombre", "No registrado"))
            st.write("**Usuario:**")
            st.write(usuario_data.get("username", "No registrado"))
        with col2:
            st.write("**Email:**")
            email = usuario_data.get("email", "No registrado")
            st.write(email)
            st.write("**Teléfono:**")
            telefono = usuario_data.get("telefono", "No registrado")
            st.write(telefono)
        
        mostrar_editar_perfil(
            usuario_data.get("id_persona"),
            usuario_data.get("nombre"),
            usuario_data.get("email"),
            usuario_data.get("telefono")
        )
    
    with tab2:
        mostrar_cambiar_password(usuario_data.get("username"))
