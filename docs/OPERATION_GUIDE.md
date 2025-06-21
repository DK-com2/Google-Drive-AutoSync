# Google-Drive-AutoSync 運用ガイド

## 🎯 システム概要

**完成したシステム**: 任意デバイス → Google Drive → 自動同期・処理・保存

## 📂 重要なファイル・フォルダ

### **🔧 必須ファイル（変更・削除禁止）**
```
├── src/                        # メインプログラム
│   ├── main.py                 # 日常運用スクリプト
│   ├── drive_monitor.py        # Google Drive監視
│   └── file_processor.py       # ファイル処理
├── config/
│   ├── config.json             # システム設定
│   └── credentials.json        # Google認証（機密）
├── data/
│   ├── token.pickle            # 認証トークン（自動生成）
│   ├── page_token.txt          # 監視位置（自動更新）
│   ├── processed_files.txt     # 処理済みリスト（自動更新）
│   └── last_run.txt           # 最終実行時刻（自動更新）
├── requirements.txt            # Python依存関係
└── README.md                   # システム説明書
```

### **📁 データフォルダ**
```
data/
├── downloads/          # ダウンロードされたファイル
├── results/            # 処理結果JSON
├── temp/               # 一時ファイル（空でOK）
└── logs/               # ログファイル
```

### **🛠️ 便利スクリプト（保持推奨）**
```
scripts/
├── run_sync.bat                # Windows実行用
├── run_sync.ps1                # PowerShell実行用
├── test_setup.py               # 設定テスト
├── process_existing_files.py   # 初回・メンテナンス用
└── diagnose_drive.py           # 診断用
```

## 🚀 **正常運用フロー**

### **Phase 1: 日常の自動運用**

#### **1. Windows Task Scheduler設定**
```
タスク名: Google Drive AutoSync
実行: 毎日 08:00-12:00
間隔: 30分ごと
実行内容: S:\python\Google-Drive-AutoSync\scripts\run_sync.bat
```

#### **2. 自動監視の動作**
```
08:00 → main.py実行 → 新しいファイルチェック
08:30 → main.py実行 → 新しいファイルチェック
09:00 → main.py実行 → 新しいファイルチェック
...
12:00 → 監視終了

新しいファイルがあれば:
→ 自動ダウンロード → 処理 → 結果保存
```

### **Phase 2: 結果確認（週1回程度）**

#### **1. 処理結果確認**
```bash
# 最新の処理結果を確認
dir data\results\

# 例:
sync_result_20250620_214825_02 Boo!.json
sync_result_20250620_214939_03 ワンテンポ遅れたMonster ain't dead.json
```

#### **2. ダウンロードファイル確認**
```bash
# ダウンロードされたファイル確認
dir data\downloads\

# 例:
01 ワタリドリ.mp3
02 Boo!.mp3
03 ワンテンポ遅れたMonster ain't dead.mp3
```

### **Phase 3: メンテナンス（月1回程度）**

#### **1. 全体チェック**
```bash
# 処理漏れがないか確認
python scripts\process_existing_files.py
```

#### **2. ログ確認**
```bash
# エラーログ確認
type data\error_flag.txt    # エラーがあれば表示

# 実行ログ確認（最新）
dir logs\ | sort /r | head -5
```

## 🗑️ **削除可能なファイル**

### **🟡 削除推奨（デバッグ用）**
```
scripts/
├── create_test_audio.py        # テスト音声作成
├── debug_file_check.py         # デバッグ用
└── config_template.json       # テンプレート
```

### **🟠 削除可能（開発用）**
```
tests/                          # テストコード
docs/installation.md           # インストール手順（完了済み）
src/__pycache__/               # Python一時ファイル
```

### **🔴 削除禁止**
```
venv/                          # Python仮想環境
config/credentials.json        # Google認証（機密）
data/token.pickle             # 認証トークン
data/processed_files.txt      # 処理済みリスト
```

## ⚙️ **トラブル時の対処**

### **問題1: ファイルが処理されない**
```bash
# 診断実行
python scripts\diagnose_drive.py

# 手動処理
python scripts\process_existing_files.py
```

