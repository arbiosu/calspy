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
        cur.execute(sql, (user.username, user.weight, user.weightGoal))
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
    sql = "SELECT id FROM users WHERE username=?"
    try:
        cur.execute(sql, (username,))
        user_id = cur.fetchone()[0]
        return user_id
    except sqlite3.Error as e:
        print(f"Could not fetch the id of the user: {username}! ({e})")


def update_user(user: User, cols_to_update: list, conn, cur):
    """
    Updates the specified user's information.

    Args:
        user: a User object.
        cols_to_update: a list representing the columns to be updated.
        conn (sqlite3.Connection): A connection object
        curr (sqlite3.Cursor): A cursor object for executing SQL queries
    """

    set_clause = ", ".join(f"{col} = ?" for col in cols_to_update)

    sql = f"""
    UPDATE users
    SET {set_clause}
    WHERE username = ?
    """

    values = [getattr(user, col) for col in cols_to_update] + [user.username]

    try:
        cur.execute(sql, tuple(values))
        conn.commit()
        print(f"Successfully updated {user.username} in the database.")
    except sqlite3.Error as e:
        print(f"ERROR: Could not update {user.username}'s profile! ({e})")
    finally:
        conn.close()


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
        conn.commit()
        print(f"Recorded {macro.name} for user {username}")
    except sqlite3.Error as e:
        print(f"ERROR: Could not record macro {macro.name}! ({e})")
    finally:
        conn.close()


def get_cal_goal(username: str, conn, cur):
    """
    Gets the user's calorie goal for a specified macro.
    NOTE: currently only retrieves the user's most recent macro.

    Args:
        username: a string representing the user
        conn (sqlite3.Connection): A connection object.
        curr (sqlite3.Cursor): A cursor object for executing SQL queries.

    Returns:
        cal_goal: the user's calorie goal for the specified macro.
    """

    user_id = select_specific_user(username, conn, cur)
    sql = """
    SELECT m.name, m.calGoal
    FROM usermacros
    JOIN macros AS m ON usermacros.macroID = m.id
    WHERE usermacros.userID = ?
    ORDER BY usermacros.macroID
    DESC LIMIT 1
    """

    try:
        cur.execute(sql, (user_id,))
        cal_goal = cur.fetchone()[1]
        return cal_goal
    except sqlite3.Error as e:
        print(f"Error getting calorie goal for {username}! ({e})")
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


def get_all_foods(conn, cur):
    """
    Retrieve all foods stored in the database, sorted in descending order of
    calorie content.

    Args:
        conn (sqlite3.Connection): A connection object.
        curr (sqlite3.Cursor): A cursor object for executing SQL queries.

    Returns:
        food_list: a table of all foods stored in the database sorted in
        descending order of calorie content.
    """

    try:
        cur.execute("SELECT * FROM foods ORDER BY calories DESC")
        food_list = cur.fetchall()
        return food_list
    except sqlite3.Error as e:
        print(f"Could not retrieve all food items! ({e})")
    finally:
        conn.close()


def update_food_item(food: Food, cols_to_update: list, conn,
                     cur):
    """
    Update a food item's information.

    Args:
        food_name: a string representing the name of the food item
        food: a Food object.
        cols_to_update: a list representing the columns to update.
        conn (sqlite3.Connection): A connection object.
        curr (sqlite3.Cursor): A cursor object for executing SQL queries.
    """

    set_clause = ", ".join(f"{col} = ?" for col in cols_to_update)

    sql = f"""
    UPDATE foods
    SET {set_clause}
    WHERE name = ?
    """

    values = [getattr(food, col) for col in cols_to_update] + [food.name]

    try:
        cur.execute(sql, tuple(values))
        conn.commit()
        print(f"Successfully updated {food.name} in the database.")
    except sqlite3.Error as e:
        print(f"Could not update {food.name} in the database! ({e})")
    finally:
        conn.close()


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


def adjust_entry(username: str, food_name: str, date: str, conn, cur):
    """
    Adjusts a foodentry for a user. Only allows you to retroactively add to
    your daily diary.

    Args:
        username: a string representing the user who is logging the entry.
        food_name: a string representing the name of the food consumed.
        date: a string representing the date of the entry. (YYYY-MM-DD)
        conn (sqlite3.Connection): A connection object.
        curr (sqlite3.Cursor): A cursor object for executing SQL queries.
    """

    user_id = select_specific_user(username, conn, cur)
    food_id = select_food_item(food_name, conn, cur)
    sql = "INSERT INTO foodentries(foodID, userID, date) VALUES(?, ?, ?)"

    try:
        cur.execute(sql, (food_id, user_id, date))
        conn.commit()
        print(f"Successfully adjusted this entry for user {username}")
    except sqlite3.Error as e:
        print(f"Could not adjust this entry! ({e})")
    finally:
        conn.close()


