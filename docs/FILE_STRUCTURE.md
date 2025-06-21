# Google-Drive-AutoSync - ファイル構成詳細

## 📁 現在の実装ファイル構成

### **🔧 コアシステム（変更・削除禁止）**
```
├── src/                        
│   ├── main.py                 # メインエントリーポイント（Task Scheduler実行）
│   ├── drive_monitor.py        # Google Drive監視エンジン（Changes API）
│   └── file_processor.py       # ファイル処理・外部システム連携
│
├── config/
│   ├── config.json             # システム設定（フォルダID、処理設定）
│   └── credentials.json        # Google認証ファイル（機密）
│
├── requirements.txt            # Python依存関係
├── README.md                   # システム説明
└── .gitignore                  # Git除外設定
```

### **🚀 実行スクリプト**
```
scripts/
├── run_sync.bat                # Windows自動実行（サイレント）
├── run_sync.ps1                # PowerShell自動実行（サイレント）
├── test_manual_run.bat         # 手動テスト実行（詳細表示）
├── test_manual_run.ps1         # PowerShell手動テスト（詳細表示）
├── test_setup.py               # 設定テスト・診断
├── process_existing_files.py   # 既存ファイル一括処理
├── diagnose_drive.py           # Google Drive診断ツール
├── check_environment.py        # 環境確認ツール
├── reset_environment.bat       # 環境リセット（バッチ）
├── reset_environment.ps1       # 環境リセット（PowerShell）
├── setup_task_scheduler.ps1    # Task Scheduler自動設定
├── task_scheduler_bat.xml      # Task Scheduler設定（バッチ用）
├── task_scheduler_ps1.xml      # Task Scheduler設定（PowerShell用）
└── test_1min_30min.xml         # テスト用（1分間隔）
```

### **📊 データ・状態管理（自動生成・更新）**
```
data/
├── downloads/                  # ダウンロードファイル
│   ├── 04 Famous Day.mp3       # 処理済みファイル
│   └── 05 Adventure.mp3        # 処理済みファイル
│
├── results/                    # 処理結果JSON
│   ├── sync_result_20250620_222912_05 Adventure.json
│   ├── sync_result_20250620_222916_04 Famous Day.json
│   └── [日付]_[時刻]_[ファイル名].json
│
├── temp/                       # 一時ファイル（通常は空）
│   └── [ファイル名].downloading # ダウンロード中の一時ファイル
│
├── token.pickle                # Google認証トークン（自動生成）
├── page_token.txt              # 監視位置（自動更新）
├── processed_files.txt         # 処理済みファイルID（自動更新）
├── last_run.txt               # 最終実行時刻（自動更新）
└── error_flag.txt             # エラー状態（エラー時のみ作成）
```

### **📝 ログ・ドキュメント**
```
├── logs/                       # 実行ログ（日付別）
│   ├── autosync_20250620.log   # 当日のログ
│   ├── autosync_20250619.log   # 前日のログ
│   └── autosync_[YYYYMMDD].log # 日付別ログファイル
│
├── docs/                       # 追加ドキュメント
│   └── installation.md        # インストール手順（参考）
│
├── tests/                      # テストコード（開発用）
│   └── test_basic.py          # 基本テスト
│
├── EXECUTION_GUIDE.md          # 実行方法ガイド
├── OPERATION_GUIDE.md          # 運用ガイド
├── FILE_STRUCTURE.md           # ファイル構成説明（このファイル）
└── TASK_SCHEDULER_SETUP.md     # Task Scheduler設定ガイド
```

### **🔧 開発・仮想環境**
```
├── venv/                       # Python仮想環境（削除禁止）
│   ├── Lib/site-packages/      # インストール済みパッケージ
│   ├── Scripts/                # 実行ファイル
│   └── Include/                # ヘッダーファイル
│
└── src/__pycache__/            # Python一時ファイル（削除可能）
    ├── drive_monitor.cpython-310.pyc
    └── file_processor.cpython-310.pyc
```

## 🎯 **ファイル分類と重要度**

### **🔴 絶対削除禁止（システム停止）**
```
src/main.py                     # メインプログラム
src/drive_monitor.py            # Google Drive監視
src/file_processor.py           # ファイル処理
config/config.json              # システム設定
config/credentials.json         # Google認証（機密）
requirements.txt                # 依存関係
venv/ (全体)                    # Python仮想環境
```

### **🟠 削除注意（データ消失リスク）**
```
data/token.pickle               # 認証トークン（削除すると再認証必要）
data/processed_files.txt        # 処理済みリスト（削除すると重複処理）
data/page_token.txt            # 監視位置（削除すると全ファイル再チェック）
data/results/                   # 処理結果（バックアップ後なら削除可能）
```

### **🟡 削除可能（容量節約）**
```
data/downloads/                 # ダウンロードファイル（容量が必要な場合）
logs/ (古いファイル)             # 30日以上前のログ
data/temp/                     # 一時ファイル（通常は自動削除）
src/__pycache__/               # Python一時ファイル
```

