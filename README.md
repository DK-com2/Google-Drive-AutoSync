# Google-Drive-AutoSync

🔄 **Google Driveファイルの自動監視・ダウンロード・処理システム**

## 🎯 システム概要

Google-Drive-AutoSyncは、Google Driveに新しくアップロードされたファイルを自動的に検知し、ローカルにダウンロードして指定の処理を実行するシステムです。現在はBirdNET鳥類音声解析システムとの統合を主目的としていますが、汎用的な設計により様々な用途に対応可能です。

### 主な機能
- 📁 **Google Drive監視**: Changes APIによる効率的な新規ファイル検出
- ⬇️ **自動ダウンロード**: 安全で高速なファイル取得（チャンク分割対応）
- 🔄 **ファイル処理**: 外部プロセス連携による柔軟な処理システム
- 🗄️ **結果管理**: JSON形式での処理結果保存
- 🔄 **自動クリーンアップ**: 処理後のGoogle Driveファイル削除
- 📝 **詳細ログ**: 日付別ログファイルによる運用監視

## 🚀 クイックスタート

### 1. 必要な環境
- Python 3.8以上
- Windows 10/11（Task Scheduler使用）
- Google Driveアカウント
- 十分なディスク容量（1GB以上推奨）

### 2. Google Drive API設定

#### Step 1: Google Cloud Consoleでプロジェクト作成
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成
3. Google Drive APIを有効化

#### Step 2: 認証情報の作成
1. 「認証情報」→「認証情報を作成」→「OAuth クライアント ID」
2. アプリケーションの種類：「デスクトップアプリケーション」
3. `credentials.json` をダウンロード
4. `S:\python\Google-Drive-AutoSync\config\` フォルダに配置

### 3. 設定ファイルの編集

`config\config.json` を編集：

```json
{
  "google_drive": {
    "target_folder_id": "YOUR_GOOGLE_DRIVE_FOLDER_ID",
    "credentials_file": "credentials.json",
    "token_file": "token.pickle",
    "page_token_file": "page_token.txt"
  },
  "file_processing": {
    "download_path": "S:/python/Google-Drive-AutoSync/data/downloads",
    "chunk_size_mb": 5,
    "min_free_space_gb": 1
  },
  "monitoring": {
    "check_interval_seconds": 30,
    "max_retries": 3,
    "retry_delay_seconds": 5
  },
  "sync_processing": {
    "processor_path": "../BirdNET-AudioAnalyzer/src/analyze_audio.py",
    "timeout_seconds": 300,
    "enabled": true
  },
  "logging": {
    "level": "INFO",
    "max_log_files": 30,
    "log_rotation_mb": 10
  }
}
```

**Google DriveフォルダIDの取得方法:**
1. Google Driveで対象フォルダを開く
2. URLの最後の部分がフォルダID
3. 例: `https://drive.google.com/drive/folders/1AbC2dEf3GhI4jKl` → `1AbC2dEf3GhI4jKl`

### 4. 必要パッケージのインストール

```bash
cd S:\python\Google-Drive-AutoSync
pip install -r requirements.txt
```

現在の`requirements.txt`の内容：
```
google-api-python-client>=2.0.0
google-auth-httplib2>=0.1.0
google-auth-oauthlib>=0.5.0
```

### 5. 設定テスト実行

```bash
python scripts\test_setup.py
```

## 📁 プロジェクト構成

```
S:\python\Google-Drive-AutoSync\
├── 📁 src\                     # メインプログラム
│   ├── 📄 main.py              # エントリーポイント
│   ├── 📄 drive_monitor.py     # Google Drive監視（Changes API）
│   └── 📄 file_processor.py    # ファイル処理・外部連携
├── 📁 config\                  # 設定ファイル
│   ├── 📄 config.json          # メイン設定
│   └── 📄 credentials.json     # Google Drive認証（機密）
├── 📁 scripts\                 # 実行スクリプト
│   ├── 📄 run_sync.bat         # Windows実行（サイレント）
│   ├── 📄 run_sync.ps1         # PowerShell実行（サイレント）
│   ├── 📄 test_manual_run.bat  # 手動テスト（詳細表示）
│   ├── 📄 test_setup.py        # 設定テスト
│   ├── 📄 process_existing_files.py  # 既存ファイル一括処理
│   └── 📄 diagnose_drive.py    # 診断ツール
├── 📁 data\                    # データ保存
│   ├── 📁 downloads\           # ダウンロードファイル
│   ├── 📁 results\             # 処理結果JSON
│   ├── 📁 temp\                # 一時ファイル
│   ├── 📄 page_token.txt       # 監視状態（自動生成）
│   ├── 📄 last_run.txt         # 最終実行時刻（自動更新）
│   ├── 📄 processed_files.txt  # 処理済みファイル（自動更新）
│   └── 📄 token.pickle         # 認証トークン（自動生成）
├── 📁 docs\                    # ドキュメント
│   ├── 📄 TASK_SCHEDULER_SETUP.md  # Task Scheduler設定ガイド
│   ├── 📄 EXECUTION_GUIDE.md      # 実行ファイル使い分けガイド
│   ├── 📄 OPERATION_GUIDE.md      # 運用ガイド
│   └── 📄 FILE_STRUCTURE.md       # ファイル構成詳細
├── 📁 logs\                    # ログファイル
│   └── 📄 autosync_YYYYMMDD.log # 日付別ログ
└── 📁 tests\                   # テストコード
```

