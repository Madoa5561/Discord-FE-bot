# Discord-FE-bot

このプロジェクトは、情報技術者試験の問題セットを管理するために設計されたDiscordボットです。ボットは毎日午前0時に指定されたチャンネルに問題を投稿し、ユーザーがボタンを使用して回答と対話できるようにします。回答を追跡し、最速の回答者を表示します。

## プロジェクト構造

```
Discord-FE-bot
├── src
│   ├── main.py                # Discordボットのエントリーポイント
│   ├── cogs
│   │   └── daily_question.py   # 日常の問題投稿ロジック
│   ├── utils
│   │   └── question_manager.py  # 問題の読み込みと管理を処理
│   └── data
│       └── questions.json      # 問題、オプション、説明を保存
├── .env                        # ボットの環境変数
├── requirements.txt            # 依存関係のリスト
└── README.md                   # プロジェクトのドキュメント
```

## セットアップ手順

1. **リポジトリをクローン:**
   ```
   git clone https://github.com/Madoa5561/Discord-FE-bot
   cd Discord-FE-bot
   ```

2. **依存関係をインストール:**
   Python 3.8以上がインストールされていることを確認してから、以下を実行してください:
   ```
   pip install -r requirements.txt
   ```

3. **環境変数を設定:**
   ルートディレクトリに`.env`ファイルを作成し、Discordボットトークンを追加してください:
   ```
   DISCORD_TOKEN=your_token_here
   CHANNEL_ID=discord_channelId
   DAILY_COUNT=5
   ```

4. **質問を追加:**
   `src/data/questions.json`ファイルを編集して、質問、オプション、説明を含めてください。

## 使用方法

ボットを実行するには、以下のコマンドを実行してください:
```
python src/main.py
```

ボットが起動し、毎日午前0時に指定されたチャンネルに問題を投稿します。ユーザーは提供されたボタンを使用して問題に回答でき、ボットは最速の回答者を表示します。

## 貢献

改善やバグ修正のためのイシューやプルリクエストを自由に送信してください。
