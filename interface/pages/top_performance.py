import streamlit as st

def render(self):
    """Page optimisée pour débutants en crypto"""
    st.title("🏆 Opportunités Crypto pour Débutants")
    
    # Section paramètres d'investissement
    st.markdown("### 💰 Vos Paramètres")
    col1, col2 = st.columns(2)
    with col1:
        budget = st.number_input(
            "Votre budget maximum (USDT)",
            min_value=10.0,
            value=100.0,
            help="Montant total que vous souhaitez investir"
        )
    with col2:
        max_crypto_price = st.number_input(
            "Prix maximum par crypto (USDT)",
            min_value=0.1,
            max_value=20.0,
            value=5.0,
            help="Plus le prix est bas, plus vous pourrez acheter de tokens"
        )

    # Critères de sécurité
    st.markdown("### 🛡️ Critères de Sécurité")
    col1, col2 = st.columns(2)
    with col1:
        min_volume = st.number_input(
            "Volume minimum 24h (USDT)",
            value=50000.0,
            help="Plus le volume est élevé, plus la crypto est active"
        )
    with col2:
        min_score = st.slider(
            "Score minimum",
            min_value=0.0,
            max_value=1.0,
            value=0.6,
            help="Score technique (plus il est élevé, plus le signal est fort)"
        )

    if st.button("🔍 Rechercher des Opportunités"):
        with st.spinner("Analyse en cours..."):
            try:
                results = self._get_best_opportunities(
                    max_price=max_crypto_price,
                    min_volume=min_volume,
                    min_score=min_score,
                    budget=budget
                )
                self._show_opportunities(results, budget)
            except Exception as e:
                st.error(f"Une erreur s'est produite: {str(e)}")

def _get_best_opportunities(self, max_price: float, min_volume: float, min_score: float, budget: float):
    try:
        markets = self.exchange.get_available_symbols()
        opportunities = []
        
        progress_bar = st.progress(0)
        total = min(len(markets), 50)  # Limite à 50 cryptos pour la rapidité
        
        for i, symbol in enumerate(markets[:total]):
            try:
                ticker = self.exchange.get_ticker(symbol)
                price = ticker['last']
                
                if price <= max_price and ticker['quoteVolume'] >= min_volume:
                    analysis = self.analyzer.analyze_symbol(symbol)
                    if analysis and analysis['score'] >= min_score:
                        tokens_possible = budget / price
                        opportunities.append({
                            'symbol': symbol,
                            'price': price,
                            'volume': ticker['quoteVolume'],
                            'change': ticker['percentage'],
                            'score': analysis['score'],
                            'tokens_possible': tokens_possible,
                            'investment': tokens_possible * price,
                            'signal': analysis['signal']
                        })
                
                progress_bar.progress((i + 1) / total)
                
            except Exception:
                continue
                
        return sorted(opportunities, key=lambda x: x['score'], reverse=True)[:10]
        
    except Exception as e:
        st.error(f"Erreur lors de la recherche : {str(e)}")
        return []

def _show_opportunities(self, opportunities: List[Dict], budget: float):
    if not opportunities:
        st.info("Aucune opportunité trouvée avec ces critères")
        return
    
    st.markdown("### ⭐ Meilleures Opportunités Trouvées")
    
    for opp in opportunities:
        with st.container():
            st.markdown(f"#### {opp['symbol']}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Prix", f"${opp['price']:.4f}", f"{opp['change']:+.2f}%")
                st.write(f"Volume: ${opp['volume']/1e6:.1f}M")
            with col2:
                tokens = opp['tokens_possible']
                investment = opp['investment']
                st.metric(
                    "Tokens possibles",
                    f"{tokens:.2f}",
                    f"Pour ${investment:.2f}"
                )
            with col3:
                st.metric("Score", f"{opp['score']:.2f}")
                st.markdown(f"Signal: **{opp['signal']}**")
            
            st.markdown(f"💡 Avec {budget} USDT, vous pouvez acheter "
                       f"**{tokens:.2f}** tokens à **${opp['price']:.4f}**")
            
            st.markdown("---")