from typing import Dict, List, Optional, TypedDict
from datetime import datetime, timedelta
from dataclasses import dataclass
from pyairtable import Api, Base, Table
import logging
from config.settings import AIRTABLE_SETTINGS

logger = logging.getLogger(__name__)

class AirtableRecordData(TypedDict):
    """Structure de données pour un enregistrement Airtable"""
    id: str
    fields: Dict
    createdTime: str

class AirtableService:
    def __init__(self):
        """Initialise la connexion à Airtable"""
        try:
            self.api = Api(AIRTABLE_SETTINGS.API_KEY)
            self._initialize_tables()
            logger.info("Service Airtable initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur d'initialisation du service de stockage: {e}")
            raise

    def _initialize_tables(self):
        """Initialise les connexions aux tables"""
        try:
            self.cryptos_suivies = Table(
                self.api,
                AIRTABLE_SETTINGS.BASE_ID,
                AIRTABLE_SETTINGS.CRYPTOS_TABLE
            )
            
            self.historique_analyses = Table(
                self.api,
                AIRTABLE_SETTINGS.BASE_ID,
                AIRTABLE_SETTINGS.ANALYSES_TABLE
            )
            
            self.utilisateurs = Table(
                self.api,
                AIRTABLE_SETTINGS.BASE_ID,
                AIRTABLE_SETTINGS.USERS_TABLE
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des tables: {e}")
            raise

    def ajouter_crypto(self, id_utilisateur: str, symbole: str) -> Optional[AirtableRecordData]:
        """
        Ajoute une crypto suivie pour un utilisateur
        
        Args:
            id_utilisateur: Identifiant de l'utilisateur
            symbole: Symbole de la crypto à suivre
            
        Returns:
            Optional[AirtableRecordData]: Données de l'enregistrement créé ou None en cas d'erreur
        """
        try:
            record = self.cryptos_suivies.create({
                "id_utilisateur": id_utilisateur,
                "symbole": symbole.upper(),
                "date_ajout": datetime.now().isoformat()
            })
            logger.info(f"Crypto {symbole} ajoutée pour l'utilisateur {id_utilisateur}")
            return record
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout de la crypto {symbole}: {e}")
            return None