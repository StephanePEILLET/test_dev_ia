"""
Convertisseur de devise amélioré avec taux en temps réel.
"""

from decimal import Decimal
from typing import Dict, Optional
from datetime import datetime
from currency import Currency
from money import Money
from currency_converter import ExchangeRate
from exchange_rate_api import ExchangeRateAPI


class EnhancedCurrencyConverter:
    """
    Convertisseur de devise avec taux de change en temps réel.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialise le convertisseur amélioré.
        
        Args:
            api_key: Clé API optionnelle pour certains services
        """
        self.api_service = ExchangeRateAPI(api_key)
        self._exchange_rates: Dict[str, ExchangeRate] = {}
    
    def convert(self, money: Money, target_currency: Currency, 
                use_cached: bool = True) -> Money:
        """
        Convertit une somme d'argent vers une devise cible.
        
        Args:
            money: Somme d'argent à convertir
            target_currency: Devise cible
            use_cached: Utiliser le cache ou forcer une mise à jour
            
        Returns:
            Nouvelle instance Money dans la devise cible
        """
        if money.currency == target_currency:
            return Money(money.amount, target_currency)
        
        if not use_cached:
            self.api_service.clear_cache()
        
        # Récupérer le taux depuis l'API
        rate = self.api_service.get_single_rate(money.currency, target_currency)
        
        if rate is None:
            raise ValueError(
                f"Impossible de récupérer le taux {money.currency.code} "
                f"vers {target_currency.code}"
            )
        
        # Créer l'ExchangeRate avec timestamp
        exchange_rate = ExchangeRate(
            money.currency, 
            target_currency, 
            rate, 
            datetime.now()
        )
        
        # Stocker pour référence
        key = self._get_rate_key(money.currency, target_currency)
        self._exchange_rates[key] = exchange_rate
        
        # Effectuer la conversion
        converted_amount = money.amount * rate
        return Money(converted_amount, target_currency)
    
    def get_current_rate(self, from_currency: Currency, 
                        to_currency: Currency) -> Optional[ExchangeRate]:
        """
        Récupère le taux de change actuel entre deux devises.
        
        Args:
            from_currency: Devise source
            to_currency: Devise cible
            
        Returns:
            Taux de change avec timestamp ou None
        """
        rate = self.api_service.get_single_rate(from_currency, to_currency)
        
        if rate is not None:
            return ExchangeRate(
                from_currency, 
                to_currency, 
                rate, 
                datetime.now()
            )
        return None
    
    def get_all_rates_from(self, base_currency: Currency) -> Dict[Currency, ExchangeRate]:
        """
        Récupère tous les taux depuis une devise de base.
        
        Args:
            base_currency: Devise de base
            
        Returns:
            Dictionnaire des taux de change
        """
        rates_data = self.api_service.get_exchange_rates(base_currency)
        exchange_rates = {}
        
        for code, rate in rates_data.items():
            if code != base_currency.code:
                try:
                    target_currency = self._get_currency_by_code(code)
                    if target_currency:
                        exchange_rates[target_currency] = ExchangeRate(
                            base_currency,
                            target_currency,
                            rate,
                            datetime.now()
                        )
                except:
                    continue
        
        return exchange_rates
    
    def _get_currency_by_code(self, code: str) -> Optional[Currency]:
        """
        Récupère une devise par son code.
        
        Args:
            code: Code de la devise
            
        Returns:
            Instance de Currency ou None
        """
        from currency import EUR, USD, GBP, JPY, CHF, CAD, AUD
        
        currency_map = {
            'EUR': EUR, 'USD': USD, 'GBP': GBP,
            'JPY': JPY, 'CHF': CHF, 'CAD': CAD, 'AUD': AUD
        }
        
        return currency_map.get(code)
    
    def _get_rate_key(self, from_currency: Currency, 
                     to_currency: Currency) -> str:
        """Génère une clé unique pour un taux de change."""
        return f"{from_currency.code}_{to_currency.code}"
    
    def get_cache_info(self) -> Dict:
        """Retourne des informations sur le cache des taux."""
        return self.api_service.get_cache_info()
    
    def clear_cache(self):
        """Vide le cache des taux de change."""
        self.api_service.clear_cache()
        self._exchange_rates.clear()
    
    def list_available_currencies(self) -> set[Currency]:
        """
        Liste les devises disponibles via l'API.
        
        Returns:
            Ensemble des devises disponibles
        """
        from currency import EUR
        
        # Utiliser EUR comme base pour lister les devises disponibles
        rates_data = self.api_service.get_exchange_rates(EUR)
        currencies = {EUR}
        
        for code in rates_data.keys():
            currency = self._get_currency_by_code(code)
            if currency:
                currencies.add(currency)
        
        return currencies 