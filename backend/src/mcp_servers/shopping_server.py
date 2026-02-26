"""
Shopping Assistant MCP Server.

Uses an in-memory product catalog (no external API needed).

Tools
-----
search_products      Search catalog by query, category, or max price
get_product_details  Full product info by ID
add_to_cart          Add product to session cart
remove_from_cart     Remove product from session cart
view_cart            Show cart contents + total
checkout             Finalize order and clear cart

Resources
---------
shop://catalog   Full product catalog document
"""

from __future__ import annotations

import uuid
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("shopping-assistant")

# ── Product catalog ───────────────────────────────────────────────────────────

_CATALOG: list[dict] = [
    {"id": "P001", "name": "Wireless Noise-Cancelling Headphones", "category": "Electronics", "price": 249.99, "rating": 4.7, "description": "Over-ear headphones with 30hr battery and active noise cancellation.", "in_stock": True},
    {"id": "P002", "name": "Mechanical Keyboard", "category": "Electronics", "price": 129.99, "rating": 4.5, "description": "Compact TKL layout with Cherry MX Blue switches and RGB backlight.", "in_stock": True},
    {"id": "P003", "name": "USB-C Hub 7-in-1", "category": "Electronics", "price": 49.99, "rating": 4.3, "description": "HDMI 4K, 3× USB-A, SD card reader, 100W PD charging.", "in_stock": True},
    {"id": "P004", "name": "Ergonomic Office Chair", "category": "Furniture", "price": 399.00, "rating": 4.6, "description": "Lumbar support, adjustable armrests, breathable mesh back.", "in_stock": True},
    {"id": "P005", "name": "Standing Desk Converter", "category": "Furniture", "price": 179.99, "rating": 4.2, "description": "Sit-stand desk riser with keyboard tray. Fits monitors up to 27\".", "in_stock": False},
    {"id": "P006", "name": "Bamboo Desk Organiser", "category": "Office", "price": 34.99, "rating": 4.4, "description": "5-slot organiser for pens, notebooks, and cables.", "in_stock": True},
    {"id": "P007", "name": "4K Webcam", "category": "Electronics", "price": 89.99, "rating": 4.1, "description": "1080p/4K at 30fps, built-in noise-cancelling mic, auto-focus.", "in_stock": True},
    {"id": "P008", "name": "Laptop Stand (Aluminium)", "category": "Electronics", "price": 59.99, "rating": 4.8, "description": "Adjustable height, foldable, supports laptops up to 17\".", "in_stock": True},
    {"id": "P009", "name": "Wireless Mouse", "category": "Electronics", "price": 39.99, "rating": 4.5, "description": "Silent clicks, 18-month battery, nano USB receiver.", "in_stock": True},
    {"id": "P010", "name": "Monitor Light Bar", "category": "Electronics", "price": 44.99, "rating": 4.6, "description": "USB-powered, no-glare, adjustable colour temperature.", "in_stock": True},
    {"id": "P011", "name": "Cable Management Kit", "category": "Office", "price": 19.99, "rating": 4.3, "description": "60-piece kit: clips, velcro ties, cable boxes.", "in_stock": True},
    {"id": "P012", "name": "Desk Pad XL (90×40cm)", "category": "Office", "price": 29.99, "rating": 4.7, "description": "Non-slip PU leather, waterproof surface, stitched edges.", "in_stock": True},
    {"id": "P013", "name": "Smart LED Desk Lamp", "category": "Electronics", "price": 69.99, "rating": 4.4, "description": "Adjustable brightness/colour, USB-A charging port, eye-care mode.", "in_stock": True},
    {"id": "P014", "name": "Noise Machine", "category": "Wellness", "price": 49.99, "rating": 4.5, "description": "30 sound profiles including white noise, rain, and fan sounds.", "in_stock": True},
    {"id": "P015", "name": "Plant Pot (Self-Watering)", "category": "Home", "price": 24.99, "rating": 4.2, "description": "17cm ceramic pot with water indicator. Perfect for succulents.", "in_stock": True},
]

# ── In-memory cart state ──────────────────────────────────────────────────────

_carts: dict[str, list[dict]] = {}   # {thread_id: [{product_id, name, qty, price}]}


def _get_cart(thread_id: str) -> list[dict]:
    return _carts.setdefault(thread_id, [])


def _cart_total(cart: list[dict]) -> float:
    return round(sum(item["price"] * item["quantity"] for item in cart), 2)


# ── Tools ─────────────────────────────────────────────────────────────────────

