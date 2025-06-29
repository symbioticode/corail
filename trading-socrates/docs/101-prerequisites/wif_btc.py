import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Add time import if fetch_with_retry is used
import time

class YahooFinanceDataHandler:
    @staticmethod
    def standardize_yahoo_data(data):
        if isinstance(data.columns, pd.MultiIndex):
            data = pd.DataFrame({
                'open': data['Open'].iloc[:, 0],
                'high': data['High'].iloc[:, 0],
                'low': data['Low'].iloc[:, 0],
                'close': data['Close'].iloc[:, 0],
                'volume': data['Volume'].iloc[:, 0]
            })
        else:
            data.columns = data.columns.str.lower()
        return data

    @staticmethod
    def validate_yahoo_data(df):
        """Validate data structure according to template"""
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing = set(required_columns) - set(df.columns)
        if missing:
            raise ValueError(f"Colonnes manquantes: {missing}")
        if df.empty:
            raise ValueError("DataFrame vide")
        return True

    @staticmethod
    def fetch_with_retry(symbol, start_date, end_date, retries=3, delay=1):
        """Enhanced download function with retry mechanism"""
        for attempt in range(retries):
            try:
                df = yf.download(symbol, start=start_date, end=end_date, progress=False)
                if df.empty:
                    raise ValueError(f"Aucune donnée disponible pour {symbol}")
                df = YahooFinanceDataHandler.standardize_yahoo_data(df)
                YahooFinanceDataHandler.validate_yahoo_data(df)
                return df
            except Exception as e:
                if attempt == retries - 1:
                    raise
                print(f"Tentative {attempt + 1} échouée pour {symbol}. Réessai dans {delay} sec...")
                time.sleep(delay)
                delay *= 2

    @staticmethod
    def safe_fetch_pair(symbol1, symbol2, start_date, end_date):
        """Safe download for crypto pairs with date validation"""
        try:
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)

            if start_dt >= end_dt:
                raise ValueError("La date de fin doit être après la date de début")

            df1 = YahooFinanceDataHandler.fetch_with_retry(symbol1, start_dt, end_dt)
            df2 = YahooFinanceDataHandler.fetch_with_retry(symbol2, start_dt, end_dt)

            common_index = df1.index.intersection(df2.index)
            if len(common_index) < 5:
                raise ValueError("Données insuffisantes après synchronisation")

            return df1.loc[common_index], df2.loc[common_index]

        except Exception as e:
            print(f"Erreur critique: {str(e)}")
            print(f"Paramètres: {symbol1}/{symbol2} de {start_date} à {end_date}")
            return None, None


