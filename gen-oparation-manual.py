# 実際にGoogle colabで動かすときは、適当にブロックを分けてください

# 必要なライブラリのインストール
from google.colab import auth
from google.auth import default
from googleapiclient.discovery import build
from google.oauth2 import service_account
import gspread
from gspread_dataframe import set_with_dataframe
import markdown
import markdown2
import re
import pandas as pd
import openai

# Google認証
auth.authenticate_user()
creds, _ = default()

# GoogleドキュメントのURLを指定
doc_url = '<URL>' # ここを転記したいGoogleドキュメントのURLに置き換えてください
doc_id = doc_url.split('/d/')[1].split('/')[0]  # ドキュメントIDを抽出
sheet_url = "<URL>" # ここを転記したいGoogleスプレッドシートのURLに置き換えてください
sheet_id = sheet_url.split('/d/')[1].split('/')[0]  # スプレッドシートIDを抽出

# OpenAI APIの設定
openai.api_key = '<API KEY>' # ここをあなたのOpenAI APIキーに置き換えてください

# 関数の定義
def ai(s):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        max_tokens=4096,
        temperature=1,
        messages=[
            {"role": "system", "content": "人間の仕事を助ける優秀なAIアシスタントとして、指示に従い、必要な情報のみを出力します。"},
            {"role": "user", "content": s},
        ]
    )
    return response["choices"][0]["message"]["content"]

# 作りたいマニュアルの内容をinputに代入
input = """
<text>
"""

# マニュアルの全体像を生成
manual_Overview = ai(f"""
マニュアル「{input}」の全体像を、下記の規則に従いマークダウン形式で構造化された日本語テキストで出力します。
\n見出し1は各ステップを順に並べてください
\n各ステップを見出し2以下にブレイクダウンして構造化してください
\n最下位の見出しには内容を箇条書きで列挙してください
""")

purpose = "# 目的 \n\n" + ai(f"下記のテキストを分析して、このマニュアルの目的を書きます。\nマニュアル「{input}」\n{manual_Overview}") + "\n\n"

# マニュアル全体像をドキュメントとスプレッドシートに格納

# Google Docs APIサービスの初期化
docs_service = build('docs', 'v1', credentials=creds)
sheets_service = build('sheets', 'v4', credentials=creds)

# テキストをGoogleドキュメントに挿入する関数
def markdown2google_doc(doc_id, text):
    document = docs_service.documents().get(documentId=doc_id).execute() 
    end_index = document['body']['content'][-1]['endIndex'] - 1

    # Google Docs APIのリクエスト
    requests = [
        {
            'insertText': {
                'location': {
                    'index': end_index,
                },
                'text': text
            }
        }
    ]
    docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()

# マークダウン形式のテキストをGoogleドキュメントに挿入
text = purpose + manual_Overview + "\n\n"
markdown2google_doc(doc_id, text)

# スプレッドシートに格納
creds, _ = default()
gc = gspread.authorize(creds)

# GoogleスプレッドシートのURLを指定
spreadsheet = gc.open_by_url(sheet_url)
worksheet = spreadsheet.sheet1

# パースしたデータを保持するリスト
data = []

# マークダウンテキストの解析とスプレッドシートの準備
lines = manual_Overview.splitlines()
max_header_level = 0
data = []

current_headers = []  # 見出しの階層ごとに値を格納
content = ""
detail_lines = []

# 行ごとに解析して見出しと内容を整理
for line in lines:
    if line.startswith("#"):
        # 新しい見出しが出現した場合、既存の内容をリストに追加
        if content or detail_lines:
            if detail_lines:
                for detail in detail_lines:
                    data.append(current_headers + [content, detail])
            else:
                data.append(current_headers + [content, ""])
            content = ""
            detail_lines = []

        # 見出しのレベルと内容の取得
        header_level = line.count("#")
        header_text = line.strip("# ").strip()

        # 見出しの深さに応じて見出しリストを更新
        current_headers = current_headers[:header_level-1] + [header_text]
        max_header_level = max(max_header_level, header_level)

    elif line.startswith("-"):
        # 箇条書き内容を収集
        detail_lines.append(line.strip("- ").strip())
    else:
        # 本文内容を記録
        content = line.strip()

# 最後の行を追加
if content or detail_lines:
    if detail_lines:
        for detail in detail_lines:
            data.append(current_headers + [content, detail])
    else:
        data.append(current_headers + [content, ""])

# カラム数に応じたデータフレームの準備
columns = [f"項目{i+1}" for i in range(max_header_level)] + ["小項目", "詳細"]
df = pd.DataFrame(data, columns=columns)

# 空のセルを埋める
df = df.fillna('')

# Googleスプレッドシートに書き込む
set_with_dataframe(worksheet, df)

print(f"""
処理が完了しました
\nドキュメント: {doc_url}
\nスプレッドシート: {sheet_url}
\n\n
""")

# 全データを取得
data = worksheet.get_all_records()
rows = worksheet.get_all_values()

 # 最初の行をカラム名として使用
df = pd.DataFrame(rows[1:], columns=rows[0])

# 行ごとに詳細マニュアルを生成してドキュメントに追記
for index, row in df.iterrows():
    title = row["詳細"]
    manual_details = ai(f"「{row}」についての詳細マニュアルを書きます。マニュアルは構造化された日本語テキストで、見出し「タイトル{title}」「必要な前提知識と用いるフレームワーク」、「手順」、「クオリティレビューの観点」を含みます")
    print(manual_details + "\n\n")
    markdown2google_doc(doc_id, manual_details + "\n\n")
