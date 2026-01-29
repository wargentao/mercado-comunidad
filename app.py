import streamlit as st
from datetime import datetime

# --- 1. CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="Mercado Comunidad", page_icon="🛒", layout="centered")

# Estilo del encabezado
def render_header():
    st.markdown("""
        <div style='text-align: center; background-color: #fce4ec; padding: 15px; border-radius: 15px; border: 3px solid #e91e63;'>
            <h1 style='color: #880e4f; margin: 0;'>🛒 MERCADO COMUNIDAD</h1>
            <p style='color: #ad1457; font-weight: bold;'>Plataforma Oficial de Tao_Creador</p>
        </div>
        <br>
    """, unsafe_allow_html=True)

# --- 2. BASES DE DATOS (Session State) ---
# Inicializamos todas las variables si no existen
for llave in ['muro', 'usuarios_db', 'baneados', 'sugerencias', 'ojo_de_tao', 'carrito', 'bloqueos', 'aviso_global', 'mantenimiento', 'panel_t']:
    if llave not in st.session_state:
        if llave == 'mantenimiento': st.session_state[llave] = False
        elif llave == 'panel_t': st.session_state[llave] = False
        elif llave in ['usuarios_db', 'bloqueos']: st.session_state[llave] = {}
        elif llave == 'aviso_global': st.session_state[llave] = None
        else: st.session_state[llave] = []

def registrar_ojo(accion):
    hora = datetime.now().strftime("%H:%M:%S")
    st.session_state.ojo_de_tao.insert(0, f"[{hora}] 👁️ {accion}")

