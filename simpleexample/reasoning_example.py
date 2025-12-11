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
        "input": "What is the meaning of life?",
        "reasoning": {"effort": "high"},
    }
    r = or_client.post(url="/responses", json=data)
    print(r.status_code)
    pprint(r.json())


def ex2():
    data = {
        "model": "nex-agi/deepseek-v3.1-nex-n1:free",
        "input": [
            {
                "type": "message",
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Was 1995 30 years ago? Show your reasoning.",
                    }
                ],
            }
        ],
        "reasoning": {"effort": "high"},
    }
    r = or_client.post(url="/responses", json=data)
    print(r.status_code)
    pprint(r.json())


def debug_streaming(input_text):
    print(input_text)


def print_streaming(input_text):
    if "OPENROUTER PROCESSING" in input_text:
        print(".", end="")

    else:
        resp_data = input_text.split("data: ")[1].strip()
        if resp_data != "[DONE]":
            try:
                resp_json = json.loads(resp_data)

                if resp_json.get("type") == "response.reasoning_text.delta":
                    print(f"{resp_json.get('delta')}", end="")
                elif resp_json.get("type") == "response.output_text.delta":
                    print(f"{resp_json.get('delta')}", end="")
                elif resp_json.get("type") == "response.completed":
                    print()
                    print("FINAL RESPONSE HIT!")
                    final_response = resp_json.get("response")["output"][0]["content"][
                        0
                    ]["text"]
                    print(final_response)
                else:
                    print()
                    print(resp_json)

            except json.JSONDecodeError as e:
                print("There's an error", e)
                print(input_text)


def ex3(debug=False):
    data = {
        "model": "amazon/nova-2-lite-v1:free",
        "input": "Solve this step by step: What is the airspeed velocity of an unlaiden swallow?",
        "reasoning": {"effort": "medium"},
        "stream": True,
    }
    with or_client.stream("POST", url="/responses", json=data) as r:
        for text in r.iter_text():
            if debug:
                debug_streaming(text)
            else:
                print_streaming(text)


if __name__ == "__main__":
    # main()
    # ex2()
    ex3(debug=False)
