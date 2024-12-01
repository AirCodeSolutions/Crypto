from dataclasses import dataclass

@dataclass
class AirtableSettings:
    """Paramètres de configuration pour Airtable"""
    API_KEY: str = "patSoNhRnQ8WV6uPi.488183127a11c9808004735f1fb7347fbc11560bd1c473a6772d84e9384c2bcf"  # À remplacer par votre vraie clé
    BASE_ID: str = "wYozXBGggzUjCW"  # À remplacer par votre vrai ID
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