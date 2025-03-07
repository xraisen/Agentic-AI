# agentic_ai.py
import requests
import json
import os

def load_config(config_file="config.json"):
    """Loads configuration from a JSON file."""
    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_file}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{config_file}'.")
        return None

def get_gemini_response(prompt, image_url=None):
    """Gets a response from Gemini via OpenRouter."""
    config = load_config()
    if not config:
        return "Configuration error."

    headers = {
        "Authorization": f"Bearer {config['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json",
        "HTTP-Referer": config.get("SITE_URL", ""),
        "X-Title": config.get("SITE_NAME", ""),
    }

    messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]

    if image_url:
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {"url": image_url}
        })

    data = {
        "model": config["MODEL"],
        "messages": messages,
    }

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(data),
        )
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Request error: {e}"
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        return f"Response parsing error: {e}"

if __name__ == "__main__":
    # Example usage (text only)
    user_prompt = "Explain quantum physics in simple terms."
    ai_response = get_gemini_response(user_prompt)
    print("Agentic AI:", ai_response)

    # Example usage (text and image)
    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
    image_prompt = "What is in this image?"
    ai_response_image = get_gemini_response(image_prompt, image_url)
    print("Agentic AI (Image):", ai_response_image)