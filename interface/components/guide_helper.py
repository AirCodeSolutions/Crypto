# interface/components/guide_helper.py
import streamlit as st

class GuideHelper:
    """Composant d'aide et de guide"""
    
    @staticmethod
    def show_indicator_help():
        """Affiche l'aide pour les indicateurs"""
        with st.expander("❓ Comprendre les indicateurs", expanded=False):
            st.markdown("""
                ### 📊 Indicateurs Techniques
                                               
                #### 🐧 RSI (0-100)
                - < 30 : Survente (opportunité d'achat)
                - 30-70 : Zone neutre
                - > 70 : Surachat (risqué pour l'achat)
                
                #### 📈 Volume
                Important pour confirmer les mouvements :
                - Volume > moyenne : Mouvement plus fiable
                - Volume faible : Prudence conseillée
                
                #### 👋 Signaux
                - STRONG_BUY : Très forte opportunité
                - BUY : Bonne opportunité
                - NEUTRAL : Pas de signal clair
                - SELL : Signal de vente

                ### 🎯 Score Technique (0-1)
                - **0.8-1.0**: Configuration idéale
                - **0.7-0.8**: Bonne opportunité
                - **0.6-0.7**: Signal faible
                - **< 0.6**: Pas de signal

                ### 💰 Paramètres d'Investissement
                - **Budget**: Capital disponible
                - **Risque**: 1-2% par position recommandé
                - **Stop Loss**: -1.5% du prix d'entrée
                - **Take Profit**: +3% minimum       
                
            """)

    @staticmethod
    def show_quick_guide():
        """Affiche un guide rapide pour le trading"""
        with st.expander("📚 Guide Rapide", expanded=False):
            st.markdown("""
                ### 🚀 Guide de Trading Rapide
                
                #### 1. Paramètres Recommandés
                - Capital initial: 100€ maximum pour débuter
                - Risque par trade: 1.5% maximum
                - Stop loss: Toujours en place
                
                #### 2. Configuration Idéale
                - Score > 0.7
                - RSI entre 30-45
                - Volume en augmentation
                - Signal BUY ou STRONG_BUY
                
                #### 3. Gestion des Risques
                - Maximum 2 positions simultanées
                - Prise de profits à +3%
                - Stop loss à -1.5%
                
                #### 4. Points d'Attention
                - Vérifier plusieurs timeframes
                - Surveiller le volume
                - Ne pas forcer les trades
            """)

    @staticmethod
    def show_pattern_guide():
        """Affiche le guide des patterns de bougies"""
        with st.expander("📈 Guide des Patterns de Bougies", expanded=False):
            st.markdown("""
            ### Comprendre les Patterns de Bougies

            #### Patterns Haussiers
            1. **Marteau** ⤴️
            - Longue mèche basse
            - Petit corps
            - Signal de retournement haussier
            ```
            ex:     ┃
                    ┃
                ────┃────
                    ┃
                    ┃
                    ┃
            ```

            2. **Englobante Haussière** 🟢
            - Bougie verte englobe précédente rouge
            - Signal fort de retournement
            ```
            ex:   ┃     ┃
                ───┃── ──┃───
                    ┃     ┃
            ```

            #### Patterns Baissiers
            1. **Étoile Filante** ⤵️
            - Longue mèche haute
            - Petit corps
            - Signal de retournement baissier
            ```
            ex:        ┃
                        ┃
                    ────┃────
                        ┃
            ```

            2. **Avalement Baissier** 🔴
            - Bougie rouge englobe précédente verte
            - Signal fort de renversement
            ```
            ex:    ┃    ┃
                ───┃── ──┃───
                    ┃     ┃
            ```

            ### Utilisation
            - Confirmer avec d'autres indicateurs
            - Observer le volume
            - Vérifier le contexte de marché
            """)
    # Guide des opportunités
    @staticmethod
    def show_opportunites_guide():
        with st.expander("ℹ️ Guide des Opportunités", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 🎯 Configuration Idéale
                - Score technique > 0.7
                - 2-3 bougies vertes consécutives
                - Volume croissant
                - Support proche (-1-2%)
                - RSI entre 30-45
                """)
                
                st.markdown("""
                ### ⏱️ Horizons de Trading
                - 5m : Scalping (15-30 min)
                - 15m : Intraday (1-4 heures)
                - 1h : Swing court (6-24 heures)
                - 4h : Swing long (2-5 jours)
                """)
            
            with col2:
                st.markdown("""
                ### 🚫 À Éviter
                - RSI > 70 (surachat)
                - Volume décroissant 
                - Résistance proche
                - Bougies rouges
                """)

        # Filtres de recherche
        st.markdown("### 🔍 Filtres de Recherche")
        
        # Variation et volume
        col1, col2, col3 = st.columns(3)
        with col1:
            min_var = st.number_input("Variation minimum (%)", value=1.0)
        with col2:
            min_vol = st.number_input("Volume minimum (USDT)", value=50000.0)
        with col3:
            min_score = st.slider(
                "Score minimum",
                min_value=0.0,
                max_value=1.0,
                value=0.7
            )

        # Timeframe et prix maximum
        col1, col2 = st.columns(2)
        with col1:
            timeframe = st.selectbox(
                "Timeframe",
                ["5m", "15m", "1h", "4h"],
                index=2,
                help="""
                5m : Trading ultra court terme (très risqué)
                15m : Trading intraday
                1h : Recommandé pour débutants
                4h : Trades plus sûrs mais moins fréquents
                """
            )
        with col2:
            max_price = st.number_input(
                "Prix maximum (USDT)", 
                value=20.0
            )

        # Note importante
        st.info("""
        ℹ️ **Note importante :**
        - Plus le timeframe est petit, plus le risque est élevé
        - Commencez par le timeframe 1h si vous débutez
        - Attendez toujours la confirmation des 3 bougies vertes
        - Vérifiez toujours la tendance sur le timeframe supérieur
        """)