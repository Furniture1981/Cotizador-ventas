import streamlit as st
import os
from email_sender import enviar_email, probar_conexion, get_zoho_creds
from apollo_client import test_connection, buscar_leads, obtener_stats_secuencia, enrolar_contacto
from database import obtener_leads, registrar_email_enviado, actualizar_estado_lead

st.set_page_config(page_title="Automatización", page_icon="📧", layout="wide")
st.title("📧 Automatización — MAGNEX INTERNATIONAL")

tab_apollo, tab_email = st.tabs(["🚀 Apollo.io", "📤 Emails Zoho"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — APOLLO
# ══════════════════════════════════════════════════════════════════════════════
with tab_apollo:
    st.subheader("Apollo.io — Gestión de secuencias")

    col_status, col_btn = st.columns([3, 1])
    with col_btn:
        if st.button("🔌 Probar conexión Apollo"):
            ok, msg = test_connection()
            if ok:
                st.success(msg)
            else:
                st.error(msg)

    st.divider()

    # Stats secuencia activa
    st.subheader("📊 Secuencia activa — Pintura Industrial")
    if st.button("Actualizar stats"):
        data = obtener_stats_secuencia()
        if "error" in data:
            st.error(data["error"])
        else:
            camp = data.get("emailer_campaign", {})
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Nombre", camp.get("name", "-"))
            c2.metric("Estado", camp.get("active", "-"))
            c3.metric("Contactos", camp.get("contact_count", "-"))
            c4.metric("Emails enviados", camp.get("num_steps", "-"))

    st.divider()

    # Buscar nuevos leads
    st.subheader("🔍 Buscar nuevos leads en Apollo")
    TITULOS = ["Procurement Manager", "Purchasing Manager", "Supply Chain Manager",
               "Operations Manager", "Gerente de Compras", "Director de Operaciones"]
    PAISES_OP = ["Panama", "Costa Rica", "Colombia", "Guatemala", "Dominican Republic",
                 "Honduras", "El Salvador", "Mexico"]

    c1, c2, c3 = st.columns(3)
    titulo_sel  = c1.selectbox("Cargo objetivo", TITULOS)
    paises_sel  = c2.multiselect("Países", PAISES_OP,
                                  default=["Panama", "Costa Rica", "Colombia"])
    por_pag     = c3.number_input("Resultados", 10, 100, 25)

    if st.button("🔍 Buscar leads", type="primary"):
        with st.spinner("Buscando en Apollo..."):
            resultado = buscar_leads(titulo_sel, paises_sel, por_pagina=por_pag)

        if "error" in resultado:
            st.error(resultado["error"])
        else:
            personas = resultado.get("people", resultado.get("contacts", []))
            st.success(f"✅ {len(personas)} leads encontrados")

            if personas:
                import pandas as pd
                filas = []
                for p in personas:
                    filas.append({
                        "Nombre":   f"{p.get('first_name','')} {p.get('last_name','')}".strip(),
                        "Empresa":  p.get("organization", {}).get("name", p.get("company", "")),
                        "Cargo":    p.get("title", ""),
                        "Email":    p.get("email", ""),
                        "País":     p.get("country", ""),
                        "ID":       p.get("id", ""),
                    })
                df = pd.DataFrame(filas)
                st.dataframe(df[["Nombre","Empresa","Cargo","Email","País"]],
                             use_container_width=True, hide_index=True)

                if st.button("➕ Enrolar todos en secuencia Pintura Industrial"):
                    ok_n = 0
                    for p in personas:
                        if p.get("id"):
                            exito, _ = enrolar_contacto(p["id"])
                            if exito:
                                ok_n += 1
                    st.success(f"✅ {ok_n}/{len(personas)} contactos enrolados en la secuencia")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ZOHO EMAIL
# ══════════════════════════════════════════════════════════════════════════════
with tab_email:
    st.subheader("Zoho Mail — Envío de emails")

    with st.sidebar:
        st.subheader("⚙️ Zoho SMTP")
        zoho_user_default, zoho_pass_default = get_zoho_creds()
        smtp_user = st.text_input("Email", value=zoho_user_default)
        smtp_pass = st.text_input("Contraseña", type="password", value=zoho_pass_default)
        if st.button("🔌 Probar Zoho"):
            ok, msg = probar_conexion(smtp_user, smtp_pass)
            st.success(msg) if ok else st.error(msg)

    TEMPLATES = {
        "Pintura Industrial — Primer contacto": {
            "asunto": "Cotización Pintura Industrial — MAGNEX INTERNATIONAL",
            "cuerpo": """Estimado/a {nombre},

Mi nombre es Miguel González, CEO de MAGNEX INTERNATIONAL, empresa panameña especializada en intermediación de commodities industriales.

Contamos con acceso a proveedores certificados de pintura industrial (anticorrosiva, epóxica, marina) a precios FOB competitivos desde China.

¿Tiene 15 minutos esta semana para revisar una propuesta sin compromiso?

Saludos,
Miguel González | CEO — MAGNEX INTERNATIONAL
mgonzalez@magnexinternational.com | +507 6593-3059
"Connecting Markets. Delivering Trust."
""",
        },
        "Seguimiento — Sin respuesta": {
            "asunto": "Seguimiento — MAGNEX INTERNATIONAL",
            "cuerpo": """Estimado/a {nombre},

Le escribo para hacer seguimiento a mi mensaje anterior sobre suministro de {producto} para {empresa}.

¿Tuvo oportunidad de revisarlo?

Saludos,
Miguel González | MAGNEX INTERNATIONAL
""",
        },
    }

    c1, c2 = st.columns(2)
    tmpl_sel      = c1.selectbox("Plantilla", list(TEMPLATES.keys()))
    estado_filtro = c2.selectbox("Leads con estado", ["nuevo", "contactado"])
    max_env       = st.number_input("Máximo envíos", 1, 50, 10)

    leads_disp = obtener_leads(estado=estado_filtro)[:max_env]
    st.info(f"Se enviarán a **{len(leads_disp)} leads**")

    if leads_disp:
        ej = leads_disp[0]
        preview = TEMPLATES[tmpl_sel]["cuerpo"].format(
            nombre=ej.get("nombre",""), empresa=ej.get("empresa",""),
            producto=ej.get("producto",""))
        with st.expander("Vista previa"):
            st.text(preview)

    if st.button("🚀 ENVIAR EMAILS", type="primary", disabled=not leads_disp):
        if not smtp_user or not smtp_pass:
            st.error("Configura Zoho en la barra lateral.")
        else:
            prog = st.progress(0)
            ok_n = 0
            for i, lead in enumerate(leads_disp):
                cuerpo = TEMPLATES[tmpl_sel]["cuerpo"].format(
                    nombre=lead.get("nombre",""),
                    empresa=lead.get("empresa",""),
                    producto=lead.get("producto",""))
                exito, _ = enviar_email(smtp_user, smtp_pass, lead["email"],
                                        TEMPLATES[tmpl_sel]["asunto"], cuerpo)
                actualizar_estado_lead(lead["id"], "contactado" if exito else lead["estado"])
                registrar_email_enviado(lead["id"], lead["email"],
                                        TEMPLATES[tmpl_sel]["asunto"],
                                        "enviado" if exito else "error")
                if exito:
                    ok_n += 1
                prog.progress((i + 1) / len(leads_disp))
            st.success(f"✅ {ok_n}/{len(leads_disp)} emails enviados")

    st.divider()
    st.subheader("Email individual")
    with st.form("email_ind"):
        dest   = st.text_input("Destinatario")
        asunto = st.text_input("Asunto")
        cuerpo = st.text_area("Mensaje", height=200)
        if st.form_submit_button("Enviar"):
            if not smtp_user or not smtp_pass:
                st.error("Configura Zoho.")
            else:
                ok, msg = enviar_email(smtp_user, smtp_pass, dest, asunto, cuerpo)
                st.success(f"✅ Enviado a {dest}") if ok else st.error(f"❌ {msg}")
