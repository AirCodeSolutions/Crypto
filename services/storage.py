from typing import Dict, List, Optional, TypedDict
from datetime import datetime, timedelta
from dataclasses import dataclass
from pyairtable import Api, Base, Table
import logging
from config.settings import AIRTABLE_SETTINGS
import streamlit as st

logger = logging.getLogger(__name__)

class AirtableRecordData(TypedDict):
    """Structure de données pour un enregistrement Airtable"""
    id: str
    fields: Dict
    createdTime: str

@dataclass
class CryptoData:
    """Structure de données pour les cryptos suivies"""
    symbol: str
    added_date: datetime
    user_id: str
    notes: Optional[str] = None

class AirtableService:
    """Gestion du stockage avec Airtable"""
    
    def __init__(self):
        """Initialise la connexion à Airtable"""
        try:
            # Récupération des secrets de manière sécurisée
            #self.api_key = st.secrets["AIRTABLE_API_KEY"]
            #self.base_id = st.secrets["AIRTABLE_BASE_ID"]
            self.api = Api(st.secrets["AIRTABLE_API_KEY"])
            self.base = Base(self.api, "appwYozXBGggzUjCW")

            # Debug - Affichons ce qu'on fait
            st.write("Création de la table...")
            st.write("Base ID:", self.base)
            self.utilisateurs = self.base.table("tblEthZxlqwvYqK3R")
            st.write("Table créée:", self.utilisateurs)

            #self.utilisateurs = self.base.table("tblEthZxlqwvYqK3R")
            logger.info("Service Airtable initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur d'initialisation du service Airtable: {e}")
            raise

 
    def utilisateurs(self):
        """Retourne la table utilisateurs"""
        return self._table           
            
    
    def test_connection(self) -> bool:
        """Teste la connexion à Airtable"""
        try:
            # Tente de lire un enregistrement de la table cryptos
            self.cryptos_suivies.all(max_records=1)
            return True
        except Exception as e:
            logger.error(f"Erreur de connexion Airtable: {e}")
            return False

    def ajouter_crypto(self, data: CryptoData) -> Optional[AirtableRecordData]:
        """
        Ajoute une crypto suivie
        
        Args:
            data: Données de la crypto à ajouter
            
        Returns:
            Optional[AirtableRecordData]: Données de l'enregistrement créé ou None
        """
        try:
            record = self.cryptos_suivies.create({
                "symbol": data.symbol.upper(),
                "date_ajout": data.added_date.isoformat(),
                "user_id": data.user_id,
                "notes": data.notes
            })
            
            logger.info(f"Crypto {data.symbol} ajoutée avec succès")
            return record
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout de la crypto {data.symbol}: {e}")
            return None

    def get_cryptos_suivies(self, user_id: str) -> List[Dict]:
        """
        Récupère les cryptos suivies par un utilisateur
        
        Args:
            user_id: Identifiant de l'utilisateur
            
        Returns:
            List[Dict]: Liste des cryptos suivies
        """
        try:
            formula = f"{{user_id}} = '{user_id}'"
            records = self.cryptos_suivies.all(formula=formula)
            return records
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des cryptos suivies: {e}")
            return []

    def ajouter_analyse(self, symbol: str, data: Dict) -> Optional[AirtableRecordData]:
        """
        Ajoute une analyse à l'historique
        
        Args:
            symbol: Symbole de la crypto
            data: Données de l'analyse
            
        Returns:
            Optional[AirtableRecordData]: Données de l'enregistrement créé ou None
        """
        try:
            record = self.historique_analyses.create({
                "symbol": symbol.upper(),
                "date_analyse": datetime.now().isoformat(),
                "prix": data.get("prix", 0),
                "signal": data.get("signal", "NEUTRAL"),
                "score": data.get("score", 0),
                "rsi": data.get("rsi", 0),
                "volume": data.get("volume", 0),
                "details": str(data.get("details", {}))
            })
            
            logger.info(f"Analyse ajoutée pour {symbol}")
            return record
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout de l'analyse pour {symbol}: {e}")
            return None

    def get_dernieres_analyses(self, limit: int = 10) -> List[Dict]:
        """
        Récupère les dernières analyses
        
        Args:
            limit: Nombre maximal d'analyses à récupérer
            
        Returns:
            List[Dict]: Liste des dernières analyses
        """
        try:
            records = self.historique_analyses.all(
                sort=["-date_analyse"],
                max_records=limit
            )
            return records
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des analyses: {e}")
            return []

# Exemple d'utilisation
if __name__ == "__main__":
    try:
        # Initialisation du service
        storage = AirtableService()
        
        # Test de connexion
        if storage.test_connection():
            print("✅ Connexion Airtable établie!")
            
            # Exemple d'ajout d'une crypto
            crypto = CryptoData(
                symbol="BTC",
                added_date=datetime.now(),
                user_id="test_user",
                notes="Test d'ajout"
            )
            
            if storage.ajouter_crypto(crypto):
                print("✅ Crypto ajoutée avec succès!")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")