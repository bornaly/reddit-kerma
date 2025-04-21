import praw

reddit = praw.Reddit(
    client_id="yhm9yGAEQ3iWtSV4Pb_emw",
    client_secret="8g8zDNL_8oqAilQ6PdItpyeiSojSxg",
    username="Ok-Tourist276",
    password="!Fark8566",
    user_agent="test bot by u/Ok-Tourist276"
)

print("✅ Logged in as:", reddit.user.me())