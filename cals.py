import typer
import datetime
from rich.console import Console
from rich.table import Table
from models import User, Macro, Food
from database import (
    create_connection,
    create_all_tables,
    create_user,
    create_macro,
    create_food,
    create_entry,
    show_current_entry,
)


console, app = Console(), typer.Typer()

conn, cur = create_connection()

create_all_tables(conn, cur)


@app.command(short_help='Creates a new user.')
def register(username: str, weight: int, weight_goal: int):
    typer.echo(f"Attempting to create profile for {username}...")
    conn, cur = create_connection()

    user = User(username, weight, weight_goal)
    create_user(user, conn, cur)


@app.command(short_help='Creates a new macro for the specified user.')
def macro(username: str, name: str, protein, fat, carbs, cal_goal: int):
    typer.echo(f"Adding {name} macro for {username}...")
    conn, cur = create_connection()

    macro = Macro(name, protein, fat, carbs, cal_goal)
    create_macro(username, macro, conn, cur)


@app.command(short_help='Adds a new food item to the database.')
def add(name: str, calories, protein, fat, carbs: int):
    typer.echo(f"Adding food item {name} to the database...")
    conn, cur = create_connection()

    food = Food(name, calories, protein, fat, carbs)
    create_food(food, conn, cur)


@app.command(short_help='Creates a new food entry for the user.')
def entry(username: str, food_name: str):
    today = datetime.datetime.now().isoformat()
    typer.echo(f"Adding {food_name} to {username}'s food diary for {today}.")

    conn, cur = create_connection()
    create_entry(username, food_name, conn, cur)


@app.command(short_help='Show all entries for the current day.')
def show(username: str):
    today = datetime.date.today()
    typer.echo(f"Printing {username}'s food diary for {today}")

    conn, cur = create_connection()
    entries = show_current_entry(username, conn, cur)
    console.print("[bold magenta]Food Diary[/bold magenta]")

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("User", style="dim", width=6)
    table.add_column("Meal", min_width=20)
    table.add_column("Calories", min_width=12)
    table.add_column("Date", min_width=12)
    table.add_column("Time", min_width=12)

    for i, entry in enumerate(entries):
        table.add_row(entry[0], entry[1], str(entry[2]), str(entry[3]))

    console.print(table)

    conn.close()


if __name__ == '__main__':
    app()
