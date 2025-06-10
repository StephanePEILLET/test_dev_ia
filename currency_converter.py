from decimal import Decimal
from typing import Dict, Optional
from datetime import datetime
from currency import Currency
from money import Money


class ExchangeRate:
    """
    Représente un taux de change entre deux devises.
    """
    
    def __init__(self, from_currency: Currency, to_currency: Currency, 
                 rate: Decimal, timestamp: Optional[datetime] = None):
        """
        Initialise un taux de change.
        
        Args:
            from_currency: Devise source
            to_currency: Devise cible
            rate: Taux de change
            timestamp: Horodatage du taux (optionnel)
        """
        self.from_currency = from_currency
        self.to_currency = to_currency
        self.rate = Decimal(str(rate))
        self.timestamp = timestamp or datetime.now()
    
    def __str__(self) -> str:
        return f"{self.from_currency.code} → {self.to_currency.code}: {self.rate}"
    
    def __repr__(self) -> str:
        return (f"ExchangeRate({self.from_currency.code}, {self.to_currency.code}, "
                f"{self.rate}, {self.timestamp})")


class CurrencyConverter:
    """
    Convertisseur de devises gérant les taux de change.
    """
    
    def __init__(self):
        """Initialise le convertisseur avec des taux par défaut."""
        self._exchange_rates: Dict[str, ExchangeRate] = {}
        self._load_default_rates()
    
    def _load_default_rates(self) -> None:
        """Charge des taux de change par défaut (simulés)."""
        # Taux par rapport à l'EUR (1 EUR = X devise)
        default_rates = {
            ('EUR', 'USD'): '1.0850',
            ('EUR', 'GBP'): '0.8320',
            ('EUR', 'JPY'): '163.50',
            ('EUR', 'CHF'): '0.9280',
            ('EUR', 'CAD'): '1.4780',
            ('EUR', 'AUD'): '1.6420',
        }
        
        # Ajouter les taux directs et inverses
        for (from_code, to_code), rate_str in default_rates.items():
            rate = Decimal(rate_str)
            
            # Import dynamique pour éviter les imports circulaires
            from currency import EUR, USD, GBP, JPY, CHF, CAD, AUD
            
            currency_map = {
                'EUR': EUR, 'USD': USD, 'GBP': GBP, 
                'JPY': JPY, 'CHF': CHF, 'CAD': CAD, 'AUD': AUD
            }
            
            from_currency = currency_map[from_code]
            to_currency = currency_map[to_code]
            
            # Taux direct
            self.add_exchange_rate(from_currency, to_currency, rate)
            
            # Taux inverse
            if rate != 0:
                inverse_rate = Decimal('1') / rate
                self.add_exchange_rate(to_currency, from_currency, inverse_rate)
    
    def add_exchange_rate(self, from_currency: Currency, to_currency: Currency, 
                         rate: Decimal, timestamp: Optional[datetime] = None) -> None:
        """
        Ajoute ou met à jour un taux de change.
        
        Args:
            from_currency: Devise source
            to_currency: Devise cible
            rate: Taux de change
            timestamp: Horodatage (optionnel)
        """
        key = self._get_rate_key(from_currency, to_currency)
        exchange_rate = ExchangeRate(from_currency, to_currency, rate, timestamp)
        self._exchange_rates[key] = exchange_rate
    
    def get_exchange_rate(self, from_currency: Currency, 
                         to_currency: Currency) -> Optional[ExchangeRate]:
        """
        Récupère le taux de change entre deux devises.
        
        Args:
            from_currency: Devise source
            to_currency: Devise cible
            
        Returns:
            Taux de change ou None si non trouvé
        """
        key = self._get_rate_key(from_currency, to_currency)
        return self._exchange_rates.get(key)
    
    def convert(self, money: Money, target_currency: Currency) -> Money:
        """
        Convertit une somme d'argent vers une devise cible.
        
        Args:
            money: Somme d'argent à convertir
            target_currency: Devise cible
            
        Returns:
            Nouvelle instance Money dans la devise cible
            
        Raises:
            ValueError: Si la conversion n'est pas possible
        """
        if money.currency == target_currency:
            return Money(money.amount, target_currency)
        
        # Chercher le taux de change direct
        exchange_rate = self.get_exchange_rate(money.currency, target_currency)
        
        if exchange_rate is None:
            # Essayer la conversion via une devise pivot (EUR)
            from currency import EUR
            
            if money.currency != EUR and target_currency != EUR:
                # Convertir d'abord vers EUR puis vers la devise cible
                eur_money = self._convert_via_pivot(money, EUR)
                if eur_money:
                    return self.convert(eur_money, target_currency)
            
            raise ValueError(
                f"Impossible de convertir {money.currency.code} vers {target_currency.code}. "
                f"Taux de change non disponible."
            )
        
        converted_amount = money.amount * exchange_rate.rate
        return Money(converted_amount, target_currency)
    
    def _convert_via_pivot(self, money: Money, pivot_currency: Currency) -> Optional[Money]:
        """
        Convertit via une devise pivot.
        
        Args:
            money: Somme à convertir
            pivot_currency: Devise pivot
            
        Returns:
            Somme convertie vers la devise pivot ou None
        """
        exchange_rate = self.get_exchange_rate(money.currency, pivot_currency)
        if exchange_rate is None:
            return None
        
        converted_amount = money.amount * exchange_rate.rate
        return Money(converted_amount, pivot_currency)
    
    def _get_rate_key(self, from_currency: Currency, to_currency: Currency) -> str:
        """
        Génère une clé unique pour un taux de change.
        
        Args:
            from_currency: Devise source
            to_currency: Devise cible
            
        Returns:
            Clé sous forme de string
        """
        return f"{from_currency.code}_{to_currency.code}"
    
    def list_available_currencies(self) -> set[Currency]:
        """
        Liste toutes les devises disponibles pour conversion.
        
        Returns:
            Ensemble des devises disponibles
        """
        currencies = set()
        for exchange_rate in self._exchange_rates.values():
            currencies.add(exchange_rate.from_currency)
            currencies.add(exchange_rate.to_currency)
        return currencies
    
    def get_all_rates_for_currency(self, currency: Currency) -> Dict[Currency, ExchangeRate]:
        """
        Récupère tous les taux de change depuis une devise donnée.
        
        Args:
            currency: Devise source
            
        Returns:
            Dictionnaire des taux de change disponibles
        """
        rates = {}
        for exchange_rate in self._exchange_rates.values():
            if exchange_rate.from_currency == currency:
                rates[exchange_rate.to_currency] = exchange_rate
        return rates