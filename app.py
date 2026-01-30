import streamlit as st
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mercado Comunidad", page_icon="🛒", layout="centered")

# --- 2. SEGURIDAD MAESTRA ---
PASSWORD_TAO = "TAO" 
ADMIN_NAME = "TAO_CREATOR"

# --- 3. BASE DE DATOS GLOBAL (Sincroniza a todos los usuarios en el servidor) ---
@st.cache_resource
def obtener_base_datos_global():
    return {
        'muro': [],
        'baneados': set(),
        'ojo_de_tao': [],
        'chats': {},
        'mantenimiento': False,
        'aviso_mantenimiento': "Mantenimiento técnico por Tao Wargen.",
        'sugerencias': []
    }

db = obtener_base_datos_global()

def registrar_actividad(usuario, accion):
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    registro = f"📌 [{ahora}] | 👤 {usuario}: {accion}"
    db['ojo_de_tao'].insert(0, registro)

# --- 4. ESTILO Y LOGO ---
def mostrar_logo():
    st.markdown("""
        <div style='text-align: center; background-color: #fce4ec; padding: 15px; border-radius: 15px; border: 3px solid #e91e63;'>
            <h1 style='color: #880e4f; margin: 0;'>🛒 MERCADO COMUNIDAD</h1>
            <p style='color: #ad1457; font-weight: bold;'>Plataforma Oficial de Tao Wargen</p>
        </div>
        <br>
    """, unsafe_allow_html=True)

# --- 5. LÓGICA DE CIERRE DE SESIÓN ---
def cerrar_sesion():
    if 'usuario' in st.session_state:
        registrar_actividad(st.session_state.usuario, "CERRÓ SESIÓN")
    for k in ['usuario', 'es_admin_real', 'nombre_falso_activo', 'mi_carrito', 'chat_activo']:
        if k in st.session_state: del st.session_state[k]
    st.rerun()

# --- 6. SISTEMA DE LOGIN (CON PASE VIP PARA ADMIN) ---
if 'usuario' not in st.session_state:
    mostrar_logo()
    if db['mantenimiento']:
        st.warning("⚠️ EL MERCADO ESTÁ EN MANTENIMIENTO. Solo el administrador puede entrar ahora.")

    with st.container(border=True):
        st.subheader("👤 Identificarse")
        nombre_in = st.text_input("Nombre de usuario:")
        pass_in = ""
        if nombre_in == ADMIN_NAME:
            pass_in = st.text_input("Llave Maestra de Tao:", type="password")
        
        if st.button("Entrar al Mercado", use_container_width=True):
            if nombre_in in db['baneados']:
                st.error("🚫 Tu acceso ha sido revocado permanentemente.")
            elif nombre_in == ADMIN_NAME:
                if pass_in == PASSWORD_TAO:
                    st.session_state.usuario = nombre_in
                    st.session_state.es_admin_real = True
                    st.session_state.nombre_falso_activo = False
                    registrar_actividad(nombre_in, "ENTRÓ (MODO ADMIN)")
                    st.rerun()
                else:
                    st.error("❌ Llave maestra incorrecta.")
            elif db['mantenimiento']:
                st.error("🛠️ Acceso denegado: El mercado está cerrado por mantenimiento.")
            elif not nombre_in.strip():
                st.warning("Por favor, escribí un nombre.")
            else:
                st.session_state.usuario = nombre_in
                st.session_state.es_admin_real = False
                registrar_actividad(nombre_in, "ENTRÓ AL MERCADO")
                st.rerun()
    st.stop()

