# Setup Instructions
1. Install Python 3.8+.
2. Create a virtual environment: python -m venv venv
3. Activate: .\venv\Scripts\Activate.ps1
4. Install dependencies: pip install -r requirements.txt
5. Install the package: pip install -e .
"@

# Créer les fichiers d'exemples (placeholders pour notebooks)
Set-Content -Path "examples\erq_btc_eth_vs_usdt.ipynb" -Value '{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}'
Set-Content -Path "examples\phase_btc_eth_vs_usdt.ipynb" -Value '{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}'
Set-Content -Path "examples\cycle_btc_eth_vs_usdt.ipynb" -Value '{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}'
Set-Content -Path "examples\tensor_portfolio_btc_eth.ipynb" -Value '{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}'
Set-Content -Path "examples\transform_btc_eth_vs_usdt.ipynb" -Value '{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}'
Set-Content -Path "examples\trader_btc_eth_futures.ipynb" -Value '{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}'

# Créer les fichiers de tests (placeholders)
Set-Content -Path "tests\test_erq.py" -Value @"
import pytest
from module_1_foundations.erq_calculation import calculate_erq
def test_erq_calculation():
    data = {'T': 0.1, 'V': 0.2, 'Phi': 0.3, 'H': 0.4}
    ref = {'T': 0, 'V': 0, 'Phi': 0, 'H': 0}
    assert calculate_erq(data, ref, leverage=1) > 0