def show_current_entry(username: str, conn, cur):
    """
    Shows all entries for today.

    Args:
        username: a string representing the user
        conn (sqlite3.Connection): A connection object.
        curr (sqlite3.Cursor): A cursor object for executing SQL queries.
    Returns:
        rows: a table showing all entries a user has made for today.
    """

    today = datetime.date.today().isoformat()
    user_id = select_specific_user(username, conn, cur)
    sql = """
    SELECT users.username, foods.name AS food, foods.calories, foodentries.time
    FROM foodentries
    JOIN users ON foodentries.userID = users.id
    JOIN foods ON foodentries.foodID = foods.id
    WHERE users.id = ? AND date = ?
    """

    try:
        cur.execute(sql, (user_id, today))
        rows = cur.fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"Could not fetch entries for {username} on {today}! ({e})")
    finally:
        conn.close()


def show_weekly_entries(username: str, conn, cur):
    """
    Shows all entries for the current week. (Sunday - Saturday)

    Args:
        username: a string representing the user
        conn (sqlite3.Connection): A connection object.
        curr (sqlite3.Cursor): A cursor object for executing SQL queries.
    Returns:
        rows: a table showing all entries a user has made for the current week.
    """

    user_id = select_specific_user(username, conn, cur)
    sql = """
    SELECT users.username, foods.name, foods.calories, foodentries.date
    FROM foodentries
    JOIN users ON foodentries.userID = users.id
    JOIN foods ON foodentries.foodID = foods.id
    WHERE foodentries.date BETWEEN DATE('now', 'weekday 0', '-6 days') AND DATE
    ('now', 'weekday 0') AND users.id = ?
    """

    try:
        cur.execute(sql, (user_id,))
        rows = cur.fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"Could not fetch the weekly entries for {username}! ({e})")
    finally:
        conn.close()


def show_monthly_entries(username: str, conn, cur):
    """
    Shows all entries for the current month.

    Args:
        username: a string representing the user
        conn (sqlite3.Connection): A connection object.
        curr (sqlite3.Cursor): A cursor object for executing SQL queries.
    Returns:
        rows:a table showing all entries a user has made for the current month.
    """

    user_id = select_specific_user(username, conn, cur)
    sql = """
    SELECT users.username, foods.name, foods.calories, foodentries.date
    FROM foodentries
    JOIN users ON foodentries.userID = users.id
    JOIN foods ON foodentries.foodID = foods.id
    WHERE foodentries.date BETWEEN DATE('now', 'start of month') AND
    DATE('now', 'start of month', '+1 month', '-1 day') AND users.id = ?
    ORDER BY foodentries.date ASC
    """

    try:
        cur.execute(sql, (user_id,))
        rows = cur.fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"Could not fetch the monthly entries for {username}! ({e})")
    finally:
        conn.close()


def get_total_calories_today(username: str, conn, cur):
    """
    Gets the user's total caloric intake for today.

    Args:
        username: a string representing the user
        conn (sqlite3.Connection): A connection object.
        curr (sqlite3.Cursor): A cursor object for executing SQL queries.
    """

    today = datetime.date.today().isoformat()
    user_id = select_specific_user(username, conn, cur)
    sql = """
    SELECT SUM(foods.calories)
    FROM foodentries
    JOIN users ON foodentries.userID = users.id
    JOIN foods ON foodentries.foodID = foods.id
    WHERE users.id = ? AND date = ?
    """

    try:
        cur.execute(sql, (user_id, today))
        total_calories = cur.fetchone()[0]
        return total_calories
    except sqlite3.Error as e:
        print(f"Could not fetch {username}'s calories for {today}! ({e})")
    finally:
        conn.close()


def get_weekly_calories(username: str, conn, cur):
    """
    Gets the user's total caloric intake for the current week.

    Args:
        username: a string representing the user
        conn (sqlite3.Connection): A connection object.
        curr (sqlite3.Cursor): A cursor object for executing SQL queries.
    """

    user_id = select_specific_user(username, conn, cur)
    sql = """
    SELECT SUM(foods.calories)
    FROM foodentries
    JOIN users ON foodentries.userID = users.id
    JOIN foods ON foodentries.foodID = foods.id
    WHERE foodentries.date BETWEEN DATE('now', 'weekday 0', '-6 days') AND DATE
    ('now', 'weekday 0') AND users.id = ?
    """

    try:
        cur.execute(sql, (user_id,))
        weekly_calories = cur.fetchone()[0]
        return weekly_calories
    except sqlite3.Error as e:
        print(f"Could not fetch {username}'s weekly calories! ({e})")
    finally:
        conn.close()


def get_monthly_calories(username: str, conn, cur):
    """
    Gets the user's total caloric intake for the current month.

    Args:
        username: a string representing the user
        conn (sqlite3.Connection): A connection object.
        curr (sqlite3.Cursor): A cursor object for executing SQL queries.
    """

    user_id = select_specific_user(username, conn, cur)
    sql = """
    SELECT SUM(foods.calories)
    FROM foodentries
    JOIN users ON foodentries.userID = users.id
    JOIN foods ON foodentries.foodID = foods.id
    WHERE foodentries.date BETWEEN DATE('now', 'start of month') AND
    DATE('now', 'start of month', '+1 month', '-1 day') AND users.id = ?
    """

    try:
        cur.execute(sql, (user_id,))
        monthly_calories = cur.fetchone()[0]
        return monthly_calories
    except sqlite3.Error as e:
        print(f"Could not fetch {username}'s monthly calories! ({e})")
    finally:
        conn.close()


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
