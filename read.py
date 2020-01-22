# -*- coding: UTF-8 -*-
import os
import json
import time
import sys
import pathlib
import cv2
import key
import path
from PIL import Image
from pyzbar import pyzbar
from pyzbar.pyzbar import decode
import requests
#import slack
from bs4 import BeautifulSoup
import unicodedata
import csv
import pprint

#SLACK_BOT_TOKEN = key.SLACK_BOT_TOKEN

def get_shortenURL(longUrl):
    url = 'https://api-ssl.bitly.com/v3/shorten'
    access_token = key.access_token
    query = {
        'access_token': access_token,
        'longurl': longUrl,
    }
    r = requests.get(url, params=query).json()
    return r


def SPOST(RN):
    slackch = key.slackch
    client = slack.WebClient(token=SLACK_BOT_TOKEN)
    response = client.chat_postMessage(channel=slackch, text=RN)


#def post(card):
    #slackch = key.slackch

    #client = slack.WebClient(token=SLACK_BOT_TOKEN)
    #response = client.chat_postMessage(channel=slackch, text=card)


def get_path():
    while True:
        try:
            path = input()
        except UnicodeDecodeError:
            print("不正な文字を入力しようとしないでください。")
            sys.exit()
        except EOFError:
            sys.exit()

        path = path.strip()

        if "exit" in path:
            exit()

        domain = pathlib.Path(path)
        domain = domain.suffix.lower()
        if_suffix = ['.jpg', '.png', '.bmp', '.tif', '.jpeg']
        if domain in if_suffix:
            pass
        elif "QR" in path:
            pass
        else:
            print(
                """サポートされていない拡張子のファイルではないと判断されました。
サポートされている拡張子はjpg/png/bmp/tif/jpegです""")
            print("再実行しますか？[Y/N]")
            try:
                retry = input().strip().lower()
            except UnicodeDecodeError:
                print("不正な文字を入力しようとしないでください。")
                sys.exit()
            except EOFError:
                print("空のまま決定しないでください")
                sys.exit()
            if retry == 'y' not in "n":
                continue
            elif retry == 'n' not in "y":
                break
            else:
                print("リトライしてください")
                continue
        return path


