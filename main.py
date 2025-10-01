import discord
import os
import random
from flask import Flask
from threading import Thread
import time

# Flaskのアプリケーションインスタンスを作成（gunicornが実行するWebサーバー）
app = Flask(__name__) 

# グローバルフラグ：Botが起動を試みたかを示す（セーフティネットとして使用）
bot_start_attempted = False

# -----------------
# Discord Bot本体の起動関数
# -----------------
def run_discord_bot():
    global bot_start_attempted

    # ランダムに選択する応答メッセージリスト
    RANDOM_RESPONSES = [
    "「全部お姉ちゃんに任せなさい！」﻿",
    "「パン作りをなめるな、みんな！ ほんの些細なことで結果が変わる、それが戦場だ！」",
    "「お姉ちゃんはね、いつだって妹たちのこと、見てるんだから！」",
    "「妹が一人増えたなら、お姉ちゃん力が二倍になっちゃう！」﻿",
    "「お姉ちゃんの背中、追いかけてきてくれたんだね！」",
    "「ご注文はぶつりですか？」",
    "「ご注文はうさぎですか？」"
    ]

    TOKEN = os.getenv("DISCORD_TOKEN") 
    intents = discord.Intents.default()
    intents.message_content = True 
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        # Botがログインしたことを示すログ
        print('---------------------------------')
        print(f'Botがログインしました: {client.user.name}')
        print('---------------------------------')

    @client.event
    async def on_message(message):
        # Bot自身のメッセージは無視
        if message.author == client.user:
            return

        # 1. 【カスタム応答】「ココアさんのバカー/バカ」に反応
        # 小文字化して、全角・半角の「バカ」に対応
        if message.content.lower() in ["ココアさんのバカー！", "ココアさんのバカ！", "ココアさんのバカー", "ココアさんのバカ"]:
            await message.channel.send("「バカって言った方がバカなのよ！」")
            return # 応答したら処理を終了
            
        # 2. 【通常応答】Botへのメンションでの応答
        elif client.user.mentioned_in(message):
            response = random.choice(RANDOM_RESPONSES)
            await message.channel.send(f'{message.author.mention} {response}')
            return 
            
        # ここに他のBot応答ロジックを追加できます

    if TOKEN:
        # Botの起動を試行する
        try:
            client.run(TOKEN)
        except Exception as e:
            # トークンエラーなど、起動失敗時のログ
            print(f"Discord Bot 起動失敗: {e}")
    else:
        print("エラー: Botトークンが設定されていません。")

# -----------------
# Webサーバーのエンドポイント (gunicornがアクセスする場所)
# -----------------
@app.route('/')
def home():
    global bot_start_attempted
    
    # 致命的な二重起動を防ぐセーフティネット
    if not bot_start_attempted:
        print("Webアクセスを検知。Discord Botの起動を試みます...")
        # フラグを立てて、このワーカーでは再起動しないようにする
        bot_start_attempted = True
        
        # Botを別スレッドで起動
        # Threadを使うことで、Webアクセスへの応答を止めずにBotを裏で実行する
        Thread(target=run_discord_bot).start()
        
        # 初回起動時は応答を返す
        return "Discord Bot is initializing... (Please check Discord in 10 seconds)"
        
    # Bot起動試行済みの場合は、Renderのヘルスチェックに応答
    return "Bot is alive!"
