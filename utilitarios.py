from datetime import datetime
import concurrent.futures

import requests
from indicadores import get_technical_indicators
from config import TLG_TOKEN, CHAT_ID

def fetch_indicators_for_symbols(symbols):
    """
    Función que consume `get_technical_indicators` para múltiples símbolos utilizando hilos.
    
    Args:
        symbols (list): Lista de símbolos para los cuales calcular los indicadores técnicos.
        
    Returns:
        dict: Un diccionario con los resultados por cada símbolo.
    """
    results = {}

    def fetch_data(symbol):
        """Función wrapper para manejar excepciones y obtener indicadores de un símbolo."""
        try:
            return symbol, get_technical_indicators(symbol)
        except Exception as e:
            print(f"Error al procesar {symbol}: {e}")
            return symbol, None

    # Usamos ThreadPoolExecutor para procesar en paralelo
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Enviamos todas las tareas al pool
        future_to_symbol = {executor.submit(fetch_data, symbol): symbol for symbol in symbols}
        
        # Procesamos los resultados a medida que están disponibles
        for future in concurrent.futures.as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                symbol, data = future.result()
                if data:
                    results[symbol] = data
            except Exception as e:
                print(f"Error inesperado al procesar {symbol}: {e}")
    
    return results

def remove_active_symbols(symbols, actives):
    """
    Elimina los elementos del arreglo `actives` del arreglo `symbols`.

    Args:
        symbols (list): Lista principal de símbolos.
        actives (list): Lista de símbolos activos a eliminar.

    Returns:
        list: Lista de símbolos actualizada.
    """
    return [symbol for symbol in symbols if symbol not in actives]

def remove_code_delimiters(text):
    import re
    # Patrón para coincidir con bloques de código delimitados por ```
    pattern = r'```(?:\w+)?\n(.*?)\n```'
    matches = re.findall(pattern, text, re.DOTALL)

    if matches:
        # Si hay múltiples bloques de código, concatenamos sus contenidos
        code_content = '\n'.join(matches)
    else:
        # Si no se encuentran bloques de código, retornamos el texto original
        code_content = text

    # Reemplazar True/False por true/false para que sea JSON válido
    code_content = code_content.replace('True', 'true').replace('False', 'false')

    return code_content.strip()


def calculate_difference_and_time(sym, indicator):
    """
    Calcula el porcentaje de diferencia entre el precio de compra y el precio actual,
    y el tiempo transcurrido desde la fecha de compra.

    Args:
        sym (dict): Información de la transacción activa.
        indicator (dict): Indicadores técnicos del símbolo.

    Returns:
        dict: Resultados con porcentaje de diferencia y tiempo transcurrido.
    """
    try:
        # Precio de compra y precio actual
        precio_compra = sym['precio_compra']
        precio_actual = indicator['PRECIO']

        # Porcentaje de diferencia
        porcentaje_diferencia = ((precio_actual - precio_compra) / precio_compra) * 100

        # Fecha de compra y fecha actual
        fecha_compra = datetime.strptime(sym['fecha_compra'], '%Y-%m-%d %H:%M:%S.%f')
        fecha_actual = datetime.now()

        # Tiempo transcurrido
        tiempo_transcurrido = fecha_actual - fecha_compra

        return {
            "simbolo": sym["simbolo"],
            "porcentaje_diferencia": porcentaje_diferencia,
            "tiempo_transcurrido": str(tiempo_transcurrido)
        }
    except Exception as e:
        print(f"Error al calcular diferencia y tiempo para {sym['simbolo']}: {e}")
        return None
    
def send_telegram_message(message):
    token = TLG_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:

        response = requests.post(url, data=data)
        return response.json()

    except Exception as e:
        print(f"Error al enviar mensaje de Telegram: {e}")