def main():
    print(
        """Aikatsu-QR-Reader Ver.WithOut-Slack-Post
該当の画像があるパスを入れてください
QRを読み取る場合はQRと入れてください
終了する場合はexitまたはCtrl+Dでお願いします"""
    )

    while True:
        path = get_path()

        if "QR" in path:
            window_name = "main"
            cap = cv2.VideoCapture(0)
            cap.set(3, 1280)
            cap.set(4, 720)
            cap.set(5, 60)
            cv2.namedWindow(window_name)

            while True:
                ret, flame = cap.read()
                cv2.imshow(window_name, flame)
                tresh = 100
                max_pixel = 255
                ret, flame = cv2.threshold(flame, tresh, max_pixel, cv2.THRESH_BINARY)
                qr_result = pyzbar.decode(flame)
                if qr_result != []:
                    path = qr_result[0][0].decode('utf-8', 'ignore')
                    print(path)
                    if "http://dcd.sc/" not in path and "http://aikatsu.com/qr/id=" in path and "AK" in path:
                        print("アイカツ以外のカードは読み込めません。悪しからず。")
                        sys.exit()
                    elif "http://dcd.sc/" not in path and "http://aikatsu.com/qr/id=" not in path and "AK" not in path:
                        print("別の物を読み込もうとしていませんか？")
                        sys.exit()
                    elif "http://dcd.sc/n2" in path:
                        target_url = path
                        try:
                            r = requests.get(target_url)
                        except UnicodeError:
                            print("UnicodeError!")
                            sys.exit(1)
                        except requests.exceptions.ConnectionError:
                            print("不正なURLを読み込んだ？")
                            sys.exit(1)
                        soup = BeautifulSoup(r.text, 'lxml')
                        try:
                            NR = soup.find("dd", class_="cardNum").get_text()
                            RR = soup.find("dd", class_="cardName").get_text()
                            RN = NR + "_" + RR
                            print(RN)
                        except AttributeError:
                            print("カード名取得失敗です。学生証を読み込んだ事またはリダイレクトの設定間違えだと思われます。")
                            RN = "カード名取得失敗です。学生証を読み込んだ事またはリダイレクトの設定間違えだと思われます。"
                            pass
                    elif "http://dcd.sc/j2" in path:
                        target_url = path
                        r = requests.get(target_url) 
                        soup = BeautifulSoup(r.text, 'lxml')
                        try:
                            NR = soup.find("div", class_="dress-detail-title clearfix").get_text()
                            print(NR)
                            RN = NR
                        except AttributeError:
                            print("カード名取得失敗です。学生証を読み込んだ事またはリダイレクトの設定間違えだと思われます。")
                            RN = "カード名取得失敗です。学生証を読み込んだ事またはリダイレクトの設定間違えだと思われます。"
                            pass
                    elif "http://dcd.sc/n3" in path or "http://dcd.sc/n1" in path:
                        NR = "学生証です。"
                        print(NR)
                        RN = NR
                    elif "http://dcd.sc/n0" in path:
                        NR = "アイドルカードです。"
                        print(NR)
                        RN = NR
                        
                    break
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        cv2.destroyAllWindows()

        if "http://aikatsu.com/qr/id=" in path or "AK" in path:
            print(
                """旧カツのカードは対応していません。
該当の画像を入れてください
終了する場合はexitまたはCtrl+Dでお願いします"""
            )
            path = None
            continue

        if "http://dcd.sc/" not in path:
            try:
                read = decode(Image.open(path))
            except FileNotFoundError:
                print("本当にそこにありますか？？？")
                print("再実行しますか？[Y/N]")
                try:
                    retry = input()
                except EOFError:
                    print("空のまま決定しないでください。")
                    sys.exit()
                except UnicodeDecodeError:
                    print("不正な文字を入力しようとしないでください。")
                    sys.exit()
                if retry.lower() in 'y' not in "n":
                    continue
                elif retry.lower() in 'n'not in "y":
                    break
                else:
                    print("リトライしてください")
                    continue
            except OSError:
                print("不正なファイルのため読み込めません。")
                print("強制終了します。")
                sys.exit()

            path = read[0][0].decode('utf-8', 'ignore')
            
            if "http://dcd.sc/n2" in path:
                target_url = path
                try:
                    r = requests.get(target_url)
                except UnicodeError:
                    sys.exit(1) 
                except requests.exceptions.ConnectionError:
                    sys.exit(1)
                soup = BeautifulSoup(r.text, 'lxml')
                try:
                    NR = soup.find("dd", class_="cardNum").get_text()
                    RR = soup.find("dd", class_="cardName").get_text()
                    RN = NR + "_" + RR
                    print(RN)
                except AttributeError:
                    print("カード名取得失敗です。学生証を読み込んだ事またはリダイレクトの設定間違えだと思われます。")
                    RN = "カード名取得失敗です。学生証を読み込んだ事またはリダイレクトの設定間違えだと思われます。"
                    pass
            elif "http://dcd.sc/j2" in path:
                target_url = path
                r = requests.get(target_url) 
                soup = BeautifulSoup(r.text, 'lxml')
                try:
                    NR = soup.find("div", class_="dress-detail-title clearfix").get_text()
                    print(NR)
                    RN = NR
                    print(RN)
                except AttributeError:
                    print("カード名取得失敗です。学生証を読み込んだ事またはリダイレクトの設定間違えだと思われます。")
                    RN = "カード名取得失敗です。学生証を読み込んだ事またはリダイレクトの設定間違えだと思われます。"
                    pass
                else:
                    pass
            elif "http://dcd.sc/n3" in path or "http://dcd.sc/n1" in path:
                NR = "学生証です。"
                print(NR)
                RN = NR
            elif "http://dcd.sc/n0" in path:
                NR = "アイドルカードです。"
                print(NR)
                RN = NR

        path = get_shortenURL(path)

        print(path)

        try:
            card = path['data']['url']
        except TypeError:
            print("旧カツカードまたは読み込めない形式のカードです。")
            print("該当の画像を入れてください")
            print("終了する場合はexitまたはCtrl+Dでお願いします")
            path = None
            continue
        
        card = RN + "\n" + card
        
        with open('result.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(card)
        
        #SPOST(RN)
    
        #post(card)

        card = image = path = RN = RR = NR = f = None

        print("該当の画像を入れてください")
        print("終了する場合はexitまたはCtrl+Dでお願いします")


if __name__ == '__main__':
    main()
