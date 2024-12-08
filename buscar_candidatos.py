import json
from indicadores import get_positive_balance_symbols
from gpt_integration import get_gpt_recommendation
from utilitarios import fetch_indicators_for_symbols, remove_code_delimiters
from database_functions import insertar_candidatos
symbols = get_positive_balance_symbols()
res = fetch_indicators_for_symbols(symbols)

prompt = f"""
como experto en tradding de crypto divisas realiza un analisis masivo de los siguientes simbolos e indicame cuales son candidatos para operar  ignora simbolos que tenga comportamientos erraticos o establecoins 
{res}
"""
recom = get_gpt_recommendation(prompt)
candidates = remove_code_delimiters(recom)
candidates = json.loads(candidates)
insertar_candidatos(candidates["candidatos"])
