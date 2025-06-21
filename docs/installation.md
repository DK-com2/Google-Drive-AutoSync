# BirdNET AutoPipeline インストールガイド

## 📋 前提条件

### システム要件
- **OS**: Windows 10/11
- **Python**: 3.8以上
- **ディスク容量**: 1GB以上の空き容量
- **メモリ**: 4GB以上のRAM
- **ネットワーク**: インターネット接続

### アカウント要件
- Google アカウント
- Google Drive ストレージ

## 🚀 インストール手順

### Step 1: Python環境の確認

```bash
# Pythonバージョン確認
python --version

# 3.8以上であることを確認
# 例: Python 3.9.7
```

### Step 2: 必要パッケージのインストール

```bash
# プロジェクトディレクトリに移動
cd S:\python\BirdNET-AutoPipeline

# 必要パッケージをインストール
pip install -r requirements.txt
```

### Step 3: Google Drive API設定

#### 3.1 Google Cloud Consoleでの設定

1. **[Google Cloud Console](https://console.cloud.google.com/) にアクセス**

2. **新しいプロジェクト作成**
   - 「プロジェクトを選択」→「新しいプロジェクト」
   - プロジェクト名: `BirdNET-AutoPipeline`
   - 「作成」をクリック

3. **Google Drive API有効化**
   - 「APIとサービス」→「ライブラリ」
   - 「Google Drive API」を検索
   - 「有効にする」をクリック

4. **OAuth認証情報作成**
   - 「APIとサービス」→「認証情報」
   - 「認証情報を作成」→「OAuth クライアント ID」
   - 「同意画面を設定」（初回のみ）
     - User Type: 外部
     - アプリ名: BirdNET AutoPipeline
     - ユーザーサポートメール: 自分のメール
     - デベロッパーの連絡先情報: 自分のメール
   - 「OAuth クライアント ID」作成
     - アプリケーションの種類: デスクトップアプリケーション
     - 名前: BirdNET AutoPipeline

5. **credentials.jsonダウンロード**
   - 作成したOAuth クライアント IDの「ダウンロード」をクリック
   - ダウンロードしたファイルを `credentials.json` にリネーム
   - `S:\python\BirdNET-AutoPipeline\config\` フォルダに配置

#### 3.2 Google DriveフォルダID取得

1. **Google Driveでフォルダ作成**
   - Google Driveで新しいフォルダを作成
   - 例: `BirdNET-Audio`

2. **フォルダIDの取得**
   - 作成したフォルダを開く
   - アドレスバーのURLを確認
   - 例: `https://drive.google.com/drive/folders/1AbC2dEf3GhI4jKl5MnO`
   - 最後の部分 `1AbC2dEf3GhI4jKl5MnO` がフォルダID

### Step 4: 設定ファイルの編集

`config\config.json` を編集：

```json
{
  "google_drive": {
    "target_folder_id": "YOUR_FOLDER_ID_HERE",  ← 取得したフォルダIDに変更
    "credentials_file": "credentials.json",
    "token_file": "token.pickle",
    "page_token_file": "page_token.txt"
  },
  "file_processing": {
    "download_path": "S:/python/BirdNET-AutoPipeline/data/downloads",
    "chunk_size_mb": 5,
    "min_free_space_gb": 1
  }
}
```

### Step 5: 初回認証

```bash
# 設定テスト実行（初回認証も含む）
python scripts\test_setup.py
```

**初回実行時の流れ:**
1. ブラウザが自動で開く
2. Googleアカウントでログイン
3. BirdNET AutoPipelineに権限を付与
4. 「認証が完了しました」メッセージを確認
5. ブラウザを閉じる

### Step 6: 動作テスト

```bash
# 手動実行テスト
python src\main.py
```

**成功時の出力例:**
```
=== BirdNET AutoPipeline 開始 ===
設定ファイル読み込み完了
Google Drive監視開始
新しいファイルはありません
=== BirdNET AutoPipeline 終了 ===
```

## ⚙️ 自動実行設定（Windows Task Scheduler）

### Task Scheduler設定

1. **Task Schedulerを開く**
   - Windowsキー + R
   - `taskschd.msc` と入力してEnter

2. **基本タスクの作成**
   - 「操作」→「基本タスクの作成」
   - 名前: `BirdNET AutoPipeline`
   - 説明: `自動音声ファイル処理`

3. **トリガー設定**
   - 「毎日」を選択
   - 開始: 今日の日付
   - 開始時刻: `08:00:00`
   - 「詳細設定」をクリック
   - ✅ 「タスクを繰り返す間隔」
   - 間隔: `30分間`
   - 継続時間: `4時間`

4. **操作設定**
   - 「プログラムの開始」を選択
   - プログラム/スクリプト: `S:\python\BirdNET-AutoPipeline\scripts\run_pipeline.bat`
   - 開始: `S:\python\BirdNET-AutoPipeline`

5. **完了**
   - 設定を確認して「完了」

### PowerShell実行ポリシー設定（PowerShell使用時）

```powershell
# PowerShell実行ポリシーを設定
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 🔧 設定のカスタマイズ

### 監視スケジュール調整

| 設定 | 説明 | 推奨値 |
|------|------|--------|
| **開始時刻** | 監視開始時間 | 08:00 |
| **繰り返し間隔** | チェック間隔 | 30分 |
| **継続時間** | 監視時間 | 4時間 |

### ファイルサイズ対応

| ファイルサイズ | チャンクサイズ | 処理時間目安 |
|----------------|----------------|--------------|
| **20-50MB** | 5MB | 2-3分 |
| **50-100MB** | 10MB | 3-5分 |
| **100MB以上** | 15MB | 5-10分 |

## 🛠️ トラブルシューティング

### インストール時の問題

#### 1. pip install エラー
```bash
# pipのアップデート
python -m pip install --upgrade pip

# 再試行
pip install -r requirements.txt
```

#### 2. Python バージョンエラー
```bash
# Python 3.8以上のインストールが必要
# https://www.python.org/downloads/ からダウンロード
```

#### 3. 権限エラー
```bash
# 管理者権限でコマンドプロンプトを開く
# または
pip install --user -r requirements.txt
```

### 認証時の問題

#### 1. ブラウザが開かない
- 手動でブラウザを開く
- 表示されたURLにアクセス
- 認証コードをコピーしてターミナルに貼り付け

#### 2. 権限エラー
- Google Cloud Consoleで同意画面を「公開」に設定
- または信頼できるユーザーとして自分のメールアドレスを追加

### 設定時の問題

#### 1. フォルダIDが見つからない
- Google DriveのURLを再確認
- フォルダが正しく作成されているか確認

#### 2. ファイルパスエラー
- パスの区切り文字を確認（Windows: `\` または `/`）
- 絶対パスで指定

## 📊 インストール確認チェックリスト

### 必須項目
- [ ] Python 3.8以上がインストール済み
- [ ] 必要パッケージがインストール済み（`pip list`で確認）
- [ ] `credentials.json`が正しい場所に配置済み
- [ ] `config.json`のフォルダIDが設定済み
- [ ] 初回認証が完了済み（`token.pickle`ファイル作成済み）
- [ ] テスト実行が成功

### オプション項目  
- [ ] Task Schedulerが設定済み
- [ ] PowerShell実行ポリシーが設定済み（PowerShell使用時）
- [ ] Windows通知が有効
- [ ] 十分なディスク容量の確保

## 🎯 次のステップ

インストールが完了したら：

1. **テスト音声ファイルで動作確認**
   - Google Driveの対象フォルダに音声ファイルをアップロード
   - 手動実行で処理されることを確認

2. **自動実行の確認**
   - Task Schedulerの次回実行時刻を確認
   - ログファイルで正常動作を確認

3. **日常運用**
   - 週1回程度の結果確認
   - 月1回程度のログ確認

---

*正しいインストールで安定した自動化を実現*