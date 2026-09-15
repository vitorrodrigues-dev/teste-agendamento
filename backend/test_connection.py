import db


def main():
    connection = db.get_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT 1 FROM DUAL")
            result = cursor.fetchone()
            print(f"Conexao com o Oracle funcionou. Resultado: {result[0]}")
        finally:
            cursor.close()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
