"""
Unit tests for all 5 MCP server tool functions.

These tests call the tool functions directly (not via MCP protocol)
so they run fast without needing running subprocesses.
"""

import pytest
import sys
import os

# Ensure src is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ── Travel server ─────────────────────────────────────────────────────────────

class TestTravelServer:
    @pytest.mark.asyncio
    async def test_search_flights_returns_results(self):
        from src.mcp_servers.travel_server import search_flights
        result = await search_flights("London", "Tokyo", "2027-06-01", passengers=2)
        assert "flights" in result
        assert len(result["flights"]) > 0
        flight = result["flights"][0]
        assert "flight_id" in flight
        assert "price_usd" in flight
        assert result["passengers"] == 2

    @pytest.mark.asyncio
    async def test_search_flights_deterministic(self):
        """Same inputs should return same flight data."""
        from src.mcp_servers.travel_server import search_flights
        r1 = await search_flights("NYC", "Paris", "2027-03-15", passengers=1)
        r2 = await search_flights("NYC", "Paris", "2027-03-15", passengers=1)
        assert r1["flights"][0]["flight_id"] == r2["flights"][0]["flight_id"]

    @pytest.mark.asyncio
    async def test_get_weather_mock_fallback(self, monkeypatch):
        """Without API key, should return mock weather data."""
        monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
        from src.mcp_servers.travel_server import get_weather
        result = await get_weather("Paris", "2027-06-01")
        assert "forecast" in result
        assert len(result["forecast"]) == 5
        assert "temp_c" in result["forecast"][0]

    @pytest.mark.asyncio
    async def test_search_hotels_returns_results(self):
        from src.mcp_servers.travel_server import search_hotels
        result = await search_hotels("Tokyo", "2027-06-01", "2027-06-07", guests=2)
        assert "hotels" in result
        assert len(result["hotels"]) > 0
        hotel = result["hotels"][0]
        assert "hotel_id" in hotel
        assert "price_per_night_usd" in hotel

    @pytest.mark.asyncio
    async def test_get_place_info_handles_failure_gracefully(self):
        from src.mcp_servers.travel_server import get_place_info
        # Should not raise even if city name is odd
        result = await get_place_info("London")
        assert "city" in result
        assert "summary" in result

    @pytest.mark.asyncio
    async def test_save_to_itinerary_persists(self):
        from src.mcp_servers.travel_server import save_to_itinerary
        result = await save_to_itinerary(1, ["Visit Eiffel Tower", "Dinner at bistro"], "test-thread")
        assert result["itinerary"][0]["day"] == 1
        assert "Visit Eiffel Tower" in result["itinerary"][0]["activities"]


# ── Trivia server ─────────────────────────────────────────────────────────────

