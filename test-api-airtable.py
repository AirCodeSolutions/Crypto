import streamlit as st
from pyairtable import Api
from pyairtable.api.table import Table
import streamlit as st
import time
import pandas as pd
from datetime import datetime
import logging

# Clés et configurations (à mettre dans .streamlit/secrets.toml sur Streamlit Cloud)
api_key = st.secrets["api_key"]
base_id = "appwYozXBGggzUjCW"
table_id = "tblEthZxlqwvYqK3R"

st.title("Test de connexion Airtable")

try:
    # Création de l'API
    api = Api(api_key)
    
    # Création de la table
    table = Table(api, base_id, table_id)
    
    # Test de récupération des données
    records = table.all()
    
    st.success("✅ Connexion réussie à Airtable!")
    st.write(f"Nombre d'enregistrements trouvés : {len(records)}")
    
    # Affichage des enregistrements
    if records:
        st.write("Premier enregistrement :")
        st.write(records[0])
    
except Exception as e:
    st.error(f"❌ Erreur de connexion : {str(e)}")