## 🔧 使用方法

### 手動実行
```bash
# バッチファイルで実行（詳細表示）
scripts\test_manual_run.bat

# PowerShellで実行（詳細表示）
powershell -ExecutionPolicy Bypass scripts\test_manual_run.ps1

# Pythonで直接実行
python src\main.py

# 既存ファイル一括処理
python scripts\process_existing_files.py

# 診断実行
python scripts\diagnose_drive.py
```

### 自動実行（Windows Task Scheduler）

#### Task Scheduler設定例
1. Windows Task Scheduler を開く
2. 「基本タスクの作成」を選択
3. 以下の設定を行う：

| 項目 | 設定値 |
|------|--------|
| **名前** | Google Drive AutoSync |
| **トリガー** | 毎日 |
| **開始時刻** | 08:00 |
| **間隔** | 30分ごとに繰り返す |
| **継続時間** | 4時間 |
| **操作** | プログラムの開始 |
| **プログラム** | `S:\python\Google-Drive-AutoSync\scripts\run_sync.bat` |
| **開始** | `S:\python\Google-Drive-AutoSync` |

詳細は [Task Scheduler設定ガイド](docs/TASK_SCHEDULER_SETUP.md) を参照

## 📊 システム動作

### 正常な動作フロー

```
1. Task Scheduler起動 (例: 08:30)
   ↓
2. main.py実行開始
   ↓
3. Google Drive Changes API で新規ファイル確認
   ↓
4. 新しいファイル検出（対象拡張子）
   ↓
5. アップロード完了確認（MD5チェックサム存在確認）
   ↓
6. ディスク容量チェック（必要容量×2.5 + 安全マージン）
   ↓
7. ファイルダウンロード（5MBチャンク、進捗表示）
   ↓
8. ファイル整合性確認（MD5ハッシュ、サイズ）
   ↓
9. 外部処理システム実行（例：BirdNET解析）
   ↓
10. 結果をJSONで保存（data/results/）
   ↓
11. Google Driveからファイル削除（権限エラー時はスキップ）
   ↓
12. 処理済みファイルリストに記録
   ↓
13. 次回まで待機
```

### 実際のログ出力例

```
2025-06-20 22:29:07,133 - Google-Drive-AutoSync - INFO - === Google Drive AutoSync 開始 ===
2025-06-20 22:29:07,142 - Google-Drive-AutoSync - INFO - 設定ファイル読み込み完了
2025-06-20 22:29:07,173 - Google-Drive-AutoSync - INFO - Google Drive監視開始
2025-06-20 22:29:07,651 - DriveMonitor - INFO - 新規ファイル検出: 05 Adventure.mp3
2025-06-20 22:29:12,465 - FileProcessor - INFO - ダウンロード完了: 05 Adventure.mp3
2025-06-20 22:29:12,468 - FileProcessor - INFO - 処理結果保存: sync_result_20250620_222912_05 Adventure.json
2025-06-20 22:29:16,838 - Google-Drive-AutoSync - INFO - === Google Drive AutoSync 終了 ===
```

### 結果確認方法

#### 処理結果の確認
新しいファイルが処理されると、`data\results\` フォルダに処理結果が保存されます：

```
data\results\
├── sync_result_20250620_222912_05 Adventure.json
├── sync_result_20250620_222916_04 Famous Day.json
└── sync_result_20250620_222920_03 Sample.json
```

#### ダウンロードファイルの確認
```
data\downloads\
├── 05 Adventure.mp3
├── 04 Famous Day.mp3
└── 03 Sample.mp3
```

#### ログ確認
```
logs\
└── autosync_20250620.log
```

#### エラー状態の確認
エラーが発生すると `data\error_flag.txt` が作成されます：
```
2025-06-20 08:30 - システムエラー: ネットワークエラー
```

## 🛠️ トラブルシューティング

### よくある問題と解決方法

#### 1. 認証エラー
```
❌ 認証ファイルが見つかりません
```
**解決方法:**
- `credentials.json` が `config\` フォルダにあるか確認
- Google Cloud ConsoleでOAuth認証情報を再作成

#### 2. フォルダIDエラー
```
❌ 対象フォルダにアクセスできません
```
**解決方法:**
- Google DriveフォルダIDが正しいか確認
- フォルダの共有設定を確認
- フォルダへのアクセス権限を確認

#### 3. ディスク容量エラー
```
❌ ディスク容量不足: 必要=125.0MB, 使用可能=50.0MB
```
**解決方法:**
- 十分な空き容量を確保（ファイルサイズ×2.5 + 1GB必要）
- `data\downloads\` と `data\temp\` の古いファイルを削除

#### 4. 処理システム連携エラー
```
⚠️ 外部処理システムが見つかりません
```
**解決方法:**
- 処理システムのパス設定を確認
- `config.json` の `sync_processing.processor_path` を確認
- 外部システムが正常にインストールされているか確認

#### 5. ネットワークエラー
```
❌ Google Drive API エラー
```
**解決方法:**
- インターネット接続を確認
- しばらく待ってから再実行
- `data\error_flag.txt` を削除してリセット

### 手動での問題解決

#### エラーフラグのクリア
```bash
# エラーフラグファイルを削除
del data\error_flag.txt
```

#### 状態のリセット
```bash
# 監視状態をリセット
del data\page_token.txt
del data\last_run.txt
```

#### 強制的な再認証
```bash
# 認証トークンを削除（次回実行時に再認証）
del data\token.pickle
```

## 📈 システム監視と運用

### 日常的な確認（週1回程度）

#### 1. 処理結果の確認
- `data\results\` に新しいファイルがあるか
- ファイル名の日付が最新か

#### 2. ログの確認
- `logs\autosync_YYYYMMDD.log` でエラーがないか
- ファイル処理の成功・失敗状況

#### 3. ディスク容量の確認
- 十分な空き容量があるか
- 不要なファイルがないか

### 定期メンテナンス（月1回程度）

#### 1. 古いファイルのクリーンアップ
```bash
# 古いログファイル削除（30日以上前）
# 古いダウンロードファイル削除（容量節約）
# 古い処理結果のアーカイブ
```

#### 2. システム状態の確認
```bash
# 全体診断実行
python scripts\diagnose_drive.py

