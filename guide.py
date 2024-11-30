from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class TradingGuide:
    """Classe principale pour gérer le guide de trading"""
    
    @dataclass
    class Section:
        """Structure pour une section du guide"""
        title: str
        content: str
        subsections: Dict[str, str] = field(default_factory=dict)
    
    sections: Dict[str, Section] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialise les sections du guide avec leur contenu"""
        self.sections = {
            "quick_start": self.Section(
                title="Guide de Démarrage Rapide Test",
                content=self._get_quick_start_content(),
                subsections={
                    "setup": "Configuration Initiale",
                    "criteria": "Critères de Sélection",
                    "validation": "Validation d'une Entrée",
                    "management": "Gestion des Positions"
                }
            ),
            "scoring": self.Section(
                title="Système de Scoring",
                content=self._get_scoring_content(),
                subsections={
                    "global": "Score Global (0-1)",
                    "rsi": "RSI (40%)",
                    "volume": "Volume (30%)",
                    "trend": "Tendance (30%)",
                    "interpretation": "Interprétation"
                }
            ),
            "risk_management": self.Section(
                title="Gestion des Risques",
                content=self._get_risk_management_content(),
                subsections={
                    "rules": "Règles de Base",
                    "diversification": "Diversification",
                    "protection": "Protection du Capital"
                }
            )
        }

    def _get_quick_start_content(self) -> str:
        return """
        # Guide de Démarrage Rapide
        
        ## Configuration Initiale
        - Capital initial: 100€ maximum pour débuter
        - Risque maximum: 1.5% par trade
        - Focus: 2-3 cryptos principales
        
        ## Critères de Sélection
        - Prix: entre 0.01 et 5 USDT
        - RSI: entre 30-45
        - Volume minimum: 50,000 USDT
        - Tendance: 3/5 bougies vertes minimum
        - Indicateur: MACD haussier
        
        ## Validation d'une Entrée
        1. Score technique supérieur à 0.7
        2. Volume en confirmation
        3. Alignement multi-timeframes
        
        ## Gestion des Positions
        - Stop loss systématique à -1.5%
        - Objectif de profit à +3%
        - Maximum 2 positions simultanées
        """
    
    def _get_scoring_content(self) -> str:
        return """
        # Système de Scoring
        
        ## Score Global (0-1)
        
        ### RSI (40%)
        - 0.4 : RSI entre 35-40
        - 0.3 : RSI entre 30-35 ou 40-45
        - 0.0 : RSI hors zones optimales
        
        ### Volume (30%)
        - 0.3 : Volume > 150% de la moyenne
        - 0.2 : Volume > 100% de la moyenne
        - 0.0 : Volume inférieur à la moyenne
        
        ### Tendance (30%)
        - 0.3 : EMA9 > EMA20 et MACD haussier
        - 0.2 : EMA9 > EMA20 uniquement
        - 0.0 : Absence de tendance claire
        
        ## Interprétation
        - Score > 0.8 : Configuration idéale
        - Score > 0.7 : Setup favorable
        - Score < 0.7 : En attente de meilleure opportunité
        """

    def _get_risk_management_content(self) -> str:
        return """
        # Gestion des Risques
        
        ## Règles de Base
        - Capital et Position
            * Maximum 100€ pour débuter
            * 30-35€ par position maximum
            * Stop loss systématique -1.5%
            * Take profit +3%
        
        ## Diversification
        - Maximum 2 positions simultanées
        - Uniquement des cryptos différentes
        - Maximum 60% du capital total engagé
        
        ## Protection du Capital
        - Règles Essentielles
            1. Interdiction de martingale
            2. Gestion émotionnelle stricte
            3. Stop loss obligatoire
            4. Prise de profits systématique
        """

@dataclass
class Documentation:
    """Documentation technique de l'application"""
    api_docs: Dict[str, Dict[str, List[str]]] = field(default_factory=dict)
    error_codes: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialise la documentation technique"""
        self.api_docs = {
            "exchange": {
                "description": "Interface avec KuCoin",
                "methods": [
                    "get_valid_symbol",
                    "fetch_ticker",
                    "fetch_ohlcv"
                ]
            },
            "indicators": {
                "description": "Indicateurs techniques",
                "methods": [
                    "calculate_rsi",
                    "calculate_support_resistance",
                    "detect_divergence"
                ]
            },
            "portfolio": {
                "description": "Gestion du portfolio",
                "methods": [
                    "add_position",
                    "update_positions",
                    "close_position"
                ]
            }
        }
        
        self.error_codes = {
            "E001": "Erreur de connexion à l'exchange",
            "E002": "Symbole invalide",
            "E003": "Capital insuffisant",
            "E004": "Erreur de calcul d'indicateur",
            "E005": "Position inexistante"
        }

    def get_api_documentation(self) -> Dict[str, Dict[str, List[str]]]:
        """Retourne la documentation de l'API"""
        return self.api_docs
    
    def get_error_codes(self) -> Dict[str, str]:
        """Retourne les codes d'erreur"""
        return self.error_codes

# Fonction principale pour initialiser la documentation
def initialize_documentation() -> Tuple[TradingGuide, Documentation]:
    """
    Initialise et retourne les instances du guide et de la documentation
    
    Returns:
        Tuple[TradingGuide, Documentation]: Guide de trading et documentation technique
    """
    guide = TradingGuide()
    docs = Documentation()
    return guide, docs