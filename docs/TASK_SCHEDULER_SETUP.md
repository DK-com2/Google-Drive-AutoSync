# Google-Drive-AutoSync - Task Scheduler設定ガイド

## 🎯 Task Scheduler自動実行の設定

### **必要なファイル**

```
S:\python\Google-Drive-AutoSync\scripts\
├── run_sync.bat                  # バッチファイル実行用
├── run_sync.ps1                  # PowerShell実行用
├── task_scheduler_bat.xml        # バッチ用XML設定
├── task_scheduler_ps1.xml        # PowerShell用XML設定
└── setup_task_scheduler.ps1      # 自動設定スクリプト
```

## 🚀 **設定方法（2つの選択肢）**

### **方法A: バッチファイル実行（推奨・安定）**

#### 1. Task Schedulerを開く
```
Windowsキー + R → taskschd.msc → Enter
```

#### 2. XMLインポート
```
右パネル「タスクのインポート」
→ scripts\task_scheduler_bat.xml を選択
→ OK
```

#### 3. 実行内容
```
プログラム: S:\python\Google-Drive-AutoSync\scripts\run_sync.bat
スケジュール: 毎日 8:00-12:00 (30分間隔)
```

---

### **方法B: PowerShell実行（高機能）**

#### 1. Task Schedulerを開く
```
Windowsキー + R → taskschd.msc → Enter
```

#### 2. XMLインポート
```
右パネル「タスクのインポート」
→ scripts\task_scheduler_ps1.xml を選択
→ OK
```

#### 3. 実行内容
```
プログラム: powershell.exe
引数: -ExecutionPolicy Bypass -File "S:\python\Google-Drive-AutoSync\scripts\run_sync.ps1" -Silent
スケジュール: 毎日 8:00-12:00 (30分間隔)
```

## ⚙️ **自動実行スケジュール**

設定完了後の動作：
```
08:00 → Google Drive AutoSync 実行
08:30 → Google Drive AutoSync 実行
09:00 → Google Drive AutoSync 実行
09:30 → Google Drive AutoSync 実行
10:00 → Google Drive AutoSync 実行
10:30 → Google Drive AutoSync 実行
11:00 → Google Drive AutoSync 実行
11:30 → Google Drive AutoSync 実行
12:00 → 監視終了
```

## 🔍 **動作確認**

### 手動テスト実行
```
# Task Schedulerで右クリック → 実行
# または PowerShellで：
schtasks /run /tn "Google Drive AutoSync"
```

### ログ確認
```
# 実行ログ確認
dir S:\python\Google-Drive-AutoSync\logs\

# エラー確認
type S:\python\Google-Drive-AutoSync\data\error_flag.txt
```

## 📊 **推奨設定**

### **システム安定性重視 → バッチファイル**
- ✅ シンプルで確実
- ✅ 文字化けなし
- ✅ Windows標準機能のみ使用

### **詳細情報取得重視 → PowerShell**
- ✅ 詳細なログ出力
- ✅ エラー詳細表示
- ✅ 結果ファイル自動確認

## 🔧 **XML設定ファイルの更新内容**

### **主な変更点**
```xml
<!-- タスク名更新 -->
<RegistrationInfo>
  <Author>Google Drive AutoSync System</Author>
  <Description>Google Driveファイルの自動監視・ダウンロード・処理</Description>
</RegistrationInfo>

<!-- 実行パス更新 -->
<Command>S:\python\Google-Drive-AutoSync\scripts\run_sync.bat</Command>
<WorkingDirectory>S:\python\Google-Drive-AutoSync</WorkingDirectory>
```

### **表示名の更新**
```
旧: BirdNET AutoPipeline
新: Google Drive AutoSync
```

## 🛠️ **トラブルシューティング**

### **Task Schedulerでの一般的な問題**

#### 1. パス設定エラー
```
❌ エラー: "指定されたファイルが見つかりません"
✅ 解決: パスを絶対パスで指定
```

#### 2. 権限エラー
```
❌ エラー: "アクセスが拒否されました"
✅ 解決: "最高の特権で実行" にチェック
```

#### 3. Python環境エラー
```
❌ エラー: "python コマンドが見つかりません"
✅ 解決: 仮想環境のactivateスクリプト確認
```

### **実行状況の確認方法**

#### 1. Task Scheduler履歴
```
Task Scheduler → タスク選択 → 履歴タブ
最近の実行結果を確認
```

#### 2. ログファイル確認
```
# 最新のログファイル確認
type S:\python\Google-Drive-AutoSync\logs\autosync_20250620.log
```

#### 3. 処理結果確認
```
# 結果ファイル確認
dir S:\python\Google-Drive-AutoSync\data\results\
```

## 🎯 **選択の推奨**

**初回設定・安定運用**: `task_scheduler_bat.xml` (バッチファイル)
**詳細管理・デバッグ**: `task_scheduler_ps1.xml` (PowerShell)

## 📝 **設定後のチェックリスト**

### **必須確認事項**
- [ ] Task Schedulerにタスクが正常登録されている
- [ ] 手動実行で正常動作する
- [ ] ログファイルが作成される
- [ ] エラーフラグが作成されない

### **動作確認手順**
1. Task Schedulerで手動実行
2. `data\results\` に結果ファイル作成確認
3. `logs\autosync_YYYYMMDD.log` でログ確認
4. エラーがないことを確認

### **長期運用確認**
- [ ] 1週間の自動実行を確認
- [ ] ディスク容量の変化を監視
- [ ] 定期的なエラーログチェック

---

**🎯 これでGoogle Drive AutoSyncの完全自動化が完成しました！**

---
