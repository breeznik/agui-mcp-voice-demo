"""
Customer Support MCP Server.

Uses a seeded mock order database (no external API needed).

Tools
-----
lookup_order          Find an order by ID
get_tracking_status   Shipping timeline for an order
initiate_refund       Start a refund process
search_knowledge_base Full-text search of FAQ/policy documents
create_ticket         Open a support ticket
escalate_to_human     Escalate issue to a human agent

Resources
---------
support://knowledge-base   FAQ and return policy documents
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("customer-support")

# ── Mock order database (20 seeded orders) ────────────────────────────────────

def _days_ago(n: int) -> str:
    return (datetime.now() - timedelta(days=n)).strftime("%Y-%m-%d")

def _days_from_now(n: int) -> str:
    return (datetime.now() + timedelta(days=n)).strftime("%Y-%m-%d")

_ORDERS: dict[str, dict] = {
    "ORD-A1B2C3": {
        "order_id": "ORD-A1B2C3", "customer": "Alex Johnson",
        "email": "alex@example.com", "status": "Delivered",
        "placed_on": _days_ago(14), "delivered_on": _days_ago(8),
        "items": [{"name": "Wireless Headphones", "qty": 1, "price": 249.99}],
        "total": 249.99, "carrier": "FedEx", "tracking": "FX1234567890",
    },
    "ORD-D4E5F6": {
        "order_id": "ORD-D4E5F6", "customer": "Sam Rivera",
        "email": "sam@example.com", "status": "In Transit",
        "placed_on": _days_ago(4), "estimated_delivery": _days_from_now(2),
        "items": [{"name": "Mechanical Keyboard", "qty": 1, "price": 129.99}, {"name": "Mouse", "qty": 1, "price": 39.99}],
        "total": 169.98, "carrier": "UPS", "tracking": "UPS9876543210",
    },
    "ORD-G7H8I9": {
        "order_id": "ORD-G7H8I9", "customer": "Jamie Lee",
        "email": "jamie@example.com", "status": "Processing",
        "placed_on": _days_ago(1), "estimated_delivery": _days_from_now(5),
        "items": [{"name": "4K Webcam", "qty": 2, "price": 89.99}],
        "total": 179.98, "carrier": "DHL", "tracking": None,
    },
    "ORD-J1K2L3": {
        "order_id": "ORD-J1K2L3", "customer": "Morgan Chen",
        "email": "morgan@example.com", "status": "Delivered",
        "placed_on": _days_ago(30), "delivered_on": _days_ago(24),
        "items": [{"name": "Ergonomic Chair", "qty": 1, "price": 399.00}],
        "total": 399.00, "carrier": "Freight", "tracking": "FR5555555",
    },
    "ORD-M4N5O6": {
        "order_id": "ORD-M4N5O6", "customer": "Taylor Kim",
        "email": "taylor@example.com", "status": "Cancelled",
        "placed_on": _days_ago(7), "cancelled_on": _days_ago(6),
        "items": [{"name": "Standing Desk Converter", "qty": 1, "price": 179.99}],
        "total": 179.99, "carrier": None, "tracking": None,
    },
}

# ── In-memory ticket store ────────────────────────────────────────────────────

_tickets: dict[str, dict] = {}


# ── Knowledge base ────────────────────────────────────────────────────────────

_KB: list[dict] = [
    {
        "id": "KB001", "title": "Return Policy",
        "content": "You can return most items within 30 days of delivery for a full refund. Items must be unused and in original packaging. Electronics have a 14-day return window. Personalised items are non-returnable.",
    },
    {
        "id": "KB002", "title": "Shipping Times",
        "content": "Standard shipping takes 3–5 business days. Express shipping takes 1–2 business days. Free standard shipping on orders over $75. International orders take 7–14 business days.",
    },
    {
        "id": "KB003", "title": "Refund Processing",
        "content": "Refunds are processed within 3–5 business days after we receive the returned item. The refund appears on your original payment method within 5–10 business days depending on your bank.",
    },
    {
        "id": "KB004", "title": "Damaged or Defective Items",
        "content": "If your item arrived damaged or defective, contact us within 7 days of delivery. We will send a replacement at no cost or issue a full refund. Please have your order ID and photos ready.",
    },
    {
        "id": "KB005", "title": "Order Cancellation",
        "content": "Orders can be cancelled within 1 hour of placement if they haven't shipped. After that, you'll need to return the item once delivered. Contact support immediately to attempt cancellation.",
    },
    {
        "id": "KB006", "title": "Tracking Your Order",
        "content": "Once your order ships, you'll receive an email with a tracking number. Use the carrier's website or our order page to track your package. Processing orders (not yet shipped) don't have a tracking number yet.",
    },
]


# ── Tools ─────────────────────────────────────────────────────────────────────

@mcp.tool()
async def lookup_order(order_id: str) -> dict:
    """
    Find an order by its order ID.

    Parameters
    ----------
    order_id : Order ID in format ORD-XXXXXX (e.g. "ORD-A1B2C3")
    """
    order = _ORDERS.get(order_id.upper())
    if not order:
        return {"error": f"Order '{order_id}' not found. Please check the order ID."}
    return order


@mcp.tool()
async def get_tracking_status(order_id: str) -> dict:
    """
    Get the detailed shipping timeline for an order.

    Parameters
    ----------
    order_id : Order ID (e.g. "ORD-D4E5F6")
    """
    order = _ORDERS.get(order_id.upper())
    if not order:
        return {"error": f"Order '{order_id}' not found."}

    if order["status"] == "Cancelled":
        return {"order_id": order_id, "status": "Cancelled", "timeline": []}

    if not order.get("tracking"):
        return {
            "order_id": order_id,
            "status": order["status"],
            "message": "Tracking not yet available — order is still being processed.",
        }

    # Build a realistic mock timeline
    placed = order["placed_on"]
    timeline = [
        {"step": "Order Placed", "date": placed, "done": True},
        {"step": "Payment Confirmed", "date": placed, "done": True},
        {"step": "Dispatched from Warehouse", "date": _days_ago(3) if order["status"] != "Processing" else None, "done": order["status"] != "Processing"},
        {"step": "In Transit", "date": _days_ago(1) if order["status"] in ("In Transit", "Delivered") else None, "done": order["status"] in ("In Transit", "Delivered")},
        {"step": "Delivered", "date": order.get("delivered_on"), "done": order["status"] == "Delivered"},
    ]

    tracking_data = {
        "order_id": order_id,
        "status": order["status"],
        "carrier": order.get("carrier"),
        "tracking_number": order.get("tracking"),
        "timeline": timeline,
    }

    return tracking_data


@mcp.tool()
async def initiate_refund(order_id: str, reason: str) -> dict:
    """
    Initiate a refund for an order.
    Only call this after confirming the order exists and the user has agreed.

    Parameters
    ----------
    order_id : Order ID to refund
    reason   : Reason for the refund (e.g. "Defective item", "Wrong item received")
    """
    order = _ORDERS.get(order_id.upper())
    if not order:
        return {"error": f"Order '{order_id}' not found."}
    if order["status"] == "Cancelled":
        return {"error": "This order was already cancelled."}

    refund_id = f"REF-{uuid.uuid4().hex[:8].upper()}"
    result = {
        "refund_id": refund_id,
        "order_id": order_id,
        "amount_usd": order["total"],
        "reason": reason,
        "status": "Approved",
        "estimated_credit": "5–10 business days",
        "message": f"Refund of ${order['total']:.2f} approved. You'll see it on your original payment method within 5–10 business days.",
    }

    return result


@mcp.tool()
async def search_knowledge_base(query: str) -> dict:
    """
    Search the FAQ and policy knowledge base.

    Parameters
    ----------
    query : Search query (e.g. "return policy", "shipping time", "damaged item")
    """
    q = query.lower()
    results = [
        kb for kb in _KB
        if q in kb["title"].lower() or any(word in kb["content"].lower() for word in q.split())
    ]

    if not results:
        results = _KB[:2]  # Fallback: return first 2 articles

    return {"query": query, "results": results[:3]}


@mcp.tool()
async def create_ticket(issue: str, priority: str = "normal") -> dict:
    """
    Create a support ticket for issues that need follow-up.

    Parameters
    ----------
    issue    : Description of the customer's issue
    priority : "low" | "normal" | "high" | "urgent"
    """
    ticket_id = f"TKT-{uuid.uuid4().hex[:6].upper()}"
    ticket = {
        "ticket_id": ticket_id,
        "issue": issue,
        "priority": priority,
        "status": "Open",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "estimated_response": "24 hours" if priority in ("low", "normal") else "4 hours",
    }

    _tickets[ticket_id] = ticket
    return ticket


@mcp.tool()
async def escalate_to_human(ticket_id: str) -> dict:
    """
    Escalate an open ticket to a human support agent.
    Use when the issue cannot be resolved with available tools,
    or when the customer explicitly requests a human agent.

    Parameters
    ----------
    ticket_id : Ticket ID from create_ticket()
    """
    ticket = _tickets.get(ticket_id)
    if not ticket:
        return {"error": f"Ticket '{ticket_id}' not found. Create a ticket first."}

    ticket["status"] = "Escalated"
    ticket["escalated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    escalation = {
        "ticket_id": ticket_id,
        "status": "Escalated",
        "message": "A human agent has been assigned and will contact you within 2 hours during business hours (9am–6pm EST, Mon–Fri).",
        "queue_position": 3,
    }

    return escalation


# ── Resources ─────────────────────────────────────────────────────────────────

@mcp.resource("support://knowledge-base")
def knowledge_base() -> str:
    """Full FAQ and return policy document."""
    lines = ["# Support Knowledge Base\n"]
    for article in _KB:
        lines.append(f"## {article['title']} (ID: {article['id']})\n{article['content']}\n")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run(transport="stdio")
