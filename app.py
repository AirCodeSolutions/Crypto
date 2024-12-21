# app.py
import os
import streamlit as st


# Configuration de la page (doit être la première commande Streamlit)
st.set_page_config(page_title="Crypto suivi by airCodeSolutions", page_icon="📈", layout="wide")

# Fonction pour récupérer la clé API
def get_airtable_key():
    try:
        # Vérifier si la clé est dans st.secrets (Streamlit Cloud)
        if "AIRTABLE_API_KEY" in st.secrets:
            return st.secrets["AIRTABLE_API_KEY"]
        else:
            # Sinon, lire le fichier secrets.toml en local
            import toml
            secrets_file = ".streamlit/secrets.toml"
            if os.path.exists(secrets_file):
                secrets = toml.load(secrets_file)
                return secrets["AIRTABLE_API_KEY"]
            else:
                st.error("Le fichier secrets.toml est manquant en local.")
                return None
    except Exception as e:
        st.error(f"Erreur lors du chargement de la clé : {str(e)}")
        return None

# Récupération de la clé
airtable_key = get_airtable_key()

# Vérification
if airtable_key:
    st.write("Clé API détectée avec succès.")
    # Pour debug uniquement, à retirer en production
    st.write("Premiers caractères de la clé :", airtable_key[:10] + "...")
else:
    st.error("Impossible de charger la clé API.")

import time
import pandas as pd
from datetime import datetime
import logging
from typing import List, Dict
from interface import TimeSelector, TradingChart, ChartConfig, GuideHelper
from services.exchange import ExchangeService
from services.storage import AirtableService
from core.analysis import MarketAnalyzer
from interface.components.alerts import AlertSystem
from interface.components.auth_manager import AuthManager
from interface.pages.live_analysis import LiveAnalysisPage

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoAnalyzerApp:
    def __init__(self):
        try:
            self.exchange = ExchangeService()
            self.analyzer = MarketAnalyzer(self.exchange)
            self.alert_system = AlertSystem()
            self.airtable = AirtableService()
            self.auth_manager = AuthManager(self.airtable)
            
            if 'analyzed_symbols' not in st.session_state:
                st.session_state.analyzed_symbols = set()
            
            if 'last_price_check' not in st.session_state:
                st.session_state.last_price_check = time.time()
            
            logger.info("Application initialisée avec succès")
            
        except Exception as e:
            logger.error(f"Erreur d'initialisation: {e}")
            raise

    def main(self):
        if not st.session_state.logged_in:
            self._show_auth_page()
            return
        self._show_main_interface()

    def _show_auth_page(self):
        st.title("Crypto Analyzer Pro - AirCodeSolutions ❤️")
        
        tab1, tab2 = st.tabs(["Connexion", "Inscription"])
        with tab1:
            self.auth_manager.render_login_form()
        with tab2:
            self.auth_manager.render_register_form()

    def _show_main_interface(self):
        st.sidebar.title(f"👤 {st.session_state.user_info['username']}")
        
        if st.sidebar.button("📤 Déconnexion"):
            self.auth_manager.logout()
            st.rerun()

        page = st.sidebar.selectbox(
            "Navigation",
            ["Analyse en Direct", "Top Performances", "Portfolio", "Paramètres", "Guide"]
        )
            
        if page == "Analyse en Direct":
            LiveAnalysisPage(
                exchange_service=self.exchange,
                analyzer_service=self.analyzer,
                alert_system=self.alert_system,
                airtable_service=self.airtable
            ).render()

        elif page == "Top Performances":
            from interface.pages.top_performance import TopPerformancePage
            top_page = TopPerformancePage(
                exchange_service=self.exchange,
                analyzer_service=self.analyzer
            )
            top_page.render()

        elif page == "Portfolio":
            self._show_portfolio_page()
                        
        elif page == "Paramètres":
            self._show_settings_page()

    def _show_portfolio_page(self):
        st.title("💼 Portfolio")
        # À implémenter

    def _show_settings_page(self):
        st.title("⚙️ Paramètres")
        settings = st.session_state.user_info.get('settings', {})
        
        with st.form("settings_form"):
            new_capital = st.number_input(
                "Capital initial (USDT)",
                min_value=0.0,
                value=float(settings.get('initial_capital', 1000))
            )
            
            new_risk = st.slider(
                "Risque par trade (%)",
                min_value=0.5,
                max_value=5.0,
                value=float(settings.get('risk_per_trade', 1.5)),
                step=0.5
            )
            
            if st.form_submit_button("Sauvegarder"):
                try:
                    self.airtable.utilisateurs.update(
                        st.session_state.user_info['id'],
                        {
                            "settings": {
                                "initial_capital": new_capital,
                                "risk_per_trade": new_risk
                            }
                        }
                    )
                    st.success("Paramètres sauvegardés !")
                    st.session_state.user_info['settings'] = {
                        "initial_capital": new_capital,
                        "risk_per_trade": new_risk
                    }
                except Exception as e:
                    st.error(f"Erreur lors de la sauvegarde: {str(e)}")

if __name__ == "__main__":
    app = CryptoAnalyzerApp()
    app.main()