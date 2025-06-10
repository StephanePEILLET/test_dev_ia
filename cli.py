#!/usr/bin/env python3
"""
Interface CLI pour le convertisseur de devise.
"""

import click
import sys
from datetime import datetime
from colorama import init, Fore, Style
from decimal import Decimal, InvalidOperation

# Initialiser colorama pour Windows
init()

from currency import Currency, EUR, USD, GBP, JPY, CHF, CAD, AUD
from money import Money
from enhanced_currency_converter import EnhancedCurrencyConverter


# Mapping des devises disponibles
CURRENCIES = {
    'EUR': EUR, 'USD': USD, 'GBP': GBP, 'JPY': JPY,
    'CHF': CHF, 'CAD': CAD, 'AUD': AUD
}


def print_header():
    """Affiche l'en-tête du programme."""
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}    💱 CONVERTISSEUR DE DEVISE EN TEMPS RÉEL 💱{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")


def print_success(message: str):
    """Affiche un message de succès."""
    print(f"{Fore.GREEN}✓{Style.RESET_ALL} {message}")


def print_error(message: str):
    """Affiche un message d'erreur."""
    print(f"{Fore.RED}✗{Style.RESET_ALL} {message}")


def print_info(message: str):
    """Affiche un message d'information."""
    print(f"{Fore.BLUE}ℹ{Style.RESET_ALL} {message}")


def print_warning(message: str):
    """Affiche un message d'avertissement."""
    print(f"{Fore.YELLOW}⚠{Style.RESET_ALL} {message}")


def format_currency_list():
    """Formate la liste des devises disponibles."""
    lines = []
    for code, currency in sorted(CURRENCIES.items()):
        symbol = f" ({currency.symbol})" if currency.symbol else ""
        lines.append(f"  • {Fore.CYAN}{code}{Style.RESET_ALL}: {currency.name}{symbol}")
    return "\n".join(lines)


@click.group()
@click.option('--api-key', envvar='EXCHANGE_API_KEY', 
              help='Clé API pour les services premium')
@click.pass_context
def cli(ctx, api_key):
    """Convertisseur de devise avec taux en temps réel."""
    ctx.ensure_object(dict)
    ctx.obj['api_key'] = api_key
    ctx.obj['converter'] = EnhancedCurrencyConverter(api_key)


@cli.command()
@click.argument('amount', type=float)
@click.argument('from_currency', type=click.Choice(list(CURRENCIES.keys())))
@click.argument('to_currency', type=click.Choice(list(CURRENCIES.keys())))
@click.option('--no-cache', is_flag=True, 
              help='Forcer la récupération de nouveaux taux')
@click.option('--precision', default=2, type=int,
              help='Nombre de décimales pour le résultat')
@click.pass_context
def convert(ctx, amount, from_currency, to_currency, no_cache, precision):
    """
    Convertit un montant d'une devise vers une autre.
    
    Exemple: convert 100 EUR USD
    """
    try:
        converter = ctx.obj['converter']
        
        # Créer l'objet Money
        from_curr = CURRENCIES[from_currency]
        to_curr = CURRENCIES[to_currency]
        money = Money(amount, from_curr)
        
        print_header()
        print_info(f"Conversion de {money} vers {to_curr.name}")
        
        if no_cache:
            print_info("Récupération de nouveaux taux...")
        
        # Effectuer la conversion
        converted = converter.convert(money, to_curr, use_cached=not no_cache)
        
        # Arrondir selon la précision demandée
        rounded_result = converted.round(precision)
        
        # Afficher le résultat
        print_success(f"Résultat: {rounded_result}")
        
        # Afficher le taux utilisé
        rate = converter.get_current_rate(from_curr, to_curr)
        if rate:
            print_info(f"Taux: 1 {from_currency} = {rate.rate} {to_currency}")
            print_info(f"Mis à jour: {rate.timestamp.strftime('%H:%M:%S')}")
        
    except ValueError as e:
        print_error(f"Erreur de conversion: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        sys.exit(1)


@cli.command()
@click.argument('base_currency', type=click.Choice(list(CURRENCIES.keys())))
@click.option('--sort-by', default='code', 
              type=click.Choice(['code', 'rate', 'name']),
              help='Critère de tri')
@click.pass_context
def rates(ctx, base_currency, sort_by):
    """
    Affiche tous les taux de change pour une devise de base.
    
    Exemple: rates EUR
    """
    try:
        converter = ctx.obj['converter']
        base_curr = CURRENCIES[base_currency]
        
        print_header()
        print_info(f"Taux de change depuis {base_curr.name} ({base_currency})")
        
        # Récupérer tous les taux
        all_rates = converter.get_all_rates_from(base_curr)
        
        if not all_rates:
            print_warning("Aucun taux de change disponible")
            return
        
        # Trier selon le critère choisi
        if sort_by == 'code':
            sorted_rates = sorted(all_rates.items(), key=lambda x: x[0].code)
        elif sort_by == 'rate':
            sorted_rates = sorted(all_rates.items(), key=lambda x: x[1].rate)
        elif sort_by == 'name':
            sorted_rates = sorted(all_rates.items(), key=lambda x: x[0].name)
        
        print(f"\n{Fore.YELLOW}{'Code':<6} {'Nom':<20} {'Taux':<12} {'Symbole'}{Style.RESET_ALL}")
        print("-" * 50)
        
        for currency, rate in sorted_rates:
            symbol = currency.symbol or ""
            rate_str = f"{rate.rate:.4f}"
            print(f"{Fore.CYAN}{currency.code:<6}{Style.RESET_ALL} "
                  f"{currency.name:<20} {rate_str:<12} {symbol}")
        
        print(f"\n{Fore.GREEN}Total: {len(all_rates)} devises{Style.RESET_ALL}")
        
        # Afficher l'heure de mise à jour
        if all_rates:
            first_rate = next(iter(all_rates.values()))
            print_info(f"Mis à jour: {first_rate.timestamp.strftime('%H:%M:%S le %d/%m/%Y')}")
        
    except Exception as e:
        print_error(f"Erreur lors de la récupération des taux: {e}")
        sys.exit(1)


@cli.command()
@click.pass_context
def currencies(ctx):
    """Affiche la liste des devises supportées."""
    print_header()
    print_info("Devises supportées:")
    print()
    print(format_currency_list())
    print(f"\n{Fore.GREEN}Total: {len(CURRENCIES)} devises disponibles{Style.RESET_ALL}")


@cli.command()
@click.pass_context
def cache(ctx):
    """Affiche des informations sur le cache des taux."""
    try:
        converter = ctx.obj['converter']
        cache_info = converter.get_cache_info()
        
        print_header()
        print_info("État du cache:")
        print()
        print(f"  • Entrées en cache: {cache_info['entries']}")
        
        if cache_info['oldest_entry']:
            oldest = cache_info['oldest_entry'].strftime('%H:%M:%S le %d/%m/%Y')
            print(f"  • Plus ancienne entrée: {oldest}")
        
        if cache_info['keys']:
            print(f"  • Clés en cache:")
            for key in cache_info['keys']:
                print(f"    - {key}")
        
    except Exception as e:
        print_error(f"Erreur lors de la récupération du cache: {e}")


@cli.command()
@click.confirmation_option(prompt='Êtes-vous sûr de vouloir vider le cache?')
@click.pass_context
def clear_cache(ctx):
    """Vide le cache des taux de change."""
    try:
        converter = ctx.obj['converter']
        converter.clear_cache()
        print_success("Cache vidé avec succès")
        
    except Exception as e:
        print_error(f"Erreur lors du vidage du cache: {e}")
        sys.exit(1)


@cli.command()
@click.pass_context
def interactive(ctx):
    """Mode interactif pour les conversions multiples."""
    converter = ctx.obj['converter']
    
    print_header()
    print_info("Mode interactif activé")
    print_info("Tapez 'quit' ou 'exit' pour quitter")
    print_info("Tapez 'help' pour l'aide")
    print()
    
    while True:
        try:
            # Demander la saisie
            user_input = input(f"{Fore.CYAN}> {Style.RESET_ALL}").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print_info("Au revoir!")
                break
            
            if user_input.lower() in ['help', 'h']:
                print_help_interactive()
                continue
            
            if user_input.lower() == 'currencies':
                print(format_currency_list())
                continue
            
            # Parser la commande de conversion
            parts = user_input.split()
            if len(parts) != 3:
                print_error("Format: <montant> <devise_source> <devise_cible>")
                continue
            
            amount_str, from_code, to_code = parts
            
            # Valider les devises
            if from_code.upper() not in CURRENCIES:
                print_error(f"Devise source inconnue: {from_code}")
                continue
            
            if to_code.upper() not in CURRENCIES:
                print_error(f"Devise cible inconnue: {to_code}")
                continue
            
            # Valider le montant
            try:
                amount = float(amount_str)
            except ValueError:
                print_error(f"Montant invalide: {amount_str}")
                continue
            
            # Effectuer la conversion
            from_curr = CURRENCIES[from_code.upper()]
            to_curr = CURRENCIES[to_code.upper()]
            money = Money(amount, from_curr)
            
            converted = converter.convert(money, to_curr)
            result = converted.round(2)
            
            print_success(f"{money} = {result}")
            
        except KeyboardInterrupt:
            print_info("\nAu revoir!")
            break
        except Exception as e:
            print_error(f"Erreur: {e}")


def print_help_interactive():
    """Affiche l'aide pour le mode interactif."""
    print(f"\n{Fore.YELLOW}Aide - Mode interactif:{Style.RESET_ALL}")
    print("  • Format de conversion: <montant> <devise_source> <devise_cible>")
    print("  • Exemple: 100 EUR USD")
    print("  • Commandes spéciales:")
    print("    - currencies : Liste des devises")
    print("    - help ou h  : Cette aide")
    print("    - quit ou q  : Quitter")
    print()


if __name__ == '__main__':
    cli() 