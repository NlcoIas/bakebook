"""
Idempotent seed script for Bakebook.

Usage:
    cd apps/api
    uv run python -m seed.seed

Seeds ~30 pantry items and 8 recipes with ingredients and steps.
Checks for existing data by name/slug before inserting.
"""

import asyncio
import sys
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models.base import Base, uuid7
from app.models.pantry import PantryItem
from app.models.recipe import Recipe, RecipeIngredient, RecipeStep

# ---------------------------------------------------------------------------
# Pantry item definitions
# ---------------------------------------------------------------------------
PANTRY_ITEMS: list[dict] = [
    # Flours
    {"name": "All-purpose flour", "cost_per_kg": Decimal("1.10"), "nutrition_ref": "all_purpose_flour", "default_role": "flour"},
    {"name": "Bread flour", "cost_per_kg": Decimal("1.20"), "nutrition_ref": "bread_flour", "default_role": "flour"},
    {"name": "Whole wheat flour", "cost_per_kg": Decimal("1.80"), "nutrition_ref": "whole_wheat_flour", "default_role": "flour"},
    {"name": "Rye flour", "cost_per_kg": Decimal("2.20"), "nutrition_ref": "rye_flour", "default_role": "flour"},
    {"name": "Spelt flour", "cost_per_kg": Decimal("2.50"), "nutrition_ref": "spelt_flour", "default_role": "flour"},
    {"name": "Zopfmehl", "cost_per_kg": Decimal("1.60"), "nutrition_ref": "zopfmehl", "default_role": "flour"},
    {"name": "Cornmeal", "cost_per_kg": Decimal("2.80"), "nutrition_ref": "cornmeal", "default_role": "flour"},
    # Leavens
    {"name": "Active dry yeast", "cost_per_kg": Decimal("18.00"), "nutrition_ref": "active_dry_yeast", "default_role": "leaven"},
    {"name": "Instant yeast", "cost_per_kg": Decimal("16.00"), "nutrition_ref": "instant_yeast", "default_role": "leaven"},
    {"name": "Fresh yeast", "cost_per_kg": Decimal("6.50"), "nutrition_ref": "fresh_yeast", "default_role": "leaven"},
    {"name": "Sourdough starter", "cost_per_kg": Decimal("0.80"), "nutrition_ref": "sourdough_starter", "default_role": "leaven"},
    {"name": "Baking powder", "cost_per_kg": Decimal("8.00"), "nutrition_ref": "baking_powder", "default_role": "leaven"},
    {"name": "Baking soda", "cost_per_kg": Decimal("4.50"), "nutrition_ref": "baking_soda", "default_role": "leaven"},
    # Dairy
    {"name": "Whole milk", "cost_per_kg": Decimal("1.60"), "nutrition_ref": "milk_whole", "default_role": "dairy"},
    {"name": "Buttermilk", "cost_per_kg": Decimal("2.40"), "nutrition_ref": "buttermilk", "default_role": "dairy"},
    {"name": "Heavy cream", "cost_per_kg": Decimal("6.80"), "nutrition_ref": "heavy_cream", "default_role": "dairy"},
    {"name": "Butter (unsalted)", "cost_per_kg": Decimal("12.00"), "nutrition_ref": "butter_unsalted", "default_role": "fat"},
    {"name": "Eggs", "cost_per_kg": Decimal("5.00"), "nutrition_ref": "egg_whole", "default_role": "egg"},
    # Sugars
    {"name": "Granulated sugar", "cost_per_kg": Decimal("1.20"), "nutrition_ref": "granulated_sugar", "default_role": "sugar"},
    {"name": "Brown sugar", "cost_per_kg": Decimal("2.80"), "nutrition_ref": "brown_sugar", "default_role": "sugar"},
    {"name": "Honey", "cost_per_kg": Decimal("14.00"), "nutrition_ref": "honey", "default_role": "sugar"},
    {"name": "Powdered sugar", "cost_per_kg": Decimal("2.50"), "nutrition_ref": "powdered_sugar", "default_role": "sugar"},
    # Fats / oils
    {"name": "Olive oil", "cost_per_kg": Decimal("9.50"), "nutrition_ref": "olive_oil", "default_role": "fat"},
    {"name": "Vegetable oil", "cost_per_kg": Decimal("3.20"), "nutrition_ref": "vegetable_oil", "default_role": "fat"},
    # Others
    {"name": "Table salt", "cost_per_kg": Decimal("0.80"), "nutrition_ref": "table_salt", "default_role": "salt"},
    {"name": "Cocoa powder", "cost_per_kg": Decimal("12.00"), "nutrition_ref": "cocoa_powder", "default_role": "other"},
    {"name": "Dark chocolate", "cost_per_kg": Decimal("16.00"), "nutrition_ref": "dark_chocolate", "default_role": "other"},
    {"name": "Vanilla extract", "cost_per_kg": Decimal("120.00"), "nutrition_ref": "vanilla_extract", "default_role": "other"},
    {"name": "Cinnamon", "cost_per_kg": Decimal("28.00"), "nutrition_ref": "cinnamon", "default_role": "other"},
    # Nuts / seeds
    {"name": "Walnuts", "cost_per_kg": Decimal("22.00"), "nutrition_ref": "walnuts", "default_role": "other"},
    {"name": "Almonds", "cost_per_kg": Decimal("18.00"), "nutrition_ref": "almonds", "default_role": "other"},
    # Extra: water (used in many bread recipes)
    {"name": "Water", "cost_per_kg": Decimal("0.00"), "nutrition_ref": "water", "default_role": "water"},
    # Banana (for banana bread)
    {"name": "Banana", "cost_per_kg": Decimal("2.50"), "nutrition_ref": "banana", "default_role": "other"},
]


