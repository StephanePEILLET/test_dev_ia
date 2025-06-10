"""
Service API pour récupérer les taux de change en temps réel.
"""

import requests
from typing import Dict, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from currency import Currency


class ExchangeRateAPI:
    """
    Service pour récupérer les taux de change depuis des APIs externes.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialise le service API.
        
        Args:
            api_key: Clé API optionnelle pour certains services
        """
        self.api_key = api_key
        self.cache = {}
        self.cache_duration = timedelta(hours=1)  # Cache valide 1 heure
        
        # URLs des APIs (par ordre de préférence)
        self.apis = [
            {
                'name': 'exchangerate-api',
                'url': 'https://open.er-api.com/v6/latest/{base}',
                'requires_key': False
            },
            {
                'name': 'fixer',
                'url': ('http://data.fixer.io/api/latest'
                        '?access_key={key}&base={base}'),
                'requires_key': True
            },
            {
                'name': 'exchangerate-host',
                'url': 'https://api.exchangerate.host/latest?base={base}',
                'requires_key': False
            }
        ]
    
    def get_exchange_rates(self, base_currency: Currency) -> Dict[str, Decimal]:
        """
        Récupère les taux de change pour une devise de base.
        
        Args:
            base_currency: Devise de base
            
        Returns:
            Dictionnaire des taux de change {code_devise: taux}
        """
        cache_key = (f"{base_currency.code}_"
                      f"{datetime.now().strftime('%Y%m%d%H')}")
        
        # Vérifier le cache
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < self.cache_duration:
                return cached_data['rates']
        
        # Récupérer depuis l'API
        rates = self._fetch_from_api(base_currency.code)
        
        if rates:
            # Mettre en cache
            self.cache[cache_key] = {
                'rates': rates,
                'timestamp': datetime.now()
            }
            return rates
        
        # Fallback vers des taux par défaut si API échoue
        return self._get_fallback_rates(base_currency.code)
    
    def _fetch_from_api(self, base_code: str) -> Optional[Dict[str, Decimal]]:
        """
        Récupère les taux depuis les APIs disponibles.
        
        Args:
            base_code: Code de la devise de base
            
        Returns:
            Dictionnaire des taux ou None si échec
        """
        for api in self.apis:
            if api['requires_key'] and not self.api_key:
                continue
                
            try:
                url = api['url'].format(
                    base=base_code, 
                    key=self.api_key if api['requires_key'] else ''
                )
                
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                # Parser selon l'API
                if api['name'] == 'exchangerate-api':
                    return self._parse_exchangerate_api(data)
                elif api['name'] == 'fixer':
                    return self._parse_fixer_api(data)
                elif api['name'] == 'exchangerate-host':
                    return self._parse_exchangerate_host_api(data)
                    
            except Exception as e:
                print(f"Erreur avec l'API {api['name']}: {e}")
                continue
        
        return None
    
    def _parse_exchangerate_api(self, data: dict) -> Optional[Dict[str, Decimal]]:
        """Parse la réponse de l'API exchangerate-api.com"""
        if data.get('result') == 'success' and 'rates' in data:
            return {
                code: Decimal(str(rate)) 
                for code, rate in data['rates'].items()
            }
        return None
    
    def _parse_fixer_api(self, data: dict) -> Optional[Dict[str, Decimal]]:
        """Parse la réponse de l'API fixer.io"""
        if data.get('success') and 'rates' in data:
            return {
                code: Decimal(str(rate)) 
                for code, rate in data['rates'].items()
            }
        return None
    
    def _parse_exchangerate_host_api(self, data: dict) -> Optional[Dict[str, Decimal]]:
        """Parse la réponse de l'API exchangerate.host"""
        if data.get('success') and 'rates' in data:
            return {
                code: Decimal(str(rate)) 
                for code, rate in data['rates'].items()
            }
        return None
    
    def _get_fallback_rates(self, base_code: str) -> Dict[str, Decimal]:
        """
        Retourne des taux de fallback si les APIs échouent.
        
        Args:
            base_code: Code de la devise de base
            
        Returns:
            Dictionnaire des taux par défaut
        """
        # Taux par défaut basés sur EUR
        default_rates_from_eur = {
            'USD': '1.0850',
            'GBP': '0.8320',
            'JPY': '163.50',
            'CHF': '0.9280',
            'CAD': '1.4780',
            'AUD': '1.6420',
            'EUR': '1.0000'
        }
        
        if base_code == 'EUR':
            return {
                code: Decimal(rate) 
                for code, rate in default_rates_from_eur.items()
            }
        
        # Pour les autres devises, calculer les taux croisés
        if base_code in default_rates_from_eur:
            base_rate = Decimal(default_rates_from_eur[base_code])
            cross_rates = {}
            
            for code, rate_str in default_rates_from_eur.items():
                if code != base_code:
                    rate = Decimal(rate_str)
                    cross_rates[code] = rate / base_rate
            
            return cross_rates
        
        # Si devise inconnue, retourner taux vides
        return {}
    
    def get_single_rate(self, from_currency: Currency, to_currency: Currency) -> Optional[Decimal]:
        """
        Récupère un taux de change spécifique entre deux devises.
        
        Args:
            from_currency: Devise source
            to_currency: Devise cible
            
        Returns:
            Taux de change ou None si indisponible
        """
        rates = self.get_exchange_rates(from_currency)
        return rates.get(to_currency.code)
    
    def clear_cache(self):
        """Vide le cache des taux de change."""
        self.cache.clear()
    
    def get_cache_info(self) -> Dict:
        """
        Retourne des informations sur le cache.
        
        Returns:
            Informations sur le cache
        """
        return {
            'entries': len(self.cache),
            'keys': list(self.cache.keys()),
            'oldest_entry': min(
                (data['timestamp'] for data in self.cache.values()),
                default=None
            )
        } 