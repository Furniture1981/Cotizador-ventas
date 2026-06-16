#!/bin/bash
# Script de despliegue rápido — MAGNEX INTERNATIONAL
# Ejecutar una sola vez desde la carpeta del proyecto

set -e

echo "=== MAGNEX INTERNATIONAL — Deploy ==="

# 1. Verificar Python
python3 --version || { echo "Instala Python 3.8+"; exit 1; }

# 2. Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Entorno virtual creado"
fi

# 3. Activar e instalar dependencias
source venv/bin/activate
pip install -q streamlit pandas

# 4. Crear .env si no existe
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "⚠️  Edita el archivo .env con tus credenciales:"
    echo "    ZOHO_EMAIL=mgonzalez@magnexinternational.com"
    echo "    ZOHO_PASSWORD=tu_contraseña"
    echo ""
fi

# 5. Cargar variables del .env
export $(grep -v '^#' .env | xargs) 2>/dev/null || true

# 6. Lanzar app
echo "✅ Iniciando app en http://localhost:8501"
streamlit run app.py --server.port 8501 --server.headless true
