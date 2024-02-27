import datetime


class User:
    """
    Represents the user table.

    username: str
    weight: int
    weight_goal: int

    """

    def __init__(self, username, weight, weight_goal):
        self.username = username
        self.weight = weight
        self.weight_goal = weight_goal


class Macro:
    """
    Represents the macro table.

    name: str
    protein_alloc: int
    fatAllocation: int
    carbAllocation: int
    calGoal: int
    """

    def __init__(self, name, protein_pct, fat_pct, carb_pct, cal_goal):

        self.name = name
        self.protein_pct = protein_pct
        self.fat_pct = fat_pct
        self.carb_pct = carb_pct
        self.cal_goal = cal_goal


class UserMacro:
    """
    Represents the usermacro intersection table.

    user_id: int
    macro_id: int
    """

    def __init__(self, user_id, macro_id):

        self.user_id = user_id
        self.macro_id = macro_id


class Food:
    """
    Represents the foods table.

    name: str
    calories: int
    protein: int
    fat: int
    carbs: int
    """

    def __init__(self, name, calories, protein,  fat, carbs):

        self.name = name
        self.calories = calories
        self.protein = protein
        self.fat = fat
        self.carbs = carbs


class FoodEntry:
    """
    Represents the foodentries table.

    entry_id: int
    food_id: int
    user_id: int
    date: current date

    """

    def __init__(self, entry_id, food_id, user_id, date):

        self.entry_id = entry_id
        self.food_id = food_id
        self.user_id = user_id
        self.date = date if not date else datetime.datetime.now().isoformat()
        # TODO: fix this date implementation
