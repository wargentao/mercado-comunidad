import streamlit as st
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mercado Comunidad", page_icon="🛒", layout="centered")

# --- 2. SEGURIDAD MAESTRA ---
# Clave actualizada a "tao" en minúsculas como pediste.
PASSWORD_TAO = "tao"  
ADMIN_NAME = "Tao_Creator"

# --- 3. BASE DE DATOS GLOBAL (SINCRONIZACIÓN TOTAL) ---
@st.cache_resource
def obtener_db_global():
    return {
        'muro': [],               # Productos compartidos
        'chats': {},              # Mensajes compartidos
        'baneados': set(),        # Usuarios bloqueados
        'ojo_de_tao': [],         # Registro de actividad (Admin)
        'mantenimiento': False,   # Estado del servidor
        'aviso_mantenimiento': "La aplicación está en mantenimiento.",
        'sugerencias': []         # Buzón de ideas
    }

db = obtener_db_global()

def registrar_actividad(usuario, accion):
    ahora = datetime.now().strftime("%H:%M:%S")
    db['ojo_de_tao'].insert(0, f"📌 [{ahora}] | 👤 {usuario}: {accion}")

# --- 4. DISEÑO Y CABECERA ---
def mostrar_logo():
    st.markdown("""
        <div style='text-align: center; background-color: #fce4ec; padding: 15px; border-radius: 15px; border: 3px solid #e91e63;'>
            <h1 style='color: #880e4f; margin: 0;'>🛒 MERCADO COMUNIDAD</h1>
            <p style='color: #ad1457; font-weight: bold;'>Plataforma Sincronizada - Creada por Tao_Creator</p>
        </div>
        <br>
    """, unsafe_allow_html=True)

# --- 5. LÓGICA DE CIERRE DE SESIÓN ---
def cerrar_sesion():
    if 'usuario' in st.session_state:
        registrar_actividad(st.session_state.usuario, "SALIÓ")
    for k in ['usuario', 'es_admin_real', 'nombre_falso_activo', 'chat_activo']:
        if k in st.session_state: del st.session_state[k]
    st.rerun()

# --- 6. SISTEMA DE LOGIN DISCRETO ---
if 'usuario' not in st.session_state:
    mostrar_logo()
    
    with st.container(border=True):
        st.subheader("👤 Identificarse")
        nombre_in = st.text_input("Nombre de usuario:")
        
        # Solo muestra la contraseña si el nombre coincide exactamente con el tuyo
        pass_in = ""
        if nombre_in == ADMIN_NAME:
            pass_in = st.text_input("Llave Maestra:", type="password")
        
        if st.button("Entrar al Mercado", use_container_width=True):
            # Caso Administrador
            if nombre_in == ADMIN_NAME:
                if pass_in == PASSWORD_TAO:
                    st.session_state.usuario = nombre_in
                    st.session_state.es_admin_real = True
                    st.session_state.nombre_falso_activo = False
                    registrar_actividad(nombre_in, "ENTRÓ (MODO CREADOR)")
                    st.rerun()
                else:
                    st.error("❌ Llave incorrecta.")
            
            # Caso Baneado
            elif nombre_in in db['baneados']:
                st.error("🚫 Acceso revocado.")
            
            # Caso Mantenimiento (Silencioso para intrusos)
            elif db['mantenimiento']:
                st.error(f"🛠️ {db['aviso_mantenimiento']}")
            
            # Caso Usuario Normal
            elif nombre_in.strip():
                st.session_state.usuario = nombre_in
                st.session_state.es_admin_real = False
                registrar_actividad(nombre_in, "ENTRÓ")
                st.rerun()
            else:
                st.warning("Escribí un nombre para continuar.")
    st.stop()

# --- 7. PANEL DE CONTROL (SIDEBAR PARA TAO_CREATOR) ---
if st.session_state.get('es_admin_real', False):
    with st.sidebar:
        st.error(f"👑 PANEL DE CONTROL")
        
        # MODO INFILTRADO
        with st.expander("🎭 Modo Infiltrado"):
            if st.session_state.get('nombre_falso_activo'):
                st.info(f"Disfraz: {st.session_state.usuario}")
                if st.button("🔙 Volver a mi nombre"):
                    st.session_state.usuario = ADMIN_NAME
                    st.session_state.nombre_falso_activo = False
                    st.rerun()
            else:
                nf = st.text_input("Nuevo nombre falso:")
                if st.button("🎭 Cambiar Identidad"):
                    if nf.strip():
                        st.session_state.usuario = nf
                        st.session_state.nombre_falso_activo = True
                        st.rerun()

        # GESTIÓN DEL MERCADO
        with st.expander("🚧 Seguridad y Estado"):
            estado = "🟢 ABRIR" if db['mantenimiento'] else "🔴 CERRAR (Mante)"
            if st.button(estado):
                db['mantenimiento'] = not db['mantenimiento']
                st.rerun()
            
            u_b = st.text_input("Usuario a banear:")
            if st.button("BLOQUEAR PERMANENTE"):
                db['baneados'].add(u_b)
                registrar_actividad(ADMIN_NAME, f"BANEÓ A {u_b}")
                st.success(f"Usuario {u_b} bloqueado.")

        # EL OJO DE TAO (COMPACTO)
        with st.expander("👁️ EL OJO DE TAO"):
            st.write("Historial reciente:")
            for log in db['ojo_de_tao'][:30]:
                st.caption(log)
            if st.button("Vaciar Historial"):
                db['ojo_de_tao'] = []
                st.rerun()

