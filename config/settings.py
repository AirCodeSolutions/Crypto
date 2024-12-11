import os
from dataclasses import dataclass
import streamlit as st


@dataclass
class AirtableSettings:
    """Paramètres de configuration pour Airtable"""
    API_KEY: str = st.secrets["AIRTABLE_API_KEY"]
    BASE_ID: str = st.secrets["AIRTABLE_BASE_ID"]
    CRYPTOS_TABLE: str = "cryptos_suivies"
    ANALYSES_TABLE: str = "historique_analyses"
    USERS_TABLE: str = "utilisateurs"

@dataclass
class AppSettings:
    """Paramètres généraux de l'application"""
    DEBUG: bool = True
    DEFAULT_TIMEFRAME: str = "1h"
    MAX_POSITIONS: int = 3
    RISK_PER_TRADE: float = 0.015  # 1.5%

# Instance globale des paramètres
AIRTABLE_SETTINGS = AirtableSettings()
APP_SETTINGS = AppSettings()