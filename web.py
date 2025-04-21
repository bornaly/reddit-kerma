from flask import Flask, render_template, jsonify
from threading import Thread
from app import RedditBot, main
from config import Config

app = Flask(__name__)
reddit_bot = main()
bot_thread = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_bot', methods=['POST'])
def start_bot():
    global bot_thread
    if bot_thread is None or not bot_thread.is_alive():
        bot_thread = Thread(target=reddit_bot.run)
        bot_thread.start()
        return jsonify({"status": "success", "message": "Reddit Bot started successfully!"})
    else:
        return jsonify({"status": "error", "message": "Reddit Bot is already running."})

@app.route('/stop_bot', methods=['POST'])
def stop_bot():
    if bot_thread is not None and bot_thread.is_alive():
        bot_thread.join()
        return jsonify({"status": "success", "message": "Reddit Bot stopped successfully!"})
    else:
        return jsonify({"status": "error", "message": "Reddit Bot is not running."})

@app.route('/log')
def log():
    with open("log.txt") as file:
        data = file.read()
        return data

@app.route('/commented')
def commented_posts():
    with open("commented_posts.txt") as file:
        data = file.read()
        return data

if __name__ == '__main__':
    app.run(debug=True)