# --- 8. INTERFAZ PRINCIPAL DEL MERCADO ---
mostrar_logo()
st.caption(f"Sesión iniciada como: **{st.session_state.usuario}**")
if st.sidebar.button("🚪 Cerrar Sesión"): cerrar_sesion()

tabs = st.tabs(["🛒 El Muro", "📦 Mis Publicaciones", "💬 Chats", "💡 Sugerencias"])

# --- TAB: EL MURO (VISIÓN GLOBAL) ---
with tabs[0]:
    with st.expander("➕ Publicar algo nuevo"):
        n_p = st.text_input("Nombre del producto:")
        p_p = st.number_input("Precio ARS $:", min_value=1)
        f_p = st.file_uploader("Sube una imagen", type=['png','jpg','jpeg'])
        if st.button("🚀 Publicar", disabled=not f_p):
            # Guardamos en la base global para que todos lo vean
            db['muro'].insert(0, {
                "id": f"{n_p}_{datetime.now().timestamp()}", 
                "n": n_p, "p": p_p, "v": st.session_state.usuario, "f": f_p
            })
            registrar_actividad(st.session_state.usuario, f"PUBLICÓ: {n_p}")
            st.success("¡Publicado en el muro global!")
            st.rerun()

    for i, item in enumerate(db['muro']):
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 2, 0.5])
            with c1: st.image(item['f'], use_container_width=True)
            with c2:
                st.subheader(item['n'])
                st.write(f"💰 ARS ${item['p']} | Vende: {item['v']}")
                if st.button(f"💬 Chat", key=f"chat_{i}"):
                    st.session_state.chat_activo = item['id']
            with c3:
                if st.session_state.get('es_admin_real'):
                    if st.button("🔴", key=f"del_{i}"):
                        db['muro'].pop(i)
                        registrar_actividad(ADMIN_NAME, f"BORRÓ {item['n']}")
                        st.rerun()

# --- TAB: MIS PUBLICACIONES ---
with tabs[1]:
    st.header("Mis Artículos")
    mis_articulos = [x for x in db['muro'] if x['v'] == st.session_state.usuario]
    if not mis_articulos:
        st.info("No has publicado productos todavía.")
    for m in mis_articulos:
        with st.container(border=True):
            st.write(f"**{m['n']}** | ARS ${m['p']}")
            if st.button("🗑️ Eliminar Publicación", key=f"del_m_{m['id']}"):
                db['muro'] = [x for x in db['muro'] if x['id'] != m['id']]
                registrar_actividad(st.session_state.usuario, f"BORRÓ SU POST: {m['n']}")
                st.rerun()

# --- TAB: CHATS ---
with tabs[2]:
    cid = st.session_state.get('chat_activo')
    if cid:
        prod_sel = next((x for x in db['muro'] if x['id'] == cid), None)
        if prod_sel:
            st.subheader(f"Chat: {prod_sel['n']}")
            mensajes = db['chats'].get(cid, [])
            for m in mensajes: st.write(f"**{m['u']}:** {m['t']}")
            msg_in = st.text_input("Escribe tu mensaje:")
            if st.button("Enviar"):
                db['chats'].setdefault(cid, []).append({"u": st.session_state.usuario, "t": msg_in})
                st.rerun()
    else:
        st.info("Seleccioná un producto del muro para hablar con el vendedor.")

# --- TAB: SUGERENCIAS ---
with tabs[3]:
    st.header("💡 Buzón de Sugerencias")
    st.write("Dejanos tu idea para mejorar la plataforma.")
    txt_sug = st.text_area("Tu sugerencia:")
    if st.button("Enviar"):
        if txt_sug.strip():
            db['sugerencias'].insert(0, {"u": st.session_state.usuario, "t": txt_sug, "f": datetime.now().strftime("%d/%m %H:%M")})
            st.success("¡Gracias! Tao_Creator revisará tu idea.")
        else: st.warning("Escribí algo primero.")
    
    # Solo el Administrador ve las sugerencias enviadas
    if st.session_state.get('es_admin_real'):
        st.divider()
        st.subheader("🕵️ Sugerencias Recibidas (Solo Admin)")
        for s in db['sugerencias']:
            st.write(f"**{s['u']}** ({s['f']}): {s['t']}")
