"""
Travel Concierge MCP Server.

Tools
-----
search_flights      Mock flight search (returns realistic fake data)
get_weather         OpenWeatherMap free API (falls back to mock if no key)
search_hotels       Mock hotel search
get_place_info      Wikipedia REST API (free, no key required)
save_to_itinerary   Persists activities to in-memory session state

Resources
---------
travel://destinations   Curated destination guide (static text)
"""

from __future__ import annotations

import json
import os
import random
from datetime import datetime, timedelta

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("travel-concierge")

# ── In-memory session state (resets on server restart) ────────────────────────
_itinerary: dict[str, list] = {}   # {thread_id: [{day, activities}]}


# ── Mock data ─────────────────────────────────────────────────────────────────

_AIRLINES = ["SkyWing", "BlueStar", "AirNova", "SwiftJet", "OceanAir"]
_HOTEL_CHAINS = ["Grand Stay", "Cozy Inn", "Luxe Palace", "Harbor View", "Garden Suites"]


def _mock_flights(origin: str, destination: str, date: str, passengers: int) -> list[dict]:
    random.seed(f"{origin}{destination}{date}")
    flights = []
    for i in range(4):
        hour = 6 + i * 3
        airline = _AIRLINES[i % len(_AIRLINES)]
        price = random.randint(250, 1200) * passengers
        flights.append({
            "flight_id": f"{airline[:2].upper()}{random.randint(100, 999)}",
            "airline": airline,
            "origin": origin.upper(),
            "destination": destination.upper(),
            "date": date,
            "departure": f"{hour:02d}:00",
            "arrival": f"{(hour + 8 + i) % 24:02d}:30",
            "duration_hours": 8 + i,
            "price_usd": price,
            "seats_available": random.randint(4, 30),
            "class": "Economy",
        })
    return sorted(flights, key=lambda x: x["price_usd"])


def _mock_hotels(city: str, check_in: str, check_out: str, guests: int) -> list[dict]:
    random.seed(f"{city}{check_in}")
    hotels = []
    for i, chain in enumerate(_HOTEL_CHAINS):
        hotels.append({
            "hotel_id": f"HTL{i+1:03d}",
            "name": f"{chain} {city.title()}",
            "city": city,
            "stars": random.randint(3, 5),
            "price_per_night_usd": random.randint(80, 400),
            "rating": round(random.uniform(7.5, 9.8), 1),
            "amenities": random.sample(["WiFi", "Pool", "Gym", "Spa", "Restaurant", "Parking"], 3),
            "check_in": check_in,
            "check_out": check_out,
            "guests": guests,
        })
    return sorted(hotels, key=lambda x: x["price_per_night_usd"])


# ── Tools ─────────────────────────────────────────────────────────────────────

@mcp.tool()
async def search_flights(
    origin: str,
    destination: str,
    date: str,
    passengers: int = 1,
) -> dict:
    """
    Search for available flights between two cities.

    Parameters
    ----------
    origin      : Departure city or airport code (e.g. "London" or "LHR")
    destination : Arrival city or airport code (e.g. "Tokyo" or "NRT")
    date        : Travel date in YYYY-MM-DD format
    passengers  : Number of passengers (default 1)
    """
    flights = _mock_flights(origin, destination, date, passengers)

    return {
        "origin": origin,
        "destination": destination,
        "date": date,
        "passengers": passengers,
        "flights": flights[:3],
        "total_results": len(flights),
    }


