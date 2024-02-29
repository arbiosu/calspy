import typer
import datetime
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated
from models import User, Macro, Food
from database import (
    create_connection,
    create_all_tables,
    create_user,
    create_macro,
    create_food,
    create_entry,
    show_current_entry,
    show_weekly_entries,
    show_monthly_entries,
    get_total_calories_today,
    get_weekly_calories,
    get_monthly_calories,
    get_cal_goal,
    get_all_foods,
    update_food_item,
    update_user,
    adjust_entry,
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
def entry(
    username: str,
    food_name: str,
    date: Annotated[str, typer.Option(
        help="Date food was consumed. MUST be in YYYY-MM-DD format."
        )] = ""
):
    if date:
        typer.echo(
            f"Adding {food_name} to {username}'s food diary for {date}."
            )
        conn, cur = create_connection()
        adjust_entry(username, food_name, date, conn, cur)
        return
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


@app.command(short_help="Update a food item, user, or macro.")
def upd(
    food: Annotated[str, typer.Option(help="given name is a food")] = "",
    user: Annotated[str, typer.Option(help="given name is a user.")] = "",
    macro: Annotated[str, typer.Option(help="given name is a macro.")] = ""

):
    if food:
        console.print(
            f"Please enter the values you would like to UPDATE for {food}" +
            "(type: [bold red]food)[/bold red]"
            )
        cols, food_item = [], Food(food)  # store columns user wants to update

        calories = input("Calories: ")
        cols.append("calories") if calories != "" else None
        food_item.calories = int(calories) if calories != "" else None

        protein = input("Protein: ")
        cols.append("protein") if protein != "" else None
        food_item.protein = int(protein) if protein != "" else None

        fat = input("Fat: ")
        cols.append("fat") if fat != "" else None
        food_item.fat = int(fat) if fat != "" else None

        carbs = input("Carbs: ")
        cols.append("carbs") if carbs != "" else None
        food_item.carbs = int(carbs) if carbs != "" else None

        conn, cur = create_connection()
        typer.echo("Updating food item...")
        update_food_item(food_item, cols, conn, cur)
    if user:
        console.print(
            f"Please enter the values you would like to UPDATE for {user}  " +
            "(type: [bold red]user)[/bold red]"
            )
        cols, user = [], User(user)

        cur_weight = input("Weight: ")
        cols.append("weight") if cur_weight != "" else None
        user.weight = int(cur_weight) if cur_weight != "" else None

        weight_goal = input("Weight Goal: ")
        cols.append("weightGoal") if weight_goal != "" else None
        user.weight_goal = weight_goal if weight_goal != "" else None

        conn, cur = create_connection()
        typer.echo("Updating user profile...")
        update_user(user, cols, conn, cur)

    if macro:
        pass


@app.command(short_help="Shows the weekly entries for the given user.")
def weekly(username: str):
    typer.echo(f"Displaying {username}'s weekly food diary...")

    conn, cur = create_connection()
    entries = show_weekly_entries(username, conn, cur)
    console.print("[bold magenta]Weekly Food Diary:  [/bold magenta]")

    table = Table(show_header=True)
    table.add_column("User", style="dim", header_style="red", width=6)
    table.add_column("Meal", justify="center", min_width=20)
    table.add_column("Calories", header_style="green", style="green",
                     min_width=12)
    table.add_column("Date", style="magenta", header_style="magenta",
                     min_width=8)

    for i, entry in enumerate(entries):
        table.add_row(entry[0], entry[1], str(entry[2]), str(entry[3]))

    console.print(table)

    conn, cur = create_connection()
    weekly_cals = get_weekly_calories(username, conn, cur)
    conn, cur = create_connection()
    cal_goal = get_cal_goal(username, conn, cur)
    cal_goal *= 7

    console.print(
        f"[green3]Weekly Calories: {weekly_cals} / [/green3]" +
        f"[bold red]{cal_goal}[/bold red]"
        )

    if weekly_cals > cal_goal:
        console.print(
            ":warning:" + " " +
            "[bold red]You have exceeded your weekly calorie goal![/bold red]"
            + ":warning:"
            )
    else:
        console.print(
            ":white_heavy_check_mark:" + " " +
            "[bold green]You are within your weekly calorie goal![/bold green]"
            + ":white_heavy_check_mark:"
            )


@app.command(short_help="Shows the monthly entries for the given user.")
def monthly(username: str):
    typer.echo(f"Displaying {username}'s monthly food diary...")

    conn, cur = create_connection()
    entries = show_monthly_entries(username, conn, cur)
    console.print("[bold magenta]Monthly Food Diary:  [/bold magenta]")

    table = Table(show_header=True)
    table.add_column("User", style="dim", header_style="red", width=6)
    table.add_column("Meal", justify="center", min_width=20)
    table.add_column("Calories", header_style="green", style="green",
                     min_width=12)
    table.add_column("Date", style="magenta", header_style="magenta",
                     min_width=8)

    for i, entry in enumerate(entries):
        table.add_row(entry[0], entry[1], str(entry[2]), str(entry[3]))

    console.print(table)

    conn, cur = create_connection()
    monthly_cals = get_monthly_calories(username, conn, cur)
    conn, cur = create_connection()
    cal_goal = get_cal_goal(username, conn, cur)
    cal_goal *= 30

    console.print(
        f"[green3]Monthly Calories: {monthly_cals} / [/green3]" +
        f"[bold red]{cal_goal}[/bold red]"
        )

    if monthly_cals > cal_goal:
        console.print(
            ":warning:" + " " +
            "[bold red]You have exceeded your monthly calorie goal![/bold red]"
            + ":warning:"
            )
    else:
        console.print(
            ":white_heavy_check_mark:" + " " +
            "[bold green]You are within your monthly calorie goal![/]"
            + ":white_heavy_check_mark:"
        )


if __name__ == '__main__':
    app()
