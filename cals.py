import typer
import datetime
from rich.console import Console
from rich.table import Table
from models import User, Macro, Food
from database import (
    create_connection,
    create_all_tables,
    create_user,
    select_specific_user,
    create_macro,
    create_food,
    select_food_item,
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
    typer.ehco(f"Adding {name} macro for {username}...")


@app.command(short_help='Adds a new food item to the database.')
def add(name:str, calories, protein, fat, carbs: int):
    typer.echo(f"Adding food item {name} to the database...")



if __name__ == '__main__':
    app()