### **問題2: エラーが発生**
```bash
# エラー内容確認
type data\error_flag.txt

# エラーリセット
del data\error_flag.txt
```

### **問題3: システムリセット**
```bash
# 監視位置リセット
del data\page_token.txt

# 処理済みリストリセット
del data\processed_files.txt
```

## 📊 **システム状況の確認方法**

### **正常運用の確認**
```
✅ data\results\ に新しいJSONファイルがある
✅ data\downloads\ にダウンロードファイルがある  
✅ data\error_flag.txt が存在しない
✅ ログにエラーがない
```

### **異常時の兆候**
```
❌ 数日間新しい結果ファイルがない
❌ data\error_flag.txt が存在する
❌ ログにERRORが記録されている
❌ Task Schedulerが実行されていない
```

## 🎯 **効率的な運用のコツ**

### **1. 定期確認の自動化**
```bash
# 週次確認スクリプト（例）
@echo off
echo === Google Drive AutoSync システム状況確認 ===
echo.
echo 📁 最新の処理結果:
dir data\results\ | tail -5
echo.
echo 📁 ダウンロードファイル数:
dir data\downloads\ | find /c ".*"
echo.
echo ⚠️ エラー確認:
if exist data\error_flag.txt (
    echo エラーあり:
    type data\error_flag.txt
) else (
    echo エラーなし
)
```

### **2. バックアップ戦略**
```
重要データのバックアップ:
1. data\results\ → 処理結果（最重要）
2. config\config.json → 設定
3. data\processed_files.txt → 処理済みリスト

月1回、別の場所にコピー保存
```

### **3. 容量管理**
```
定期的なクリーンアップ:
1. data\downloads\ → 古いダウンロードファイル削除
2. logs\ → 古いログファイル削除
3. data\temp\ → 一時ファイル削除（通常は空）
```

## 🔄 **外部システム連携**

### **BirdNET音声解析との連携例**
```
Google-Drive-AutoSync が新しい音声ファイルを検出
    ↓
BirdNET-AudioAnalyzer で鳥種識別実行
    ↓
結果をdata\results\に保存
```

### **他システムとの連携設定**
```json
// config/config.json の処理システム設定
{
  "sync_processing": {
    "enabled": true,
    "processor_path": "../Your-Analysis-System/src/analyze.py",
    "processor_args": ["--config", "config.json"],
    "timeout_seconds": 300
  }
}
```

## 📈 **運用統計の確認**

### **週次レポート例**
```bash
# 処理統計確認
echo 📊 今週の処理統計:
echo ダウンロードファイル数: $(ls data/downloads/ | wc -l)
echo 処理結果数: $(ls data/results/ | wc -l)
echo 最終実行: $(cat data/last_run.txt)
```

### **パフォーマンス監視**
```
監視項目:
- ディスク使用量
- 処理成功率
- 平均処理時間
- エラー発生頻度
```

## 🛡️ **セキュリティ考慮事項**

### **認証ファイル管理**
```
config/credentials.json     # Google API認証（機密）
data/token.pickle          # アクセストークン（機密）

注意:
- 定期的な認証更新
- ファイル権限の適切な設定
- バックアップ時の除外設定
```

### **ログ情報の管理**
```
logs/autosync_*.log        # 機密情報の確認
- ファイル名は記録されるが内容は記録されない
- API呼び出し情報のみ
- 個人情報は含まれない
```

## 🎯 **将来の拡張予定**

### **対応予定の処理システム**
- 📄 **文書OCR**: PDFや画像からテキスト抽出
- 🖼️ **画像分類**: 写真の自動分類・タグ付け
- 🎵 **音楽解析**: ジャンル分類・特徴抽出
- 📊 **データ変換**: CSV・Excel等の形式変換

### **システム改善計画**
- 🔄 **リアルタイム監視**: Webhook対応
- 📧 **通知機能**: 処理完了・エラー通知
- 🌐 **Web UI**: ブラウザでの状態確認
- 📱 **モバイル対応**: スマートフォンでの操作

---

**🎉 完全自動化システムの運用準備完了！**

---
