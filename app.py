import streamlit as st
from datetime import datetime, timedelta
import time

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mercado Comunidad", page_icon="🛒", layout="centered")

# --- 2. SEGURIDAD MAESTRA ---
PASSWORD_TAO = "tao"  
ADMIN_NAME = "Tao_Creator"

# --- 3. BASE DE DATOS GLOBAL (COMPARTIDA POR TODOS) ---
@st.cache_resource
def obtener_db_global():
    return {
        'muro': [],               
        'chats': {},              
        'baneos_temporales': {},  # Diccionario: {usuario: hora_fin_castigo}
        'ojo_de_tao': [],         
        'mantenimiento': False,   
        'aviso_mantenimiento': "La aplicación está en mantenimiento técnico.",
        'sugerencias': []         
    }

db = obtener_db_global()

def registrar_actividad(usuario, accion):
    ahora = datetime.now().strftime("%H:%M:%S")
    db['ojo_de_tao'].insert(0, f"📌 [{ahora}] | 👤 {usuario}: {accion}")

# --- 4. ESTÉTICA DE LA CABECERA ---
def mostrar_logo():
    st.markdown("""
        <div style='text-align: center; background-color: #fce4ec; padding: 15px; border-radius: 15px; border: 3px solid #e91e63;'>
            <h1 style='color: #880e4f; margin: 0;'>🛒 MERCADO COMUNIDAD</h1>
            <p style='color: #ad1457; font-weight: bold;'>Plataforma Sincronizada - Creado por Tao_Creator</p>
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

# --- 6. LOGIN DISCRETO CON BANEO TEMPORAL ---
if 'usuario' not in st.session_state:
    mostrar_logo()
    
    with st.container(border=True):
        st.subheader("👤 Identificarse")
        nombre_in = st.text_input("Nombre de usuario:")
        
        # Solo aparece la llave maestra si el nombre coincide con el tuyo
        pass_in = ""
        if nombre_in == ADMIN_NAME:
            pass_in = st.text_input("Llave Maestra:", type="password")
        
        if st.button("Entrar", use_container_width=True):
            ahora = datetime.now()
            
            # Verificar si está baneado temporalmente
            esta_baneado = False
            if nombre_in in db['baneos_temporales']:
                fin_ban = db['baneos_temporales'][nombre_in]
                if ahora < fin_ban:
                    minutos_faltan = int((fin_ban - ahora).total_seconds() / 60)
                    st.error(f"🚫 Acceso denegado. Estás baneado temporalmente. Podrás volver en {minutos_faltan + 1} minuto(s).")
                    esta_baneado = True
                else:
                    del db['baneos_temporales'][nombre_in] # El tiempo ya pasó

            if not esta_baneado:
                # 1. Es el Creador (Tao_Creator)
                if nombre_in == ADMIN_NAME:
                    if pass_in == PASSWORD_TAO:
                        st.session_state.usuario = nombre_in
                        st.session_state.es_admin_real = True
                        registrar_actividad(nombre_in, "ENTRÓ (CREADOR)")
                        st.rerun()
                    else:
                        st.error("❌ Llave incorrecta.")
                
                # 2. El mercado está en mantenimiento (Silencioso)
                elif db['mantenimiento']:
                    st.error(f"🛠️ {db['aviso_mantenimiento']}")
                
                # 3. Usuario común entra
                elif nombre_in.strip():
                    st.session_state.usuario = nombre_in
                    st.session_state.es_admin_real = False
                    registrar_actividad(nombre_in, "ENTRÓ")
                    st.rerun()
                else:
                    st.warning("Por favor, ingresá un nombre.")
    st.stop()

# --- 7. PANEL DE CONTROL TAO (LATERAL) ---
if st.session_state.get('es_admin_real', False):
    with st.sidebar:
        st.error(f"👑 PANEL DE CONTROL")
        
        with st.expander("🎭 Modo Infiltrado"):
            if st.session_state.get('nombre_falso_activo'):
                st.info(f"Disfraz: {st.session_state.usuario}")
                if st.button("🔙 Volver a mi identidad"):
                    st.session_state.usuario = ADMIN_NAME
                    st.session_state.nombre_falso_activo = False
                    st.rerun()
            else:
                nf = st.text_input("Nombre falso:")
                if st.button("Infiltrarse"):
                    st.session_state.usuario = nf
                    st.session_state.nombre_falso_activo = True
                    st.rerun()

        with st.expander("🚧 Gestión y Castigos"):
            # Baneo Temporal
            u_ban = st.text_input("Usuario a castigar:")
            mins = st.number_input("Minutos de baneo:", min_value=1, value=5)
            if st.button("BANEAR TEMPORALMENTE"):
                db['baneos_temporales'][u_ban] = datetime.now() + timedelta(minutes=mins)
                registrar_actividad(ADMIN_NAME, f"BANEÓ A {u_ban} POR {mins} MIN")
                st.success(f"Usuario {u_ban} castigado.")

            st.divider()
            # Mantenimiento
            btn_txt = "🟢 ABRIR MERCADO" if db['mantenimiento'] else "🔴 CERRAR (Mante)"
            if st.button(btn_txt):
                db['mantenimiento'] = not db['mantenimiento']
                st.rerun()

        with st.expander("👁️ EL OJO DE TAO"):
            for log in db['ojo_de_tao'][:25]:
                st.caption(log)
            if st.button("Limpiar historial"):
                db['ojo_de_tao'] = []
                st.rerun()

# --- 8. INTERFAZ DE USUARIO ---
mostrar_logo()
st.caption(f"Conectado como: **{st.session_state.usuario}**")
if st.sidebar.button("🚪 Cerrar Sesión"): cerrar_sesion()

tabs = st.tabs(["🛒 El Muro", "📦 Mis Publicaciones", "💬 Chats", "💡 Sugerencias"])

# TAB: EL MURO
with tabs[0]:
    with st.expander("➕ Publicar algo nuevo"):
        n_p = st.text_input("Producto:")
        p_p = st.number_input("Precio ARS $:", min_value=1)
        f_p = st.file_uploader("Subir foto", type=['png','jpg','jpeg'])
        if st.button("🚀 Publicar", disabled=not f_p):
            db['muro'].insert(0, {"id": f"{n_p}_{time.time()}", "n": n_p, "p": p_p, "v": st.session_state.usuario, "f": f_p})
            registrar_actividad(st.session_state.usuario, f"PUBLICÓ: {n_p}")
            st.rerun()

    for i, item in enumerate(db['muro']):
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 2, 0.5])
            with col1: st.image(item['f'])
            with col2:
                st.subheader(item['n'])
                st.write(f"💰 ARS ${item['p']} | Vende: {item['v']}")
                if st.button(f"💬 Chat", key=f"chat_{i}"): st.session_state.chat_activo = item['id']
            with col3:
                if st.session_state.get('es_admin_real'):
                    if st.button("🔴", key=f"del_{i}"):
                        db['muro'].pop(i); st.rerun()

# TAB: MIS PUBLICACIONES
with tabs[1]:
    st.header("Mis Artículos")
    mis_art = [x for x in db['muro'] if x['v'] == st.session_state.usuario]
    for m in mis_art:
        with st.container(border=True):
            st.write(f"✅ **{m['n']}** | ${m['p']}")
            if st.button("🗑️ Eliminar", key=f"del_mio_{m['id']}"):
                db['muro'] = [x for x in db['muro'] if x['id'] != m['id']]
                st.rerun()

# TAB: CHATS
with tabs[2]:
    cid = st.session_state.get('chat_activo')
    if cid:
        for m in db['chats'].get(cid, []): st.write(f"**{m['u']}:** {m['t']}")
        txt = st.text_input("Escribir mensaje:")
        if st.button("Enviar"):
            db['chats'].setdefault(cid, []).append({"u": st.session_state.usuario, "t": txt})
            st.rerun()
    else: st.info("Elegí un producto del muro para chatear.")

# TAB: SUGERENCIAS
with tabs[3]:
    st.header("💡 Sugerencias")
    nueva_s = st.text_area("¿Qué podemos mejorar?")
    if st.button("Enviar"):
        db['sugerencias'].insert(0, {"u": st.session_state.usuario, "t": nueva_s, "h": datetime.now().strftime("%H:%M")})
        st.success("¡Gracias! Tao_Creator lo revisará.")
    if st.session_state.get('es_admin_real'):
        st.divider()
        st.subheader("🕵️ Buzón Privado")
        for s in db['sugerencias']:
            st.write(f"**{s['u']}** ({s['h']}): {s['t']}")
