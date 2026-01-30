import streamlit as st
from datetime import datetime

# --- 1. CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="Mercado Comunidad", page_icon="🛒")

# --- 2. SEGURIDAD MAESTRA ---
# Cambia esta contraseña por la que tú quieras
PASSWORD_TAO = "TAO2024" 

# --- 3. BASES DE DATOS (Session State) ---
for llave in ['muro', 'usuarios_db', 'baneados', 'sugerencias', 'ojo_de_tao', 'carrito', 'bloqueos', 'aviso_global', 'mantenimiento']:
    if llave not in st.session_state:
        if llave == 'mantenimiento': st.session_state[llave] = False
        elif llave in ['usuarios_db', 'bloqueos']: st.session_state[llave] = {}
        elif llave == 'aviso_global': st.session_state[llave] = None
        else: st.session_state[llave] = []

def registrar_ojo(accion):
    hora = datetime.now().strftime("%H:%M:%S")
    st.session_state.ojo_de_tao.insert(0, f"[{hora}] 👁️ {accion}")

# --- 4. FUNCIÓN DE CABECERA ---
def mostrar_logo():
    st.markdown("""
        <div style='text-align: center; background-color: #fce4ec; padding: 15px; border-radius: 15px; border: 3px solid #e91e63;'>
            <h1 style='color: #880e4f; margin: 0;'>🛒 MERCADO COMUNIDAD</h1>
            <p style='color: #ad1457; font-weight: bold;'>Plataforma Oficial de Tao_Creador</p>
        </div>
        <br>
    """, unsafe_allow_html=True)