class TestTriviaServer:
    @pytest.mark.asyncio
    async def test_get_categories_returns_list(self):
        from src.mcp_servers.trivia_server import get_categories
        result = await get_categories()
        assert "categories" in result
        assert len(result["categories"]) > 0
        assert "id" in result["categories"][0]
        assert "name" in result["categories"][0]

    @pytest.mark.asyncio
    async def test_check_answer_correct(self):
        from src.mcp_servers.trivia_server import _sessions, check_answer
        # Set up a fake current question in session
        _sessions["trivia-test"] = {
            "score": 0, "questions_asked": 1, "correct": 0,
            "current_question": {
                "question_id": "q_1",
                "question": "What is 2+2?",
                "difficulty": "easy",
                "correct_answer": "4",
                "all_answers": ["3", "4", "5", "6"],
            }
        }
        result = await check_answer("4", thread_id="trivia-test")
        assert result["is_correct"] is True
        assert result["points_earned"] == 1   # easy = 1 point

    @pytest.mark.asyncio
    async def test_check_answer_incorrect(self):
        from src.mcp_servers.trivia_server import _sessions, check_answer
        _sessions["trivia-test2"] = {
            "score": 5, "questions_asked": 2, "correct": 1,
            "current_question": {
                "question_id": "q_2",
                "question": "Capital of France?",
                "difficulty": "medium",
                "correct_answer": "Paris",
                "all_answers": ["Berlin", "Madrid", "Paris", "Rome"],
            }
        }
        result = await check_answer("Berlin", thread_id="trivia-test2")
        assert result["is_correct"] is False
        assert result["points_earned"] == 0
        assert result["correct_answer"] == "Paris"

    @pytest.mark.asyncio
    async def test_end_game_resets_session(self):
        from src.mcp_servers.trivia_server import _sessions, end_game
        _sessions["end-test"] = {
            "score": 10, "questions_asked": 5, "correct": 4, "current_question": None
        }
        result = await end_game(thread_id="end-test")
        assert result["final_score"] == 10
        assert result["accuracy_pct"] == 80.0
        assert "performance_tier" in result
        # Session should be reset
        assert _sessions["end-test"]["score"] == 0

    @pytest.mark.asyncio
    async def test_check_answer_no_active_question(self):
        from src.mcp_servers.trivia_server import check_answer
        result = await check_answer("anything", thread_id="empty-session-xyz")
        assert "error" in result


# ── Shopping server ───────────────────────────────────────────────────────────

class TestShoppingServer:
    @pytest.mark.asyncio
    async def test_search_products_by_query(self):
        from src.mcp_servers.shopping_server import search_products
        result = await search_products(query="keyboard")
        assert result["total_found"] >= 1
        assert any("keyboard" in r["name"].lower() for r in result["results"])

    @pytest.mark.asyncio
    async def test_search_products_by_max_price(self):
        from src.mcp_servers.shopping_server import search_products
        result = await search_products(max_price=50.0)
        assert all(r["price"] <= 50.0 for r in result["results"])

    @pytest.mark.asyncio
    async def test_add_and_view_cart(self):
        from src.mcp_servers.shopping_server import add_to_cart, view_cart
        thread = "cart-test-001"
        add_result = await add_to_cart("P001", quantity=1, thread_id=thread)
        assert add_result["total"] > 0
        view_result = await view_cart(thread_id=thread)
        assert view_result["item_count"] >= 1

    @pytest.mark.asyncio
    async def test_remove_from_cart(self):
        from src.mcp_servers.shopping_server import add_to_cart, remove_from_cart, view_cart
        thread = "cart-test-002"
        await add_to_cart("P002", quantity=1, thread_id=thread)
        await remove_from_cart("P002", thread_id=thread)
        view = await view_cart(thread_id=thread)
        assert view["item_count"] == 0

    @pytest.mark.asyncio
    async def test_checkout_clears_cart(self):
        from src.mcp_servers.shopping_server import add_to_cart, checkout, view_cart
        thread = "cart-test-003"
        await add_to_cart("P003", quantity=2, thread_id=thread)
        order = await checkout(thread_id=thread)
        assert "order_id" in order
        assert order["status"] == "Confirmed"
        view = await view_cart(thread_id=thread)
        assert view["item_count"] == 0

    @pytest.mark.asyncio
    async def test_checkout_empty_cart_returns_error(self):
        from src.mcp_servers.shopping_server import checkout
        result = await checkout(thread_id="empty-cart-xyz")
        assert "error" in result

    @pytest.mark.asyncio
    async def test_add_out_of_stock_returns_error(self):
        from src.mcp_servers.shopping_server import add_to_cart
        # P005 is out of stock in our catalog
        result = await add_to_cart("P005", quantity=1, thread_id="oos-test")
        assert "error" in result


# ── Chef server ───────────────────────────────────────────────────────────────

