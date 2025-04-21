# === config.py ===

import random

# Configure multiple Reddit accounts
class Config:
    accounts = [
        {
            "client_id" : "yhm9yGAEQ3iWtSV4Pb_emw",
            "client_secret" : "8g8zDNL_8oqAilQ6PdItpyeiSojSxg",
            "username" : "Ok-Tourist276",
            "password" : "!Fark8566",
            "user_agent" : "test bot by u/Ok-Tourist276",
        },
    ]

import itertools

class Botconfig:
    proxies = [
        # Add more proxies as needed
    ]

    new_posts = False
    cooldown = 10  # Faster cooldown for testing; increase for production use
    webhook = ""
    discord_webhook = False
    type = "ai"  # Options: 'ai', 'ad', or 'post'
    all_subreddits = True

    ads = [
        '''
        Advertisement 1: Type what u want to advertise here the exact same message will be commented on random posts!
        ''',
        '''
        Advertisement 2: Another ad message here!
        ''' ,
        '''
        Advertisement 3: Yet another ad message here!
        '''
    ]

    # subreddits = [
    #     "AskReddit", "funny", "todayilearned", "aww", "interestingasfuck",
    #     "mildlyinteresting", "Showerthoughts", "lifeprotips", "explainlikeimfive",
    #     "gadgets", "dataisbeautiful", "linux", "cybersecurity",
    #     "gachagaming", "TowerofGod", "wholesomememes", "MadeMeSmile",
    #     "nottheonion", "NoStupidQuestions", "technology"
    # ]

    subreddits = [
        "old_recipes", "CasualConversation", "AskReddit", "funny", "todayilearned",
        "mildlyinteresting", "Showerthoughts", "lifeprotips", "explainlikeimfive",
        "gadgets", "dataisbeautiful", "gachagaming", "TowerofGod", "wholesomememes",
        "MadeMeSmile", "nottheonion", "NoStupidQuestions", "aww", "interestingasfuck"
    ]


    posts = [
        {"title": "Hey there, upvote for an upvote!", "body": "UPVOTE PLEASE"},
        {"title": "Upvote for upvote, part 2!", "body": "UPVOTE PLEASE"}
    ]

    log_file = "commented_posts.txt"

    # Initialize a rotating subreddit generator
    subreddit_cycle = itertools.cycle(subreddits)

    # Karma tracker settings
    enable_karma_tracking = True
    karma_log_file = "karma_tracker.log"

    @staticmethod
    def get_random_proxy():
        if Botconfig.proxies:
            return random.choice(Botconfig.proxies)
        return None