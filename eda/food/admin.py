import datetime as dt

from django.contrib import admin

from eda.food import models


class IngredientInline(admin.TabularInline):
    model = models.Ingredient
    extra = 1


class MenuRecipeInline(admin.TabularInline):
    model = models.MenuRecipes
    extra = 3


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    fields = ["name", "how_to", "num_portions"]
    inlines = [IngredientInline]
    list_display = ["name", "num_portions"]


@admin.register(models.Menu)
class MenuAdmin(admin.ModelAdmin):
    inlines = [MenuRecipeInline]
    list_display = ["date", "is_today", "breakfast", "lunch", "dinner"]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                "menu_recipes",
                "menu_recipes__recipe",
            )
        )

    def is_today(self, obj: models.Menu) -> bool:
        return obj.date == dt.date.today()

    def breakfast(self, menu: models.Menu) -> str:
        return self._format_mealtime_recipes(
            menu, models.MenuRecipes.Mealtime.BREAKFAST
        )

    def lunch(self, menu: models.Menu) -> str:
        return self._format_mealtime_recipes(menu, models.MenuRecipes.Mealtime.LUNCH)

    def dinner(self, menu: models.Menu) -> str:
        return self._format_mealtime_recipes(menu, models.MenuRecipes.Mealtime.DINNER)

    @staticmethod
    def _format_mealtime_recipes(menu: models.Menu, mealtime) -> str:
        qs = menu.menu_recipes.filter(mealtime=mealtime)
        return ", ".join([str(recipe.recipe) for recipe in qs.all()])

    is_today.boolean = True  # type: ignore
    is_today.short_description = "Сегодня"

    breakfast.short_description = "Завтрак"
    lunch.short_description = "Обед"
    dinner.short_description = "Ужин"
