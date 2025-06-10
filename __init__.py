"""
Convertisseur de devise - Package principal.

Ce package fournit des classes pour gérer les devises, les montants d'argent
et les conversions entre devises.

Classes principales:
- Currency: Représente une devise
- Money: Représente une somme d'argent dans une devise
- CurrencyConverter: Effectue les conversions entre devises
- ExchangeRate: Représente un taux de change entre deux devises

Exemple d'utilisation:
    from currency_converter import Currency, Money, CurrencyConverter, EUR, USD
    
    # Créer une somme d'argent
    euros = Money(100, EUR)
    
    # Initialiser le convertisseur
    converter = CurrencyConverter()
    
    # Convertir
    dollars = converter.convert(euros, USD)
    print(f"{euros} = {dollars}")
"""

from currency import Currency, EUR, USD, GBP, JPY, CHF, CAD, AUD
from money import Money
from currency_converter import CurrencyConverter, ExchangeRate

__version__ = "1.0.0"
__author__ = "Currency Converter"
__email__ = "contact@example.com"

__all__ = [
    # Classes principales
    "Currency",
    "Money", 
    "CurrencyConverter",
    "ExchangeRate",
    
    # Devises prédéfinies
    "EUR",
    "USD", 
    "GBP",
    "JPY",
    "CHF",
    "CAD",
    "AUD",
] 