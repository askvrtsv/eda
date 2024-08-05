import collections
import datetime as dt

from asgiref.sync import sync_to_async
from django.db.models import Case, IntegerField, Prefetch, When

from eda.food import models


@sync_to_async(thread_sensitive=False)
def get_menu_recipes_at(menu_date: dt.date) -> collections.defaultdict[str, list[str]]:
    menu_recipes = collections.defaultdict(list)
    menu = (
        models.Menu.objects.filter(date=menu_date)
        .prefetch_related(
            Prefetch(
                "menu_recipes",
                queryset=models.MenuRecipes.objects.annotate(
                    ordering=Case(
                        When(mealtime="breakfast", then=0),
                        When(mealtime="lunch", then=1),
                        When(mealtime="dinner", then=2),
                        output_field=IntegerField(),
                    )
                ).order_by("ordering"),
            ),
            "menu_recipes__recipe",
        )
        .get()
    )
    for menu_recipe in menu.menu_recipes.all():
        mealtime = menu_recipe.get_mealtime_display()
        menu_recipes[mealtime].append(menu_recipe.recipe.name)
    return menu_recipes


@sync_to_async(thread_sensitive=False)
def get_grocery_list(from_date: dt.date, to_date: dt.date) -> list[str]:
    products = (
        models.Menu.objects.filter(
            date__gte=from_date,
            date__lte=to_date,
            menu_recipes__recipe__ingredients__product__show_in_grocery_list=True,
        )
        .prefetch_related(
            "menu_recipes",
            "menu_recipes__recipe",
            "menu_recipes__recipe__ingredients",
            "menu_recipes__recipe__ingredients__product",
        )
        .values_list("menu_recipes__recipe__ingredients__product__name", flat=True)
    )
    return sorted(set(products))