# --- 7. BLOQUEO DE MANTENIMIENTO POST-LOGIN ---
# Si sos usuario normal y activan el mantenimiento mientras estás dentro, esto te saca.
if db['mantenimiento'] and not st.session_state.get('es_admin_real', False):
    mostrar_logo()
    st.markdown(f"""
        <div style='text-align: center; background-color: #1a1a1a; padding: 60px; border-radius: 30px; border: 5px solid red;'>
            <h1 style='color: white;'>🛠️ MANTENIMIENTO ACTIVADO</h1>
            <p style='color: #eeeeee; font-size: 20px;'>"{db['aviso_mantenimiento']}"</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Cerrar Sesión"): cerrar_sesion()
    st.stop()

# --- 8. PANEL DE ADMINISTRADOR (LATERAL) ---
if st.session_state.get('es_admin_real', False):
    with st.sidebar:
        st.error(f"👑 CONTROL DE {ADMIN_NAME}")
        
        # MODO INCOGNITO
        st.subheader("🕵️ Identidad Oculta")
        if not st.session_state.get('nombre_falso_activo'):
            nf = st.text_input("Nuevo nombre falso:")
            if st.button("🎭 Cambiar Identidad"):
                if nf.strip() and nf != ADMIN_NAME:
                    st.session_state.usuario = nf
                    st.session_state.nombre_falso_activo = True
                    registrar_actividad(ADMIN_NAME, f"INFILTRADO COMO: {nf}")
                    st.rerun()
        else:
            st.warning(f"Actualmente sos: {st.session_state.usuario}")
            if st.button("🔙 Volver a TAO_CREATOR"):
                st.session_state.usuario = ADMIN_NAME
                st.session_state.nombre_falso_activo = False
                st.rerun()

        st.divider()
        st.subheader("🚧 Gestión de Mantenimiento")
        txt_mante = st.text_area("Mensaje de bloqueo:", value=db['aviso_mantenimiento'])
        label_btn = "🟢 ABRIR MERCADO" if db['mantenimiento'] else "🔴 CERRAR MERCADO"
        if st.button(label_btn):
            db['mantenimiento'] = not db['mantenimiento']
            db['aviso_mantenimiento'] = txt_mante
            registrar_actividad(ADMIN_NAME, f"ESTADO MANTENIMIENTO: {db['mantenimiento']}")
            st.rerun()
        
        st.divider()
        st.subheader("👁️ OJO DE TAO (Actividad Global)")
        for log in db['ojo_de_tao'][:20]: st.caption(log)
        
        st.divider()
        u_a_ban = st.text_input("Usuario a banear:")
        if st.button("EJECUTAR BAN"): 
            db['baneados'].add(u_a_ban)
            registrar_actividad(ADMIN_NAME, f"BANEÓ A: {u_a_ban}")
            st.success(f"Usuario {u_a_ban} bloqueado.")
            st.rerun()

# --- 9. INTERFAZ PRINCIPAL ---
mostrar_logo()
st.caption(f"Sesión activa: **{st.session_state.usuario}**")

if st.sidebar.button("🚪 Cerrar Sesión"): cerrar_sesion()

tabs = st.tabs(["🛒 El Muro", "📦 Mis Publicaciones", "🛍️ Carrito", "💬 Chats"])

# --- TAB 1: EL MURO ---
with tabs[0]:
    with st.expander("➕ Publicar Nuevo Producto"):
        c1, c2 = st.columns(2)
        with c1:
            prod_n = st.text_input("¿Qué vendés?")
            prod_p = st.number_input("Precio ARS $:", min_value=1)
        with c2:
            es_sub = st.checkbox("¿Es subasta?")
            foto_p = st.file_uploader("Foto Principal (Obligatoria)", type=['png', 'jpg', 'jpeg'])
        
        if st.button("🚀 Publicar", disabled=(not foto_p or not prod_n)):
            id_p = f"{prod_n}_{datetime.now().timestamp()}"
            db['muro'].insert(0, {
                "id": id_p, "n": prod_n, "p": prod_p, "v": st.session_state.usuario, 
                "s": es_sub, "g": "Nadie", "f": foto_p
            })
            registrar_actividad(st.session_state.usuario, f"PUBLICÓ: {prod_n}")
            st.rerun()

    for i, item in enumerate(db['muro']):
        with st.container(border=True):
            ci, ct, cc = st.columns([1.5, 2.5, 0.8])
            with ci: st.image(item['f'], use_container_width=True)
            with ct:
                st.subheader(item['n'])
                if item['s']:
                    st.info(f"🔨 Puja: ARS ${item['p']} | Líder: {item['g']}")
                    of = st.number_input("Ofertar:", min_value=int(item['p']+1), key=f"of_{i}")
                    if st.button("Ofertar", key=f"bof_{i}"):
                        item['p'] = of; item['g'] = st.session_state.usuario
                        registrar_actividad(st.session_state.usuario, f"OFERTÓ ARS ${of} en {item['n']}")
                        st.rerun()
                else:
                    st.write(f"💰 **ARS ${item['p']}** | Vendedor: {item['v']}")
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button("🛒 Guardar", key=f"ca_{i}"):
                            st.session_state.setdefault('mi_carrito', []).append(item)
                            st.toast("Añadido al carrito")
                    with col_b2:
                        if st.button("💬 Chat", key=f"ch_{i}"):
                            st.session_state.chat_activo = item['id']
                            st.toast("Abrí la pestaña de Chats")
            with cc:
                if st.session_state.get('es_admin_real'):
                    if st.button("🔴", key=f"t_{i}"):
                        db['muro'].pop(i)
                        registrar_actividad(ADMIN_NAME, f"BORRÓ PRODUCTO: {item['n']}")
                        st.rerun()

# --- TAB 2: MIS PUBLICACIONES ---
with tabs[1]:
    st.header("📦 Mis Artículos")
    mis_articulos = [p for p in db['muro'] if p['v'] == st.session_state.usuario]
    if not mis_articulos:
        st.info("Todavía no publicaste nada.")
    else:
        for idx, mi_p in enumerate(mis_articulos):
            with st.container(border=True):
                ca, cb, cc = st.columns([1, 2, 1])
                with ca: st.image(mi_p['f'], width=80)
                with cb: st.write(f"**{mi_p['n']}**\nARS ${mi_p['p']}")
                with cc:
                    if st.button("🗑️ Quitar", key=f"del_mio_{idx}"):
                        indice_real = next(i for i, x in enumerate(db['muro']) if x['id'] == mi_p['id'])
                        db['muro'].pop(indice_real)
                        registrar_actividad(st.session_state.usuario, f"ELIMINÓ SU PROPIO ARTÍCULO: {mi_p['n']}")
                        st.rerun()

# --- TAB 3: CARRITO ---
with tabs[2]:
    st.header("🛍️ Mi Carrito")
    carrito = st.session_state.get('mi_carrito', [])
    for c in carrito: st.write(f"📦 {c['n']} - ARS ${c['p']} (Vendedor: {c['v']})")

# --- TAB 4: CHATS ---
with tabs[3]:
    cid = st.session_state.get('chat_activo')
    if cid:
        prod = next((x for x in db['muro'] if x['id'] == cid), None)
        if prod:
            st.subheader(f"Chat: {prod['n']}")
            msjs = db['chats'].get(cid, [])
            for m in msjs: st.write(f"**{m['u']}:** {m['t']}")
            n_m = st.text_input("Mensaje:", key="in_chat")
            if st.button("Enviar"):
                db['chats'].setdefault(cid, []).append({"u": st.session_state.usuario, "t": n_m})
                st.rerun()
    else:
        st.write("Elegí un producto en el muro para hablar con el vendedor.")
