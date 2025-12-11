#! /usr/bin/env -S uv run
import httpx
import json
from os import getenv
from pprint import pprint

from dotenv import load_dotenv

load_dotenv()
OPENROUTER_KEY = getenv("OPENROUTER_KEY")

headers = {
    "Authorization": f"Bearer {OPENROUTER_KEY}",
}
or_client = httpx.Client(
    base_url="https://openrouter.ai/api/v1/", headers=headers, timeout=60
)


def main():
    data = {
        "model": "nex-agi/deepseek-v3.1-nex-n1:free",
        "messages": [
            {"role": "user", "content": "What is today's weather in New York?"}
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get today's weather for a specific City.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city_name": {
                                "type": "string",
                                "description": "The city to fetch weather for.",
                            }
                        },
                        "required": ["city_name"],
                    },
                },
            }
        ],
    }
    r = or_client.post(url="/chat/completions", json=data)
    print(r.status_code)
    pprint(r.json())
    tool_call = r.json()["choices"][0]["message"]["tool_calls"]
    data["messages"].append(
        {"role": "assistant", "content": "", "tool_calls": tool_call}
    )
    data["messages"].append(
        {
            "role": "tool",
            "tool_call_id": tool_call[0]["id"],
            "content": json.dumps({"temp": 75, "weather": "overcast"}),
        }
    )
    r = or_client.post(url="/chat/completions", json=data)
    print(r.status_code)
    pprint(r.json())


if __name__ == "__main__":
    main()