# ---------------------------------------------------------------------------
# Recipe definitions
# ---------------------------------------------------------------------------
# Helper: ingredient tuples = (pantry_name, display_name, grams, role, ord, group_label, unit_display, unit_display_qty, notes)
# Helper: step tuples = (ord, title, body, timer_seconds, min_seconds, max_seconds, target_temp_c, temp_kind)

def _build_recipes(pantry_map: dict[str, PantryItem]) -> list[dict]:
    """Return recipe definitions with ingredients and steps.
    pantry_map maps PantryItem.name -> PantryItem instance (for id lookup).
    """

    recipes = []

    # -----------------------------------------------------------------------
    # 1. Buttermilk Cornbread
    # -----------------------------------------------------------------------
    recipes.append({
        "recipe": {
            "title": "Buttermilk Cornbread",
            "slug": "buttermilk-cornbread",
            "category": "quick",
            "summary": "Classic Southern-style cornbread baked in a cast iron skillet. Crispy edges, tender crumb, tangy buttermilk flavor.",
            "yields": "1 skillet, ~680 g",
            "servings": 8,
            "serving_g": Decimal("85.00"),
            "total_time_min": 40,
            "active_time_min": 15,
            "difficulty": 1,
            "equipment": ["cast iron skillet", "mixing bowl", "whisk"],
            "source": "family recipe",
            "notes": "Preheat the skillet with butter for crispy edges. Do not overmix.",
        },
        "ingredients": [
            # (pantry_name, display_name, grams, role, ord, group_label)
            ("Cornmeal", "Cornmeal", Decimal("170.00"), "other", 1, None),
            ("All-purpose flour", "All-purpose flour", Decimal("130.00"), "other", 2, None),
            ("Granulated sugar", "Sugar", Decimal("50.00"), "other", 3, None),
            ("Table salt", "Salt", Decimal("6.00"), "other", 4, None),
            ("Baking powder", "Baking powder", Decimal("8.00"), "other", 5, None),
            ("Baking soda", "Baking soda", Decimal("3.00"), "other", 6, None),
            ("Buttermilk", "Buttermilk", Decimal("240.00"), "other", 7, None),
            ("Eggs", "Egg", Decimal("50.00"), "other", 8, None),
            ("Butter (unsalted)", "Butter, melted", Decimal("56.00"), "other", 9, None),
        ],
        "steps": [
            (1, "Preheat oven", "Preheat oven to 220 C (425 F). Place cast iron skillet in the oven while it heats.", 600, 600, 900, Decimal("220.0"), "oven"),
            (2, "Mix dry ingredients", "In a large bowl, whisk together cornmeal, flour, sugar, salt, baking powder, and baking soda.", None, 60, 120, None, None),
            (3, "Mix wet ingredients", "In a separate bowl, whisk buttermilk, egg, and melted butter until combined.", None, 60, 120, None, None),
            (4, "Combine", "Pour wet ingredients into dry and stir until just combined. A few lumps are fine -- do not overmix.", None, 30, 60, None, None),
            (5, "Prepare skillet", "Carefully remove hot skillet from oven. Add a small pat of butter and swirl to coat the bottom and sides.", None, 30, 60, None, None),
            (6, "Pour batter", "Pour batter into the hot skillet. It should sizzle. Spread evenly.", None, 15, 30, None, None),
            (7, "Bake", "Bake until golden brown on top and a toothpick inserted in the center comes out clean.", 1200, 1200, 1500, Decimal("220.0"), "oven"),
            (8, "Cool", "Let cool in skillet for 5 minutes before slicing.", 300, 300, 600, None, None),
        ],
    })

    # -----------------------------------------------------------------------
    # 2. Swiss Butterzopf
    # -----------------------------------------------------------------------
    recipes.append({
        "recipe": {
            "title": "Swiss Butterzopf",
            "slug": "swiss-butterzopf",
            "category": "bread",
            "summary": "Traditional Swiss braided bread. Rich, buttery, with a golden egg-wash crust. Sunday breakfast staple.",
            "yields": "1 braided loaf, ~750 g",
            "servings": 8,
            "serving_g": Decimal("94.00"),
            "total_time_min": 180,
            "active_time_min": 40,
            "difficulty": 3,
            "equipment": ["stand mixer", "baking sheet", "pastry brush"],
            "source": "Swiss classic",
            "notes": "Zopfmehl (Swiss bread flour with slightly lower protein) gives the traditional soft texture. Bread flour works too.",
        },
        "ingredients": [
            ("Zopfmehl", "Zopfmehl", Decimal("500.00"), "flour", 1, "Dough"),
            ("Table salt", "Salt", Decimal("10.00"), "salt", 2, "Dough"),
            ("Granulated sugar", "Sugar", Decimal("40.00"), "sugar", 3, "Dough"),
            ("Fresh yeast", "Fresh yeast", Decimal("25.00"), "leaven", 4, "Dough"),
            ("Whole milk", "Whole milk, warm", Decimal("150.00"), "dairy", 5, "Dough"),
            ("Butter (unsalted)", "Butter, softened", Decimal("80.00"), "fat", 6, "Dough"),
            ("Eggs", "Eggs (2 for dough)", Decimal("100.00"), "egg", 7, "Dough"),
            ("Eggs", "Egg yolk (for wash)", Decimal("18.00"), "egg", 8, "Egg wash"),
            ("Whole milk", "Milk (for wash)", Decimal("15.00"), "dairy", 9, "Egg wash"),
        ],
        "steps": [
            (1, "Dissolve yeast", "Crumble fresh yeast into warm milk (about 35 C). Stir to dissolve and let sit 5 minutes.", 300, 300, 600, Decimal("35.0"), "water"),
            (2, "Mix dough", "In a stand mixer with the dough hook, combine flour, salt, and sugar. Add yeast-milk mixture and eggs. Mix on low for 2 minutes.", 120, 120, 180, None, None),
            (3, "Add butter", "With the mixer running on medium-low, add softened butter in pieces. Knead for 8-10 minutes until the dough is smooth, elastic, and pulls away from the sides.", 540, 480, 600, None, None),
            (4, "First rise", "Cover bowl with a damp towel or plastic wrap. Let rise at room temperature until doubled, about 1.5 hours.", 5400, 4500, 7200, None, None),
            (5, "Divide and shape strands", "Punch down dough. Divide into 2 equal pieces. Roll each into a strand about 50 cm long, thicker in the middle and tapered at the ends.", None, 300, 600, None, None),
            (6, "Braid", "Cross the two strands in the middle. Braid by alternately folding the outer strand over the inner one on each side. Tuck the ends under. Place on a parchment-lined baking sheet.", None, 180, 420, None, None),
            (7, "Second rise", "Cover loosely with a towel. Let rise 30-45 minutes until puffy but not quite doubled.", 2400, 1800, 2700, None, None),
            (8, "Preheat oven", "Preheat oven to 190 C (375 F).", 900, 600, 900, Decimal("190.0"), "oven"),
            (9, "Egg wash", "Whisk egg yolk with a tablespoon of milk. Brush the loaf generously, getting into the braid crevices.", None, 60, 120, None, None),
            (10, "Bake", "Bake on the middle rack for 30-35 minutes until deep golden brown. Internal temperature should reach 88-92 C.", 1920, 1800, 2100, Decimal("190.0"), "oven"),
            (11, "Cool", "Transfer to a wire rack. Let cool at least 20 minutes before slicing.", 1200, 1200, 1800, None, None),
        ],
    })

    # -----------------------------------------------------------------------
    # 3. No-Knead Dutch Oven Loaf
    # -----------------------------------------------------------------------
    recipes.append({
        "recipe": {
            "title": "No-Knead Dutch Oven Loaf",
            "slug": "no-knead-dutch-oven-loaf",
            "category": "bread",
            "summary": "Effortless artisan bread. Long, slow fermentation develops deep flavor with minimal hands-on work.",
            "yields": "1 round loaf, ~800 g",
            "servings": 10,
            "serving_g": Decimal("80.00"),
            "total_time_min": 960,
            "active_time_min": 15,
            "difficulty": 1,
            "equipment": ["Dutch oven", "mixing bowl", "parchment paper"],
            "source": "Jim Lahey / Sullivan Street Bakery",
            "notes": "Start the dough the evening before. The long fermentation is what gives this bread its character.",
        },
        "ingredients": [
            ("Bread flour", "Bread flour", Decimal("400.00"), "flour", 1, None),
            ("Table salt", "Salt", Decimal("8.00"), "salt", 2, None),
            ("Instant yeast", "Instant yeast", Decimal("2.00"), "leaven", 3, None),
            ("Water", "Water, room temperature", Decimal("310.00"), "water", 4, None),
        ],
        "steps": [
            (1, "Mix dough", "In a large bowl, whisk together flour, salt, and yeast. Add water and stir with a wooden spoon or spatula until a shaggy, sticky dough forms. No dry flour should remain.", None, 120, 300, None, None),
            (2, "Long ferment", "Cover bowl tightly with plastic wrap or a plate. Let sit at room temperature (18-22 C) for 12-18 hours. The dough is ready when the surface is dotted with bubbles and it has more than doubled.", 50400, 43200, 64800, None, None),
            (3, "Shape", "Flour your work surface generously. Scrape the dough out -- it will be very sticky. Fold it over on itself once or twice. Shape into a rough ball using floured hands or a bench scraper. Do not knead.", None, 120, 300, None, None),
            (4, "Second rise", "Place dough seam-side down on a piece of parchment paper. Dust top with flour. Cover with a towel. Let rise 1-2 hours until nearly doubled and the dough holds a finger indent slowly.", 5400, 3600, 7200, None, None),
            (5, "Preheat oven and Dutch oven", "Place the Dutch oven with its lid inside the oven. Preheat to 230 C (450 F) for at least 30 minutes.", 2400, 1800, 2400, Decimal("230.0"), "oven"),
            (6, "Score and load", "Carefully remove the hot Dutch oven. Lift the dough by the parchment and lower it in. Score the top with a sharp knife or razor blade -- one long slash or a cross.", None, 60, 120, None, None),
            (7, "Bake covered", "Cover with the lid. Bake for 30 minutes. The lid traps steam for oven spring and a crispy crust.", 1800, 1800, 2100, Decimal("230.0"), "oven"),
            (8, "Bake uncovered", "Remove the lid. Reduce oven to 210 C (410 F). Bake another 15-20 minutes until deep golden brown. Internal temperature should reach 95-98 C.", 1080, 900, 1200, Decimal("210.0"), "oven"),
            (9, "Cool", "Remove loaf from Dutch oven. Let cool on a wire rack for at least 45 minutes before cutting. The bread is still baking inside.", 2700, 2700, 3600, None, None),
        ],
    })

    # -----------------------------------------------------------------------
    # 4. Focaccia
    # -----------------------------------------------------------------------
    recipes.append({
        "recipe": {
            "title": "Focaccia",
            "slug": "focaccia",
            "category": "bread",
            "summary": "Olive oil-rich Italian flatbread. Crispy bottom, airy crumb, dimpled top loaded with flaky salt and herbs.",
            "yields": "1 sheet pan, ~900 g",
            "servings": 8,
            "serving_g": Decimal("112.00"),
            "total_time_min": 240,
            "active_time_min": 25,
            "difficulty": 2,
            "equipment": ["sheet pan", "mixing bowl"],
            "source": "Bon Appetit / Basically",
            "notes": "Generous olive oil is essential -- it fries the bottom and creates the signature crisp. Use good quality extra virgin.",
        },
        "ingredients": [
            ("Bread flour", "Bread flour", Decimal("500.00"), "flour", 1, "Dough"),
            ("Table salt", "Salt", Decimal("10.00"), "salt", 2, "Dough"),
            ("Granulated sugar", "Sugar", Decimal("10.00"), "sugar", 3, "Dough"),
            ("Instant yeast", "Instant yeast", Decimal("7.00"), "leaven", 4, "Dough"),
            ("Water", "Warm water", Decimal("375.00"), "water", 5, "Dough"),
            ("Olive oil", "Olive oil (for dough)", Decimal("30.00"), "fat", 6, "Dough"),
            ("Olive oil", "Olive oil (for pan and top)", Decimal("45.00"), "fat", 7, "Topping"),
            ("Table salt", "Flaky salt (for top)", Decimal("3.00"), "salt", 8, "Topping"),
        ],
        "steps": [
            (1, "Mix dough", "In a large bowl, combine flour, salt, sugar, and yeast. Add warm water (about 38 C) and olive oil. Mix with a spatula until a shaggy dough forms.", None, 120, 240, None, None),
            (2, "Stretch and fold", "Let the dough rest 10 minutes. Then perform a series of stretch-and-folds: pull one side up and fold over, rotate the bowl 90 degrees, repeat 4 times. Do this every 30 minutes for 1.5 hours (3 sets total).", 5400, 5400, 7200, None, None),
            (3, "Oil the pan", "Pour 2-3 tablespoons of olive oil into a sheet pan (about 33x23 cm). Spread to coat.", None, 60, 120, None, None),
            (4, "Transfer and stretch", "Transfer dough to the oiled pan. Gently stretch it toward the edges. If it springs back, let it rest 10 minutes and stretch again. It does not need to reach the corners yet.", None, 120, 300, None, None),
            (5, "Second rise", "Drizzle remaining olive oil over the top. Cover loosely. Let rise 45-60 minutes until puffy, bubbly, and filling the pan.", 3000, 2700, 3600, None, None),
            (6, "Preheat oven", "Preheat oven to 220 C (425 F).", 900, 600, 900, Decimal("220.0"), "oven"),
            (7, "Dimple", "Oil your fingers. Press them into the dough to create deep dimples across the entire surface, stretching it to fill the pan. Sprinkle with flaky salt.", None, 60, 120, None, None),
            (8, "Bake", "Bake for 25-30 minutes until golden brown on top and crispy on the bottom. The bottom should be deeply golden when you lift it with a spatula.", 1620, 1500, 1800, Decimal("220.0"), "oven"),
            (9, "Cool", "Remove from pan immediately onto a wire rack. Let cool at least 10 minutes.", 600, 600, 900, None, None),
        ],
    })

    # -----------------------------------------------------------------------
    # 5. Cinnamon Rolls
    # -----------------------------------------------------------------------
    recipes.append({
        "recipe": {
            "title": "Cinnamon Rolls",
            "slug": "cinnamon-rolls",
            "category": "sweet",
            "summary": "Soft, pillowy cinnamon rolls with a gooey brown sugar filling and cream cheese glaze.",
            "yields": "12 rolls, ~1200 g",
            "servings": 12,
            "serving_g": Decimal("100.00"),
            "total_time_min": 210,
            "active_time_min": 45,
            "difficulty": 3,
            "equipment": ["stand mixer", "rolling pin", "9x13 baking pan"],
            "source": "classic American",
            "notes": "For overnight rolls, refrigerate after shaping. Pull out in the morning and let come to room temperature (about 1 hour) before baking.",
        },
        "ingredients": [
            # Dough
            ("Bread flour", "Bread flour", Decimal("500.00"), "flour", 1, "Dough"),
            ("Granulated sugar", "Sugar", Decimal("65.00"), "sugar", 2, "Dough"),
            ("Table salt", "Salt", Decimal("7.00"), "salt", 3, "Dough"),
            ("Instant yeast", "Instant yeast", Decimal("7.00"), "leaven", 4, "Dough"),
            ("Whole milk", "Whole milk, warm", Decimal("180.00"), "dairy", 5, "Dough"),
            ("Eggs", "Egg", Decimal("50.00"), "egg", 6, "Dough"),
            ("Butter (unsalted)", "Butter, softened", Decimal("55.00"), "fat", 7, "Dough"),
            # Filling
            ("Butter (unsalted)", "Butter, softened (filling)", Decimal("40.00"), "fat", 8, "Filling"),
            ("Brown sugar", "Brown sugar", Decimal("150.00"), "sugar", 9, "Filling"),
            ("Cinnamon", "Ground cinnamon", Decimal("12.00"), "other", 10, "Filling"),
            # Glaze
            ("Heavy cream", "Heavy cream", Decimal("30.00"), "dairy", 11, "Glaze"),
            ("Powdered sugar", "Powdered sugar", Decimal("120.00"), "sugar", 12, "Glaze"),
            ("Vanilla extract", "Vanilla extract", Decimal("5.00"), "other", 13, "Glaze"),
        ],
        "steps": [
            (1, "Make dough", "In the stand mixer with dough hook, combine flour, sugar, salt, and yeast. Add warm milk and egg. Mix on low until combined, then medium for 5 minutes.", 300, 300, 420, None, None),
            (2, "Add butter to dough", "With mixer on medium-low, add softened butter a tablespoon at a time. Knead 5-7 minutes more until dough is smooth and elastic.", 420, 300, 420, None, None),
            (3, "First rise", "Place dough in a greased bowl. Cover with plastic wrap. Let rise until doubled, about 1-1.5 hours.", 4500, 3600, 5400, None, None),
            (4, "Prepare filling", "Mix brown sugar and cinnamon in a small bowl. Have softened butter ready.", None, 60, 120, None, None),
            (5, "Roll out dough", "On a lightly floured surface, roll the dough into a rectangle about 40 x 30 cm.", None, 180, 300, None, None),
            (6, "Fill and roll", "Spread softened butter evenly over the dough. Sprinkle the cinnamon-sugar filling all the way to the edges. Starting from the long side, roll tightly into a log.", None, 180, 300, None, None),
            (7, "Cut rolls", "Using a sharp knife or dental floss, cut the log into 12 equal pieces (~3 cm each). Place cut-side up in a greased 9x13 baking pan.", None, 120, 240, None, None),
            (8, "Second rise", "Cover the pan. Let rolls rise for 30-40 minutes until puffy and touching each other.", 2100, 1800, 2400, None, None),
            (9, "Preheat oven", "Preheat oven to 180 C (350 F).", 600, 600, 900, Decimal("180.0"), "oven"),
            (10, "Bake", "Bake for 22-28 minutes until golden brown on top. They should still feel slightly soft in the center.", 1500, 1320, 1680, Decimal("180.0"), "oven"),
            (11, "Make glaze", "While rolls bake, whisk together powdered sugar, heavy cream, and vanilla until smooth.", None, 60, 180, None, None),
            (12, "Glaze and serve", "Let rolls cool 5 minutes in the pan. Drizzle glaze over warm rolls. Serve immediately.", 300, 300, 600, None, None),
        ],
    })

    # -----------------------------------------------------------------------
    # 6. Toastbread / Sandwich Loaf
    # -----------------------------------------------------------------------
    recipes.append({
        "recipe": {
            "title": "Toastbread / Sandwich Loaf",
            "slug": "toastbread-sandwich-loaf",
            "category": "bread",
            "summary": "Soft, fine-crumbed sandwich bread with a thin crust. Perfect for toast and sandwiches.",
            "yields": "1 loaf, ~600 g",
            "servings": 12,
            "serving_g": Decimal("50.00"),
            "total_time_min": 180,
            "active_time_min": 25,
            "difficulty": 2,
            "equipment": ["stand mixer", "loaf pan (9x5 inch)"],
            "source": "King Arthur Baking",
            "notes": "Milk and butter give this bread its soft, tender crumb. Great base for cinnamon swirl variations.",
        },
        "ingredients": [
            ("Bread flour", "Bread flour", Decimal("360.00"), "flour", 1, None),
            ("Table salt", "Salt", Decimal("7.00"), "salt", 2, None),
            ("Granulated sugar", "Sugar", Decimal("25.00"), "sugar", 3, None),
            ("Instant yeast", "Instant yeast", Decimal("5.00"), "leaven", 4, None),
            ("Whole milk", "Whole milk, warm", Decimal("180.00"), "dairy", 5, None),
            ("Water", "Water, warm", Decimal("40.00"), "water", 6, None),
            ("Butter (unsalted)", "Butter, softened", Decimal("30.00"), "fat", 7, None),
        ],
        "steps": [
            (1, "Combine ingredients", "In a stand mixer with dough hook, combine flour, salt, sugar, and yeast. Add warm milk, water, and softened butter.", None, 120, 180, None, None),
            (2, "Knead", "Mix on low for 2 minutes to combine, then medium for 8-10 minutes until the dough is smooth, supple, and slightly tacky.", 600, 480, 720, None, None),
            (3, "First rise", "Place dough in a lightly greased bowl. Cover. Let rise until doubled, about 1-1.5 hours.", 4500, 3600, 5400, None, None),
            (4, "Shape", "Punch down dough. On a lightly floured surface, pat into a rectangle the width of your loaf pan. Roll up tightly from the short end. Pinch the seam closed.", None, 180, 300, None, None),
            (5, "Pan and proof", "Place seam-side down in a greased loaf pan. Cover. Let rise until the dough crowns about 2 cm above the rim, about 45-60 minutes.", 3000, 2700, 3600, None, None),
            (6, "Preheat oven", "Preheat oven to 180 C (350 F).", 600, 600, 900, Decimal("180.0"), "oven"),
            (7, "Bake", "Bake for 30-35 minutes until golden brown. Internal temperature should reach 88-90 C. If the top browns too fast, tent with foil.", 1920, 1800, 2100, Decimal("180.0"), "oven"),
            (8, "Cool", "Remove from pan immediately. Cool on a wire rack for at least 30 minutes before slicing. This lets the crumb set.", 1800, 1800, 2700, None, None),
        ],
    })

    # -----------------------------------------------------------------------
    # 7. Bagels
    # -----------------------------------------------------------------------
    recipes.append({
        "recipe": {
            "title": "Bagels",
            "slug": "bagels",
            "category": "bread",
            "summary": "Chewy, malty bagels with a glossy crust from the traditional boil-then-bake method.",
            "yields": "8 bagels, ~720 g",
            "servings": 8,
            "serving_g": Decimal("90.00"),
            "total_time_min": 300,
            "active_time_min": 45,
            "difficulty": 3,
            "equipment": ["stand mixer", "large pot", "baking sheet", "slotted spoon"],
            "source": "Peter Reinhart, The Bread Baker's Apprentice",
            "notes": "The overnight cold retard develops flavor. Barley malt syrup in the boil gives the classic glossy crust -- honey works as a substitute.",
        },
        "ingredients": [
            ("Bread flour", "Bread flour", Decimal("500.00"), "flour", 1, "Dough"),
            ("Table salt", "Salt", Decimal("10.00"), "salt", 2, "Dough"),
            ("Granulated sugar", "Sugar", Decimal("15.00"), "sugar", 3, "Dough"),
            ("Instant yeast", "Instant yeast", Decimal("5.00"), "leaven", 4, "Dough"),
            ("Water", "Water, room temperature", Decimal("290.00"), "water", 5, "Dough"),
            ("Honey", "Honey (for boiling water)", Decimal("30.00"), "sugar", 6, "Boil"),
        ],
        "steps": [
            (1, "Mix dough", "In a stand mixer with dough hook, combine flour, salt, sugar, and yeast. Add water. Mix on low for 3 minutes, then medium for 5-6 minutes. The dough should be stiff and smooth -- stiffer than normal bread dough.", 480, 480, 600, None, None),
            (2, "Rest", "Cover dough and let rest for 10 minutes.", 600, 600, 900, None, None),
            (3, "Divide and shape", "Divide dough into 8 equal pieces (about 105 g each). Shape each into a tight ball. Poke a hole through the center with your thumb, then stretch and rotate to form a ring about 8 cm in diameter. The hole should be 3-4 cm wide (it will shrink).", None, 300, 600, None, None),
            (4, "Cold retard (overnight)", "Place shaped bagels on a parchment-lined baking sheet, spaced apart. Cover tightly with plastic wrap. Refrigerate overnight (8-16 hours).", 43200, 28800, 57600, None, None),
            (5, "Float test", "The next morning, fill a bowl with water and drop one bagel in. It should float within 10 seconds. If it sinks, let the bagels sit at room temperature for 15-20 minutes and test again.", None, 60, 1200, None, None),
            (6, "Preheat oven and boil water", "Preheat oven to 230 C (450 F). Bring a large pot of water to a rolling boil. Add honey.", 900, 600, 1200, Decimal("230.0"), "oven"),
            (7, "Boil bagels", "Working in batches of 2-3, drop bagels into the boiling water. Boil 1 minute per side. Remove with a slotted spoon and place on a parchment-lined baking sheet.", 120, 90, 180, None, None),
            (8, "Top (optional)", "While still wet, dip in or sprinkle with your choice of toppings: sesame seeds, poppy seeds, everything seasoning, or leave plain.", None, 60, 180, None, None),
            (9, "Bake", "Bake for 18-22 minutes, rotating the pan halfway through, until deep golden brown.", 1200, 1080, 1320, Decimal("230.0"), "oven"),
            (10, "Cool", "Let cool on a wire rack for at least 15 minutes. The crust will crisp up as they cool.", 900, 900, 1800, None, None),
        ],
    })

    # -----------------------------------------------------------------------
    # 8. Banana Bread
    # -----------------------------------------------------------------------
    recipes.append({
        "recipe": {
            "title": "Banana Bread",
            "slug": "banana-bread",
            "category": "sweet",
            "summary": "Moist, deeply banana-flavored quick bread with brown sugar and a hint of vanilla. Walnuts optional.",
            "yields": "1 loaf, ~850 g",
            "servings": 8,
            "serving_g": Decimal("106.00"),
            "total_time_min": 80,
            "active_time_min": 15,
            "difficulty": 1,
            "equipment": ["loaf pan (9x5 inch)", "mixing bowl", "fork"],
            "source": "family recipe",
            "notes": "The bananas should be very ripe -- brown-spotted or even black. Overripe bananas have more sugar and flavor. Freezing and thawing works too.",
        },
        "ingredients": [
            ("Banana", "Ripe bananas (3 large)", Decimal("340.00"), "other", 1, None),
            ("All-purpose flour", "All-purpose flour", Decimal("250.00"), "other", 2, None),
            ("Baking soda", "Baking soda", Decimal("5.00"), "other", 3, None),
            ("Table salt", "Salt", Decimal("3.00"), "other", 4, None),
            ("Brown sugar", "Brown sugar", Decimal("150.00"), "other", 5, None),
            ("Butter (unsalted)", "Butter, melted", Decimal("75.00"), "other", 6, None),
            ("Eggs", "Egg", Decimal("50.00"), "other", 7, None),
            ("Vanilla extract", "Vanilla extract", Decimal("5.00"), "other", 8, None),
            ("Walnuts", "Walnuts, roughly chopped", Decimal("60.00"), "other", 9, None),
        ],
        "steps": [
            (1, "Preheat oven", "Preheat oven to 175 C (350 F). Grease a 9x5 inch loaf pan.", 600, 600, 900, Decimal("175.0"), "oven"),
            (2, "Mash bananas", "In a large bowl, mash bananas with a fork until mostly smooth with a few small chunks remaining.", None, 60, 120, None, None),
            (3, "Mix wet ingredients", "Add melted butter to bananas and stir. Mix in brown sugar, egg, and vanilla extract.", None, 60, 120, None, None),
            (4, "Add dry ingredients", "Add flour, baking soda, and salt to the wet mixture. Fold gently until just combined -- do not overmix.", None, 60, 120, None, None),
            (5, "Add walnuts", "Fold in chopped walnuts (reserve a few for the top if desired).", None, 30, 60, None, None),
            (6, "Pour and top", "Pour batter into the prepared loaf pan. Smooth the top. Optionally press a few walnut halves into the surface.", None, 30, 60, None, None),
            (7, "Bake", "Bake for 55-65 minutes until the top is golden brown and a toothpick inserted in the center comes out clean or with just a few moist crumbs.", 3600, 3300, 3900, Decimal("175.0"), "oven"),
            (8, "Cool", "Let cool in pan for 10 minutes, then turn out onto a wire rack. Cool at least 20 minutes before slicing.", 1200, 600, 1800, None, None),
        ],
    })

    return recipes