# --- 3. FILTRO DE ACCESO (EL CANDADO DE MANTENIMIENTO) ---
# Si el modo mantenimiento está ON y el usuario NO es Tao, bloqueamos la app.
if st.session_state.mantenimiento and st.session_state.get('usuario') != "Tao_Creador":
    render_header()
    st.markdown(f"""
        <div style='text-align: center; background-color: #1e1e1e; padding: 40px; border-radius: 20px; border: 4px solid #ff4b4b;'>
            <h1 style='color: white; font-size: 50px;'>🛠️</h1>
            <h2 style='color: #ff4b4b;'>MODO MANTENIMIENTO</h2>
            <p style='color: #cccccc; font-size: 18px;'>
                {st.session_state.aviso_global if st.session_state.aviso_global else "Estamos haciendo ajustes técnicos. Volveremos pronto."}
            </p>
            <hr style='border: 1px solid #333;'>
            <p style='color: #666;'>Atentamente: Tao_Creador</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# --- 4. SISTEMA DE LOGIN ---
if 'usuario' not in st.session_state:
    render_header()
    with st.container(border=True):
        st.subheader("👤 Identificarse")
        nombre = st.text_input("Ingresa tu nombre de usuario:")
        if st.button("Entrar al Mercado", use_container_width=True):
            if nombre in st.session_state.baneados:
                st.error("🚫 Tu acceso ha sido restringido por el Administrador.")
            elif nombre.strip() == "":
                st.warning("Escribe un nombre válido.")
            else:
                st.session_state.usuario = nombre
                st.session_state.es_admin = (nombre == "Tao_Creador")
                registrar_ojo(f"{nombre} inició sesión.")
                st.rerun()
    st.stop()

# --- 5. PANEL DE CONTROL (SOLO TAO) ---
if st.session_state.es_admin or st.session_state.get('incognito'):
    with st.sidebar:
        st.error("👑 PANEL MAESTRO")
        
        # BOTÓN DE PÁNICO / MANTENIMIENTO
        if not st.session_state.mantenimiento:
            if st.button("🔴 CERRAR MERCADO (Mantenimiento)", use_container_width=True):
                st.session_state.mantenimiento = True
                registrar_ojo("Tao activó el modo mantenimiento.")
                st.rerun()
        else:
            if st.button("🟢 ABRIR MERCADO AL PÚBLICO", use_container_width=True):
                st.session_state.mantenimiento = False
                registrar_ojo("Tao desactivó el modo mantenimiento.")
                st.rerun()

        # BOTÓN "T" PARA OPCIONES EXTRA
        if st.button("⚙️ Configurar Mensajes"):
            st.session_state.panel_t = not st.session_state.panel_t
        
        if st.session_state.panel_t:
            st.divider()
            st.subheader("📢 Comunicación")
            msg = st.text_input("Mensaje de aviso/mantenimiento:")
            col_msg1, col_msg2 = st.columns(2)
            with col_msg1:
                if st.button("Fijar"): st.session_state.aviso_global = msg; st.rerun()
            with col_msg2:
                if st.button("Limpiar"): st.session_state.aviso_global = None; st.rerun()

            st.divider()
            st.subheader("🔍 Registro de Actividad")
            for log in st.session_state.ojo_de_tao[:5]:
                st.caption(log)

# --- 6. INTERFAZ PRINCIPAL ---
render_header()

# Aviso visual si el Admin tiene el mercado cerrado
if st.session_state.mantenimiento:
    st.warning("⚠️ **ESTADO: MANTENIMIENTO ACTIVO.** Los usuarios no pueden entrar, pero tú tienes acceso total.")

if st.session_state.aviso_global and not st.session_state.mantenimiento:
    st.info(f"📢 **AVISO:** {st.session_state.aviso_global}")

tabs = st.tabs(["🛒 Mercado", "🛍️ Mi Carrito", "💡 Sugerencias"])

# --- TAB 1: MERCADO ---
with tabs[0]:
    with st.expander("➕ Publicar nuevo artículo"):
        nom = st.text_input("Nombre del producto:")
        precio = st.number_input("Precio o Puja inicial:", min_value=1)
        es_sub = st.checkbox("¿Es una subasta?")
        if st.button("Publicar ahora"):
            st.session_state.muro.append({
                "n": nom, "p": precio, "v": st.session_state.usuario, 
                "s": es_sub, "g": "Nadie"
            })
            registrar_ojo(f"{st.session_state.usuario} publicó {nom}")
            st.success("¡Publicado!")
            st.rerun()

    if not st.session_state.muro:
        st.write("No hay artículos publicados todavía.")
    
    for i, item in enumerate(st.session_state.muro):
        # Filtro de bloqueos personales
        if item['v'] in st.session_state.bloqueos.get(st.session_state.usuario, []):
            continue

        with st.container(border=True):
            st.subheader(item['n'])
            st.caption(f"Vendedor: {item['v']}")
            
            if item['s']:
                st.info(f"🔨 Subasta: ${item['p']} | Líder: {item['g']}")
                puja = st.number_input(f"Tu oferta por {item['n']}:", min_value=int(item['p']+1), key=f"p_{i}")
                if st.button(f"Pujar ${puja}", key=f"bp_{i}"):
                    item['p'] = puja
                    item['g'] = st.session_state.usuario
                    registrar_ojo(f"{st.session_state.usuario} pujó ${puja} por {item['n']}")
                    st.rerun()
            else:
                st.write(f"💰 Precio: ${item['p']}")
                if st.button("🛒 Guardar en Carrito", key=f"cart_{i}"):
                    st.session_state.carrito.append(item)
                    st.toast("Añadido al carrito")

            # Controles de seguridad
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("🚩 Reportar", key=f"rep_{i}"): 
                    registrar_ojo(f"⚠️ REPORTE contra {item['v']} por {item['n']}")
                    st.toast("Reporte enviado")
            with c2:
                if st.button("🚫 Bloquear", key=f"bloq_{i}"):
                    st.session_state.bloqueos.setdefault(st.session_state.usuario, []).append(item['v'])
                    st.rerun()
            with c3:
                # Botón "T" para borrar (Solo para Tao o Incógnito)
                if st.session_state.usuario == "Tao_Creador" or st.session_state.get('incognito'):
                    if st.button("🔴 T (Borrar)", key=f"del_{i}"):
                        st.session_state.muro.pop(i)
                        registrar_ojo(f"Tao borró el artículo: {item['n']}")
                        st.rerun()

# --- TAB 2: CARRITO ---
with tabs[1]:
    st.header("Tus cosas guardadas")
    if not st.session_state.carrito:
        st.write("Tu carrito está vacío.")
    else:
        for c_item in st.session_state.carrito:
            st.write(f"📦 **{c_item['n']}** - ${c_item['p']} (Vendedor: {c_item['v']})")
        if st.button("Limpiar Carrito"):
            st.session_state.carrito = []
            st.rerun()

# --- TAB 3: SUGERENCIAS ---
with tabs[2]:
    st.header("Mejoras para el Mercado")
    idea = st.text_area("¿Qué te gustaría añadir?")
    if st.button("Enviar sugerencia"):
        if idea:
            st.session_state.sugerencias.append(f"{st.session_state.usuario}: {idea}")
            registrar_ojo(f"{st.session_state.usuario} envió una sugerencia.")
            st.success("¡Gracias por tu idea!")
        else:
            st.warning("Escribe algo primero.")
