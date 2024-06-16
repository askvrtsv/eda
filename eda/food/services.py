import collections
import datetime as dt

from eda.food import models


def get_menu_recipes_at(menu_date: dt.date) -> collections.defaultdict[str, list[str]]:
    menu_recipes = collections.defaultdict(list)
    menu = (
        models.Menu.objects.filter(date=menu_date)
        .prefetch_related("menu_recipes", "menu_recipes__recipe")
        .get()
    )
    for menu_recipe in menu.menu_recipes.all():
        mealtime = menu_recipe.get_mealtime_display()
        menu_recipes[mealtime].append(menu_recipe.recipe.name)
    return menu_recipes
