import streamlit as st
from datetime import datetime, timedelta
import time

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mercado Comunidad", page_icon="🛒", layout="centered")

# --- 2. SEGURIDAD MAESTRA ---
PASSWORD_TAO = "TAGO"  
ADMIN_NAME = "Tao_Creator"

# --- 3. BASE DE DATOS GLOBAL (COMPARTIDA) ---
@st.cache_resource
def obtener_db_global():
    return {
        'muro': [],               
        'chats': {},              
        'baneos_temporales': {},  
        'ojo_de_tao': [],         
        'mantenimiento': False,   
        'aviso_mantenimiento': "La aplicación está en mantenimiento técnico.",
        'aviso_global': "",       # Sección para Actualizaciones
        'sugerencias': []         
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
            <p style='color: #ad1457; font-weight: bold;'>Plataforma Sincronizada - Creado por Tao_Creator</p>
        </div>
        <br>
    """, unsafe_allow_html=True)

def cerrar_sesion():
    if 'usuario' in st.session_state:
        registrar_actividad(st.session_state.usuario, "SALIÓ")
    for k in ['usuario', 'es_admin_real', 'nombre_falso_activo', 'chat_activo']:
        if k in st.session_state: del st.session_state[k]
    st.rerun()

# --- 5. LOGIN DISCRETO CON FILTROS ---
if 'usuario' not in st.session_state:
    mostrar_logo()
    with st.container(border=True):
        st.subheader("👤 Identificarse")
        nombre_in = st.text_input("Nombre de usuario:")
        pass_in = ""
        if nombre_in == ADMIN_NAME:
            pass_in = st.text_input("Llave Maestra:", type="password")
        
        if st.button("Entrar", use_container_width=True):
            ahora = datetime.now()
            
            # Verificación de Baneo Temporal
            esta_baneado = False
            if nombre_in in db['baneos_temporales']:
                fin_ban = db['baneos_temporales'][nombre_in]
                if ahora < fin_ban:
                    mins = int((fin_ban - ahora).total_seconds() / 60)
                    st.error(f"🚫 Acceso denegado. Estás baneado temporalmente. Volvé en {mins + 1} min.")
                    esta_baneado = True
                else:
                    del db['baneos_temporales'][nombre_in]

            if not esta_baneado:
                if nombre_in == ADMIN_NAME:
                    if pass_in == PASSWORD_TAO:
                        st.session_state.usuario = nombre_in
                        st.session_state.es_admin_real = True
                        registrar_actividad(nombre_in, "ENTRÓ (CREADOR)")
                        st.rerun()
                    else: st.error("❌ Llave incorrecta.")
                elif db['mantenimiento']:
                    st.error(f"🛠️ {db['aviso_mantenimiento']}")
                elif nombre_in.strip():
                    st.session_state.usuario = nombre_in
                    st.session_state.es_admin_real = False
                    registrar_actividad(nombre_in, "ENTRÓ")
                    st.rerun()
                else:
                    st.warning("Ingresá un nombre.")
    st.stop()

# --- 6. PANEL DE CONTROL (SIDEBAR) ---
if st.session_state.get('es_admin_real', False):
    with st.sidebar:
        st.error(f"👑 PANEL DE CONTROL")
        
        # AVISO DE ACTUALIZACIONES (MENSAJE GLOBAL)
        with st.expander("📢 Publicar Actualización"):
            db['aviso_global'] = st.text_area("Detalles de la actualización:", value=db['aviso_global'])
            if st.button("Lanzar Actualización"):
                registrar_actividad(ADMIN_NAME, "PUBLICÓ ACTUALIZACIÓN")
                st.success("Aviso enviado a todos.")
            if st.button("Quitar Aviso"):
                db['aviso_global'] = ""
                st.rerun()

        # GESTIÓN DE MANTENIMIENTO
        with st.expander("🚧 Mantenimiento"):
            db['aviso_mantenimiento'] = st.text_area("Mensaje de cierre:", value=db['aviso_mantenimiento'])
            if db['mantenimiento']:
                if st.button("🟢 ABRIR MERCADO"):
                    db['mantenimiento'] = False; st.rerun()
            else:
                if st.button("🔴 CERRAR POR MANTENIMIENTO"):
                    db['mantenimiento'] = True; st.rerun()

        # BANEO TEMPORAL
        with st.expander("🚫 Castigos"):
            u_ban = st.text_input("Usuario a banear:")
            m_ban = st.number_input("Minutos:", min_value=1, value=5)
            if st.button("Castigar"):
                db['baneos_temporales'][u_ban] = datetime.now() + timedelta(minutes=m_ban)
                registrar_actividad(ADMIN_NAME, f"BANEÓ A {u_ban} POR {m_ban} MIN")
                st.success(f"Castigado: {u_ban}")

        # EL OJO DE TAO
        with st.expander("👁️ EL OJO DE TAO"):
            for log in db['ojo_de_tao'][:25]: st.caption(log)
            if st.button("Limpiar historial"):
                db['ojo_de_tao'] = []
                st.rerun()

# --- 7. INTERFAZ PRINCIPAL ---
mostrar_logo()

# MOSTRAR ACTUALIZACIÓN SI EXISTE (Color Info para actualizaciones)
if db['aviso_global']:
    st.info(f"✨ **NUEVA ACTUALIZACIÓN:** {db['aviso_global']}")

st.caption(f"Usuario: **{st.session_state.usuario}**")
if st.sidebar.button("🚪 Salir"): cerrar_sesion()

tabs = st.tabs(["🛒 El Muro", "📦 Mis Publicaciones", "💬 Chats", "💡 Sugerencias"])

# TAB: EL MURO
with tabs[0]:
    with st.expander("➕ Publicar algo"):
        np = st.text_input("Producto:")
        pp = st.number_input("Precio:", min_value=1)
        fp = st.file_uploader("Foto", type=['png','jpg','jpeg'])
        if st.button("🚀 Publicar"):
            db['muro'].insert(0, {"id": f"{np}_{time.time()}", "n": np, "p": pp, "v": st.session_state.usuario, "f": fp})
            registrar_actividad(st.session_state.usuario, f"PUBLICÓ: {np}")
            st.rerun()
    for i, item in enumerate(db['muro']):
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 2, 0.5])
            with c1: st.image(item['f'])
            with c2:
                st.subheader(item['n'])
                st.write(f"💰 ${item['p']} | Vende: {item['v']}")
                if st.button("Chat", key=f"c_{i}"): st.session_state.chat_activo = item['id']
            with c3:
                if st.session_state.get('es_admin_real') and st.button("🔴", key=f"d_{i}"):
                    db['muro'].pop(i); st.rerun()

# TAB: MIS PUBLICACIONES
with tabs[1]:
    st.header("Mis Artículos")
    mis = [x for x in db['muro'] if x['v'] == st.session_state.usuario]
    for m in mis:
        st.write(f"✅ {m['n']} - ${m['p']}")
        if st.button("Borrar", key=f"del_{m['id']}"):
            db['muro'] = [x for x in db['muro'] if x['id'] != m['id']]; st.rerun()

# TAB: CHATS
with tabs[2]:
    cid = st.session_state.get('chat_activo')
    if cid:
        for m in db['chats'].get(cid, []): st.write(f"**{m['u']}:** {m['t']}")
        txt = st.text_input("Mensaje:")
        if st.button("Enviar"):
            db['chats'].setdefault(cid, []).append({"u": st.session_state.usuario, "t": txt}); st.rerun()

# TAB: SUGERENCIAS
with tabs[3]:
    st.header("💡 Sugerencias")
    s_in = st.text_area("¿Cómo mejorar?")
    if st.button("Enviar Sugerencia"):
        db['sugerencias'].insert(0, {"u": st.session_state.usuario, "t": s_in, "h": datetime.now().strftime("%H:%M")})
        st.success("Enviado.")
    if st.session_state.get('es_admin_real'):
        st.divider()
        for s in db['sugerencias']: st.write(f"**{s['u']}**: {s['t']}")
