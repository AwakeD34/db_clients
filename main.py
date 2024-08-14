import psycopg2


def create_db(conn):
    cur = conn.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS clients_db;")
    conn.commit()
    cur.close()


def add_client(conn, first_name, last_name, email, phones=None):
    cur = conn.cursor()
    cur.execute("INSERT INTO clients (first_name, last_name, email) VALUES (%s, %s, %s) RETURNING id;", (first_name, last_name, email))
    client_id = cur.fetchone()
    conn.commit()
    cur.close()
    if phones:
        for phone in phones:
            add_phone(conn, client_id, phone)
    return client_id


def add_phone(conn, client_id, phone):
    cur = conn.cursor()
    cur.execute("INSERT INTO phones (client_id, phone) VALUES (%s, %s);", (client_id, phone))
    conn.commit()
    cur.close()


def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    cur = conn.cursor()
    if first_name:
        cur.execute("UPDATE clients SET first_name = %s WHERE id = %s;", (first_name, client_id))
    if last_name:
        cur.execute("UPDATE clients SET last_name = %s WHERE id = %s;", (last_name, client_id))
    if email:
        cur.execute("UPDATE clients SET email = %s WHERE id = %s;", (email, client_id))
    if phones:
        for phone in phones:
            add_phone(conn, client_id, phone)
    conn.commit()
    cur.close()


def delete_phone(conn, client_id, phone):
    cur = conn.cursor()
    cur.execute("DELETE FROM phones WHERE client_id = %s AND phone = %s;", (client_id, phone))
    conn.commit()
    cur.close()


def delete_client(conn, client_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM phones WHERE client_id = %s;", (client_id,))
    cur.execute("DELETE FROM clients WHERE id = %s;", (client_id,))
    conn.commit()
    cur.close()


def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    cur = conn.cursor()
    if first_name and last_name and email:
        cur.execute("SELECT * FROM clients WHERE first_name = %s AND last_name = %s AND email = %s;", (first_name, last_name, email))
    elif phone:
        cur.execute("""
            SELECT c.* FROM clients c
            JOIN phones p ON c.id = p.client_id
            WHERE p.phone = %s;
        """, (phone,))
    else:
        raise ValueError("Недостаточно данных для поиска")
    client = cur.fetchone()
    cur.close()
    return client


with psycopg2.connect(database="clients_db", user="postgres", password="489E6564k6!") as conn:
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS phones (
            id SERIAL PRIMARY KEY,
            client_id INTEGER NOT NULL,
            phone VARCHAR(20) NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        );
    """)
    conn.commit()
    cur.close()

    
    client_id = add_client(conn, "Сергей", "Аббазов", "whaterser@mail.ru", ["+79023607997", "+79582717185"])
    print(f"Добавлен клиент с id {client_id}")

    change_client(conn, client_id, email="whaterser@mail.ru")
    print("Данные о клиенте изменены")

    delete_phone(conn, client_id, "+79023607997")
    print("Телефон удален")

    delete_client(conn, client_id)
    print("Клиент удален")

    client = find_client(conn, phone="+79023607997")
    print(f"Найден клиент: {client}")

conn.close()