### **🟢 削除推奨（不要ファイル）**
```
scripts/archive/               # アーカイブファイル（開発用）
    ├── create_test_audio.py   # テスト音声作成
    ├── debug_file_check.py    # デバッグ用
    ├── run_pipeline.bat       # 旧版バッチファイル
    └── run_pipeline.ps1       # 旧版PowerShellファイル
```

## 🔄 **ファイルの自動生成・更新タイミング**

### **初回実行時に自動作成**
```
data/token.pickle              # Google認証時に作成
data/page_token.txt           # 初回監視時に作成
data/processed_files.txt      # 初回処理時に作成
data/last_run.txt            # 初回実行時に作成
logs/autosync_[今日の日付].log  # 日次で新規作成
```

### **ファイル処理時に更新**
```
data/processed_files.txt      # 新規ファイル処理後に追記
data/last_run.txt            # 毎回実行後に更新
data/page_token.txt          # Google Drive監視後に更新
```

### **エラー時に作成**
```
data/error_flag.txt           # エラー発生時のみ作成
```

## 📊 **容量使用状況の目安**

### **システムファイル**
```
src/ + config/ + scripts/      # 約500KB
venv/                          # 約50MB
docs/ + tests/                 # 約100KB
requirements.txt等             # 約10KB
```

### **データファイル**
```
data/downloads/                # ファイルサイズに依存（例: 10MB/ファイル）
data/results/                  # 1-2KB/処理結果
logs/                          # 50-100KB/日
その他状態ファイル             # 数KB
```

### **推奨ディスク容量**
```
最小システム: 100MB
通常運用: 500MB
大量処理: 2GB以上
```

## 🧹 **定期メンテナンス対象**

### **週次クリーンアップ（自動化推奨）**
```bash
# 古いログファイル確認
dir logs\ | findstr /v %date:~0,4%%date:~5,2%%date:~8,2%

# ディスク使用量確認
dir data\downloads\ | find /c ".*"
```

### **月次クリーンアップ**
```bash
# 30日以上前のログ削除
forfiles /p logs /s /m *.log /d -30 /c "cmd /c del @path"

# 古い処理結果のアーカイブ（オプション）
# 古いダウンロードファイルの削除（容量節約時）
```

### **年次メンテナンス**
```bash
# 処理結果の年次バックアップ
# 設定ファイルのバックアップ
# システム全体の動作確認
```

## 🎯 **運用環境での推奨ファイル管理**

### **バックアップ対象**
```
重要度1: config/config.json      # 設定
重要度2: data/results/            # 処理結果
重要度3: data/processed_files.txt # 処理履歴
```

### **監視対象**
```
data/error_flag.txt               # エラー監視
logs/autosync_[今日].log          # 動作監視
data/downloads/ (容量)            # ディスク容量監視
```

### **アクセス権限設定**
```
config/credentials.json          # 読み取り専用推奨
data/ (全体)                     # 読み書き必要
logs/                            # 読み書き必要
src/                             # 読み取り専用
```

## 🔄 **リポジトリ名変更に伴う更新箇所**

### **更新済みファイル**
```
README.md                        # プロジェクト名・説明を更新
FILE_STRUCTURE.md               # このファイル - 全体的に名前統一
```

### **今後更新が必要なファイル**
```
src/main.py                     # ログ出力のプロジェクト名
scripts/*.bat                   # バッチファイルのコメント
scripts/*.ps1                   # PowerShellスクリプトのコメント
scripts/*.xml                   # Task Scheduler設定の表示名
config/config.json              # 必要に応じてパス設定
EXECUTION_GUIDE.md              # 実行方法ガイド
OPERATION_GUIDE.md              # 運用ガイド
TASK_SCHEDULER_SETUP.md         # Task Scheduler設定ガイド
```

### **設定ファイルの推奨更新**
```json
// config/config.json の推奨更新
{
  "system_info": {
    "name": "Google-Drive-AutoSync",
    "version": "2.0.0",
    "description": "Google Driveファイル自動同期システム"
  },
  "file_processing": {
    "download_path": "S:/python/Google-Drive-AutoSync/data/downloads"
  }
}
```

## 🎯 **汎用化対応のファイル構成**

### **将来の拡張を考慮した設計**
```
├── processors/                 # 将来: 外部処理システム設定
│   ├── birdnet_config.json     # BirdNET用設定
│   ├── ocr_config.json         # OCR用設定（将来）
│   └── image_config.json       # 画像処理用設定（将来）
│
├── templates/                  # 将来: 設定テンプレート
│   ├── audio_analysis.json     # 音声解析用テンプレート
│   ├── document_processing.json # 文書処理用テンプレート
│   └── image_processing.json   # 画像処理用テンプレート
```

### **現在の単純構成維持**
現時点では上記の拡張構成は**実装しない**：
- ✅ YAGNI原則に従う
- ✅ 現在の単純構成を維持
- ✅ 必要になった時点で検討

---

**🎉 Google-Drive-AutoSyncとして整理完了！汎用的で拡張しやすい構成になりました**

---
