# === llm/main.py ===

import asyncio
import time
import random
import g4f
from g4f.client import Client
from config import Botconfig
import atexit

# === Ensure asyncio event loop works in all threads ===
def ensure_event_loop():
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

# === Provider mapping ===
provider_model_map = {
    g4f.Provider.You: ["gpt-4o-mini"],
    g4f.Provider.MetaAI: ["gpt-4o-mini"],
}

# === Default fallback response ===
def fallback_response():
    fallback = random.choice(Botconfig.ads).strip()
    print(f"🪫 Fallback Ad Used: {fallback}")
    return fallback

# === AI response generator ===
def create_response(post: str) -> str:
    for provider, models in provider_model_map.items():
        for model in models:
            print(f"🤁 Selected provider: {provider.__name__} with model: {model}")
            client = None
            try:
                client = Client(provider=provider)
                start = time.time()
                chat_completion = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": post}],
                    stream=False
                )
                elapsed = round(time.time() - start, 2)
                response = chat_completion.choices[0].message.content.strip()

                if response.startswith('"') and response.endswith('"'):
                    response = response[1:-1]

                print(f"✅ AI Response Time: {elapsed}s")
                if response.lower() in ["none", "null", "", "n/a"]:
                    raise ValueError("AI returned empty or meaningless response.")
                return response

            except Exception as e:
                err_msg = str(e).lower()
                if any(code in err_msg for code in ["403", "cloudflare", "401", "404"]):
                    print(f"⚠️ Provider blocked or unavailable: {provider.__name__}")
                else:
                    print(f"⚠️ Error: {e}")
                time.sleep(1)

            finally:
                try:
                    loop = ensure_event_loop()

                    if client and hasattr(client, "close") and asyncio.iscoroutinefunction(client.close):
                        loop.run_until_complete(client.close())

                    session_obj = getattr(client, "session", None)
                    if session_obj and hasattr(session_obj, "close"):
                        loop.run_until_complete(session_obj.close())

                except Exception as cleanup_err:
                    print(f"⚠️ Failed to close session: {cleanup_err}")

    print("⚠️ Max retries reached. Switching to fallback.")
    return fallback_response()

# === Cleanup on exit ===
@atexit.register
def cleanup_global_sessions():
    try:
        import gc
        for obj in gc.get_objects():
            if isinstance(obj, Client):
                loop = ensure_event_loop()
                if hasattr(obj, "close") and asyncio.iscoroutinefunction(obj.close):
                    loop.run_until_complete(obj.close())
                if hasattr(obj, "session") and hasattr(obj.session, "close"):
                    loop.run_until_complete(obj.session.close())
    except Exception as e:
        print(f"⚠️ Global session cleanup error: {e}")

if __name__ == "__main__":
    example_post = "Tell me something fun about Linux"
    print(create_response(example_post))