# --- 5. FILTRO DE MANTENIMIENTO (EL CANDADO) ---
if st.session_state.mantenimiento and st.session_state.get('usuario') != "Tao_Creador":
    mostrar_logo()
    st.markdown(f"""
        <div style='text-align: center; background-color: #333; padding: 50px; border-radius: 20px; border: 5px solid red;'>
            <h1 style='color: white;'>🚧 MANTENIMIENTO 🚧</h1>
            <p style='color: #ff4b4b; font-size: 20px; font-weight: bold;'>
                {st.session_state.aviso_global if st.session_state.aviso_global else "Estamos haciendo mejoras técnicas."}
            </p>
            <p style='color: gray;'>Vuelve pronto.</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# --- 6. SISTEMA DE LOGIN SEGURO ---
if 'usuario' not in st.session_state:
    mostrar_logo()
    with st.container(border=True):
        st.subheader("👤 Identificarse")
        nombre = st.text_input("Tu nombre de usuario:")
        
        pass_input = ""
        if nombre == "Tao_Creador":
            pass_input = st.text_input("Introduce tu Llave Maestra:", type="password")
            
        if st.button("Entrar al Mercado", use_container_width=True):
            if nombre in st.session_state.baneados:
                st.error("🚫 Tu acceso ha sido restringido.")
            elif nombre == "Tao_Creador" and pass_input != PASSWORD_TAO:
                st.error("❌ Contraseña incorrecta, Tao.")
            elif nombre.strip() == "":
                st.warning("Escribe un nombre.")
            else:
                st.session_state.usuario = nombre
                st.session_state.es_admin = (nombre == "Tao_Creador")
                registrar_ojo(f"{nombre} inició sesión.")
                st.rerun()
    st.stop()

# --- 7. PANEL MAESTRO (SOLO PARA TAO_CREADOR) ---
if st.session_state.es_admin:
    with st.sidebar:
        st.error("👑 HERRAMIENTAS DE TAO")
        
        # INTERRUPTOR DE PÁNICO
        if not st.session_state.mantenimiento:
            if st.button("🔴 CERRAR TODO (Mantenimiento)", use_container_width=True):
                st.session_state.mantenimiento = True
                registrar_ojo("Tao activó Mantenimiento")
                st.rerun()
        else:
            if st.button("🟢 REABRIR MERCADO", use_container_width=True):
                st.session_state.mantenimiento = False
                registrar_ojo("Tao abrió el mercado")
                st.rerun()

        # MENSAJE GLOBAL
        msg = st.text_input("Mensaje de aviso/bloqueo:")
        if st.button("Fijar Mensaje"): st.session_state.aviso_global = msg; st.rerun()

        # BANEO DE USUARIOS
        st.divider()
        u_ban = st.text_input("Usuario a expulsar:")
        if st.button("Banear para siempre"):
            st.session_state.baneados.append(u_ban)
            registrar_ojo(f"Baneado: {u_ban}")
            st.toast(f"Usuario {u_ban} bloqueado.")

        # OJO DE TAO
        st.divider()
        st.subheader("👁️ Ojo de Tao")
        for log in st.session_state.ojo_de_tao[:8]:
            st.caption(log)

# --- 8. INTERFAZ PRINCIPAL ---
mostrar_logo()
if st.session_state.mantenimiento:
    st.warning("⚠️ **ESTÁS EN MODO EDICIÓN.** Los demás usuarios están bloqueados.")

tabs = st.tabs(["🛒 Mercado", "🛍️ Mi Carrito", "💡 Sugerencias"])

# --- TAB MERCADO ---
with tabs[0]:
    with st.expander("➕ Vender algo"):
        nom = st.text_input("¿Qué vendes?")
        precio = st.number_input("Precio/Puja:", min_value=1)
        es_sub = st.checkbox("¿Es una subasta?")
        if st.button("Publicar en el Muro"):
            st.session_state.muro.append({"n": nom, "p": precio, "v": st.session_state.usuario, "s": es_sub, "g": "Nadie"})
            registrar_ojo(f"{st.session_state.usuario} publicó {nom}")
            st.rerun()

    for i, item in enumerate(st.session_state.muro):
        # Filtro de bloqueos personales
        if item['v'] in st.session_state.bloqueos.get(st.session_state.usuario, []): continue

        with st.container(border=True):
            col_info, col_btn = st.columns([3, 1])
            
            with col_info:
                st.subheader(item['n'])
                if item['s']:
                    st.info(f"🔨 Subasta: ${item['p']} | Ganador actual: {item['g']}")
                    puja = st.number_input(f"Ofertar por {item['n']}:", min_value=int(item['p']+1), key=f"puja_{i}")
                    if st.button(f"Pujar ${puja}", key=f"bpuja_{i}"):
                        item['p'] = puja
                        item['g'] = st.session_state.usuario
                        registrar_ojo(f"{st.session_state.usuario} pujó ${puja} por {item['n']}")
                        st.rerun()
                else:
                    st.write(f"💰 Precio: ${item['p']} | Vendedor: {item['v']}")
                    if st.button("🛒 Guardar", key=f"cart_{i}"):
                        st.session_state.carrito.append(item)
                        st.toast("Añadido al carrito")
            
            with col_btn:
                # BOTÓN 🔴 T (Solo visible para Tao)
                if st.session_state.es_admin:
                    if st.button(f"🔴 T", key=f"t_del_{i}"):
                        st.session_state.muro.pop(i)
                        registrar_ojo(f"Tao borró {item['n']}")
                        st.rerun()
                
                if st.button("🚩", key=f"rep_{i}"): registrar_ojo(f"Reporte contra {item['v']}")
                if st.button("🚫", key=f"bloq_{i}"):
                    st.session_state.bloqueos.setdefault(st.session_state.usuario, []).append(item['v'])
                    st.rerun()

# --- TAB CARRITO ---
with tabs[1]:
    st.header("Tus cosas guardadas")
    for c_item in st.session_state.carrito:
        st.write(f"📦 {c_item['n']} - ${c_item['p']}")

# --- TAB SUGERENCIAS ---
with tabs[2]:
    idea = st.text_area("¿Qué falta en la App?")
    if st.button("Enviar"): 
        st.session_state.sugerencias.append(f"{st.session_state.usuario}: {idea}")
        st.success("¡Enviado!")
