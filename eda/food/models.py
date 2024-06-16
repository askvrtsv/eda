from django.db import models
from django.utils import formats

from eda.core.models import BaseModel


class Product(BaseModel):
    name = models.CharField("название", max_length=255, unique=True)

    class Meta:
        db_table = "products"
        ordering = ["name"]
        verbose_name = "продукт"
        verbose_name_plural = "продукты"


class Recipe(BaseModel):
    name = models.CharField("название", max_length=255, unique=True)
    num_portions = models.PositiveSmallIntegerField("количество порций", default=1)
    how_to = models.TextField("инструкция", max_length=4096, null=True, blank=True)

    class Meta:
        db_table = "recipes"
        ordering = ["name"]
        verbose_name = "блюдо"
        verbose_name_plural = "блюда"


class Ingredient(BaseModel):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredients",
        verbose_name="блюдо",
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name="продукт"
    )
    weight = models.PositiveSmallIntegerField("вес")

    class Meta:
        db_table = "ingredients"
        ordering = ["-weight", "product__name"]
        unique_together = ["recipe", "product"]
        verbose_name = "ингредиент"
        verbose_name_plural = "ингредиенты"


class Menu(BaseModel):
    date = models.DateField("дата", unique=True)

    def __str__(self) -> str:
        return formats.date_format(self.date)

    class Meta:
        db_table = "menus"
        ordering = ["-date"]
        verbose_name = "меню"
        verbose_name_plural = "меню"


class MenuRecipes(BaseModel):
    class Mealtime(models.TextChoices):
        BREAKFAST = "breakfast", "завтрак"
        LUNCH = "lunch", "обед"
        DINNER = "dinner", "ужин"

    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name="menu_recipes",
        verbose_name="меню",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="breakfast_recipes",
        verbose_name="блюдо",
    )
    mealtime = models.CharField(max_length=16, choices=Mealtime)
    count = models.FloatField("количество", default=1.0)

    class Meta:
        db_table = "menu_recipes"
        ordering = ["recipe__name"]
        verbose_name = "блюдо"
        verbose_name_plural = "завтрак"
