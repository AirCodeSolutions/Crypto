# interface/components/trade_card.py
import streamlit as st
from dataclasses import dataclass
from typing import Dict, Optional, List

@dataclass
class TradeCardData:
    """Structure de données pour une carte de trading"""
    symbol: str
    price: float
    score: float
    volume: float
    change_24h: float
    stop_loss: Optional[float] = None
    target_1: Optional[float] = None
    target_2: Optional[float] = None
    reasons: List[str] = None

class TradeCard:
    """Composant réutilisable pour afficher une opportunité de trading"""
    
    def __init__(self, data: TradeCardData):
        self.data = data
    
    def render(self):
        """Affiche la carte de trading dans l'interface Streamlit"""
        with st.expander(f"💫 {self.data.symbol} - Score: {self.data.score:.2f}"):
            # Métriques principales
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Prix",
                    f"${self.data.price:.4f}",
                    f"{self.data.change_24h:+.2f}%"
                )
            with col2:
                st.metric(
                    "Volume 24h",
                    f"${self.data.volume/1e6:.1f}M"
                )
            with col3:
                st.metric(
                    "Score Technique",
                    f"{self.data.score:.2f}",
                    help="Score > 0.7 recommandé"
                )

            # Niveaux de trading si disponibles
            if all([self.data.stop_loss, self.data.target_1, self.data.target_2]):
                st.markdown("### Niveaux de Trading")
                levels_col1, levels_col2, levels_col3 = st.columns(3)
                with levels_col1:
                    st.write("🔴 Stop Loss:", f"${self.data.stop_loss:.4f}")
                with levels_col2:
                    st.write("🎯 Target 1:", f"${self.data.target_1:.4f}")
                with levels_col3:
                    st.write("🎯 Target 2:", f"${self.data.target_2:.4f}")

            # Raisons du signal
            if self.data.reasons:
                st.markdown("### Analyse")
                for reason in self.data.reasons:
                    st.write(f"✅ {reason}")

            # Bouton d'action
            return st.button(
                "📝 Préparer l'ordre",
                key=f"prep_{self.data.symbol}"
            )