# interface/components/filter_section.py
import streamlit as st
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class FilterCriteria:
    """Structure de données pour les critères de filtrage"""
    min_volume: float = 100000.0
    max_price: float = 20.0
    min_score: float = 0.7
    timeframe: str = "1h"
    rsi_range: tuple = (30, 45)

class FilterSection:
    """Composant pour gérer les filtres de recherche d'opportunités"""
    
    def __init__(self, default_criteria: Optional[FilterCriteria] = None):
        """
        Initialise la section de filtres avec des critères par défaut ou personnalisés.
        Les critères permettent de personnaliser les valeurs initiales des filtres.
        """
        self.criteria = default_criteria or FilterCriteria()

    def render(self) -> Dict:
        """
        Affiche l'interface de filtrage et retourne les valeurs sélectionnées.
        Cette méthode crée une interface utilisateur cohérente pour le filtrage
        des opportunités de trading.
        """
        st.markdown("### 🔍 Filtres de Recherche")
        
        with st.container():
            # Première ligne de filtres
            col1, col2, col3 = st.columns(3)
            
            with col1:
                min_volume = st.number_input(
                    "Volume minimum (USDT)",
                    min_value=10000.0,
                    value=self.criteria.min_volume,
                    step=10000.0,
                    help="Volume minimal sur 24h pour considérer une crypto"
                )
                
            with col2:
                max_price = st.number_input(
                    "Prix maximum (USDT)",
                    min_value=0.1,
                    value=self.criteria.max_price,
                    step=0.1,
                    help="Prix unitaire maximum pour la crypto"
                )
                
            with col3:
                min_score = st.slider(
                    "Score minimum",
                    min_value=0.0,
                    max_value=1.0,
                    value=self.criteria.min_score,
                    help="Score technique minimum pour considérer une opportunité"
                )

            # Deuxième ligne de filtres
            col1, col2 = st.columns(2)
            
            with col1:
                timeframe = st.selectbox(
                    "Timeframe",
                    options=["5m", "15m", "1h", "4h"],
                    index=2,  # 1h par défaut
                    help="""
                    5m : Trading ultra court terme (très risqué)
                    15m : Trading intraday
                    1h : Recommandé pour débutants
                    4h : Trades plus sûrs mais moins fréquents
                    """
                )

            with col2:
                rsi_range = st.slider(
                    "Plage RSI",
                    min_value=0,
                    max_value=100,
                    value=self.criteria.rsi_range,
                    help="Plage RSI pour filtrer les opportunités"
                )

        # Retourne tous les critères dans un dictionnaire
        return {
            "min_volume": min_volume,
            "max_price": max_price,
            "min_score": min_score,
            "timeframe": timeframe,
            "rsi_range": rsi_range
        }

@dataclass
class SearchStatus:
    """Composant pour afficher l'état de la recherche"""
    
    def show_progress(self, current: int, total: int, message: str):
        """Affiche une barre de progression avec un message"""
        progress = st.progress(0)
        status = st.empty()
        
        progress.progress(current / total)
        status.text(message)
        
    def clear(self):
        """Efface les éléments de statut"""
        st.empty()