# ---------------------------------------------------------------------------
# Seed logic
# ---------------------------------------------------------------------------

async def seed_pantry(session: AsyncSession) -> dict[str, PantryItem]:
    """Insert pantry items. Returns name -> PantryItem map (including pre-existing)."""
    existing_q = await session.execute(select(PantryItem))
    existing = {item.name: item for item in existing_q.scalars().all()}

    created = 0
    for item_def in PANTRY_ITEMS:
        if item_def["name"] in existing:
            continue
        item = PantryItem(
            id=uuid7(),
            name=item_def["name"],
            cost_per_kg=item_def["cost_per_kg"],
            nutrition_ref=item_def["nutrition_ref"],
            default_role=item_def["default_role"],
        )
        session.add(item)
        existing[item.name] = item
        created += 1

    if created:
        await session.flush()
    print(f"Pantry items: {created} created, {len(existing) - created} already existed.")
    return existing


async def seed_recipes(session: AsyncSession, pantry_map: dict[str, PantryItem]) -> None:
    """Insert recipes with ingredients and steps."""
    # Check which slugs already exist
    existing_q = await session.execute(select(Recipe.slug))
    existing_slugs = {row[0] for row in existing_q.all()}

    recipe_defs = _build_recipes(pantry_map)
    created = 0

    for rdef in recipe_defs:
        r = rdef["recipe"]
        if r["slug"] in existing_slugs:
            print(f"  Recipe '{r['title']}' already exists (slug: {r['slug']}), skipping.")
            continue

        recipe_id = uuid7()
        recipe = Recipe(
            id=recipe_id,
            version_number=1,
            title=r["title"],
            slug=r["slug"],
            category=r["category"],
            summary=r.get("summary"),
            yields=r.get("yields"),
            servings=r["servings"],
            serving_g=r.get("serving_g"),
            total_time_min=r.get("total_time_min"),
            active_time_min=r.get("active_time_min"),
            difficulty=r.get("difficulty"),
            equipment=r.get("equipment", []),
            source=r.get("source"),
            notes=r.get("notes"),
        )
        session.add(recipe)

        # Add ingredients
        for ing_def in rdef["ingredients"]:
            pantry_name, display_name, grams, role, ord_val, group_label = ing_def
            pantry_item = pantry_map.get(pantry_name)
            ingredient = RecipeIngredient(
                id=uuid7(),
                recipe_id=recipe_id,
                pantry_item_id=pantry_item.id if pantry_item else None,
                ord=ord_val,
                group_label=group_label,
                name=display_name,
                grams=grams,
                role=role,
                optional=False,
            )
            session.add(ingredient)

        # Add steps
        for step_def in rdef["steps"]:
            ord_val, title, body, timer_sec, min_sec, max_sec, target_temp, temp_kind = step_def
            step = RecipeStep(
                id=uuid7(),
                recipe_id=recipe_id,
                ord=ord_val,
                title=title,
                body=body,
                timer_seconds=timer_sec,
                min_seconds=min_sec,
                max_seconds=max_sec,
                target_temp_c=target_temp,
                temp_kind=temp_kind,
            )
            session.add(step)

        created += 1
        print(f"  Created recipe: {r['title']} ({len(rdef['ingredients'])} ingredients, {len(rdef['steps'])} steps)")

    if created:
        await session.flush()
    print(f"Recipes: {created} created, {len(recipe_defs) - created} already existed.")


async def main():
    print("=" * 60)
    print("Bakebook seed script")
    print("=" * 60)
    print(f"Database: {settings.database_url.split('@')[-1] if '@' in settings.database_url else '(local)'}")
    print()

    engine = create_async_engine(settings.database_url, echo=False)
    async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_factory() as session:
        async with session.begin():
            print("--- Seeding pantry items ---")
            pantry_map = await seed_pantry(session)
            print()
            print("--- Seeding recipes ---")
            await seed_recipes(session, pantry_map)
            print()
            print("Committing...")

    await engine.dispose()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