# 既存ファイル再チェック
python scripts\process_existing_files.py
```

## 🔧 設定のカスタマイズ

### 監視間隔の調整
```json
{
  "monitoring": {
    "check_interval_seconds": 60  // 60秒間隔に変更
  }
}
```

### ダウンロード性能の調整
```json
{
  "file_processing": {
    "chunk_size_mb": 10,  // 10MBチャンクで高速化
    "min_free_space_gb": 2  // 安全マージンを2GBに
  }
}
```

### 外部処理システムの設定
```json
{
  "sync_processing": {
    "processor_path": "../Your-Analysis-System/src/analyze.py",
    "processor_args": ["--config", "config.json", "--verbose"],
    "timeout_seconds": 600
  }
}
```

### ログレベルの変更
```json
{
  "logging": {
    "level": "DEBUG",  // より詳細なログ
    "max_log_files": 60  // 60日分保持
  }
}
```

## 🚀 拡張・連携例

### BirdNET音声解析システムとの連携
```bash
# BirdNET-AudioAnalyzerとの統合例
Google-Drive-AutoSync + BirdNET-AudioAnalyzer
→ 鳥類音声の自動識別システム
```

### 将来の拡張可能性
- 📄 **文書OCR処理**: Google-Drive-AutoSync + Document-OCR-Engine
- 🖼️ **画像分類システム**: Google-Drive-AutoSync + Image-Classification-AI
- 🎵 **音楽分析**: Google-Drive-AutoSync + Music-Genre-Classifier
- 📊 **データ解析**: Google-Drive-AutoSync + Data-Analysis-Pipeline

## 📚 ドキュメント一覧

### 🛠️ **セットアップ・設定**
- 🔧 [Task Scheduler設定ガイド](docs/TASK_SCHEDULER_SETUP.md) - Windows自動実行の設定手順
- ⚙️ [実行ファイル使い分けガイド](docs/EXECUTION_GUIDE.md) - スクリプトの選び方と使用方法

### 📋 **運用・保守**
- 🛡️ [運用ガイド](docs/OPERATION_GUIDE.md) - 日常運用とメンテナンス手順
- 📁 [ファイル構成詳細](docs/FILE_STRUCTURE.md) - プロジェクトのファイル構成と重要度

### 🔗 **クイックアクセス**

| 目的 | ドキュメント | 内容 |
|------|------------|------|
| **初回設定** | [Task Scheduler設定](docs/TASK_SCHEDULER_SETUP.md) | 自動実行の設定 |
| **手動テスト** | [実行ファイルガイド](docs/EXECUTION_GUIDE.md) | スクリプトの使い分け |
| **トラブル解決** | [運用ガイド](docs/OPERATION_GUIDE.md) | エラー対応、メンテナンス |
| **ファイル管理** | [ファイル構成](docs/FILE_STRUCTURE.md) | どのファイルを削除していいか |

---

## 🤝 サポート・開発情報

### 問題報告時に含める情報
- エラーログの内容（`logs\autosync_YYYYMMDD.log`）
- 設定ファイルの内容（認証情報は除く）
- 実行環境の詳細（Windows版、Python版など）

### 開発者向け情報
- **汎用設計**: 様々な処理システムとの連携に対応
- **モジュラー構造**: 理解しやすいコンポーネント分離
- **設定駆動**: 動作をJSONで柔軟に制御
- **拡張性**: 新しい処理システムの追加が容易

---

*Google Driveを起点とした自動ファイル処理の汎用基盤システム*
