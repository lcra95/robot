import json
from database_functions import get_active_transactions_details
from gpt_integration import get_gpt_recommendation
from indicadores import get_technical_indicators
from utilitarios import calculate_difference_and_time, remove_code_delimiters
from binance_functions import get_symbol_value_in_usdt, sell_crypto
from database_functions import process_sale
actives = get_active_transactions_details()

for sym in actives:
    indicator = get_technical_indicators(sym["simbolo"])
    info = calculate_difference_and_time(sym, indicator)
    sym["PORCENTAJE_DE_GANANCIA"] = info["porcentaje_diferencia"]
    sym["TIEMPO_TRANSCURRIDO_DESDE_LA_COMPRA"] = info["tiempo_transcurrido"]
    balance = get_symbol_value_in_usdt(sym["simbolo"].split('USDT')[0])

    prompt = f"""
                como experto en tradding de crypto divisas realiza un analisis de venta del siguiente simbolos e indicame si es viable vender o esperar actualmente tu balance para el simbolo {sym["simbolo"]} es
                {balance} tu obejtivo es maximizar tus ganancias y reducir perdidas para lograr la meta establecida en la base de conocimientos 
                analiza los suientes datos antes de decidir
                {sym}
                """
    recom = get_gpt_recommendation(prompt)
    venta = json.loads(remove_code_delimiters(recom))
    if venta["accion"] == 'VENDER':
        sell_order = sell_crypto(sym["simbolo"])
        sell_order["id_transaccion"] = sym["id"]
        sell_order["procentaje_ganancia"] = info["porcentaje_diferencia"]  
        process_sale(sell_order)