class TJCBacktest:
    def __init__(self, symbol1='WIF-USD', symbol2='BTC-USD', start='2025-01-01', end='2025-05-01'):
        self.symbol1 = symbol1
        self.symbol2 = symbol2
        self.start = start
        self.end = end
        self.results = None
        self.df = None

    def fetch_data(self):
        try:
            print(f"Téléchargement des données pour {self.symbol1} et {self.symbol2}...")

            # Télécharger les données complètes
            data1 = yf.download(self.symbol1, start=self.start, end=self.end, progress=False)
            data2 = yf.download(self.symbol2, start=self.start, end=self.end, progress=False)

            # Vérifier que les données ne sont pas vides
            if data1.empty:
                raise ValueError(f"Aucune donnée disponible pour {self.symbol1}")
            if data2.empty:
                raise ValueError(f"Aucune donnée disponible pour {self.symbol2}")

            print(f"Données téléchargées: {len(data1)} points pour {self.symbol1}, {len(data2)} points pour {self.symbol2}")

            # Extraire les prix de clôture
            if isinstance(data1.columns, pd.MultiIndex):
                close1 = data1['Close'].iloc[:, 0] if len(data1['Close'].columns) > 0 else data1['Close']
                close2 = data2['Close'].iloc[:, 0] if len(data2['Close'].columns) > 0 else data2['Close']
            else:
                close1 = data1['Close']
                close2 = data2['Close']

            # Créer le DataFrame avec gestion des index
            df = pd.DataFrame({
                'asset1': close1,
                'asset2': close2
            })

            # Supprimer les valeurs manquantes
            df = df.dropna()

            if df.empty:
                raise ValueError("Aucune donnée commune après nettoyage")

            print(f"Données après nettoyage: {len(df)} points communs")

            # Calculer les rendements logarithmiques
            df['r1'] = np.log(df['asset1'] / df['asset1'].shift(1))
            df['r2'] = np.log(df['asset2'] / df['asset2'].shift(1))
            df = df.dropna()

            if df.empty:
                raise ValueError("Aucune donnée après calcul des rendements")

            print(f"Données finales: {len(df)} points avec rendements calculés")
            self.df = df

        except Exception as e:
            print(f"Erreur lors du téléchargement des données: {str(e)}")
            self.df = None

    def run_strategy(self):
        if self.df is None or self.df.empty:
            print("Aucune donnée disponible pour exécuter la stratégie.")
            return

        print("Exécution de la stratégie TJC...")
        df = self.df.copy()

        # Calcul de la différence de phase
        df['phase_diff'] = df['r1'] - df['r2']
        df['position'] = np.sign(df['phase_diff'])

        # Rendement de la stratégie
        df['strategy_ret'] = df['position'].shift(1) * (df['r1'] - df['r2'])
        df['strategy_ret'] = df['strategy_ret'].fillna(0)  # Remplacer les NaN par 0
        df['strategy_val'] = 100 * (1 + df['strategy_ret']).cumprod()

        # Buy & Hold 50/50
        df['bh_ret'] = 0.5 * df['r1'] + 0.5 * df['r2']
        df['bh_val'] = 100 * (1 + df['bh_ret']).cumprod()

        # Calcul des drawdowns
        if not df['strategy_val'].empty:
            df['strategy_dd'] = (df['strategy_val'] - df['strategy_val'].cummax()) / df['strategy_val'].cummax() * 100
        else:
            df['strategy_dd'] = pd.Series(dtype=float, index=df.index)

        if not df['bh_val'].empty:
            df['bh_dd'] = (df['bh_val'] - df['bh_val'].cummax()) / df['bh_val'].cummax() * 100
        else:
            df['bh_dd'] = pd.Series(dtype=float, index=df.index)

        self.results = df
        print("Stratégie exécutée avec succès!")

    def plot_backtest(self):
        if self.results is None or self.results.empty:
            print("Aucun résultat à afficher.")
            return

        df = self.results
        plt.figure(figsize=(14, 6))
        plt.plot(df.index, df['strategy_val'], label='Stratégie Phase (TJC)', color='purple', linewidth=2)
        plt.plot(df.index, df['bh_val'], label='Buy & Hold 50/50', color='gray', linestyle='--', linewidth=2)
        plt.title(f"Évolution de la Valeur du Portefeuille\n{self.symbol1} vs {self.symbol2}")
        plt.ylabel("Valeur (base 100)")
        plt.xlabel("Date")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

    def plot_drawdowns(self):
        if self.results is None or self.results.empty:
            print("Aucun résultat pour afficher les drawdowns.")
            return

        df = self.results
        plt.figure(figsize=(14, 4))
        plt.fill_between(df.index, df['strategy_dd'], 0, alpha=0.3, color='red', label='Drawdown TJC')
        plt.fill_between(df.index, df['bh_dd'], 0, alpha=0.3, color='black', label='Drawdown Buy & Hold')
        plt.plot(df.index, df['strategy_dd'], color='red', linewidth=1)
        plt.plot(df.index, df['bh_dd'], color='black', linewidth=1, linestyle='--')
        plt.title("Drawdowns Relatifs")
        plt.ylabel("Drawdown (%)")
        plt.xlabel("Date")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

    def plot_3d_phase(self):
        if self.results is None or self.results.empty or 'r1' not in self.results.columns or 'r2' not in self.results.columns:
            print("Aucune donnée de rendement disponible pour le graphique 3D.")
            return

        df = self.results
        theta1 = df['r1'].cumsum()
        theta2 = df['r2'].cumsum()

        if theta1.empty or theta2.empty:
            print("Les données de phase cumulatives sont vides.")
            return

        t = np.arange(len(df))

        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(np.cos(theta1), np.sin(theta1), t, label=f'{self.symbol1} Phase', color='blue', linewidth=2)
        ax.plot(np.cos(theta2), np.sin(theta2), t, label=f'{self.symbol2} Phase', color='orange', linewidth=2)
        ax.set_xlabel('Cos(θ)')
        ax.set_ylabel('Sin(θ)')
        ax.set_zlabel('Temps')
        ax.set_title("Évolution des Phases dans l'Espace Complexe 3D")
        ax.legend()
        plt.tight_layout()
        plt.show()

    def print_performance_stats(self):
        """Affiche les statistiques de performance"""
        if self.results is None or self.results.empty:
            print("Aucun résultat disponible pour les statistiques.")
            return

        df = self.results

        # Calculs de performance
        strategy_return = (df['strategy_val'].iloc[-1] / 100 - 1) * 100
        bh_return = (df['bh_val'].iloc[-1] / 100 - 1) * 100

        strategy_volatility = df['strategy_ret'].std() * np.sqrt(252) * 100
        bh_volatility = df['bh_ret'].std() * np.sqrt(252) * 100

        strategy_sharpe = df['strategy_ret'].mean() / df['strategy_ret'].std() * np.sqrt(252) if df['strategy_ret'].std() > 0 else 0
        bh_sharpe = df['bh_ret'].mean() / df['bh_ret'].std() * np.sqrt(252) if df['bh_ret'].std() > 0 else 0

        max_dd_strategy = df['strategy_dd'].min()
        max_dd_bh = df['bh_dd'].min()

        print("\n" + "="*60)
        print("STATISTIQUES DE PERFORMANCE")
        print("="*60)
        print(f"Période: {df.index[0].strftime('%Y-%m-%d')} à {df.index[-1].strftime('%Y-%m-%d')}")
        print(f"Nombre de jours: {len(df)}")
        print("-"*60)
        print(f"{'Métrique':<25} {'Stratégie TJC':<15} {'Buy & Hold':<15}")
        print("-"*60)
        print(f"{'Rendement Total (%)':<25} {strategy_return:>14.2f} {bh_return:>14.2f}")
        print(f"{'Volatilité Ann. (%)':<25} {strategy_volatility:>14.2f} {bh_volatility:>14.2f}")
        print(f"{'Ratio de Sharpe':<25} {strategy_sharpe:>14.2f} {bh_sharpe:>14.2f}")
        print(f"{'Max Drawdown (%)':<25} {max_dd_strategy:>14.2f} {max_dd_bh:>14.2f}")
        print("="*60)

    def run_all(self):
        """Exécute l'analyse complète"""
        print("Démarrage de l'analyse TJC Backtest...")
        print(f"Symboles: {self.symbol1} vs {self.symbol2}")
        print(f"Période: {self.start} à {self.end}")
        print("-"*50)

        self.fetch_data()
        if self.df is None or self.df.empty:
            print("Échec du téléchargement des données. Arrêt de l'analyse.")
            return

        self.run_strategy()
        if self.results is None:
            print("Échec de l'exécution de la stratégie. Arrêt de l'analyse.")
            return

        self.print_performance_stats()
        self.plot_backtest()
        self.plot_drawdowns()
        self.plot_3d_phase()

        print("\nAnalyse terminée avec succès!")



