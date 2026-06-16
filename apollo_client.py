import requests
import os

def get_api_key():
    try:
        import streamlit as st
        return st.secrets.get("APOLLO_API_KEY", os.getenv("APOLLO_API_KEY", ""))
    except Exception:
        return os.getenv("APOLLO_API_KEY", "")

BASE = "https://api.apollo.io/v1"

def headers():
    return {"Content-Type": "application/json", "Cache-Control": "no-cache"}


def test_connection() -> tuple[bool, str]:
    try:
        r = requests.post(f"{BASE}/auth/health",
                          json={"api_key": get_api_key()},
                          headers=headers(), timeout=10)
        if r.status_code == 200:
            return True, "Apollo conectado ✅"
        return False, f"Error {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return False, str(e)


def buscar_leads(titulo="Procurement Manager", paises=None, pagina=1, por_pagina=25) -> dict:
    if paises is None:
        paises = ["Panama", "Costa Rica", "Colombia", "Guatemala", "Dominican Republic"]
    payload = {
        "api_key": get_api_key(),
        "page": pagina,
        "per_page": por_pagina,
        "person_titles": [titulo],
        "person_locations": paises,
        "contact_email_status": ["verified", "likely to engage"],
    }
    try:
        r = requests.post(f"{BASE}/mixed_people/search",
                          json=payload, headers=headers(), timeout=15)
        if r.status_code == 200:
            return r.json()
        return {"error": f"{r.status_code}: {r.text[:300]}"}
    except Exception as e:
        return {"error": str(e)}


def obtener_stats_secuencia(sequence_id="6a277369cff2870014970d16") -> dict:
    try:
        r = requests.get(
            f"{BASE}/emailer_campaigns/{sequence_id}",
            params={"api_key": get_api_key()},
            headers=headers(), timeout=10
        )
        if r.status_code == 200:
            return r.json()
        return {"error": f"{r.status_code}: {r.text[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def enrolar_contacto(contact_id: str, sequence_id="6a277369cff2870014970d16",
                     mailbox_id="6a14d2271d3a61001c4d3b7d") -> tuple[bool, str]:
    payload = {
        "api_key": get_api_key(),
        "contact_ids": [contact_id],
        "emailer_campaign_id": sequence_id,
        "send_email_from_email_account_id": mailbox_id,
    }
    try:
        r = requests.post(f"{BASE}/emailer_campaigns/add_contact_ids",
                          json=payload, headers=headers(), timeout=10)
        if r.status_code == 200:
            return True, "Contacto enrolado"
        return False, f"Error {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return False, str(e)
