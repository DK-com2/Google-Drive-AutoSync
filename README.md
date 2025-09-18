# Google-Drive-AutoSync（PyDrive2版）

PyDrive2を使用したシンプルで効率的なGoogle Driveファイル自動同期システム

## このシステムでできること

- Google Driveの指定したフォルダを監視
- 新しくアップロードされた音声ファイルを自動検出
- ファイルを安全にパソコンにダウンロード
- 重複ダウンロードを防止
- 定期実行で完全自動化
- PyDrive2による簡素化された認証システム

## 必要なもの

- Windows 10/11
- Python 3.8以上
- Google アカウント
- 十分なディスク容量（1GB以上推奨）

## PyDrive2移行の利点

### 🔧 認証の簡素化
- **旧版**: credentials.json + token.pickle + page_token.txt
- **新版**: client_secrets.json + credentials.json のみ

### 📝 コード量の削減
- **旧版**: 複雑なGoogle API Client設定
- **新版**: PyDrive2のシンプルなAPI

### 🔄 自動リフレッシュ
- PyDrive2が認証トークンを自動更新
- より安定した長期運用

## セットアップ手順

### 1. Google Drive API の設定

#### Google Cloud Console での作業
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成
3. 「APIとサービス」→「ライブラリ」から「Google Drive API」を検索して有効化

#### 認証情報の作成（PyDrive2版）
1. 「APIとサービス」→「認証情報」
2. 「認証情報を作成」→「OAuth クライアント ID」
3. アプリケーションの種類：「デスクトップアプリケーション」
4. 作成後、JSONファイルをダウンロード
5. **重要**: ダウンロードしたファイルを `client_secrets.json` にリネーム
6. `client_secrets.json` を `config` フォルダに配置

### 2. 監視するフォルダの設定

#### Google Drive フォルダ ID の取得
1. Google Drive で監視したいフォルダを開く
2. ブラウザのアドレスバーから URL をコピー
3. URL の最後の部分がフォルダ ID
   - 例: `https://drive.google.com/drive/folders/1AbC2dEf3GhI4jKl`
   - フォルダ ID: `1AbC2dEf3GhI4jKl`

#### 設定ファイルの編集
1. `config\config.json` を開く
2. `target_folder_id` の値を取得したフォルダ ID に変更

```json
{
  "google_drive": {
    "target_folder_id": "ここにフォルダIDを入力",
    "client_secrets_file": "client_secrets.json",
    "credentials_file": "credentials.json"
  },
  "file_processing": {
    "download_path": "D:/Documents/Google-Drive-AutoSync/data/downloads",
    "chunk_size_mb": 5,
    "min_free_space_gb": 1
  },
  "logging": {
    "level": "INFO",
    "max_log_files": 30,
    "log_rotation_mb": 10
  }
}
```

### 3. Python環境の準備

#### 仮想環境の作成（推奨）
```
python -m venv venv
venv\Scripts\activate
```

#### PyDrive2のインストール
```
pip install -r requirements.txt
```

**requirements.txt の内容（PyDrive2版）**:
```
PyDrive2>=1.17.0
requests>=2.31.0
```

### 4. 動作テスト

```
python test.py
```

このコマンドで以下がチェックされます：
- PyDrive2ライブラリが正しくインストールされているか
- client_secrets.jsonが配置されているか
- Google Drive に接続できるか
- フォルダにアクセスできるか
- 必要なフォルダが作成されているか

初回実行時は、ブラウザが開いて Google アカウントでの認証が必要です。

## 使用方法

### 手動で1回だけ実行

#### 方法1: バッチファイルを使用（簡単）
```
main.bat
```

#### 方法2: Pythonコマンドを直接使用
```
python main.py
```

### 自動実行の設定（Windows Task Scheduler）

毎日決まった時間に自動実行するには：

1. Windows の「タスク スケジューラ」を開く
2. 「基本タスクの作成」を選択
3. 以下のように設定：

| 項目 | 設定値 |
|------|--------|
| 名前 | Google Drive AutoSync (PyDrive2) |
| トリガー | 毎日 |
| 開始時刻 | 08:00（お好みで変更） |
| 間隔 | 30分ごとに繰り返す |
| 継続時間 | 4時間 |
| 操作 | プログラムの開始 |
| プログラム | `main.bat` |
| 開始場所 | プロジェクトフォルダのパス |

## ファイルの確認方法

### ダウンロードされたファイル
```
data\downloads\
├── 音楽ファイル1.mp3
├── 音楽ファイル2.wav
├── 音楽ファイル3.flac
└── ...
```

### ログファイル
```
logs\
└── autosync_20241221.log
```

ログファイルで処理の成功・失敗を確認できます。

## 設定のカスタマイズ

`config\config.json` で以下を調整できます：

### ダウンロード先の変更
```json
{
  "file_processing": {
    "download_path": "C:/Users/あなたの名前/Documents/Downloads"
  }
}
```

### ダウンロード速度の調整
```json
{
  "file_processing": {
    "chunk_size_mb": 10
  }
}
```


## よくある問題と解決方法

### PyDrive2認証エラーが出る
- `client_secrets.json` が正しい場所にあるか確認
- Google Cloud Console で Google Drive API が有効になっているか確認
- 初回認証でブラウザが開かない場合は手動で認証URLにアクセス

### ファイルが検出されない
- フォルダ ID が正しいか確認
- フォルダへのアクセス権限があるか確認
- 対象ファイルが音声形式か確認（.wav, .mp3, .flac, .aac）

### "client_secrets.json not found" エラー
- Google Cloud Consoleからダウンロードしたファイルが正しい名前でconfig/フォルダに配置されているか確認

### ディスク容量不足
- ダウンロード先ドライブに十分な空き容量を確保
- 古いファイルを削除

### PyDrive2のリフレッシュトークンエラー
- `config/credentials.json` を削除して再認証
- Google Cloud Consoleでプロジェクトの認証設定を確認

## プロジェクト構成（PyDrive2版）

```
Google-Drive-AutoSync\
├── main.py              # メインプログラム（PyDrive2対応）
├── main.bat             # 実行用バッチファイル
├── test.py              # テスト・診断ツール（PyDrive2対応）
├── requirements.txt     # PyDrive2依存関係
├── config\
│   ├── config.json      # 設定ファイル（簡素化）
│   ├── client_secrets.json # Google認証情報（PyDrive2）
│   └── credentials.json # 自動生成認証キャッシュ
├── data\                # ダウンロードファイル保存場所
├── logs\                # ログファイル
└── src\                 # PyDrive2対応プログラム
    ├── drive_monitor.py # PyDrive2監視モジュール
    └── file_processor.py # PyDrive2処理モジュール
```

## サポート

問題が発生した場合：
1. ログファイル（`logs` フォルダ）を確認
2. `python test.py` で診断を実行（PyDrive2対応版）
3. 設定ファイルを確認
4. PyDrive2のドキュメントを参照: https://github.com/iterative/PyDrive2

## 更新履歴

### v2.0.0 (Current - PyDrive2版)
- PyDrive2による簡素化された認証システム
- 自動リフレッシュトークンによる長期安定運用
- コード量の大幅削減とエラーハンドリング改善

---

*PyDrive2による効率的なGoogle Drive自動同期システム*