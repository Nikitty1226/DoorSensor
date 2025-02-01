import RPi.GPIO as GPIO
import os
import logging
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

from linebot import LineBotApi
from linebot.models import TextSendMessage


# 環境変数読み込み
load_dotenv()

# ユーザーIDとLINEチャネルアクセストークンを設定
user_id = ""
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")

if not CHANNEL_ACCESS_TOKEN:
    print("CHANNEL_ACCESS_TOKENが設定されていません")
    exit(1)

# LINEメッセージの送信のためのLINE Bot APIインスタンスを作成
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

# ログ設定
logging.basicConfig(
    filename="logfile.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# LINEにメッセージを送る関数
def line_notify(message):
    try:
        messages = TextSendMessage(text=message)
        line_bot_api.push_message(user_id, messages)
        logging.info(f"LINE通知送信: {message}")
    except Exception as e:
        logging.error(f"LINE送信エラー: {e}, LINE通知内容: {message}")

# GPIOの設定
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# GPIOと時刻の初期状態の入力
past_value = GPIO.input(18)
last_open_time = datetime.now()

# メインループ
try:
    while True:
        value = GPIO.input(18)
        if value != past_value:
            if value == 1:
                message = "[通知] ドアが開きました！"
                line_notify(message)  
                last_open_time = datetime.now()

        if datetime.now() - last_open_time > timedelta(minutes=5):
            message = "[通知] ドアが24時間開かれていません。大丈夫かな・・・"
            line_notify(message)
            last_open_time = datetime.now()

        past_value = value
        time.sleep(1)

# キーボード割り込みやエラーが発生した場合の処理
except KeyboardInterrupt:
    logging.info("Control+Cを検知しました")

except Exception as e:
    message = f"[エラー通知] {e}"
    line_notify(message)
    logging.error(f"エラー: {e}")

# 処理終了時にGPIOピンの設定をクリーンアップ
finally:
    message = "[終了通知] プログラムが停止しました"
    line_notify(message)
    logging.info("プログラム終了")
    GPIO.cleanup()