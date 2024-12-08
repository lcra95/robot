from binance.client import Client
import pandas as pd
from config import BINANCE_API_KEY, BINANCE_SECRET_KEY
from utilitarios import send_telegram_message
# Configura tus claves de API

client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
def get_available_balance():
    try:
        balance_info = client.get_asset_balance('USDT')
        available_balance = float(balance_info.get("free", 1))
        return available_balance
    except Exception as e:
        print(f"Error al obtener el saldo disponible para USDT: {e}")
        return 0.0

def get_symbol_value_in_usdt(symbol):
    """
    Calcula el valor en USDT de un símbolo específico en la billetera spot.

    Args:
        symbol (str): El símbolo del activo (por ejemplo, "BTC").

    Returns:
        float: Valor en USDT del símbolo en la billetera spot.
    """
    try:
        # Obtener el balance disponible para el símbolo
        balance_info = client.get_asset_balance(asset=symbol)
        if balance_info is None:
            print(f"No se encontró información del balance para {symbol}.")
            return 0.0

        balance = float(balance_info.get("free", 0.0))
        if balance == 0.0:
            print(f"No tienes balance disponible para {symbol}.")
            return 0.0

        # Obtener el precio actual del símbolo en USDT
        ticker = client.get_symbol_ticker(symbol=f"{symbol}USDT")
        current_price = float(ticker['price'])

        # Calcular el valor en USDT
        value_in_usdt = balance * current_price
        return value_in_usdt

    except Exception as e:
        print(f"Error al calcular el valor en USDT para {symbol}: {e}")
        return 0.0

def get_lot_size(client, symbol):
    info = client.get_symbol_info(symbol)
    for filter in info['filters']:
        if filter['filterType'] == 'LOT_SIZE':
            return {
                'minQty': float(filter['minQty']),
                'maxQty': float(filter['maxQty']),
                'stepSize': float(filter['stepSize'])
            }
    return None

def get_current_price(symbol):
    ticker = client.get_symbol_ticker(symbol=symbol)
    return float(ticker['price'])

def round_step_size(quantity, step_size):
    """
    Redondea la cantidad al múltiplo más cercano del stepSize permitido.
    """
    return round(quantity - (quantity % step_size), 8)  # Hasta 8 decimales.


def buy_crypto(symbol, amount_usd):
    current_price = get_current_price(symbol)
    lot_size = get_lot_size(client, symbol)

    if lot_size:
        quantity = amount_usd / current_price

        # Ajustar la cantidad al múltiplo más cercano del stepSize
        quantity = round_step_size(quantity, lot_size['stepSize'])

        if quantity < lot_size['minQty'] or quantity > lot_size['maxQty']:
            print("Cantidad fuera del rango permitido por LOT_SIZE")
            return None

        try:
            order = client.order_market_buy(symbol=symbol, quantity=quantity)
            print(f"Orden de compra ejecutada: {order}")
            send_telegram_message(f"Compra de {symbol} a {current_price} la cantidad de {quantity}")
            return order
        except Exception as e:
            print(f"Error al realizar la compra: {e}")
            return None
    else:
        print("No se pudo obtener la información de LOT_SIZE")
        return None


def get_all_symbols_in_spot_wallet():
    """
    Lista todos los símbolos en la billetera spot de Binance con balance mayor a cero.

    Returns:
        list: Lista de símbolos presentes en la billetera spot.
    """
    try:
        # Obtener la información de la cuenta
        account_info = client.get_account()
        
        # Extraer los balances con fondos disponibles
        symbols = [
            balance['asset']
            for balance in account_info['balances']
            if float(balance['free']) > 0 or float(balance['locked']) > 0
        ]

        return symbols

    except Exception as e:
        print(f"Error al obtener los símbolos de la billetera spot: {e}")
        return []
    
def adjust_quantity(quantity, step_size):
    return round(quantity - (quantity % step_size), len(str(step_size).split('.')[1]))


def sell_crypto(symbol):
    try:
        balance = client.get_asset_balance(asset=symbol.replace("USDT", ""))
        quantity = float(balance['free'])
        lot_size = get_lot_size(client, symbol)

        if lot_size:
            quantity = adjust_quantity(quantity, lot_size['stepSize'])

            if quantity < lot_size['minQty'] or quantity > lot_size['maxQty']:
                print("Cantidad de venta fuera del rango permitido por LOT_SIZE")
                return None

            order = client.order_market_sell(symbol=symbol, quantity=quantity)
            
            print(f"Orden de venta ejecutada: {order}")
            send_telegram_message(f"Venta {symbol} la cantidad de {quantity}")
            return order
        else:

            print("No se pudo obtener la información de LOT_SIZE para la venta")
            return None
    except Exception as e:
        print(f"Error al realizar la venta: {e}")
        return None
