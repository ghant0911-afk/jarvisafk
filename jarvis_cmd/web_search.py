"""
Web search integration for Jarvis.
Provides real-time internet search capabilities.
"""
import os
import json
from typing import Optional, List, Dict
from dataclasses import dataclass

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


def search_web(query: str, num_results: int = 5) -> Optional[List[SearchResult]]:
    """
    Search the web using DuckDuckGo (no API key required).

    Args:
        query: Search query
        num_results: Number of results to return

    Returns:
        List of SearchResult objects or None if failed
    """
    if not REQUESTS_AVAILABLE:
        return None

    try:
        # DuckDuckGo Instant Answer API (free, no key needed)
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1,
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []

        # Abstract (main answer)
        if data.get("Abstract"):
            results.append(SearchResult(
                title=data.get("Heading", "DuckDuckGo"),
                url=data.get("AbstractURL", ""),
                snippet=data.get("Abstract", "")
            ))

        # Related topics
        for topic in data.get("RelatedTopics", [])[:num_results]:
            if isinstance(topic, dict) and "Text" in topic:
                results.append(SearchResult(
                    title=topic.get("Text", "")[:100],
                    url=topic.get("FirstURL", ""),
                    snippet=topic.get("Text", "")
                ))

        return results if results else None

    except Exception:
        return None


def search_wikipedia(query: str) -> Optional[str]:
    """
    Search Wikipedia for quick facts.

    Args:
        query: Search query

    Returns:
        Summary text or None if not found
    """
    if not REQUESTS_AVAILABLE:
        return None

    try:
        url = "https://ru.wikipedia.org/api/rest_v1/page/summary/" + query.replace(" ", "_")
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return data.get("extract", None)

        return None

    except Exception:
        return None


def get_weather(city: str = "Moscow") -> Optional[Dict]:
    """
    Get current weather for a city.
    Uses wttr.in (free, no API key).

    Args:
        city: City name

    Returns:
        Weather data dict or None
    """
    if not REQUESTS_AVAILABLE:
        return None

    try:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        current = data.get("current_condition", [{}])[0]

        return {
            "temp_c": current.get("temp_C", "N/A"),
            "feels_like_c": current.get("FeelsLikeC", "N/A"),
            "description": current.get("weatherDesc", [{}])[0].get("value", "N/A"),
            "humidity": current.get("humidity", "N/A"),
            "wind_kph": current.get("windspeedKmph", "N/A"),
        }

    except Exception:
        return None


def format_search_results(results: List[SearchResult]) -> str:
    """Format search results for display."""
    if not results:
        return "Ничего не найдено."

    output = []
    for i, result in enumerate(results, 1):
        output.append(f"{i}. {result.title}")
        if result.snippet:
            output.append(f"   {result.snippet[:200]}...")
        if result.url:
            output.append(f"   {result.url}")
        output.append("")

    return "\n".join(output)


def format_weather(weather: Dict) -> str:
    """Format weather data for display."""
    return (
        f"🌡️ Температура: {weather['temp_c']}°C (ощущается как {weather['feels_like_c']}°C)\n"
        f"☁️ Погода: {weather['description']}\n"
        f"💧 Влажность: {weather['humidity']}%\n"
        f"💨 Ветер: {weather['wind_kph']} км/ч"
    )
