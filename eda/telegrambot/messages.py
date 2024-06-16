def generate_menu_message(menu: dict[str, list[str]]) -> str:
    lines = [
        f"*{mealtime.capitalize()}*\n" + "\n".join(recipes)
        for mealtime, recipes in menu.items()
        if recipes
    ]
    return "\n\n".join(lines).strip()