###########################
class CryptoPhaseTrading:
    def __init__(self, symbol1='WIF-USD', symbol2='BTC-USD', start_date='2025-01-01', end_date='2025-05-01'):
        self.symbol1 = symbol1
        self.symbol2 = symbol2
        self.start_date = start_date
        self.end_date = end_date
        self.data = None
        self.results = None

    def fetch_data(self):
        def download_and_clean(symbol):
            df = yf.download(symbol, start=self.start_date, end=self.end_date, progress=False)
            return df['Close'].rename(symbol.split('-')[0])

        try:
            price1 = download_and_clean(self.symbol1)
            price2 = download_and_clean(self.symbol2)
            self.data = pd.concat([price1, price2], axis=1).dropna()
            return True
        except:
            return False

    def calculate_phases(self):
        # Calcul des rendements logarithmiques
        returns = np.log(self.data / self.data.shift(1)).dropna()

        # Calcul des phases cumulatives
        theta1 = returns.iloc[:, 0].cumsum()
        theta2 = returns.iloc[:, 1].cumsum()

        # Cohérence de phase instantanée
        coherence = np.cos(theta1 - theta2)

        # Stratégie de trading (basée sur la dérivée de la différence de phase)
        phase_diff = theta1 - theta2
        positions = -np.sin(phase_diff)  # Signal proportionnel à la dérivée

        # Calcul du PnL réaliste
        strategy_returns = positions.shift(1) * returns.mean(axis=1)
        strategy_value = 100 * (1 + strategy_returns).cumprod()

        # Benchmark équipondéré
        bh_value = 100 * (1 + returns.mean(axis=1)).cumprod()

        # Calcul des drawdowns
        def compute_drawdown(series):
            rolling_max = series.expanding().max()
            return (series - rolling_max) / rolling_max * 100

        # Calcul des drawdowns complexes (partie importante !)
        strategy_dd = compute_drawdown(strategy_value)
        benchmark_dd = compute_drawdown(bh_value)

        # Transformation des drawdowns en coordonnées complexes
        # Les drawdowns négatifs deviennent des rotations dans l'espace complexe
        dd_phase_strategy = np.angle(strategy_dd + 1j * np.abs(strategy_dd))
        dd_phase_benchmark = np.angle(benchmark_dd + 1j * np.abs(benchmark_dd))

        # Magnitude complexe du drawdown (révèle la cohérence cachée)
        dd_magnitude_strategy = np.sqrt(strategy_dd**2 + coherence**2)
        dd_magnitude_benchmark = np.sqrt(benchmark_dd**2 + coherence**2)

        self.results = {
            'phases': pd.DataFrame({
                'θ1': theta1,
                'θ2': theta2,
                'coherence': coherence,
                'phase_diff': phase_diff
            }),
            'portfolio': pd.DataFrame({
                'strategy': strategy_value,
                'benchmark': bh_value,
                'strategy_dd': strategy_dd,
                'benchmark_dd': benchmark_dd,
                'dd_phase_strategy': dd_phase_strategy,
                'dd_phase_benchmark': dd_phase_benchmark,
                'dd_magnitude_strategy': dd_magnitude_strategy,
                'dd_magnitude_benchmark': dd_magnitude_benchmark
            }),
            'positions': positions
        }
        return self.results

    def plot_drawdown_complex_3d(self):
        """
        Représentation 3D des drawdowns dans l'espace complexe
        Révèle la cohérence positive cachée derrière les pertes apparentes
        """
        fig = plt.figure(figsize=(18, 12))

        # Données pour la visualisation
        time = np.arange(len(self.results['portfolio']))
        strategy_dd = self.results['portfolio']['strategy_dd'].values
        benchmark_dd = self.results['portfolio']['benchmark_dd'].values
        coherence = self.results['phases']['coherence'].values

        # === Graphique 1: Drawdowns traditionnels vs Représentation complexe ===
        ax1 = fig.add_subplot(221, projection='3d')

        # Surface de cohérence positive (révèle la structure cachée)
        T, C = np.meshgrid(time[::5], np.linspace(-1, 1, 20))
        Z_surface = np.zeros_like(T)
        for i, t_idx in enumerate(range(0, len(time), 5)):
            if t_idx < len(coherence):
                Z_surface[i, :] = coherence[t_idx]

        ax1.plot_surface(T, C, Z_surface, alpha=0.2, color='gold', label='Cohérence Cachée')

        # Trajectoire des drawdowns dans l'espace complexe
        # Transformation: drawdown négatif → rotation dans plan complexe
        complex_dd_strategy = strategy_dd + 1j * coherence
        complex_dd_benchmark = benchmark_dd + 1j * coherence

        ax1.plot(time, np.real(complex_dd_strategy), np.imag(complex_dd_strategy),
                color='red', linewidth=3, label='Drawdown Stratégie (Complexe)')
        ax1.plot(time, np.real(complex_dd_benchmark), np.imag(complex_dd_benchmark),
                color='blue', linewidth=3, label='Drawdown Benchmark (Complexe)')

        ax1.set_xlabel('Temps')
        ax1.set_ylabel('Partie Réelle (Drawdown %)')
        ax1.set_zlabel('Partie Imaginaire (Cohérence)')
        ax1.set_title('Drawdowns dans l\'Espace Complexe 3D\n(Révèle la Cohérence Positive Cachée)')
        ax1.legend()

        # === Graphique 2: Magnitude complexe du drawdown ===
        ax2 = fig.add_subplot(222)

        # La magnitude révèle la vraie "distance" dans l'espace complexe
        magnitude_strategy = np.abs(complex_dd_strategy)
        magnitude_benchmark = np.abs(complex_dd_benchmark)

        ax2.plot(time, magnitude_strategy, color='purple', linewidth=2,
                label='Magnitude Complexe Stratégie')
        ax2.plot(time, magnitude_benchmark, color='orange', linewidth=2,
                label='Magnitude Complexe Benchmark')
        ax2.plot(time, np.abs(strategy_dd), color='red', linestyle='--', alpha=0.5,
                label='Drawdown Réel Stratégie')
        ax2.plot(time, np.abs(benchmark_dd), color='blue', linestyle='--', alpha=0.5,
                label='Drawdown Réel Benchmark')

        ax2.set_title('Magnitude Complexe vs Drawdown Traditionnel')
        ax2.set_ylabel('Magnitude')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # === Graphique 3: Phase des drawdowns ===
        ax3 = fig.add_subplot(223)

        phase_strategy = np.angle(complex_dd_strategy)
        phase_benchmark = np.angle(complex_dd_benchmark)

        ax3.plot(time, phase_strategy, color='crimson', linewidth=2, label='Phase Stratégie')
        ax3.plot(time, phase_benchmark, color='navy', linewidth=2, label='Phase Benchmark')
        ax3.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax3.axhline(y=np.pi/2, color='green', linestyle=':', alpha=0.7, label='Cohérence Pure')
        ax3.axhline(y=-np.pi/2, color='green', linestyle=':', alpha=0.7)

        ax3.set_title('Phase des Drawdowns Complexes\n(Orientation dans l\'Espace Complexe)')
        ax3.set_ylabel('Phase (radians)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # === Graphique 4: Projection dans le plan complexe ===
        ax4 = fig.add_subplot(224)

        # Cercle de référence
        theta_circle = np.linspace(0, 2*np.pi, 100)
        max_magnitude = max(np.max(magnitude_strategy), np.max(magnitude_benchmark))
        ax4.plot(max_magnitude * np.cos(theta_circle),
                max_magnitude * np.sin(theta_circle),
                'k--', alpha=0.3, label='Cercle de Référence')

        # Trajectoire dans le plan complexe
        scatter_strategy = ax4.scatter(np.real(complex_dd_strategy), np.imag(complex_dd_strategy),
                                     c=time, cmap='Reds', s=20, alpha=0.7, label='Stratégie')
        scatter_benchmark = ax4.scatter(np.real(complex_dd_benchmark), np.imag(complex_dd_benchmark),
                                      c=time, cmap='Blues', s=20, alpha=0.7, label='Benchmark')

        ax4.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
        ax4.axvline(x=0, color='gray', linestyle='-', alpha=0.3)
        ax4.set_xlabel('Partie Réelle (Drawdown %)')
        ax4.set_ylabel('Partie Imaginaire (Cohérence)')
        ax4.set_title('Projection des Drawdowns Complexes\n(Code Couleur: Temps)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

        # Analyse quantitative
        print("\n=== ANALYSE DES DRAWDOWNS COMPLEXES ===")
        print(f"Drawdown max traditionnel Stratégie: {np.min(strategy_dd):.2f}%")
        print(f"Drawdown max traditionnel Benchmark: {np.min(benchmark_dd):.2f}%")
        print(f"Magnitude complexe moyenne Stratégie: {np.mean(magnitude_strategy):.2f}")
        print(f"Magnitude complexe moyenne Benchmark: {np.mean(magnitude_benchmark):.2f}")
        print(f"Cohérence moyenne positive: {np.mean(np.abs(coherence)):.3f}")
        print(f"Ratio Cohérence/Drawdown Stratégie: {np.mean(np.abs(coherence))/np.mean(np.abs(strategy_dd)):.3f}")
        print(f"Ratio Cohérence/Drawdown Benchmark: {np.mean(np.abs(coherence))/np.mean(np.abs(benchmark_dd)):.3f}")

    def plot_coherence_emergence(self):
        """
        Visualise comment la cohérence positive émerge des drawdowns négatifs
        """
        fig = plt.figure(figsize=(16, 10))

        coherence = self.results['phases']['coherence'].values
        strategy_dd = self.results['portfolio']['strategy_dd'].values
        time = np.arange(len(coherence))

        # === Graphique principal: Émergence de la cohérence ===
        ax1 = fig.add_subplot(211, projection='3d')

        # Surface de transformation (de négatif à positif)
        for i in range(0, len(time), len(time)//20):
            if i < len(coherence):
                # Ligne de transformation: drawdown négatif → cohérence positive
                ax1.plot([strategy_dd[i], strategy_dd[i]],
                        [0, coherence[i]],
                        [time[i], time[i]],
                        'g-', alpha=0.6, linewidth=2)

                # Points de départ (drawdown négatif)
                ax1.scatter([strategy_dd[i]], [0], [time[i]],
                          c='red', s=50, alpha=0.8)

                # Points d'arrivée (cohérence positive)
                ax1.scatter([strategy_dd[i]], [coherence[i]], [time[i]],
                          c='gold', s=50, alpha=0.8)

        ax1.set_xlabel('Drawdown (%)')
        ax1.set_ylabel('Cohérence')
        ax1.set_zlabel('Temps')
        ax1.set_title('Émergence de la Cohérence Positive\nà partir des Drawdowns Négatifs')

        # === Graphique 2D: Corrélation inverse ===
        ax2 = fig.add_subplot(212)

        ax2.fill_between(time, strategy_dd, 0, where=(strategy_dd < 0),
                        color='red', alpha=0.3, label='Drawdowns Négatifs')
        ax2.fill_between(time, 0, coherence, where=(coherence > 0),
                        color='gold', alpha=0.3, label='Cohérence Positive')

        ax2.plot(time, strategy_dd, color='darkred', linewidth=2, label='Drawdown Stratégie')
        ax2.plot(time, coherence * 50, color='orange', linewidth=2, label='Cohérence × 50')
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)

        ax2.set_title('Corrélation Inverse: Drawdowns ↔ Cohérence\n(Plus le drawdown est fort, plus la cohérence cachée est révélée)')
        ax2.set_ylabel('Valeur')
        ax2.set_xlabel('Temps')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

        # Calcul de la corrélation inverse
        correlation = np.corrcoef(strategy_dd, coherence)[0, 1]
        print(f"\nCorrélation Drawdown-Cohérence: {correlation:.3f}")
        print("Note: Une corrélation négative révèle que les drawdowns cachent une cohérence positive !")

    def plot_real_pnl_and_drawdown(self):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

        # Graphique de valeur
        ax1.plot(self.results['portfolio']['strategy'], label='Stratégie de Phase', color='royalblue')
        ax1.plot(self.results['portfolio']['benchmark'], label='Benchmark 50/50', color='gray', linestyle='--')
        ax1.set_title('Évolution de la Valeur du Portefeuille')
        ax1.set_ylabel('Valeur (base 100)')
        ax1.legend()

        # Graphique de drawdown
        ax2.plot(self.results['portfolio']['strategy_dd'], label='Drawdown Stratégie', color='crimson')
        ax2.plot(self.results['portfolio']['benchmark_dd'], label='Drawdown Benchmark', color='darkorange', alpha=0.7)
        ax2.fill_between(self.results['portfolio'].index,
                        self.results['portfolio']['strategy_dd'], 0,
                        where=self.results['portfolio']['strategy_dd'] < 0,
                        color='crimson', alpha=0.3)
        ax2.axhline(y=0, color='black', linestyle='--', linewidth=1)
        ax2.set_title('Drawdown Comparatif (%)')
        ax2.set_ylabel('Drawdown')
        ax2.legend()

        plt.tight_layout()
        plt.show()

    def plot_complex_representation(self):
        fig = plt.figure(figsize=(16, 6))

        # 1. Représentation des phases dans le plan complexe
        ax1 = fig.add_subplot(121)
        theta1 = self.results['phases']['θ1']
        theta2 = self.results['phases']['θ2']

        for t in range(1, len(theta1), len(theta1)//20):
            z1 = np.exp(1j * theta1.iloc[t])
            z2 = np.exp(1j * theta2.iloc[t])
            ax1.plot([0, z1.real], [0, z1.imag], 'b-', alpha=0.5)
            ax1.plot([0, z2.real], [0, z2.imag], 'r-', alpha=0.5)

        circle = plt.Circle((0, 0), 1, color='gray', fill=False, linestyle='--')
        ax1.add_patch(circle)
        ax1.set_xlim(-1.5, 1.5)
        ax1.set_ylim(-1.5, 1.5)
        ax1.set_title('Espace des Phases Complexes\n(Projection des vecteurs de phase)')
        ax1.set_xlabel('Réel')
        ax1.set_ylabel('Imaginaire')

        # 2. Evolution temporelle de la cohérence
        ax2 = fig.add_subplot(122)
        ax2.plot(self.results['phases']['coherence'], color='purple')
        ax2.axhline(y=0, color='gray', linestyle='--')
        ax2.set_title('Cohérence de Phase au Cours du Temps')
        ax2.set_ylabel('cos(θ1 - θ2)')

        plt.tight_layout()
        plt.show()

    def plot_3d_phase_evolution(self):
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')

        theta1 = self.results['phases']['θ1']
        theta2 = self.results['phases']['θ2']
        time = np.arange(len(theta1))

        # Surface de référence
        u = np.linspace(0, 2*np.pi, 100)
        v = np.linspace(0, max(time), 100)
        U, V = np.meshgrid(u, v)
        X, Y = np.cos(U), np.sin(U)
        Z = V
        ax.plot_surface(X, Y, Z, alpha=0.1, color='gray')

        # Trajectoire des phases
        ax.plot(np.cos(theta1), np.sin(theta1), time,
               label=f'Phase {self.symbol1.split("-")[0]}', linewidth=2)
        ax.plot(np.cos(theta2), np.sin(theta2), time,
               label=f'Phase {self.symbol2.split("-")[0]}', linewidth=2)

        ax.set_xlabel('cos(θ)')
        ax.set_ylabel('sin(θ)')
        ax.set_zlabel('Temps')
        ax.set_title('Évolution Temporelle des Phases Complexes')
        ax.legend()
        plt.show()

    def analyze(self):
        if not self.fetch_data():
            print("Erreur lors du téléchargement des données")
            return

        self.calculate_phases()

        # Nouvelles visualisations complexes des drawdowns
        self.plot_drawdown_complex_3d()
        self.plot_coherence_emergence()

        # Visualisations traditionnelles
        self.plot_real_pnl_and_drawdown()
        self.plot_complex_representation()
        self.plot_3d_phase_evolution()

        # Calcul des métriques de performance
        strat_ret = self.results['portfolio']['strategy'].pct_change().dropna()
        bench_ret = self.results['portfolio']['benchmark'].pct_change().dropna()

        print("\n=== Métriques de Performance ===")
        print(f"Sharpe Ratio Stratégie: {np.sqrt(252)*strat_ret.mean()/strat_ret.std():.2f}")
        print(f"Sharpe Ratio Benchmark: {np.sqrt(252)*bench_ret.mean()/bench_ret.std():.2f}")
        print(f"Max Drawdown Stratégie: {self.results['portfolio']['strategy_dd'].min():.2f}%")
        print(f"Max Drawdown Benchmark: {self.results['portfolio']['benchmark_dd'].min():.2f}%")


# Exemple d'utilisation
if __name__ == "__main__":
    try:
        # Test de la stratégie TJC
        strategy = TJCBacktest(
            symbol1='WIF-USD',
            symbol2='BTC-USD',
            start='2025-01-01',
            end='2025-05-01'  # Période étendue pour plus de données
        )
        strategy.run_all()
        analyzer.analyze()

    except Exception as e:
        print(f"Erreur inattendue lors de l'exécution de la stratégie: {str(e)}")
        print("\nSolutions possibles:")
        print("1. Vérifiez les symboles (ex: 'BTC-USD' au lieu de 'BTC')")
        print("2. Essayez une période plus récente ou différente")
        print("3. Vérifiez votre connexion internet")
        print("4. Installez les dépendances: pip install yfinance pandas numpy matplotlib")