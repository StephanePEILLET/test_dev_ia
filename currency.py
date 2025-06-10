from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Currency:
    """
    Représente une devise avec son code ISO, son nom et son symbole.
    """
    code: str  # Code ISO 4217 (ex: EUR, USD, GBP)
    name: str  # Nom complet (ex: "Euro", "US Dollar")
    symbol: Optional[str] = None  # Symbole (ex: "€", "$", "£")
    
    def __post_init__(self):
        """Validation des données après initialisation."""
        if not self.code or len(self.code) != 3:
            raise ValueError("Le code de devise doit être composé de 3 caractères")
        
        if not self.name:
            raise ValueError("Le nom de devise ne peut pas être vide")
        
        # Conversion en majuscules pour standardisation
        object.__setattr__(self, 'code', self.code.upper())
    
    def __str__(self) -> str:
        if self.symbol:
            return f"{self.name} ({self.code}) - {self.symbol}"
        return f"{self.name} ({self.code})"
    
    def __repr__(self) -> str:
        return f"Currency(code='{self.code}', name='{self.name}', symbol='{self.symbol}')"


# Devises courantes prédéfinies
EUR = Currency("EUR", "Euro", "€")
USD = Currency("USD", "US Dollar", "$")
GBP = Currency("GBP", "British Pound", "£")
JPY = Currency("JPY", "Japanese Yen", "¥")
CHF = Currency("CHF", "Swiss Franc", "CHF")
CAD = Currency("CAD", "Canadian Dollar", "C$")
AUD = Currency("AUD", "Australian Dollar", "A$") 