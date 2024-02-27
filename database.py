import sqlite3
import datetime


def create_connection(db_file="calories.db") -> tuple[sqlite3.Connection,
                                                      sqlite3.Cursor]:
    """
    Establishes a connection to the calories database.

    Args:
        db_file (str): Path to the SQLite database file (default: "calories.db)

    Returns:
        conn (sqlite3.Connection): A connection object
        curr (sqlite3.Cursor): A cursor object for executing SQL queries
    """

    try:
        conn = sqlite3.connect("calories.db")
        cur = conn.cursor()
        print(f"Connected to the database '{db_file} successfully!")
        return conn, cur
    except sqlite3.Error as e:
        print(f"ERROR: could not establish connection to '{db_file}' ({e})")


def create_users_table(conn: sqlite3.Connection, cur: sqlite3.Cursor) -> None:
    """
    Creates the users table.

    Args:
        conn (sqlite3.Connection): A connection object
        curr (sqlite3.Cursor): A cursor object for executing SQL queries

    Schema:
        id: primary key
        username: specified username
        weight: the user's current weight
        weightGoal: the user's goal weight
    """

    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                weight INTEGER,
                weightGoal INTEGER);
                """)
        conn.commit()
        print("Successfully created the users table.")
    except sqlite3.Error as e:
        print(f"ERROR: could not create users table! ({e})")
    finally:
        conn.close()


def create_macros_table(conn: sqlite3.Connection, cur: sqlite3.Cursor) -> None:
    """
    Creates the macros table.

    Args:
        conn (sqlite3.Connection): A connection object
        curr (sqlite3.Cursor): A cursor object for executing SQL queries

    Schema:
        id: primary key
        name: name of the macro
        proteinAllocation: the allocated percentage of calories towards protein
        fatAllocation: the allocated percentage of calories towards fat
        carbAllocation: the allocated percentage of calories towards carbs
        calGoal: the daily caloric intake goal for this macro
    """

    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS macros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                proteinAllocation INTEGER,
                fatAllocation INTEGER,
                carbAllocation INTEGER,
                calGoal INTEGER);
                """)
        conn.commit()
        print("Successfully created the macros table.")
    except sqlite3.Error as e:
        print(f"ERROR: could not create macros table! ({e})")
    finally:
        conn.close()


def create_usermacros_table(conn: sqlite3.Connection, cur: sqlite3.Cursor) ->None:
    """
    Creates the usermacros intersection table.

    Args:
        conn (sqlite3.Connection): A connection object
        curr (sqlite3.Cursor): A cursor object for executing SQL queries

    Schema:
        userID: fk references users(id)
        macroID: fk references macros(id)
    """

    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS usermacros (
                userID INTEGER REFERENCES users(id),
                macroID INTEGER REFERENCES macros(id));
                """)
        conn.commit()
        print("Successfully created the usermacros table.")
    except sqlite3.Error as e:
        print(f"ERROR: could not create usermacros table! ({e})")
    finally:
        conn.close()


def create_foods_table(conn: sqlite3.Connection, cur: sqlite3.Cursor) ->None:
    """
    Creates the foods table.

    Args:
        conn (sqlite3.Connection): A connection object
        curr (sqlite3.Cursor): A cursor object for executing SQL queries

    Schema:
        id: pk
        name: name of the food item
        calories: total calories
        protein: total grams of protein
        fat: total grams of fat
        carbs: total grams of carbs
    """

    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS foods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                calories INTEGER NOT NULL,
                protein INTEGER,
                fat INTEGER,
                carbs INTEGER);
                """)
        conn.commit()
        print("Successfully created the foods table.")
    except sqlite3.Error as e:
        print(f"ERROR: could not create foods table! ({e})")
    finally:
        conn.close()


def create_foodentries_table(conn: sqlite3.Connection, cur: sqlite3.Cursor) ->None:
    """
    Creates the foodentries intersection table.

    Args:
        conn (sqlite3.Connection): A connection object
        curr (sqlite3.Cursor): A cursor object for executing SQL queries

    Schema:
        id: pk
        foodID: fk references foods(id)
        userID: fk references users(id)
        date: date of the entry, defaults to the current day
        time: the time the entry was created
    """

    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS foodentries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                foodID INTEGER REFERENCES foods(id),
                userID INTEGER REFERENCES users(id),
                date DATETIME DEFAULT CURRENT_DATE,
                time DATETIME DEFAULT CURRENT_TIME
                );
                """)
        conn.commit()
        print("Successfully created the foodentries table.")
    except sqlite3.Error as e:
        print(f"ERROR: could not create foodentries table! ({e})")
    finally:
        conn.close()