# gen-Operation-Manual
このプロジェクトでは、AIでオペレーションマニュアルを自動生成し、マークダウン形式のテキストをGoogleドキュメントおよびGoogleスプレッドシートに自動的に格納します。サービスではなく社内利用を想定して、Google colabで動作します。OpenAIのAPIを使用してテキストを解析・生成し、Google DocsとGoogle Sheets APIを活用してデータを操作します。

---

### 必要なライブラリのインストール

次のライブラリをインストールしてください：

```bash
!pip install openai google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client markdown2 gspread pandas
```

### 認証手順

1. Google Colabで認証を行い、Google APIにアクセスできるようにします。
2. 使用するGoogleドキュメントのURLとGoogleスプレッドシートのURLを設定し、APIアクセス用のドキュメントIDとスプレッドシートIDを取得します。

### 構成と手順

1. **OpenAI APIの設定**：
    - OpenAI APIキーを設定し、モデルを使用して入力テキストから構造化されたマニュアルの概要を生成します。
2. **Googleドキュメントにデータを挿入**：
    - マークダウン形式で生成されたマニュアル概要を、Google Docs APIを使って指定されたGoogleドキュメントの末尾に追記します。
3. **マークダウン形式のテキストをスプレッドシートに変換**：
    - マークダウンテキストを行ごとに解析し、見出し階層に応じてスプレッドシートのカラムを動的に追加します。
    - 解析結果をGoogleスプレッドシートに書き込み、各見出しとその詳細を整理して格納します。
4. **詳細マニュアルの生成とGoogleドキュメントへの追記**：
    - Googleスプレッドシートに格納された内容を元に、行ごとに詳細なマニュアルを生成し、Googleドキュメントの末尾に追記します。

### 実行手順

1. `input`変数に、生成したいマニュアルの概要を含むテキストを指定します。
2. プログラムを実行すると、指定されたGoogleドキュメントとGoogleスプレッドシートに、構造化されたマニュアルが格納されます。

### 注意事項

- Googleドキュメントやスプレッドシートにアクセスするために、適切な共有設定を行ってください。
- OpenAI APIキーを使用するため、セキュリティに注意し、キーを他人と共有しないでください。

---

### 出力サンプル

- https://docs.google.com/document/d/1UJ7ki3waNGKFdqNXneLiHLJgKWxtw2KL-f5OIzYPJCk/edit
- https://docs.google.com/spreadsheets/d/1jv9QisZnJfh7E_QcAQeYRbRsDUnguahEy5GbjU3PMik/edit

### 参考

- **Google API**：このプロジェクトは、GoogleのAPI（Docs, Sheets）を使用しているため、Google Cloud ConsoleでAPIを有効化し、認証情報を適切に設定してください。
- **OpenAI API**：テキスト生成にはOpenAIのAPIを利用しています。利用にはOpenAIのアカウントが必要です。

---

このプロジェクトは、マニュアル作成やデータの自動化、API連携の学習に役立つ実装例です。APIの利用にはコストがかかるため、実行する際にはご注意ください。
