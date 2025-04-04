#ライブラリ

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.dummy import DummyClassifier
import discord
from discord.ext import commands
from collections import deque
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# メッセージ履歴を追跡するための辞書
message_history = {}

# スパム検出ログ用のチャンネルID
SPAM_LOG_CHANNEL_ID = 1357807824301854830  # 実際のチャンネルIDに置き換えてください

@bot.event
async def on_message(message):
    # ボット自身のメッセージは無視
    if message.author == bot.user:
        return

    # メッセージ履歴の更新
    if message.author.id not in message_history:
        message_history[message.author.id] = deque(maxlen=10)
    message_history[message.author.id].append(message)

    # スパム検出
    if len(message_history[message.author.id]) == 10:
        oldest_message = message_history[message.author.id][0]
        newest_message = message_history[message.author.id][-1]
        time_diff = newest_message.created_at - oldest_message.created_at

        if time_diff.total_seconds() <= 7:
            # スパム検出時の処理
            await delete_spam_messages(message.author, message.channel)
            await timeout_user(message.author, message.channel)
            await log_spam_detection(message.author, message.channel)

async def delete_spam_messages(user, channel):
    # スパムメッセージの削除
    async for message in channel.history(limit=100):
        if message.author == user:
            await message.delete()

async def timeout_user(user, channel):
    # ユーザーのタイムアウト
    duration = timedelta(minutes=5)
    await user.timeout(duration)

    # タイムアウト通知の送信
    await channel.send(f"スパムが検出されたため {user.mention} を5分間タイムアウトしました")

async def log_spam_detection(user, channel):
    # スパム検出ログの埋め込みメッセージを作成
    embed = discord.Embed(
        title="スパム検出ログ",
        color=discord.Color.red(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="ユーザー", value=f"{user.name} ({user.id})")
    embed.add_field(name="チャンネル", value=f"{channel.name} ({channel.id})")
    embed.add_field(name="アクション", value="5分間のタイムアウト")

    # スパム検出ログをログチャンネルに送信
    log_channel = bot.get_channel(SPAM_LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(embed=embed)

# Botの実行
bot.run('t')