@mcp.tool()
async def get_weather(city: str, date: str) -> dict:
    """
    Get the weather forecast for a city on a given date.

    Uses OpenWeatherMap free API if OPENWEATHER_API_KEY is set,
    otherwise returns realistic mock data.

    Parameters
    ----------
    city : City name (e.g. "Tokyo", "Paris")
    date : Date in YYYY-MM-DD format
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if api_key:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://api.openweathermap.org/data/2.5/forecast",
                    params={"q": city, "appid": api_key, "units": "metric", "cnt": 5},
                )
                resp.raise_for_status()
                data = resp.json()
                forecast = [
                    {
                        "date": item["dt_txt"][:10],
                        "temp_c": round(item["main"]["temp"]),
                        "feels_like_c": round(item["main"]["feels_like"]),
                        "condition": item.get("weather", [{}])[0].get("description", "Clear").title(),
                        "icon": item.get("weather", [{}])[0].get("icon", ""),
                        "humidity_pct": item["main"]["humidity"],
                        "wind_kph": round(item["wind"]["speed"] * 3.6),
                    }
                    for item in data["list"][:5]
                ]
                weather = {"city": city, "forecast": forecast}
                return weather
        except Exception:
            pass  # Fall through to mock

    # Mock fallback
    random.seed(f"{city}{date}")
    conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Light Rain", "Clear"]
    forecast = []
    base_date = datetime.strptime(date, "%Y-%m-%d")
    for i in range(5):
        forecast.append({
            "date": (base_date + timedelta(days=i)).strftime("%Y-%m-%d"),
            "temp_c": random.randint(10, 32),
            "feels_like_c": random.randint(8, 30),
            "condition": conditions[random.randint(0, len(conditions) - 1)],
            "humidity_pct": random.randint(40, 85),
            "wind_kph": random.randint(5, 40),
        })

    return {"city": city, "forecast": forecast, "source": "mock"}


@mcp.tool()
async def search_hotels(
    city: str,
    check_in: str,
    check_out: str,
    guests: int = 1,
) -> dict:
    """
    Search for available hotels in a city.

    Parameters
    ----------
    city      : Destination city (e.g. "Tokyo")
    check_in  : Check-in date in YYYY-MM-DD format
    check_out : Check-out date in YYYY-MM-DD format
    guests    : Number of guests (default 1)
    """
    hotels = _mock_hotels(city, check_in, check_out, guests)

    return {
        "city": city,
        "check_in": check_in,
        "check_out": check_out,
        "guests": guests,
        "hotels": hotels[:3],
    }


@mcp.tool()
async def get_place_info(city: str) -> dict:
    """
    Get a description of a travel destination using Wikipedia.

    Parameters
    ----------
    city : City or country name (e.g. "Kyoto", "Iceland")
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://en.wikipedia.org/api/rest_v1/page/summary/" + city.replace(" ", "_"),
                headers={"User-Agent": "agui-mcp-voice-demo/1.0"},
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "city": city,
                "summary": data.get("extract", ""),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
            }
    except Exception as exc:
        return {"city": city, "summary": f"Could not fetch info for {city}.", "error": str(exc)}


@mcp.tool()
async def save_to_itinerary(
    day: int,
    activities: list[str],
    thread_id: str = "default",
) -> dict:
    """
    Save planned activities to the user's itinerary.

    Parameters
    ----------
    day        : Day number (1 = first day of trip)
    activities : List of activity descriptions for that day
    thread_id  : Session identifier (auto-managed by the agent)
    """
    if thread_id not in _itinerary:
        _itinerary[thread_id] = []

    # Update or insert the day
    existing = next((d for d in _itinerary[thread_id] if d["day"] == day), None)
    if existing:
        existing["activities"] = activities
    else:
        _itinerary[thread_id].append({"day": day, "activities": activities})
        _itinerary[thread_id].sort(key=lambda x: x["day"])

    return {"thread_id": thread_id, "itinerary": _itinerary[thread_id]}


# ── Resources ─────────────────────────────────────────────────────────────────

@mcp.resource("travel://destinations")
def destinations_guide() -> str:
    """Curated guide to popular travel destinations."""
    return """# Top Travel Destinations Guide

## Tokyo, Japan
Best time to visit: March–May (cherry blossom) or October–November (autumn foliage).
Must-see: Shibuya Crossing, Senso-ji Temple, Tsukiji Market, TeamLab.
Getting around: IC card (Suica/Pasmo) for trains and buses.

## Paris, France
Best time to visit: April–June or September–October.
Must-see: Eiffel Tower, Louvre, Montmartre, Versailles.
Getting around: Metro is excellent. Buy a carnet for 10 tickets.

## Bali, Indonesia
Best time to visit: April–October (dry season).
Must-see: Ubud rice terraces, Tanah Lot temple, Mount Batur sunrise hike.
Getting around: Hire a private driver for day trips.

## New York, USA
Best time to visit: September–November or March–May.
Must-see: Central Park, MoMA, Brooklyn Bridge, High Line.
Getting around: Subway MetroCard — 24/7 service.

## Cape Town, South Africa
Best time to visit: November–March (summer, dry).
Must-see: Table Mountain, Cape Point, Boulders Beach penguins, Stellenbosch wine.
Getting around: Uber is reliable and affordable.
"""


if __name__ == "__main__":
    mcp.run(transport="stdio")
