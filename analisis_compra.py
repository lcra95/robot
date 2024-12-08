import json
from gpt_integration import get_gpt_recommendation
from binance_functions import get_available_balance, buy_crypto
from database_functions import insert_transaction, get_active_transactions, obtener_candidatos_status_1
from utilitarios import fetch_indicators_for_symbols, remove_active_symbols , remove_code_delimiters

balance = get_available_balance()
if balance > 5:
    simbolos = obtener_candidatos_status_1()
    actives = get_active_transactions()
    simbolos = remove_active_symbols(simbolos,actives)
    data = fetch_indicators_for_symbols(simbolos)

    prompt = f"""
    como experto en tradding de crypto divisas realiza un analisis de compra de los siguientes simbolos e indicame si es viable comprar o esperar y cuanto del presupuesto asignarias a cada una si es viable comprar
    tienes disponible el balance {balance} solo debes responder en el formato que se indica en la base de conocimientos solo opera con simbolos que tenga señal fuerte, ignorar cualquier simbolo que muestre señales confusas
    {data}
    """

    recom = get_gpt_recommendation(prompt)
    compras = json.loads(remove_code_delimiters(recom))

    for compra in compras["simbolos"]:
        order = buy_crypto(compra["simbolo"], compra["budget"])
        insert_transaction(order)
else:
    print("No balance Available")