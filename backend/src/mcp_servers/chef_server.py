"""
Personal Chef MCP Server.

Uses a built-in recipe database (no external API needed).

Tools
-----
search_recipes          Find recipes by ingredients, cuisine, or dietary tag
get_nutritional_info    Macro breakdown for a recipe
plan_meals              Generate a multi-day meal plan
generate_shopping_list  Consolidated ingredient list from a meal plan
save_recipe             Save a recipe to the session cookbook

Resources
---------
chef://recipes   Full recipe collection
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("personal-chef")

# ── Recipe database ───────────────────────────────────────────────────────────

_RECIPES: list[dict] = [
    {
        "id": "R001", "name": "Spaghetti Carbonara", "cuisine": "Italian",
        "dietary": [], "prep_min": 10, "cook_min": 20, "servings": 2,
        "ingredients": ["200g spaghetti", "100g pancetta", "2 eggs", "50g parmesan", "black pepper", "salt"],
        "steps": ["Cook pasta in salted water.", "Fry pancetta until crispy.", "Mix eggs and parmesan.", "Combine hot pasta with pancetta, remove from heat, add egg mix, toss quickly."],
        "nutrition": {"calories": 620, "protein_g": 28, "carbs_g": 72, "fat_g": 22},
    },
    {
        "id": "R002", "name": "Chicken Tikka Masala", "cuisine": "Indian",
        "dietary": ["gluten-free"], "prep_min": 20, "cook_min": 35, "servings": 4,
        "ingredients": ["500g chicken breast", "400ml coconut cream", "400g tinned tomatoes", "1 onion", "tikka masala paste", "garlic", "ginger", "rice"],
        "steps": ["Marinate chicken in tikka paste.", "Fry onion, garlic, ginger.", "Add chicken and brown.", "Add tomatoes and cream, simmer 25 min.", "Serve with rice."],
        "nutrition": {"calories": 480, "protein_g": 38, "carbs_g": 45, "fat_g": 14},
    },
    {
        "id": "R003", "name": "Avocado Toast with Poached Egg", "cuisine": "American",
        "dietary": ["vegetarian"], "prep_min": 5, "cook_min": 10, "servings": 1,
        "ingredients": ["2 slices sourdough", "1 avocado", "2 eggs", "lemon juice", "chilli flakes", "salt"],
        "steps": ["Toast bread.", "Mash avocado with lemon juice and salt.", "Poach eggs 3–4 min.", "Spread avocado, top with egg and chilli."],
        "nutrition": {"calories": 410, "protein_g": 18, "carbs_g": 38, "fat_g": 22},
    },
    {
        "id": "R004", "name": "Lentil Soup", "cuisine": "Middle Eastern",
        "dietary": ["vegan", "gluten-free"], "prep_min": 10, "cook_min": 30, "servings": 4,
        "ingredients": ["300g red lentils", "1 onion", "2 carrots", "cumin", "turmeric", "garlic", "olive oil", "vegetable stock"],
        "steps": ["Soften onion and carrots in oil.", "Add spices and garlic.", "Add lentils and stock.", "Simmer 25 min, blend half for creaminess."],
        "nutrition": {"calories": 280, "protein_g": 16, "carbs_g": 48, "fat_g": 4},
    },
    {
        "id": "R005", "name": "Beef Stir-Fry with Noodles", "cuisine": "Chinese",
        "dietary": [], "prep_min": 15, "cook_min": 15, "servings": 2,
        "ingredients": ["300g beef sirloin", "200g noodles", "1 bell pepper", "broccoli", "soy sauce", "oyster sauce", "sesame oil", "garlic", "ginger"],
        "steps": ["Cook noodles per packet.", "Slice beef thin.", "Stir-fry beef 2 min, set aside.", "Stir-fry vegetables.", "Return beef, add sauces and noodles, toss."],
        "nutrition": {"calories": 540, "protein_g": 42, "carbs_g": 55, "fat_g": 16},
    },
    {
        "id": "R006", "name": "Greek Salad", "cuisine": "Greek",
        "dietary": ["vegetarian", "gluten-free"], "prep_min": 10, "cook_min": 0, "servings": 2,
        "ingredients": ["2 tomatoes", "1 cucumber", "1 red onion", "200g feta", "olives", "olive oil", "oregano"],
        "steps": ["Chop all vegetables.", "Crumble feta on top.", "Drizzle with olive oil, season with oregano."],
        "nutrition": {"calories": 310, "protein_g": 12, "carbs_g": 14, "fat_g": 24},
    },
    {
        "id": "R007", "name": "Banana Oat Pancakes", "cuisine": "American",
        "dietary": ["vegetarian", "gluten-free"], "prep_min": 5, "cook_min": 10, "servings": 2,
        "ingredients": ["2 ripe bananas", "2 eggs", "80g rolled oats", "pinch of cinnamon", "maple syrup"],
        "steps": ["Blend all ingredients.", "Cook on medium heat 2 min per side.", "Serve with maple syrup."],
        "nutrition": {"calories": 320, "protein_g": 12, "carbs_g": 58, "fat_g": 6},
    },
    {
        "id": "R008", "name": "Salmon with Roasted Vegetables", "cuisine": "Mediterranean",
        "dietary": ["gluten-free"], "prep_min": 10, "cook_min": 25, "servings": 2,
        "ingredients": ["2 salmon fillets", "courgette", "cherry tomatoes", "bell pepper", "olive oil", "garlic", "lemon", "herbs"],
        "steps": ["Toss vegetables in oil and roast at 200°C 15 min.", "Season salmon, bake 12 min.", "Serve with lemon wedge."],
        "nutrition": {"calories": 490, "protein_g": 44, "carbs_g": 18, "fat_g": 26},
    },
]

# ── In-memory cookbooks and meal plans ────────────────────────────────────────

_cookbooks: dict[str, list[str]] = {}   # {thread_id: [recipe_ids]}
_meal_plans: dict[str, dict] = {}       # {thread_id: {plan_id: {days: [...]}}}


def _get_cookbook(thread_id: str) -> list[str]:
    return _cookbooks.setdefault(thread_id, [])


# ── Tools ─────────────────────────────────────────────────────────────────────

@mcp.tool()
async def search_recipes(
    ingredients: list[str] | None = None,
    cuisine: str = "",
    dietary: str = "",
) -> dict:
    """
    Search recipes by available ingredients, cuisine style, or dietary tag.

    Parameters
    ----------
    ingredients : List of ingredients you have (e.g. ["chicken", "garlic"])
    cuisine     : Cuisine style (e.g. "Italian", "Indian", "Chinese")
    dietary     : Dietary tag: "vegan", "vegetarian", or "gluten-free"
    """
    results = list(_RECIPES)

    if ingredients:
        ing_lower = [i.lower() for i in ingredients]
        results = [
            r for r in results
            if any(any(ing in rl.lower() for ing in ing_lower) for rl in r["ingredients"])
        ]

    if cuisine:
        results = [r for r in results if r["cuisine"].lower() == cuisine.lower()]

    if dietary:
        results = [r for r in results if dietary.lower() in r["dietary"]]

    return {
        "results": results[:6],
        "total_found": len(results),
    }


@mcp.tool()
async def get_nutritional_info(recipe_id: str) -> dict:
    """
    Get macro breakdown for a specific recipe.

    Parameters
    ----------
    recipe_id : Recipe ID from search_recipes results (e.g. "R001")
    """
    recipe = next((r for r in _RECIPES if r["id"] == recipe_id), None)
    if not recipe:
        return {"error": f"Recipe '{recipe_id}' not found."}

    return {"recipe": recipe["name"], **recipe["nutrition"]}


@mcp.tool()
async def plan_meals(
    days: int = 3,
    dietary: str = "",
    cuisine_variety: bool = True,
    thread_id: str = "default",
) -> dict:
    """
    Generate a meal plan for a given number of days.

    Parameters
    ----------
    days            : Number of days to plan (1–7)
    dietary         : Dietary restriction to apply throughout
    cuisine_variety : Whether to vary cuisines across days (default True)
    thread_id       : Session identifier
    """
    days = max(1, min(7, days))
    pool = [r for r in _RECIPES if not dietary or dietary.lower() in r["dietary"]] or _RECIPES

    # Simple round-robin assignment
    plan = []
    for day in range(1, days + 1):
        offset = (day - 1) * 3
        plan.append({
            "day": day,
            "breakfast": pool[(offset) % len(pool)]["name"],
            "breakfast_id": pool[(offset) % len(pool)]["id"],
            "lunch": pool[(offset + 1) % len(pool)]["name"],
            "lunch_id": pool[(offset + 1) % len(pool)]["id"],
            "dinner": pool[(offset + 2) % len(pool)]["name"],
            "dinner_id": pool[(offset + 2) % len(pool)]["id"],
        })

    import uuid
    plan_id = f"MP-{uuid.uuid4().hex[:6].upper()}"
    _meal_plans.setdefault(thread_id, {})[plan_id] = {"days": plan}

    return {"plan_id": plan_id, "days": plan}


@mcp.tool()
async def generate_shopping_list(
    plan_id: str,
    thread_id: str = "default",
) -> dict:
    """
    Generate a consolidated shopping list from a meal plan.

    Parameters
    ----------
    plan_id   : Plan ID from plan_meals()
    thread_id : Session identifier
    """
    plans = _meal_plans.get(thread_id, {})
    plan = plans.get(plan_id)
    if not plan:
        return {"error": f"Plan '{plan_id}' not found. Call plan_meals first."}

    # Collect all recipe IDs in the plan
    recipe_ids = set()
    for day in plan["days"]:
        recipe_ids.update([day["breakfast_id"], day["lunch_id"], day["dinner_id"]])

    # Gather ingredients
    all_ingredients: list[str] = []
    for rid in recipe_ids:
        recipe = next((r for r in _RECIPES if r["id"] == rid), None)
        if recipe:
            all_ingredients.extend(recipe["ingredients"])

    # Group by rough category (simple keyword matching)
    grouped: dict[str, list[str]] = {
        "Produce": [], "Protein": [], "Dairy": [],
        "Pantry": [], "Grains": [],
    }
    produce_kw = ["tomato", "onion", "garlic", "carrot", "pepper", "cucumber", "avocado", "lemon", "banana", "courgette", "broccoli"]
    protein_kw = ["chicken", "beef", "salmon", "egg", "pancetta", "feta"]
    dairy_kw = ["parmesan", "cream", "feta", "egg"]
    grain_kw = ["spaghetti", "pasta", "noodle", "rice", "oat", "bread", "sourdough"]

    for ing in all_ingredients:
        ing_lower = ing.lower()
        if any(k in ing_lower for k in produce_kw):
            grouped["Produce"].append(ing)
        elif any(k in ing_lower for k in protein_kw):
            grouped["Protein"].append(ing)
        elif any(k in ing_lower for k in dairy_kw):
            grouped["Dairy"].append(ing)
        elif any(k in ing_lower for k in grain_kw):
            grouped["Grains"].append(ing)
        else:
            grouped["Pantry"].append(ing)

    # Deduplicate
    grouped = {cat: list(dict.fromkeys(items)) for cat, items in grouped.items() if items}

    return {"plan_id": plan_id, "shopping_list": grouped}


@mcp.tool()
async def save_recipe(recipe_id: str, thread_id: str = "default") -> dict:
    """
    Save a recipe to the user's personal cookbook.

    Parameters
    ----------
    recipe_id : Recipe ID to save
    thread_id : Session identifier
    """
    recipe = next((r for r in _RECIPES if r["id"] == recipe_id), None)
    if not recipe:
        return {"error": f"Recipe '{recipe_id}' not found."}

    cookbook = _get_cookbook(thread_id)
    if recipe_id not in cookbook:
        cookbook.append(recipe_id)

    return {"saved": True, "recipe": recipe["name"], "cookbook_size": len(cookbook)}


# ── Resources ─────────────────────────────────────────────────────────────────

@mcp.resource("chef://recipes")
def recipe_collection() -> str:
    """Full recipe collection as a reference document."""
    lines = ["# Recipe Collection\n"]
    for r in _RECIPES:
        dietary_str = ", ".join(r["dietary"]) if r["dietary"] else "none"
        lines.append(
            f"## {r['name']} (ID: {r['id']})\n"
            f"Cuisine: {r['cuisine']} | Prep: {r['prep_min']}min | Cook: {r['cook_min']}min | "
            f"Dietary: {dietary_str}\n"
            f"Ingredients: {', '.join(r['ingredients'])}\n"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run(transport="stdio")
