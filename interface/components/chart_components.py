# interface/components/chart_components.py
import streamlit as st  # Ajout de l'import streamlit
import pandas as pd
import plotly.graph_objects as go
import ta  # Ajout de l'import ta
from dataclasses import dataclass, field
from typing import List, Optional, Dict
@dataclass
class ChartConfig:
    """Configuration pour personnaliser les graphiques"""
    height: int = 600
    template: str = "plotly_dark"
    show_volume: bool = True
    show_indicators: bool = True
    ema_periods: List[int] = field(default_factory=lambda: [9, 20, 50])

class TradingChart:
    """Composant pour créer et afficher des graphiques de trading"""
    
    def __init__(self, config: Optional[ChartConfig] = None):
        """
        Initialise le composant avec une configuration
        Args:
            config: Configuration personnalisée (optionnel)
        """
        self.config = config or ChartConfig()

    def render(self, df: pd.DataFrame, symbol: str, show_signals: bool = False):
        """
        Affiche le graphique avec les données fournies
        Args:
            df: DataFrame avec données OHLCV
            symbol: Symbole de la crypto
            show_signals: Afficher les signaux techniques
        """
        if df.empty:
            st.warning("Aucune donnée disponible pour le graphique")
            return

        st.markdown(f"### 📈 {symbol}")
        
        fig = self._create_candlestick_chart(df)
        st.plotly_chart(fig, use_container_width=True)

    def _create_candlestick_chart(self, df: pd.DataFrame) -> go.Figure:
        """
        Crée le graphique en chandeliers
        Args:
            df: DataFrame avec données OHLCV
        Returns:
            Figure Plotly
        """
        fig = go.Figure()
        
        # Chandeliers
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name="Prix"
        ))

        # EMAs si activés
        if self.config.show_indicators:
            for period in self.config.ema_periods:
                ema = ta.trend.ema_indicator(df['close'], window=period)
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=ema,
                    name=f"EMA {period}",
                    line=dict(width=1)
                ))

        # Configuration du graphique
        fig.update_layout(
            height=self.config.height,
            template=self.config.template,
            xaxis_title="Date",
            yaxis_title="Prix",
            showlegend=True
        )

        return fig