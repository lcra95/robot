from datetime import datetime
import os
import time
from binance.client import Client
from config import BINANCE_API_KEY, BINANCE_SECRET_KEY
import pandas as pd


client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

def get_technical_indicators(symbol):
   
    try:
        # Obtener datos históricos de precios
        klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE, '1 day ago UTC')

        # Crear un DataFrame
        data = pd.DataFrame(klines, columns=['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume',
                                                'Close Time', 'Quote Asset Volume', 'Number of Trades',
                                                'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume',
                                                'Ignore'])
        
        # Convertir el tipo de datos
        data['Close'] = data['Close'].astype(float)
        data['Volume'] = data['Volume'].astype(float)

        # Calcular RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]

        # Calcular MACD
        short_ema = data['Close'].ewm(span=12, adjust=False).mean()
        long_ema = data['Close'].ewm(span=26, adjust=False).mean()
        macd = short_ema - long_ema
        signal = macd.ewm(span=9, adjust=False).mean()
        macd_value = macd.iloc[-1] - signal.iloc[-1]

        # Calcular medias móviles
        mm30 = data['Close'].rolling(window=30).mean().iloc[-1]
        mm120 = data['Close'].rolling(window=120).mean().iloc[-1]
        mm180 = data['Close'].rolling(window=180).mean().iloc[-1]

        # Obtener volumen y precio actual
        current_price = client.get_symbol_ticker(symbol=symbol)['price']
        volume = data['Volume'].sum()

        # Obtener la fecha y hora actuales
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Preparar el resultado
        result = {
            "SYMBOL": symbol,
            "PRECIO": float(current_price),
            "FechaHora": timestamp,
            "RSI": rsi,
            "MACD": macd_value,
            "SMA30": mm30,
            "SMA120": mm120,
            "SMA180": mm180,
            "VOLUMEN": volume,
        }

        return result

    except Exception as e:
        print(f"Error al obtener datos: {e}.")


def get_technical_indicators_hours(symbol):
    # Obtener datos históricos de precios utilizando datos horarios
    klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1HOUR, '1 month ago UTC')

    # Crear un DataFrame
    data = pd.DataFrame(klines, columns=['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume',
                                          'Close Time', 'Quote Asset Volume', 'Number of Trades',
                                          'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume',
                                          'Ignore'])
    
    # Convertir el tipo de datos
    data['Close'] = data['Close'].astype(float)
    data['Volume'] = data['Volume'].astype(float)

    # Calcular RSI
    delta = data['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs)).iloc[-1]

    # Calcular MACD
    short_ema = data['Close'].ewm(span=12, adjust=False).mean()
    long_ema = data['Close'].ewm(span=26, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=9, adjust=False).mean()
    macd_value = (macd - signal).iloc[-1]

    # Calcular medias móviles
    mm30 = data['Close'].rolling(window=30).mean().iloc[-1]
    mm120 = data['Close'].rolling(window=120).mean().iloc[-1]
    mm180 = data['Close'].rolling(window=180).mean().iloc[-1]

    # Obtener volumen total y precio actual
    volume = data['Volume'].sum()
    current_price = float(client.get_symbol_ticker(symbol=symbol)['price'])

    # Obtener la fecha y hora actuales
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Preparar el resultado
    result = {
        "FechaHora": timestamp,
        "RSI": rsi,
        "MACD": macd_value,
        "SMA30": mm30,
        "SMA120": mm120,
        "SMA180": mm180,
        "VOLUMEN": volume,
        "PRECIO": current_price
    }

    return result

def get_positive_balance_symbols():
    # Obtener información de todos los tickers
    tickers = client.get_ticker()
    positive_balance_symbols = [ticker['symbol'] for ticker in tickers if ticker['symbol'].endswith('USDT') and float(ticker['priceChangePercent']) > 0]

    return positive_balance_symbols

def get_technical_indicators_wo_retry(symbol):
        try:
            # Obtener datos históricos de precios
            klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE, '1 day ago UTC')

            # Crear un DataFrame
            data = pd.DataFrame(klines, columns=['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume',
                                                  'Close Time', 'Quote Asset Volume', 'Number of Trades',
                                                  'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume',
                                                  'Ignore'])
            
            # Convertir el tipo de datos
            data['Close'] = data['Close'].astype(float)
            data['Volume'] = data['Volume'].astype(float)

            # Calcular RSI
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]

            # Calcular MACD
            short_ema = data['Close'].ewm(span=12, adjust=False).mean()
            long_ema = data['Close'].ewm(span=26, adjust=False).mean()
            macd = short_ema - long_ema
            signal = macd.ewm(span=9, adjust=False).mean()
            macd_value = macd.iloc[-1] - signal.iloc[-1]

            # Calcular medias móviles
            mm30 = data['Close'].rolling(window=30).mean().iloc[-1]
            mm120 = data['Close'].rolling(window=120).mean().iloc[-1]
            mm180 = data['Close'].rolling(window=180).mean().iloc[-1]

            # Obtener volumen y precio actual
            current_price = client.get_symbol_ticker(symbol=symbol)['price']
            volume = data['Volume'].sum()

            # Obtener la fecha y hora actuales
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Preparar el resultado
            result = {
                "FechaHora": timestamp,
                "RSI": rsi,
                "MACD": macd_value,
                "SMA30": mm30,
                "SMA120": mm120,
                "SMA180": mm180,
                "VOLUMEN": volume,
                "PRECIO": float(current_price)
            }

            return result

        except Exception as e:
            print(f"Error al obtener datos: {e}. Reintentando en 2 segundos...")
