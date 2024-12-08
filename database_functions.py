import psycopg2
from datetime import datetime
from config import DB_CONFIG

def insert_transaction(data):
    """
    Inserta una transacción en la tabla `transacciones` basada en el objeto recibido.

    Args:
        data (dict): Objeto con la información de la transacción.
    """
    # Obtener valores del objeto
    simbolo = data["symbol"]
    precio_compra = float(data["fills"][0]["price"])
    cantidad = float(data["fills"][0]["qty"])
    fecha_compra = datetime.now()  # Fecha y hora actual
    status = "1"  # Por defecto, el status es 1

    # Crear conexión con la base de datos
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Insertar la transacción en la tabla
        query = """
        INSERT INTO transacciones (simbolo, precio_compra, cantidad, fecha_compra, status)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (simbolo, precio_compra, cantidad, fecha_compra, status)
        cursor.execute(query, values)

        # Confirmar la transacción
        connection.commit()
        print(f"Transacción insertada exitosamente: {simbolo}, {cantidad} a {precio_compra}.")

    except Exception as e:
        print(f"Error al insertar la transacción: {e}")
    finally:
        # Cerrar conexión
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_active_transactions():
    """
    Consulta la base de datos y devuelve un arreglo con todas las transacciones en estado 1.

    Returns:
        list: Lista de transacciones con estado 1.
    """
    try:
        # Conexión a la base de datos
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Consulta SQL para obtener las transacciones con estado 1
        query = """
        SELECT id, simbolo, precio_compra, cantidad, fecha_compra, status
        FROM transacciones
        WHERE status = '1';
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        # Crear un arreglo con los resultados
        transactions = [
            row[1]
            for row in rows
        ]

        return transactions

    except Exception as e:
        print(f"Error al obtener las transacciones activas: {e}")
        return []

    finally:
        # Cerrar conexión
        if cursor:
            cursor.close()
        if connection:
            connection.close()



def get_active_transactions_details():
    """
    Consulta la base de datos y devuelve un arreglo con todas las transacciones en estado 1.

    Returns:
        list: Lista de transacciones con estado 1.
    """
    try:
        # Conexión a la base de datos
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Consulta SQL para obtener las transacciones con estado 1
        query = """
        SELECT id, simbolo, precio_compra, cantidad, fecha_compra, status
        FROM transacciones
        WHERE status = '1';
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        # Crear un arreglo con los resultados
        transactions = [
            {
                "id": row[0],
                "simbolo": row[1],
                "precio_compra": float(row[2]),
                "cantidad": float(row[3]),
                "fecha_compra": str(row[4]),
                "status": row[5],
            }
            for row in rows
        ]

        return transactions

    except Exception as e:
        print(f"Error al obtener las transacciones activas: {e}")
        return []

    finally:
        # Cerrar conexión
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def process_sale(data):
    
    """
    Inserta una venta en la tabla `ventas` y actualiza el estado de la transacción en la tabla `transacciones`.

    Args:
        data (dict): Objeto con los detalles de la venta.
    """
    try:
        # Conexión a la base de datos
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Extraer datos del objeto
        id_transaccion = data["id_transaccion"]
        porcentaje_ganancia = data["procentaje_ganancia"]
        precio_venta = float(data["fills"][0]["price"])
        cantidad = float(data["fills"][0]["qty"])
        fecha_venta = datetime.fromtimestamp(data["transactTime"] / 1000)

        # Insertar en la tabla ventas
        insert_query = """
        INSERT INTO ventas (precio_venta, cantidad, fecha_venta, id_transaccion, porcentaje_ganancia)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (precio_venta, cantidad, fecha_venta, id_transaccion, porcentaje_ganancia))

        # Actualizar el estado de la transacción en la tabla transacciones
        update_query = """
        UPDATE transacciones
        SET status = '2'
        WHERE id = %s
        """
        cursor.execute(update_query, (id_transaccion,))

        # Confirmar la transacción
        connection.commit()
        print(f"Venta procesada exitosamente para la transacción ID {id_transaccion}.")

    except Exception as e:
        print(f"Error al procesar la venta: {e}")
    finally:
        # Cerrar conexión
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def insertar_candidatos(simbolos):
    """
    Actualiza el estado de los candidatos existentes a 2 y 
    agrega nuevos candidatos con estado 1.

    Args:
        simbolos (list): Lista de símbolos a insertar con estado 1.
    """
    try:
        # Conexión a la base de datos
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Actualizar el estado de los candidatos existentes con estado 1 a estado 2
        update_query = """
        UPDATE candidatos
        SET status = '2'
        WHERE status = '1';
        """
        cursor.execute(update_query)

        # Insertar nuevos candidatos con estado 1
        insert_query = """
        INSERT INTO candidatos (simbolo, status)
        VALUES (%s, '1');
        """
        for simbolo in simbolos:
            cursor.execute(insert_query, (simbolo,))

        # Confirmar las transacciones
        connection.commit()
        print(f"Se actualizaron los candidatos existentes y se insertaron {len(simbolos)} nuevos símbolos.")

    except Exception as e:
        print(f"Error al procesar los candidatos: {e}")
    finally:
        # Cerrar conexión
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def obtener_candidatos_status_1():
    """
    Obtiene un arreglo con los símbolos de candidatos que tienen status = 1.

    Returns:
        list: Lista de símbolos con status 1.
    """
    try:
        # Conexión a la base de datos
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Consulta para obtener los símbolos con status = 1
        query = """
        SELECT simbolo
        FROM candidatos
        WHERE status = '1';
        """
        cursor.execute(query)

        # Obtener los resultados como una lista de símbolos
        resultados = [row[0] for row in cursor.fetchall()]
        return resultados

    except Exception as e:
        print(f"Error al obtener los candidatos con status 1: {e}")
        return []

    finally:
        # Cerrar conexión
        if cursor:
            cursor.close()
        if connection:
            connection.close()