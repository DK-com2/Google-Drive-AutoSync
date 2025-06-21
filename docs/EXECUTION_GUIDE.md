# Google-Drive-AutoSync - 実行ファイル使い分けガイド

## 📁 **ファイル構成と用途**

### **🔄 自動実行用（Task Scheduler）**
```
scripts/
├── run_sync.bat               # バッチファイル（サイレント実行）
├── run_sync.ps1               # PowerShell（サイレント実行）
├── task_scheduler_bat.xml     # バッチ用XML設定
└── task_scheduler_ps1.xml     # PowerShell用XML設定
```

**特徴:**
- ✅ **出力なし**（サイレント実行）
- ✅ **自動で閉じる**（pauseなし）
- ✅ **Task Scheduler専用**
- ✅ **ログファイルに記録**

---

### **🧪 手動テスト用**
```
scripts/
├── test_manual_run.bat        # バッチファイル（詳細表示）
├── test_manual_run.ps1        # PowerShell（詳細表示）
└── test_1min_30min.xml        # 1分間隔テスト用XML
```

**特徴:**
- ✅ **詳細な出力表示**
- ✅ **結果確認待ち**（pause付き）
- ✅ **手動実行専用**
- ✅ **エラー詳細表示**

---

### **🔍 診断・メンテナンス用**
```
scripts/
├── diagnose_drive.py          # Google Drive診断
├── process_existing_files.py  # 既存ファイル処理
└── test_setup.py              # 設定テスト
```

## 🎯 **使用場面別の実行方法**

### **日常の自動運用**
```
Task Scheduler設定:
→ task_scheduler_bat.xml または task_scheduler_ps1.xml

実行内容:
→ run_sync.bat または run_sync.ps1（サイレント）
```

### **手動での動作確認**
```
バッチファイル:
→ scripts\test_manual_run.bat をダブルクリック

PowerShell:
→ scripts\test_manual_run.ps1 を右クリック→PowerShellで実行
```

### **XMLテスト（1分間隔）**
```
Task Scheduler:
→ test_1min_30min.xml をインポート
→ 30分間、1分ごとに自動実行（サイレント）
```

### **問題診断**
```
# 設定確認
python scripts\test_setup.py

# Google Drive確認
python scripts\diagnose_drive.py

# 既存ファイル処理
python scripts\process_existing_files.py
```

## 📊 **実行方法の比較**

| 用途 | ファイル | 出力表示 | 自動終了 | 使用場面 |
|------|----------|----------|----------|----------|
| **自動実行** | `run_sync.bat/ps1` | なし | はい | Task Scheduler |
| **手動テスト** | `test_manual_run.bat/ps1` | あり | pauseあり | 動作確認 |
| **診断** | `diagnose_drive.py` | あり | pauseあり | 問題調査 |

## 🚀 **推奨使用方法**

### **初回設定時**
```
1. python scripts\test_setup.py          # 設定確認
2. scripts\test_manual_run.bat            # 手動テスト
3. task_scheduler_bat.xml インポート      # 自動実行設定
```

### **日常運用**
```
Task Scheduler → 自動実行（サイレント）
結果確認 → data\results\ フォルダ
```

### **問題発生時**
```
1. scripts\test_manual_run.bat            # 手動実行で詳細確認
2. python scripts\diagnose_drive.py       # 診断実行
3. data\error_flag.txt 確認               # エラー詳細
```

## 🔄 **リポジトリ名変更による更新**

### **スクリプト名変更**
- `run_pipeline.bat` → `run_sync.bat`
- `run_pipeline.ps1` → `run_sync.ps1`

### **パス更新**
すべてのスクリプトで以下のパス更新：
```
旧: S:\python\BirdNET-AutoPipeline
新: S:\python\Google-Drive-AutoSync
```

### **Task Scheduler設定名**
```
旧: BirdNET AutoPipeline
新: Google Drive AutoSync
```

---

**🎯 これで自動実行は完全にサイレント、手動実行は詳細表示と使い分けが完璧になりました！**

---
