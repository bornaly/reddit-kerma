# === app.py ===

import os
import praw
from requests import Session
from time import sleep
from datetime import datetime, timedelta
from fake_useragent import UserAgent
from praw.exceptions import RedditAPIException
from llm.main import create_response
from config import Config, Botconfig
import random
from modules.sleep.main import goto_sleep
from modules.logging.main import write_log
from reddit_tone_templates import generate_fallback, get_sleep_log_line

class RedditBot:
    def __init__(self, account, proxy=None) -> None:
        self.username = account['username']
        self.password = account['password']
        self.client_id = account['client_id']
        self.client_secret = account['client_secret']
        self.proxy = proxy
        self.session = Session()

        if proxy:
            self.configure_proxy(self.session, proxy)

        self.reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            username=self.username,
            password=self.password,
            user_agent=UserAgent().random,
            requestor_kwargs={"session": self.session}
        )
        self.log_file = Botconfig.log_file or "commented_posts.txt"

    def configure_proxy(self, session, proxy):
        proxy_parts = proxy.split(':')
        if len(proxy_parts) == 4:
            ip, port, proxy_username, proxy_password = proxy_parts
            proxy_url = f"http://{proxy_username}:{proxy_password}@{ip}:{port}"
            session.proxies['http'] = proxy_url
            session.proxies['https'] = proxy_url
            print("[Using proxy:] - ", proxy_url)
        else:
            print("[PROXY] - Proxy format is incorrect. Expected format is 'ip:port:username:password'")

    def login(self) -> bool:
        try:
            print(f"[LOGIN] - Attempting login for {self.username}")
            user = self.reddit.user.me()
            print(f"[LOGIN] - Logged in as {user}")
            write_log(f"[LOGIN] - Logged in as {user}")
            print(f"[KARMA] - Account {self.username}: {user.comment_karma} comment / {user.link_karma} post karma")
            write_log(f"[KARMA] - {self.username} → {user.comment_karma}C / {user.link_karma}L")
            return True
        except Exception as e:
            print(f"[LOGIN] - Failed to log in: {e}")
            write_log(f"[LOGIN] - Failed to log in: {e}")
            return False

    def get_rotating_subreddit(self):
        subreddit_name = next(Botconfig.subreddit_cycle)
        print(f"📌 Commenting in subreddit: r/{subreddit_name}")
        write_log(f"[SUBREDDIT] - Commenting in r/{subreddit_name}")
        return self.reddit.subreddit(subreddit_name)

    def get_trending_topics(self, subreddit) -> list:
        trending_topics = []
        commented_posts = self.load_commented_posts()
        source = subreddit.new(limit=500) if Botconfig.new_posts else subreddit.hot(limit=500)

        for submission in source:
            if submission.id not in commented_posts:
                trending_topics.append(submission)
        return trending_topics

    def extract_text_title(self, submission) -> str:
        return submission.title

    def extract_text_content(self, submission) -> str:
        return submission.selftext or ""

    def extract_comment_content_and_upvotes(self, submission) -> list:
        submission.comments.replace_more(limit=0)
        comments = submission.comments.list()
        return [(comment.body, comment.score) for comment in comments]

    def generate_comment(self, submission, title, post_text, comments) -> None:
        comments = sorted(comments, key=lambda c: c[1], reverse=True)[:4]
        comments_text = ", ".join([c[0] for c in comments])

        prompt = f'''
        You are a funny, smart, helpful Reddit user. Respond to this post in a way that is engaging, witty, or adds value.

        Post: "{title}"
        Top Comments: "{comments_text}"

        Write a comment that would get upvoted:
        '''

        try:
            if Botconfig.type == "ai":
                comment = create_response(post=prompt)
            else:
                comment = None
        except Exception as e:
            comment = None
            print(f"⚠️ AI failed to generate comment: {e}")
            write_log(f"[ERROR] - AI generation failed: {e}")

        if not comment or comment.strip().lower() in ["none", "null"]:
            subreddit_name = submission.subreddit.display_name
            comment = generate_fallback(subreddit_name)

        while True:
            try:
                submission.reply(comment)
                print("[SUCCESS] - Replied to the post!")
                write_log("[SUCCESS] - Replied to the post")
                break
            except RedditAPIException as e:
                error_type = e.items[0].error_type
                if error_type == "RATELIMIT":
                    print("[RATE LIMIT] - Detected, sleeping for 10 minutes...")
                    write_log("[RATE LIMIT] - Sleeping for 10 minutes...")
                    base_time = datetime.now()
                    wake_time = (base_time + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M")
                    print(f"[WAKE TIME] - Will resume at {wake_time}")
                    write_log(f"[WAKE TIME] - Will resume at {wake_time}")
                    for m in range(10, 0, -1):
                        line = get_sleep_log_line(m, base_time)
                        print(line)
                        write_log(line)
                        sleep(60)
                elif error_type == "THREAD_LOCKED":
                    print("[THREAD LOCKED] - Skipping.")
                    write_log("[THREAD LOCKED] - Skipping.")
                    break
                else:
                    print(f"[API ERROR] - {error_type}")
                    write_log(f"[API ERROR] - {error_type}")
                    break

        print(f"[Replied to] - {submission.title} with {comment}")
        write_log(f"[Replied to] - {submission.title} with {comment}")
        self.log_commented_post(submission.id)

    def load_commented_posts(self) -> list:
        try:
            with open(self.log_file, "r") as f:
                return f.read().splitlines()
        except FileNotFoundError:
            return []

    def log_commented_post(self, post_id: str) -> None:
        with open(self.log_file, "a") as f:
            f.write(post_id + "\n")

def get_working_proxy(account):
    for _ in range(len(Botconfig.proxies)):
        proxy = random.choice(Botconfig.proxies)
        bot = RedditBot(account, proxy=proxy)
        if bot.login():
            return proxy
    return None

def main():
    for account in Config.accounts:
        proxy = get_working_proxy(account)
        reddit_bot = RedditBot(account, proxy=proxy) if proxy else RedditBot(account)

        if reddit_bot.login():
            subreddit = reddit_bot.get_rotating_subreddit()
            trending_topics = reddit_bot.get_trending_topics(subreddit)

            for submission in trending_topics:
                print(f"[PROCESSING POST] - '{submission.title}'")
                write_log(f"[PROCESSING POST] - '{submission.title}'")

                reddit_bot.generate_comment(
                    submission,
                    reddit_bot.extract_text_title(submission),
                    reddit_bot.extract_text_content(submission),
                    reddit_bot.extract_comment_content_and_upvotes(submission),
                )

                print(f"[ACCOUNT COMPLETE] - Commented with account {account['username']}")
                write_log(f"[ACCOUNT COMPLETE] - Commented with account {account['username']}" )

                base_time = datetime.now()
                for minutes in range(Botconfig.cooldown // 60, 0, -1):
                    line = get_sleep_log_line(minutes, base_time)
                    print(line)
                    write_log(line)
                    sleep(60)
                remaining = Botconfig.cooldown % 60
                if remaining:
                    sleep(remaining)
        else:
            print(f"[LOGIN FAILED] - Skipping account {account['username']}")
            write_log(f"[LOGIN FAILED] - Skipping account {account['username']}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Script stopped manually by user.")

