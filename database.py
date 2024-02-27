import sqlite3
import datetime
from models import User, Macro, Food


def create_connection(db_file="calories.db"):
    """
    Establishes a connection to the calories database.

    Args:
        db_file (str): Path to the SQLite database file (default: "calories.db)

    Returns:
        A tuple containing:
            conn (sqlite3.Connection): A connection object
            curr (sqlite3.Cursor): A cursor object for executing SQL queries
    """

    try:
        conn = sqlite3.connect("calories.db")
        cur = conn.cursor()
        return conn, cur
    except sqlite3.Error as e:
        print(f"ERROR: could not establish connection to '{db_file}' ({e})")


def create_users_table(conn, cur):
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


def create_macros_table(conn, cur):
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


def create_usermacros_table(conn, cur):
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


def create_foods_table(conn, cur):
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


def create_foodentries_table(conn, cur):
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


def create_user(user: User, conn, cur):
    """
    Create a user.

    Args:
        user (User): a User object
        conn (sqlite3.Connection): A connection object
        curr (sqlite3.Cursor): A cursor object for executing SQL queries
    """

    sql = "INSERT INTO users(username, weight, weightGoal) VALUES (?, ?, ?)"
    try:
        cur.execute(sql, (user.username, user.weight, user.weight_goal))
        conn.commit()
        print(f"Welcome, {user.username}.")
    except sqlite3.Error as e:
        print(f"ERROR: could not create user! ({e})")
    finally:
        conn.close()


def select_specific_user(username: str, conn, cur) -> str:
    """
    Select a specific user by their username.
    Args:
        user (User): a User object
        conn (sqlite3.Connection): A connection object
        curr (sqlite3.Cursor): A cursor object for executing SQL queries

    Returns:
        user_id: the id of the user specified
    """
    #sql = "SELECT id FROM users WHERE username=?"
    try:
        cur.execute("SELECT id FROM users WHERE username=?", (username,))
        user_id = cur.fetchone()[0]
        return user_id
    except sqlite3.Error as e:
        print(f"Could not fetch the id of the user: {username}! ({e})")


def create_macro(username: str, macro: Macro, conn, cur):
    """
    Creates a macro for a specified user and records it into usermacros.

    Args:
        username: the username of the user creating a macro.
        macro: a Macro object.
        conn (sqlite3.Connection): A connection object
        curr (sqlite3.Cursor): A cursor object for executing SQL queries
    """
    user_id = select_specific_user(username, conn, cur)

    sql = """
    INSERT INTO macros(id, name, proteinAllocation, fatAllocation,
    carbAllocation, calGoal) VALUES (?, ?, ?, ?, ?, ?)
    """
    usermacros_sql = "INSERT INTO usermacros(userID, macroID) VALUES (?, ?)"
    try:
        cur.execute(sql, (None, macro.name, macro.protein_pct, macro.fat_pct,
                          macro.carb_pct, macro.cal_goal))
        conn.commit()
        macro_id = cur.lastrowid
        cur.execute(usermacros_sql, (user_id, macro_id))
        print(f"Recorded {macro.name} for user {username}")
    except sqlite3.Error as e:
        print(f"ERROR: Could not record macro {macro.name}! ({e})")
    finally:
        conn.close()


def create_food(food: Food, conn, cur):
    """
    Creates a food item.

    Args:
        food: a Food object.
        conn (sqlite3.Connection): A connection object
        curr (sqlite3.Cursor): A cursor object for executing SQL queries
    """

    sql = """
    INSERT INTO foods(id, name, calories, protein, fat, carbs)
    VALUES (?, ?, ?, ?, ?, ?)
    """

    try:
        cur.execute(sql, (None, food.name, food.calories, food.protein,
                          food.fat, food.carbs))
        conn.commit()
        print(f"Successfully logged {food.name} into the database.")
    except sqlite3.Error as e:
        print(f"Could not log {food.name} into the database! ({e})")
    finally:
        conn.close()


def select_food_item(food_name: str, conn, cur) -> str:
    """
    Gets the id of the food item.

    Args:
        food_name: a string representing the name of the food item.
        conn (sqlite3.Connection): A connection object.
        curr (sqlite3.Cursor): A cursor object for executing SQL queries.

    Returns:
        food_id: the id of the food specified.
    """

    sql = "SELECT id FROM foods WHERE name=?"

    try:
        cur.execute(sql, (food_name,))
        food_id = cur.fetchone()[0]
        return food_id
    except sqlite3.Error as e:
        print(f"Could not fetch the id of {food_name}! ({e})")


def create_entry(username: str, food_name: str, conn, cur):
    """
    Creates a foodentry for a user, indicating they consumed this food on the
    given date. Date defaults to current day and time.

    Args:
        username: a string representing the user who is logging the entry.
        food_name: a string representing the name of the food consumed.
        conn (sqlite3.Connection): A connection object.
        curr (sqlite3.Cursor): A cursor object for executing SQL queries.
    """

    user_id = select_specific_user(username, conn, cur)
    food_id = select_food_item(food_name, conn, cur)
    sql = "INSERT INTO foodentries(foodID, userID) VALUES(?, ?)"

    try:
        cur.execute(sql, (food_id, user_id))
        conn.commit()
        print(f"Successfully recorded this entry for user {username}")
    except sqlite3.Error as e:
        print(f"Could not log this entry! ({e})")
    finally:
        conn.close()


def show_current_entry(username: str, conn, cur):
    """
    Shows all entries for today.

    Args:
        username: a string representing the user
        conn (sqlite3.Connection): A connection object.
        curr (sqlite3.Cursor): A cursor object for executing SQL queries.
    """

    today = datetime.date.today().isoformat()
    user_id = select_specific_user(username, conn, cur)
    sql = "SELECT * FROM foodentries WHERE userID=? AND date=?"

    try:
        cur.execute(sql, (user_id, today))
        rows = cur.fetchall()
        for row in rows:
            print(row)
    except sqlite3.Error as e:
        print(f"Could not fetch entries for {username} on {today}! ({e})")


def create_all_tables(conn, cur):
    """
    Creates all tables for the calories database.

    Args:
        conn (sqlite3.Connection): A connection object.
        curr (sqlite3.Cursor): A cursor object for executing SQL queries.
    """

    create_users_table(conn, cur)
    conn, cur = create_connection()
    create_macros_table(conn, cur)
    conn, cur = create_connection()
    create_usermacros_table(conn, cur)
    conn, cur = create_connection()
    create_foods_table(conn, cur)
    conn, cur = create_connection()
    create_foodentries_table(conn, cur)
    conn, cur = create_connection()
