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
USER_ID = os.getenv("USER_ID")
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")

if not all([USER_ID, CHANNEL_ACCESS_TOKEN]):
    print("環境変数が設定されていません")
    exit(1)

# LINEメッセージの送信のためのLINE Bot APIインスタンスを作成
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

# ログ設定
logging.basicConfig(
    filename="logfile.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def line_notify(message):
    """LINEにメッセージを送る関数"""
    try:
        messages = TextSendMessage(text=message)
        line_bot_api.push_message(USER_ID, messages)
        logging.info(f"LINE通知送信: {message}")
    except Exception as e:
        logging.error(f"LINE送信エラー: {e}, LINE通知内容: {message}")

# GPIOの設定
try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.IN, pull_up_down = GPIO.PUD_UP)
except Exception as e:
    message = f"GPIO設定エラー: {e}"
    logging.error(message)
    line_notify(f"[エラー通知] {message}")
    exit(1)

# 開始通知
logging.info("プログラム開始")
message = "[起動通知] プログラムを開始します"
line_notify(message)

def main():
    """メイン処理"""
    
    # GPIOと時刻の初期状態の入力
    past_value = GPIO.input(18)
    last_open_time = datetime.now()

    try:
        while True:
            value = GPIO.input(18)
            if value != past_value:
                if value == 1:
                    message = "[通知] ドアが開きました！"
                    line_notify(message)  
                    last_open_time = datetime.now()

            if datetime.now() - last_open_time > timedelta(hours=24):
                message = "[通知] ドアが24時間開かれていません。大丈夫かな・・・"
                line_notify(message)
                last_open_time = datetime.now()

            past_value = value
            time.sleep(1)

    # キーボード割り込みやエラーが発生した場合の処理
    except KeyboardInterrupt:
        logging.info("通知：手動停止（Control+C）を検知")
        message = "[通知] プログラムが手動で停止されました"
        line_notify(message)

    except Exception as e:
        logging.error(f"エラー：{e}")
        message = f"[エラー通知] {e}"
        line_notify(message)
        
    # 処理終了時にGPIOピンの設定をクリーンアップ
    finally:
        message = "[終了通知] プログラムが停止しました"
        line_notify(message)
        logging.info("プログラム終了")
        GPIO.cleanup()

if __name__ == "__main__":
    main()