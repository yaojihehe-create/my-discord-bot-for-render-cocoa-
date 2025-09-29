import discord
import os
import random
from flask import Flask
from threading import Thread

# Flaskのアプリケーションインスタンスを作成（gunicornが実行するWebサーバー）
app = Flask(__name__) 
# Botがすでに起動しているかを示すフラグ（ワーカーごとにチェック）
# gunicornのワーカープロセスが立ち上がるときにFalseに初期化されます
app.bot_started = False 

# -----------------
# Discord Bot本体の起動関数
# -----------------
def run_discord_bot():
    # ランダムに選択する応答メッセージリスト
    RANDOM_RESPONSES = [
    "「ちょっと待ったぁーーーーー！！！！！！！！！」﻿",
    "「行くぞ、シャローーーー！！」",
    "「特殊部隊に推薦できる腕前だー！」",
    "「これでも食らえー！」﻿",
    "「いつも一緒にいるだけが、友達じゃないだろ？」﻿",
    "「物理部好きだろ？」"
    ]

    TOKEN = os.getenv("DISCORD_TOKEN") 
    intents = discord.Intents.default()
    intents.message_content = True 
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        global app
        print('---------------------------------')
        print(f'Botがログインしました: {client.user.name}')
        print('---------------------------------')
        # Botが起動に成功したらフラグを立てる
        app.bot_started = True 

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        if client.user.mentioned_in(message):
            response = random.choice(RANDOM_RESPONSES)
            await message.channel.send(f'{message.author.mention} {response}')
            return 
    
    if TOKEN:
        client.run(TOKEN)
    else:
        print("エラー: Botトークンが設定されていません。")

# -----------------
# Webサーバーのエンドポイント (gunicornがアクセスする場所)
# -----------------
@app.route('/')
def home():
    # Botが起動していない場合のみ、Botを起動する
    if not app.bot_started:
        # WebアクセスをきっかけにBotを別スレッドで起動
        # この処理はgunicornワーカー内で1回だけ実行されます
        Thread(target=run_discord_bot).start()
        return "Discord Bot is initializing..."
    
    # Botが起動済みの場合は、Renderのヘルスチェックに応答
    return "Bot is alive!"

# ----------------------------------------------------
# gunicornは 'app' インスタンスをWebサーバーとして起動します。
# ----------------------------------------------------
