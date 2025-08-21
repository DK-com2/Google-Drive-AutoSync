# Google-Drive-AutoSync

Google Driveに新しくアップロードされたファイルを自動的にダウンロードするシステム

## このシステムでできること

- Google Driveの指定したフォルダを監視
- 新しくアップロードされた音声・動画ファイルを自動検出
- ファイルを安全にパソコンにダウンロード
- 重複ダウンロードを防止
- 定期実行で完全自動化

## 必要なもの

- Windows 10/11
- Python 3.8以上
- Google アカウント
- 十分なディスク容量（1GB以上推奨）

## セットアップ手順

### 1. Google Drive API の設定

#### Google Cloud Console での作業
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成
3. 「APIとサービス」→「ライブラリ」から「Google Drive API」を検索して有効化

#### 認証情報の作成
1. 「APIとサービス」→「認証情報」
2. 「認証情報を作成」→「OAuth クライアント ID」
3. アプリケーションの種類：「デスクトップアプリケーション」
4. 作成後、`credentials.json` をダウンロード
5. ダウンロードした `credentials.json` を `config` フォルダに配置

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
    "target_folder_id": "ここにフォルダIDを入力"
  }
}
```

### 3. Python環境の準備

#### 仮想環境の作成（推奨）
```
python -m venv venv
venv\Scripts\activate
```

#### 必要なライブラリのインストール
```
pip install -r requirements.txt
```

### 4. 動作テスト

```
python test.py
```

このコマンドで以下がチェックされます：
- 設定ファイルが正しいか
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
| 名前 | Google Drive AutoSync |
| トリガー | 毎日 |
| 開始時刻 | 08:00（お好みで変更） |
| 間隔 | 30分ごとに繰り返す |
| 継続時間 | 4時間 |
| 操作 | プログラムの開始 |
| プログラム | `main.bat` |
| 開始場所 | プロジェクトフォルダのパス |

`main.bat`を使用することで、Pythonのパスや仮想環境の設定を気にする必要がありません。

## ファイルの確認方法

### ダウンロードされたファイル
```
data\downloads\
├── 音楽ファイル1.mp3
├── 動画ファイル1.mp4
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

詳細は `config\config_説明.md` を参照してください。

## よくある問題と解決方法

### 認証エラーが出る
- `credentials.json` が正しい場所にあるか確認
- Google Cloud Console で API が有効になっているか確認

### ファイルが検出されない
- フォルダ ID が正しいか確認
- フォルダへのアクセス権限があるか確認
- 対象ファイルが音声・動画形式か確認（.mp3, .mp4, .wav など）

### ディスク容量不足
- ダウンロード先ドライブに十分な空き容量を確保
- 古いファイルを削除

### Google Drive からファイルが削除されない
これは正常な動作です。権限の関係でファイルを削除できない場合があります。必要に応じて手動で削除してください。

## プロジェクト構成

```
Google-Drive-AutoSync\
├── main.py              # メインプログラム
├── main.bat             # 実行用バッチファイル（Windowsで簡単実行）
├── test.py              # テスト・診断ツール
├── config\              # 設定ファイル
├── data\                # ダウンロードファイル保存場所
├── logs\                # ログファイル
└── src\                 # プログラムの部品
```

## サポート

問題が発生した場合：
1. ログファイル（`logs` フォルダ）を確認
2. `python test.py` で診断を実行
3. 設定ファイルを確認

*Google Drive の自動ファイル取得システム*