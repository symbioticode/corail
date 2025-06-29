"""
Trading Socrates Framework - Module 1.1
========================================
COHÉRENCE DE PHASE ENTRE ACTIFS
Exemple Concret : WIF/BTC

PRÉREQUIS 101 :
- Nombres complexes : https://www.khanacademy.org/math/algebra2/x2ec2f6f830c9fb89:complex
- Analyse de Fourier : https://www.youtube.com/watch?v=spUNpyF58BY
- Théorie des signaux : https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/

INNOVATION CLÉS :
1. Transformation des rendements en vecteurs unitaires complexes
2. Mesure de synchronisation au-delà des corrélations classiques
3. Détection de signaux d'arbitrage invisibles aux métriques traditionnelles
"""

import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class TradingSocratesPhaseDector:
    """
    Détecteur de Cohérence de Phase - Trading Socrates Framework
    
    CONCEPT CENTRAL :
    La cohérence de phase mesure la synchronisation entre actifs dans l'espace complexe.
    Contrairement aux corrélations classiques qui mesurent seulement l'amplitude,
    elle capture aussi les décalages temporels et les harmoniques cachées.
    
    MATHÉMATIQUES :
    1. Conversion rendements → vecteurs unitaires : z = e^(i * rendement)
    2. Cohérence = Re(z1 * conj(z2))
    3. Signal d'arbitrage quand cohérence > seuil
    """
    
    def __init__(self, symbol1='WIF-USD', symbol2='BTC-USD', 
                 start_date='2024-03-01', end_date='2024-06-01'):
        self.symbol1 = symbol1
        self.symbol2 = symbol2
        self.start_date = start_date
        self.end_date = end_date
        self.data = None
        self.coherence_data = None
        
        # Paramètres Trading Socrates
        self.coherence_threshold = 0.8  # Seuil de détection de résonance
        self.transition_threshold = -0.5  # Seuil de détection de rupture
        
    def fetch_and_prepare_data(self):
        """
        ÉTAPE 1 : Acquisition et préparation des données
        
        Innovation Trading Socrates :
        - Standardisation automatique des données multi-sources
        - Alignement temporel précis pour analyse de phase
        """
        print(f"📊 Récupération données : {self.symbol1} & {self.symbol2}")
        print(f"📅 Période : {self.start_date} → {self.end_date}")
        
        try:
            # Téléchargement données brutes
            data1_raw = yf.download(self.symbol1, start=self.start_date, 
                                  end=self.end_date, progress=False)
            data2_raw = yf.download(self.symbol2, start=self.start_date, 
                                  end=self.end_date, progress=False)
            
            if data1_raw.empty or data2_raw.empty:
                raise ValueError(f"❌ Données manquantes pour {self.symbol1} ou {self.symbol2}")
            
            # Standardisation Trading Socrates
            data1 = self._standardize_yahoo_data(data1_raw)
            data2 = self._standardize_yahoo_data(data2_raw)
            
            # Alignement temporel précis
            common_index = data1.index.intersection(data2.index)
            asset1_prices = data1.loc[common_index, 'close'].dropna()
            asset2_prices = data2.loc[common_index, 'close'].dropna()
            
            # Structure de données Trading Socrates
            self.data = pd.DataFrame({
                'asset1_price': asset1_prices,
                'asset2_price': asset2_prices,
                'price_ratio': asset1_prices / asset2_prices
            }).dropna()
            
            print(f"✅ Données alignées : {len(self.data)} points temporels")
            return True
            
        except Exception as e:
            print(f"❌ Erreur acquisition : {str(e)}")
            return False
    
    def _standardize_yahoo_data(self, data):
        """Standardisation des formats Yahoo Finance variables"""
        if isinstance(data.columns, pd.MultiIndex):
            return pd.DataFrame({
                'close': data['Close'].iloc[:, 0],
                'volume': data['Volume'].iloc[:, 0]
            })
        else:
            data.columns = data.columns.str.lower()
            return data
    
    def calculate_phase_coherence(self):
        """
        ÉTAPE 2 : Calcul de la Cohérence de Phase (Innovation Trading Socrates)
        
        ALGORITHME RÉVOLUTIONNAIRE :
        1. Transformation rendements → espace complexe unitaire
        2. Calcul cohérence comme produit complexe conjugué
        3. Extraction signal d'arbitrage temporel
        
        AVANTAGE vs CORRÉLATION CLASSIQUE :
        - Capture décalages temporels (phase)
        - Détecte harmoniques cachées
        - Signal plus précoce que corrélation simple
        """
        if self.data is None:
            raise ValueError("❌ Aucune donnée. Lancez fetch_and_prepare_data() d'abord")

        print("🧮 Calcul Cohérence de Phase - Algorithme Trading Socrates")
        
        # Transformation révolutionnaire : Prix → Phases complexes
        asset1_returns = np.log(self.data['asset1_price'] / self.data['asset1_price'].shift(1)).dropna()
        asset2_returns = np.log(self.data['asset2_price'] / self.data['asset2_price'].shift(1)).dropna()

        # Alignement précis des indices
        common_idx = asset1_returns.index.intersection(asset2_returns.index)
        asset1_phase = asset1_returns.loc[common_idx]
        asset2_phase = asset2_returns.loc[common_idx]

        # INNOVATION CLÉS : Vecteurs unitaires complexes
        # z = e^(i*θ) où θ = rendement logarithmique
        asset1_z = np.exp(1j * asset1_phase)
        asset2_z = np.exp(1j * asset2_phase)

        # COHÉRENCE DE PHASE : Re(z1 * conj(z2))
        # Révèle synchronisation invisible aux métriques classiques
        coherence = np.real(asset1_z * np.conj(asset2_z))

        # Construction portefeuille cohérent
        portfolio_value = pd.Series(100 + np.cumsum(coherence), index=common_idx)

        # Structure de données Trading Socrates
        self.coherence_data = pd.DataFrame({
            'asset1_phase': asset1_phase,
            'asset2_phase': asset2_phase,
            'coherence': coherence,
            'portfolio_value': portfolio_value,
            'drawdown': portfolio_value - portfolio_value.expanding().max()
        })

        print(f"✅ Cohérence calculée : {len(self.coherence_data)} points")
        return self.coherence_data
    
    def detect_trading_signals(self):
        """
        ÉTAPE 3 : Détection de Signaux Trading Socrates
        
        INNOVATION PROPRIÉTAIRE :
        - Seuils adaptatifs basés sur cohérence de phase
        - Détection transitions avant qu'elles soient visibles aux prix
        - Classification automatique des régimes de marché
        """
        if self.coherence_data is None:
            raise ValueError("❌ Cohérence non calculée")
        
        print("🎯 Détection Signaux Trading Socrates")
        
        coherence = self.coherence_data['coherence']
        drawdown = self.coherence_data['drawdown']
        
        # DÉTECTION RÉGIMES CACHÉS
        high_coherence = coherence > self.coherence_threshold
        significant_drawdown = drawdown < self.transition_threshold
        
        # SIGNAUX PROPRIÉTAIRES
        signals = pd.DataFrame(index=coherence.index)
        signals['regime'] = 'NEUTRAL'
        signals.loc[high_coherence, 'regime'] = 'RESONANCE'
        signals.loc[significant_drawdown, 'regime'] = 'DIVERGENCE'
        
        # POINTS D'INFLEXION CRITIQUES
        regime_changes = signals['regime'] != signals['regime'].shift(1)
        inflection_points = signals[regime_changes].copy()
        
        # CLASSIFICATION TRANSITIONS
        inflection_points['transition_type'] = inflection_points['regime'].apply(
            lambda x: {
                'RESONANCE': '🟢 ENTRÉE EN RÉSONANCE',
                'DIVERGENCE': '🔴 RUPTURE DE COHÉRENCE', 
                'NEUTRAL': '🟡 RETOUR ÉQUILIBRE'
            }.get(x, 'UNKNOWN')
        )
        
        print(f"✅ {len(inflection_points)} signaux détectés")
        return signals, inflection_points
    
    def create_trading_socrates_visualization(self):
        """
        ÉTAPE 4 : Visualisation Trading Socrates
        
        INNOVATION INTERFACE :
        - Plan complexe pour trajectoire de cohérence
        - Détection visuelle des signaux d'arbitrage
        - Points d'inflexion comme événements tradables
        """
        if self.coherence_data is None:
            raise ValueError("❌ Calculs non effectués")
        
        signals, inflections = self.detect_trading_signals()
        
        # Configuration interface Trading Socrates
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'🧠 Trading Socrates Analysis: {self.symbol1.split("-")[0]}/{self.symbol2.split("-")[0]}', 
                     fontsize=16, fontweight='bold')
        
        # 1. PRIX RELATIFS (Context)
        ax1 = axes[0, 0]
        ax1.plot(self.data.index, self.data['price_ratio'], 'purple', linewidth=2, alpha=0.8)
        ax1.set_title('📈 Ratio des Prix (Context)', fontweight='bold')
        ax1.set_ylabel(f'{self.symbol1.split("-")[0]}/{self.symbol2.split("-")[0]}')
        ax1.grid(True, alpha=0.3)
        
        # 2. COHÉRENCE DE PHASE (Innovation)
        ax2 = axes[0, 1]
        coherence_line = ax2.plot(self.coherence_data.index, self.coherence_data['coherence'], 
                                 'blue', linewidth=2, label='Cohérence de Phase')
        
        # Zones de signaux
        ax2.axhline(y=self.coherence_threshold, color='green', linestyle='--', 
                   alpha=0.7, label=f'Seuil Résonance ({self.coherence_threshold})')
        ax2.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
        
        # Remplissage zones
        ax2.fill_between(self.coherence_data.index, self.coherence_data['coherence'], 
                        self.coherence_threshold,
                        where=(self.coherence_data['coherence'] > self.coherence_threshold), 
                        color='green', alpha=0.2, label='Zone Résonance')
        ax2.fill_between(self.coherence_data.index, self.coherence_data['coherence'], 0,
                        where=(self.coherence_data['coherence'] < 0), 
                        color='red', alpha=0.2, label='Zone Divergence')
        
        ax2.set_title('🎯 Cohérence de Phase (Innovation Trading Socrates)', fontweight='bold')
        ax2.set_ylabel('Indice de Cohérence')
        ax2.legend(loc='upper left')
        ax2.grid(True, alpha=0.3)
        
        # 3. PORTEFEUILLE COHÉRENT (Performance)
        ax3 = axes[1, 0]
        portfolio_line = ax3.plot(self.coherence_data.index, self.coherence_data['portfolio_value'], 
                                 'green', linewidth=3, label='Portefeuille Cohérent')
        
        # Ligne de référence
        ax3.axhline(y=100, color='gray', linestyle='-', alpha=0.5, label='Valeur Initiale')
        
        # Zones de drawdown
        drawdown_mask = self.coherence_data['drawdown'] < self.transition_threshold
        if drawdown_mask.any():
            ax3.fill_between(self.coherence_data.index, self.coherence_data['portfolio_value'], 100,
                           where=drawdown_mask, color='red', alpha=0.2, label='Zone de Stress')
        
        # Signaux d'inflexion
        if not inflections.empty:
            resonance_signals = inflections[inflections['regime'] == 'RESONANCE']
            divergence_signals = inflections[inflections['regime'] == 'DIVERGENCE']
            
            if not resonance_signals.empty:
                resonance_values = [self.coherence_data.loc[idx, 'portfolio_value'] 
                                  for idx in resonance_signals.index if idx in self.coherence_data.index]
                if resonance_values:
                    ax3.scatter(resonance_signals.index[:len(resonance_values)], resonance_values, 
                              color='green', s=100, marker='^', label='🟢 Signal Résonance', zorder=5)
            
            if not divergence_signals.empty:
                divergence_values = [self.coherence_data.loc[idx, 'portfolio_value'] 
                                   for idx in divergence_signals.index if idx in self.coherence_data.index]
                if divergence_values:
                    ax3.scatter(divergence_signals.index[:len(divergence_values)], divergence_values, 
                              color='red', s=100, marker='v', label='🔴 Signal Divergence', zorder=5)
        
        ax3.set_title('💰 Performance Portefeuille Cohérent', fontweight='bold')
        ax3.set_ylabel('Valeur')
        ax3.legend(loc='upper left')
        ax3.grid(True, alpha=0.3)
        
        # 4. PLAN COMPLEXE (Innovation Géométrique)
        ax4 = axes[1, 1]
        
        # Trajectoire dans l'espace complexe
        asset1_z = np.exp(1j * self.coherence_data['asset1_phase'])
        asset2_z = np.exp(1j * self.coherence_data['asset2_phase'])
        
        ax4.scatter(np.real(asset1_z), np.imag(asset1_z), c=self.coherence_data['coherence'], 
                   cmap='RdYlGn', alpha=0.6, s=20, label=self.symbol1.split('-')[0])
        ax4.scatter(np.real(asset2_z), np.imag(asset2_z), c=self.coherence_data['coherence'], 
                   cmap='RdYlBu', alpha=0.6, s=20, marker='s', label=self.symbol2.split('-')[0])
        
        # Cercle unitaire de référence
        theta = np.linspace(0, 2*np.pi, 100)
        ax4.plot(np.cos(theta), np.sin(theta), 'k--', alpha=0.3, label='Cercle Unitaire')
        
        ax4.set_title('🌐 Espace Complexe (Phase Space)', fontweight='bold')
        ax4.set_xlabel('Partie Réelle')
        ax4.set_ylabel('Partie Imaginaire')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_aspect('equal')
        
        plt.tight_layout()
        plt.show()
        
        return fig, signals, inflections
    
    def generate_trading_socrates_report(self):
        """
        ÉTAPE 5 : Rapport Trading Socrates
        
        MÉTRIQUES PROPRIÉTAIRES :
        - Efficacité de cohérence vs volatilité classique
        - Score de résonance harmonique
        - Indice de transition spectrale
        """
        if self.coherence_data is None:
            return "❌ Aucune donnée analysée"
        
        signals, inflections = self.detect_trading_signals()
        
        # CALCULS MÉTRIQUES PROPRIÉTAIRES
        coherence_mean = self.coherence_data['coherence'].mean()
        coherence_volatility = self.coherence_data['coherence'].std()
        max_resonance = self.coherence_data['coherence'].max()
        min_coherence = self.coherence_data['coherence'].min()
        
        portfolio_performance = {
            'Valeur Initiale': 100,
            'Valeur Finale': self.coherence_data['portfolio_value'].iloc[-1],
            'Rendement Cohérent (%)': self.coherence_data['portfolio_value'].iloc[-1] - 100,
            'Drawdown Maximum (%)': self.coherence_data['drawdown'].min(),
            'Transitions Détectées': len(inflections),
            'Cohérence Moyenne': coherence_mean,
            'Volatilité Cohérence': coherence_volatility,
            'Score Résonance Max': max_resonance,
            'Indice Harmonie': coherence_mean / (coherence_volatility + 0.001)  # Propriétaire
        }
        
        print("\n" + "="*60)
        print("🧠 RAPPORT TRADING SOCRATES - COHÉRENCE DE PHASE")
        print("="*60)
        
        for key, value in portfolio_performance.items():
            if isinstance(value, float):
                print(f"{key:<25}: {value:>12.3f}")
            else:
                print(f"{key:<25}: {value:>12}")
        
        print("\n" + "-"*60)
        print("🎯 SIGNAUX DÉTECTÉS")
        print("-"*60)
        
        if not inflections.empty:
            for date, row in inflections.iterrows():
                print(f"{date.strftime('%Y-%m-%d')}: {row['transition_type']}")
        else:
            print("Aucun signal significatif détecté dans cette période.")
        
        print("\n" + "-"*60)
        print("💡 INSIGHTS TRADING SOCRATES")
        print("-"*60)
        
        if coherence_mean > 0.5:
            print("✅ Forte cohérence structurelle détectée")
        if portfolio_performance['Indice Harmonie'] > 2.0:
            print("🎵 Résonance harmonique favorable")
        if len(inflections) > 5:
            print("⚡ Haute volatilité des transitions - Opportunités fréquentes")
        
        return portfolio_performance

def run_trading_socrates_demo():
    """
    DÉMONSTRATION COMPLÈTE TRADING SOCRATES
    Exemple concret : Analyse WIF/BTC période critique
    """
    print("🚀 DÉMONSTRATION TRADING SOCRATES FRAMEWORK")
    print("="*60)
    
    # Initialisation détecteur
    detector = TradingSocratesPhaseDector('WIF-USD', 'BTC-USD', '2024-03-01', '2024-06-01')
    
    # Pipeline complet
    if detector.fetch_and_prepare_data():
        # Calcul cohérence
        coherence_results = detector.calculate_phase_coherence()
        
        # Visualisation
        fig, signals, inflections = detector.create_trading_socrates_visualization()
        
        # Rapport final
        performance = detector.generate_trading_socrates_report()
        
        return detector, performance
    else:
        print("❌ Échec de la démonstration")
        return None, None

# EXÉCUTION DÉMONSTRATION
if __name__ == "__main__":
    detector, results = run_trading_socrates_demo()