class TestChefServer:
    @pytest.mark.asyncio
    async def test_search_recipes_by_cuisine(self):
        from src.mcp_servers.chef_server import search_recipes
        result = await search_recipes(cuisine="Italian")
        assert result["total_found"] >= 1
        assert all(r["cuisine"] == "Italian" for r in result["results"])

    @pytest.mark.asyncio
    async def test_search_recipes_by_dietary(self):
        from src.mcp_servers.chef_server import search_recipes
        result = await search_recipes(dietary="vegan")
        assert result["total_found"] >= 1
        assert all("vegan" in r["dietary"] for r in result["results"])

    @pytest.mark.asyncio
    async def test_get_nutritional_info(self):
        from src.mcp_servers.chef_server import get_nutritional_info
        result = await get_nutritional_info("R001")
        assert "calories" in result
        assert result["calories"] > 0

    @pytest.mark.asyncio
    async def test_plan_meals_returns_correct_days(self):
        from src.mcp_servers.chef_server import plan_meals
        result = await plan_meals(days=3, thread_id="chef-test")
        assert len(result["days"]) == 3
        for day in result["days"]:
            assert "breakfast" in day
            assert "lunch" in day
            assert "dinner" in day

    @pytest.mark.asyncio
    async def test_generate_shopping_list(self):
        from src.mcp_servers.chef_server import plan_meals, generate_shopping_list
        plan = await plan_meals(days=2, thread_id="chef-list-test")
        shopping = await generate_shopping_list(plan["plan_id"], thread_id="chef-list-test")
        assert "shopping_list" in shopping
        assert len(shopping["shopping_list"]) > 0

    @pytest.mark.asyncio
    async def test_save_recipe(self):
        from src.mcp_servers.chef_server import save_recipe
        result = await save_recipe("R001", thread_id="chef-save-test")
        assert result["saved"] is True
        assert result["cookbook_size"] >= 1


# ── Support server ────────────────────────────────────────────────────────────

class TestSupportServer:
    @pytest.mark.asyncio
    async def test_lookup_order_found(self):
        from src.mcp_servers.support_server import lookup_order
        result = await lookup_order("ORD-A1B2C3")
        assert result["order_id"] == "ORD-A1B2C3"
        assert "status" in result
        assert "total" in result

    @pytest.mark.asyncio
    async def test_lookup_order_not_found(self):
        from src.mcp_servers.support_server import lookup_order
        result = await lookup_order("ORD-INVALID")
        assert "error" in result

    @pytest.mark.asyncio
    async def test_get_tracking_status(self):
        from src.mcp_servers.support_server import get_tracking_status
        result = await get_tracking_status("ORD-D4E5F6")
        assert "timeline" in result
        assert len(result["timeline"]) > 0

    @pytest.mark.asyncio
    async def test_initiate_refund(self):
        from src.mcp_servers.support_server import initiate_refund
        result = await initiate_refund("ORD-A1B2C3", reason="Item defective")
        assert "refund_id" in result
        assert result["status"] == "Approved"
        assert result["amount_usd"] == 249.99

    @pytest.mark.asyncio
    async def test_search_knowledge_base(self):
        from src.mcp_servers.support_server import search_knowledge_base
        result = await search_knowledge_base("return policy")
        assert "results" in result
        assert len(result["results"]) > 0

    @pytest.mark.asyncio
    async def test_create_ticket(self):
        from src.mcp_servers.support_server import create_ticket
        result = await create_ticket("My order is missing", priority="high")
        assert "ticket_id" in result
        assert result["status"] == "Open"

    @pytest.mark.asyncio
    async def test_escalate_to_human(self):
        from src.mcp_servers.support_server import create_ticket, escalate_to_human
        ticket = await create_ticket("Complex issue", priority="urgent")
        result = await escalate_to_human(ticket["ticket_id"])
        assert result["status"] == "Escalated"

    @pytest.mark.asyncio
    async def test_escalate_unknown_ticket(self):
        from src.mcp_servers.support_server import escalate_to_human
        result = await escalate_to_human("TKT-FAKE")
        assert "error" in result
