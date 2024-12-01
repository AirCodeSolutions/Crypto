# interface/components/chart_components.py
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from dataclasses import dataclass
from typing import List, Optional, Dict
import ta

@dataclass
class ChartConfig:
    """Configuration pour personnaliser l'apparence et le comportement des graphiques"""
    height: int = 600
    template: str = "plotly_dark"
    show_volume: bool = True
    show_indicators: bool = True
    ema_periods: List[int] = None
    
    def __post_init__(self):
        """Initialise les valeurs par défaut si non spécifiées"""
        if self.ema_periods is None:
            self.ema_periods = [9, 20, 50]

class TradingChart:
    """
    Composant pour créer des graphiques de trading avancés.
    Ce composant permet d'afficher les prix, volumes et indicateurs techniques
    de manière interactive et professionnelle.
    """
    
    def __init__(self, config: Optional[ChartConfig] = None):
        """
        Initialise le composant de graphique
        
        Args:
            config: Configuration personnalisée pour le graphique
        """
        self.config = config or ChartConfig()
        
    def _create_candlestick_chart(self, df: pd.DataFrame, title: str) -> go.Figure:
        """
        Crée le graphique en chandeliers japonais de base
        
        Args:
            df: DataFrame avec les données OHLCV
            title: Titre du graphique
            
        Returns:
            go.Figure: Figure Plotly
        """
        fig = go.Figure()
        
        # Ajout des chandeliers
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name="Prix"
            )
        )
        
        # Ajout des EMAs si demandé
        if self.config.show_indicators:
            for period in self.config.ema_periods:
                ema = ta.trend.ema_indicator(df['close'], window=period)
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=ema,
                        name=f"EMA {period}",
                        line=dict(width=1)
                    )
                )
        
        # Configuration de la mise en page
        fig.update_layout(
            title=title,
            height=self.config.height,
            template=self.config.template,
            xaxis_title="Date",
            yaxis_title="Prix",
            showlegend=True
        )
        
        return fig
        
    def _add_volume_subplot(self, fig: go.Figure, df: pd.DataFrame):
        """
        Ajoute un sous-graphique pour le volume
        
        Args:
            fig: Figure Plotly existante
            df: DataFrame avec les données OHLCV
        """
        colors = ['red' if close < open else 'green' 
                 for close, open in zip(df['close'], df['open'])]
                 
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['volume'],
                name="Volume",
                marker_color=colors,
                opacity=0.5
            ),
            row=2, col=1
        )
        
    def render(self, df: pd.DataFrame, symbol: str, show_signals: bool = False):
        """
        Affiche le graphique complet avec indicateurs
        
        Args:
            df: DataFrame avec les données OHLCV
            symbol: Symbole de la crypto
            show_signals: Active l'affichage des signaux techniques
        """
        st.markdown(f"### 📈 Graphique {symbol}")
        
        # Création du graphique principal
        fig = self._create_candlestick_chart(
            df,
            f"Analyse technique de {symbol}"
        )
        
        # Ajout du volume si demandé
        if self.config.show_volume:
            fig = go.Figure(fig)
            fig.update_layout(
                yaxis2=dict(
                    title="Volume",
                    overlaying="y",
                    side="right"
                )
            )
            self._add_volume_subplot(fig, df)
            
        # Ajout des indicateurs supplémentaires si demandé
        if show_signals:
            self._add_technical_signals(fig, df)
            
        # Affichage du graphique
        st.plotly_chart(fig, use_container_width=True)
        
    def _add_technical_signals(self, fig: go.Figure, df: pd.DataFrame):
        """
        Ajoute les signaux techniques au graphique
        
        Args:
            fig: Figure Plotly existante
            df: DataFrame avec les données OHLCV
        """
        # Calcul du RSI
        rsi = ta.momentum.RSIIndicator(df['close']).rsi()
        
        # Ajout du RSI comme indicateur supplémentaire
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=rsi,
                name="RSI",
                line=dict(color='purple'),
                yaxis="y3"
            )
        )
        
        # Configuration de l'axe RSI
        fig.update_layout(
            yaxis3=dict(
                title="RSI",
                overlaying="y",
                side="right",
                position=0.95,
                range=[0, 100]
            )
        )

# Exemple d'utilisation:
if __name__ == "__main__":
    # Configuration personnalisée
    config = ChartConfig(
        height=800,
        show_volume=True,
        show_indicators=True,
        ema_periods=[9, 21, 50]
    )
    
    # Création du composant
    chart = TradingChart(config)
    
    # Utilisation dans votre application
    # chart.render(your_dataframe, "BTC/USDT")