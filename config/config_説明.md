## 各設定項目の詳細

### google_drive セクション
Google Drive APIとの連携に関する設定

| 項目 | 説明 | 設定例 |
|------|------|--------|
| `target_folder_id` | 監視対象のGoogle DriveフォルダID<br/>（URLの最後の部分を指定）| `"17E1enGLVkaT2iogeZRyQ1cg7hnIlPDXI"` |
| `credentials_file` | Google Drive API認証情報ファイル<br/>（Google Cloud Consoleからダウンロード） | `"credentials.json"` |
| `token_file` | OAuth認証トークンファイル<br/>（自動生成される） | `"token.pickle"` |
| `page_token_file` | 変更監視のページトークンファイル<br/>（自動生成される） | `"page_token.txt"` |

フォルダIDの取得方法:
1. Google Driveで対象フォルダを開く
2. URLの最後の部分がフォルダID
3. 例: `https://drive.google.com/drive/folders/1AbC2dEf3GhI4jKl` → `1AbC2dEf3GhI4jKl`

### file_processing セクション
ファイルのダウンロードに関する設定

| 項目 | 説明 | 設定例 | 推奨値 |
|------|------|--------|--------|
| `download_path` | ダウンロード先フォルダパス（絶対パス推奨） | `"D:/Documents/Google-Drive-AutoSync/data/downloads"` | 十分な容量のあるドライブ |
| `chunk_size_mb` | ダウンロード時のチャンクサイズ（MB）。大きいほど高速だが、メモリ使用量も増加 | `5` | 5-10MB（通常） |
| `min_free_space_gb` | 最小空き容量要件（GB）。この容量を下回るとダウンロードを停止 | `1` | 1-2GB（安全マージン） |

### logging セクション
ログ出力に関する設定

| 項目 | 説明 | 設定例 | 選択肢 |
|------|------|--------|--------|
| `level` | ログレベル | `"INFO"` | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `max_log_files` | 保持するログファイル数（日数） | `30` | 7-60日 |
| `log_rotation_mb` | ログローテーションサイズ（MB） | `10` | 5-50MB |

## カスタマイズ例

### 高速化設定
```json
{
  "file_processing": {
    "chunk_size_mb": 10,
    "min_free_space_gb": 2
  }
}
```

### 詳細ログ設定
```json
{
  "logging": {
    "level": "DEBUG",
    "max_log_files": 60,
    "log_rotation_mb": 20
  }
}
```

## 注意事項

1. **JSONフォーマット**: コメントは使用できません
2. **パス指定**: Windowsでは`/`または`\\`を使用
3. **文字エンコード**: UTF-8で保存してください
4. **権限**: フォルダへの読み書き権限が必要
5. **容量**: ダウンロード先に十分な空き容量を確保

## 設定変更後の手順

1. config.jsonを保存
2. テスト実行で動作確認

```bash
python test.py
```