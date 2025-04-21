# === reddit_tone_templates.py ===

from datetime import datetime, timedelta
import random

# Fallback comment templates organized by tone
tone_templates = {
    "funny": [
        "😂 This cracked me up — 10/10 would read again!",
        "Lol I wasn’t ready for that ending 🤣",
        "Tag yourself, I’m the confused one in the back 👀"
    ],
    "wholesome": [
        "This just made my day 🥹 thank you for sharing!",
        "Internet needs more of this energy ❤️",
        "So pure, so beautiful ✨"
    ],
    "serious": [
        "This is an important point and worth reflecting on.",
        "It’s great to see thoughtful discussions like this.",
        "Strong take — and honestly I agree."
    ],
    "informative": [
        "Thanks for the info! I didn’t know that. 💡",
        "Solid breakdown — definitely saving this.",
        "Great context here. Appreciate the clarity."
    ],
    "conversational": [
        "This is exactly the kind of convo I love 😄",
        "Haha yeah, I’ve totally had moments like that too!",
        "Let’s keep this going — curious what others think."
    ]
}

# Subreddit → tone mappings
subreddit_tone_map = {
    "science": "informative",
    "memes": "funny",
    "AskMen": "conversational",
    "Fitness": "serious",
    "DIY": "informative",
    "CasualConversation": "conversational",
    "old_recipes": "wholesome"
}

def generate_fallback(subreddit: str) -> str:
    tone = subreddit_tone_map.get(subreddit.lower(), "conversational")
    options = tone_templates.get(tone, tone_templates["conversational"])
    return random.choice(options)

def get_sleep_log_line(remaining_minutes: int, start_time: datetime = None) -> str:
    if not start_time:
        start_time = datetime.now()
    elapsed = 10 - remaining_minutes  # count upward
    timestamp = (start_time + timedelta(minutes=elapsed)).strftime("%Y-%m-%d-%H:%M")
    return f"[SLEEP] - {remaining_minutes} minute(s) left [{timestamp}]"

# Test print
if __name__ == "__main__":
    base_time = datetime.now()
    for m in range(10, 0, -1):
        print(get_sleep_log_line(m, base_time))