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
    get_total_calories_today,
    get_cal_goal,
    get_all_foods,
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

    conn, cur = create_connection()
    total_cals = get_total_calories_today(username, conn, cur)

    conn, cur = create_connection()
    cal_goal = get_cal_goal(username, conn, cur)

    console.print("[bold magenta]Food Diary:  [/bold magenta]" + f"{today}")

    table = Table(show_header=True)
    table.add_column("User", style="dim", header_style="red", width=6)
    table.add_column("Meal", justify="center", min_width=20)
    table.add_column("Calories", header_style="green", style="green",
                     min_width=12)
    table.add_column("Time", style="magenta", header_style="magenta",
                     min_width=8)

    for i, entry in enumerate(entries):
        table.add_row(entry[0], entry[1], str(entry[2]), str(entry[3]))

    console.print(table)

    console.print(
        f"[green3] Total Calories: {total_cals} / [/green3]" +
        f"[bold red]{cal_goal}[/bold red]"
        )


@app.command(short_help="Retrieves all foods in the database.")
def foods():
    typer.echo("Retrieving all food items...")

    conn, cur = create_connection()
    foods = get_all_foods(conn, cur)

    table = Table()
    table.add_column("Name")
    table.add_column("Calories", header_style="green", style="green")
    table.add_column("Protein", header_style="purple", style="purple")
    table.add_column("Fat", header_style="dark_orange", style="dark_orange")
    table.add_column("Carbs", header_style="light_sky_blue1",
                     style="light_sky_blue1")

    for i, food in enumerate(foods):
        table.add_row(food[1], str(food[2]), str(food[3]), str(food[4]),
                      str(food[5]))

    console.print(table)


if __name__ == '__main__':
    app()
