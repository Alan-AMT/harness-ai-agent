import os
from dotenv import load_dotenv
import httpx
from domain.ports.tool import AgentTool


class FastForexAPI(AgentTool):
    # {
    #   "base": "USD",
    #   "result": {
    #     "EUR": 0.865385
    #   },
    #   "updated": "2026-08-06T00:16:53Z",
    #   "ms": 7
    # }
    BASE_URL = "https://api.fastforex.io"

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("FASTFOREX_API_KEY")
        self.client = httpx.AsyncClient(base_url=self.BASE_URL)
        self.name = "currency_exchange"
        self.description = "Use this tool when you need to convert currencies. You must provide the currency you want to convert from and the currency you want to convert to. Returns the exchange rate between the two currencies."
        self.run_args_schema = {
            "type": "object",
            "properties": {
                "from_currency": {
                    "type": "string",
                    "description": "The currency to convert from."
                },
                "to_currency": {
                    "type": "string",
                    "description": "The currency to convert to."
                }
            },
            "required": ["from_currency", "to_currency"]
        }
    
    async def run(self, from_currency: str, to_currency: str) -> float:
        """Fetches the exchange rate between two currencies."""
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        response = await self.client.get(
            "/fetch-one",
            params={
                "from": from_currency,
                "to": to_currency,
            },
            headers={
                "Authorization": f"Bearer {self.api_key}"
            },
        )
        response.raise_for_status()

        data = response.json()

        try:
            return data["result"][to_currency]
        except KeyError:
            raise ValueError(f"No exchange rate found for {from_currency} -> {to_currency}")
    
    # async def fetch_all(self, from_currency: str) -> dict:
    #     """Fetches exchange rates for all currencies against the base currency."""
    #     url = f"https://api.fastforex.io/fetch-all?from={from_currency}"
    #     headers = {"Authorization": f"Bearer {self.api_key}"}
    #     response = await httpx.get(url, headers=headers)
    #     response.raise_for_status()
    #     data = response.json()
    #     return data["result"]
    
    # async def fetch_bulk(self, from_currency: str, to_currencies: list[str]) -> dict:
    #     """Fetches exchange rates for a list of currencies against the base currency."""
    #     url = f"https://api.fastforex.io/fetch-bulk?from={from_currency}&to={','.join(to_currencies)}"
    #     headers = {"Authorization": f"Bearer {self.api_key}"}
    #     response = await httpx.get(url, headers=headers)
    #     response.raise_for_status()
    #     data = response.json()
    #     return data["result"]
    
    # async def fetch_historical(self, from_currency: str, to_currency: str, date: str) -> float:
    #     """Fetches the exchange rate for a specific date."""
    #     url = f"https://api.fastforex.io/fetch-historical?from={from_currency}&to={to_currency}&date={date}"
    #     headers = {"Authorization": f"Bearer {self.api_key}"}
    #     response = await httpx.get(url, headers=headers)
    #     response.raise_for_status()
    #     data = response.json()
    #     return data["result"][to_currency]
    
    # async def fetch_historical_bulk(self, from_currency: str, to_currencies: list[str], date: str) -> dict:
    #     """Fetches exchange rates for a list of currencies for a specific date."""
    #     url = f"https://api.fastforex.io/fetch-historical-bulk?from={from_currency}&to={','.join(to_currencies)}&date={date}"
    #     headers = {"Authorization": f"Bearer {self.api_key}"}
    #     response = await httpx.get(url, headers=headers)
    #     response.raise_for_status()
    #     data = response.json()
    #     return data["result"]