@mcp.tool()
async def search_products(
    query: str = "",
    category: str = "",
    max_price: float = 0,
) -> dict:
    """
    Search the product catalog.

    Parameters
    ----------
    query     : Keyword search on product name and description
    category  : Filter by category (Electronics, Furniture, Office, Wellness, Home)
    max_price : Maximum price in USD (0 = no limit)
    """
    results = list(_CATALOG)

    if query:
        q = query.lower()
        results = [p for p in results if q in p["name"].lower() or q in p["description"].lower()]

    if category:
        results = [p for p in results if p["category"].lower() == category.lower()]

    if max_price > 0:
        results = [p for p in results if p["price"] <= max_price]

    return {
        "query": query,
        "results": results[:8],
        "total_found": len(results),
    }


@mcp.tool()
async def get_product_details(product_id: str) -> dict:
    """
    Get full details for a product by its ID.

    Parameters
    ----------
    product_id : Product ID from search_products results (e.g. "P001")
    """
    product = next((p for p in _CATALOG if p["id"] == product_id), None)
    if not product:
        return {"error": f"Product '{product_id}' not found."}

    return product


@mcp.tool()
async def add_to_cart(
    product_id: str,
    quantity: int = 1,
    thread_id: str = "default",
) -> dict:
    """
    Add a product to the shopping cart.

    Parameters
    ----------
    product_id : Product ID from search results
    quantity   : Number of units to add (default 1)
    thread_id  : Session identifier
    """
    product = next((p for p in _CATALOG if p["id"] == product_id), None)
    if not product:
        return {"error": f"Product '{product_id}' not found."}
    if not product["in_stock"]:
        return {"error": f"'{product['name']}' is currently out of stock."}

    cart = _get_cart(thread_id)

    # If already in cart, increase quantity
    existing = next((i for i in cart if i["product_id"] == product_id), None)
    if existing:
        existing["quantity"] += quantity
    else:
        cart.append({
            "product_id": product_id,
            "name": product["name"],
            "price": product["price"],
            "quantity": quantity,
        })

    total = _cart_total(cart)
    return {
        "cart": cart,
        "total": total,
        "item_count": len(cart),
        "message": f"Added {quantity}× {product['name']} to cart.",
    }


@mcp.tool()
async def remove_from_cart(
    product_id: str,
    thread_id: str = "default",
) -> dict:
    """
    Remove a product from the shopping cart.

    Parameters
    ----------
    product_id : Product ID to remove
    thread_id  : Session identifier
    """
    cart = _get_cart(thread_id)
    original_len = len(cart)
    _carts[thread_id] = [i for i in cart if i["product_id"] != product_id]

    if len(_carts[thread_id]) == original_len:
        return {"error": f"Product '{product_id}' not in cart."}

    total = _cart_total(_carts[thread_id])
    return {"cart": _carts[thread_id], "total": total, "item_count": len(_carts[thread_id])}


@mcp.tool()
async def view_cart(thread_id: str = "default") -> dict:
    """Show the current cart contents and running total."""
    cart = _get_cart(thread_id)
    total = _cart_total(cart)
    return {"cart": cart, "total": total, "item_count": len(cart)}


@mcp.tool()
async def checkout(thread_id: str = "default") -> dict:
    """
    Finalize the cart and generate a mock order confirmation.
    Clears the cart after checkout.
    """
    cart = _get_cart(thread_id)
    if not cart:
        return {"error": "Your cart is empty. Add some products first."}

    total = _cart_total(cart)
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"

    order = {
        "order_id": order_id,
        "items": cart.copy(),
        "total": total,
        "status": "Confirmed",
        "estimated_delivery": "3–5 business days",
    }

    # Clear cart
    _carts[thread_id] = []

    return order


# ── Resources ─────────────────────────────────────────────────────────────────

@mcp.resource("shop://catalog")
def product_catalog() -> str:
    """Full product catalog as a structured document."""
    lines = ["# Product Catalog\n"]
    by_category: dict[str, list] = {}
    for p in _CATALOG:
        by_category.setdefault(p["category"], []).append(p)

    for cat, products in sorted(by_category.items()):
        lines.append(f"\n## {cat}\n")
        for p in products:
            stock = "In Stock" if p["in_stock"] else "Out of Stock"
            lines.append(f"- **{p['name']}** (ID: {p['id']}) — ${p['price']} — {stock}")
            lines.append(f"  {p['description']}\n")

    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run(transport="stdio")
