#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google-Drive-AutoSync 統合テストスクリプト（PyDrive2版）
PyDrive2移行後の全ての診断・テスト機能を1つにまとめました
"""

import json
import sys
import logging
from pathlib import Path
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.drive_monitor import DriveMonitor
    from src.file_processor import FileProcessor
except ImportError as e:
    print(f"ERROR: Module import error: {e}")
    print("Please install PyDrive2: pip install PyDrive2>=1.17.0")
    sys.exit(1)


def print_header(title):
    """セクションヘッダーを印刷"""
    print(f"\n{'='*50}")
    print(f"🔧 {title}")
    print(f"{'='*50}")


def test_environment():
    """環境・依存関係チェック"""
    print_header("環境チェック")
    
    print(f"📍 プロジェクトルート: {project_root}")
    print(f"🐍 Python: {sys.version}")
    
    # 必要なライブラリチェック（PyDrive2版）
    required_packages = [
        'pydrive2.auth',
        'pydrive2.drive',
        'pydrive2.files',
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - PyDrive2のインストールが必要")
            return False
    
    return True


def test_config_file():
    """設定ファイルのテスト"""
    print_header("設定ファイルテスト")
    
    config_file = project_root / "config" / "config.json"
    
    if not config_file.exists():
        print(f"❌ 設定ファイルが見つかりません: {config_file}")
        return False, None
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✅ 設定ファイル読み込み成功")
        
        # 必要なキーの確認（PyDrive2版）
        required_keys = [
            'google_drive.target_folder_id',
            'google_drive.client_secrets_file',
            'google_drive.credentials_file',
            'file_processing.download_path'
        ]
        
        for key in required_keys:
            keys = key.split('.')
            value = config
            try:
                for k in keys:
                    value = value[k]
                print(f"✅ {key}: {value}")
            except KeyError:
                print(f"❌ 必須設定が不足: {key}")
                return False, None
        
        return True, config
        
    except json.JSONDecodeError as e:
        print(f"❌ 設定ファイル形式エラー: {e}")
        return False, None


def test_credentials():
    """PyDrive2認証ファイルテスト"""
    print_header("認証ファイルテスト（PyDrive2版）")
    
    client_secrets_file = project_root / "config" / "client_secrets.json"
    credentials_file = project_root / "config" / "credentials.json"
    settings_file = project_root / "config" / "settings.yaml"
    
    if not client_secrets_file.exists():
        print(f"❌ client_secrets.jsonが見つかりません: {client_secrets_file}")
        print("   Google Cloud Consoleから client_secrets.json をダウンロードしてください")
        print("   （PyDrive2では credentials.json ではなく client_secrets.json が必要です）")
        return False
    
    print("✅ client_secrets.json 確認")
    
    if not settings_file.exists():
        print(f"❌ settings.yamlが見つかりません: {settings_file}")
        print("   PyDrive2設定ファイルが作成されていません")
        return False
    
    print("✅ settings.yaml 確認")
    
    if credentials_file.exists():
        print("✅ credentials.json 確認（PyDrive2認証済み）")
    else:
        print("⚠️ credentials.json なし（初回認証が必要）")
    
    return True


def test_directory_structure():
    """ディレクトリ構造テスト"""
    print_header("ディレクトリ構造テスト")
    
    required_dirs = [
        "src",
        "config", 
        "data",
        "data/downloads",
        "data/temp",
        "logs"
    ]
    
    all_ok = True
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ が見つかりません")
            # 自動作成を試行
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"   → 自動作成しました: {dir_name}/")
            except Exception as e:
                print(f"   → 作成失敗: {e}")
                all_ok = False
    
    return all_ok


def test_drive_connection(config):
    """PyDrive2接続テスト"""
    print_header("PyDrive2接続テスト")
    
    try:
        # DriveMonitor初期化テスト
        print("DriveMonitor初期化中...")
        monitor = DriveMonitor(config)
        print("✅ DriveMonitor初期化成功")
        
        # PyDrive2 Driveサービステスト
        if monitor.drive:
            print("✅ PyDrive2 Driveサービス接続成功")
            
            # 簡単なAPI呼び出しテスト
            try:
                # AboutAPIを使用してユーザー情報を取得
                about_file = monitor.drive.CreateFile()
                about_info = monitor.drive.auth.service.about().get(fields="user").execute()
                user_email = about_info.get('user', {}).get('emailAddress', 'Unknown')
                print(f"✅ 認証ユーザー: {user_email}")
                return True, monitor
            except Exception as e:
                print(f"❌ API呼び出しエラー: {e}")
                return False, None
        else:
            print("❌ Driveサービス初期化失敗")
            return False, None
            
    except Exception as e:
        print(f"❌ 接続テストエラー: {e}")
        if "client_secrets" in str(e):
            print("💡 client_secrets.jsonファイルが正しく配置されているか確認してください")
        elif "credentials" in str(e) or "auth" in str(e):
            print("💡 初回認証の場合、ブラウザでの認証が必要です")
        return False, None


def diagnose_drive_folder(monitor, config):
    """Google Driveフォルダ診断（PyDrive2版）"""
    print_header("Google Driveフォルダ診断")
    
    try:
        folder_id = config['google_drive']['target_folder_id']
        print(f"📁 対象フォルダID: {folder_id}")
        
        # フォルダ内のファイル一覧を取得（PyDrive2）
        query = f"'{folder_id}' in parents and trashed=false"
        file_list = monitor.drive.ListFile({'q': query}).GetList()
        
        if not file_list:
            print("❌ フォルダ内にファイルがありません")
            print("   以下を確認してください:")
            print("   1. フォルダIDが正しいか")
            print("   2. フォルダにファイルがアップロードされているか")
            print("   3. フォルダへのアクセス権限があるか")
            return False
        
        print(f"✅ {len(file_list)}個のファイルを発見")
        
        target_files = 0
        for i, file_obj in enumerate(file_list, 1):
            title = file_obj.get('title', 'Unknown')
            file_size = file_obj.get('fileSize', 'Unknown')
            mime_type = file_obj.get('mimeType', 'Unknown')
            
            print(f"\n  {i}. 📄 {title}")
            print(f"     💾 サイズ: {file_size} bytes")
            print(f"     🎭 MIMEタイプ: {mime_type}")
            
            # ターゲットファイル判定
            is_target = monitor._is_target_file(file_obj)
            print(f"     🎯 対象ファイル: {'✅ YES' if is_target else '❌ NO'}")
            
            if is_target:
                target_files += 1
            elif not is_target:
                title_ext = Path(title).suffix.lower()
                if title_ext not in monitor.AUDIO_EXTENSIONS:
                    print(f"        理由: 拡張子 '{title_ext}' は対象外")
        
        print(f"\n📊 処理対象ファイル: {target_files}個")
        return True
        
    except Exception as e:
        print(f"❌ フォルダ診断エラー: {e}")
        return False


def test_file_processor(config):
    """FileProcessor初期化テスト"""
    print_header("FileProcessor初期化テスト")
    
    try:
        # FileProcessor初期化
        processor = FileProcessor(config)
        print("✅ FileProcessor初期化成功")
        
        # ディレクトリ作成確認
        if processor.download_path.exists():
            print(f"✅ ダウンロードパス: {processor.download_path}")
        else:
            print(f"❌ ダウンロードパス作成失敗: {processor.download_path}")
            return False
        
        # ディスク容量チェック
        import shutil
        free_space = shutil.disk_usage(processor.download_path).free / (1024**3)  # GB
        min_space = config.get('file_processing', {}).get('min_free_space_gb', 1)
        
        print(f"💾 利用可能容量: {free_space:.1f}GB")
        print(f"🎯 最小必要容量: {min_space}GB")
        
        if free_space >= min_space:
            print("✅ 容量チェック通過")
        else:
            print("⚠️ 容量不足の可能性")
        
        return True
        
    except Exception as e:
        print(f"❌ FileProcessor初期化エラー: {e}")
        return False


def process_existing_files(monitor, processor):
    """既存ファイル処理オプション"""
    print_header("既存ファイル処理")
    
    answer = input("既存の処理対象ファイルを今すぐ処理しますか？ (y/N): ").strip().lower()
    
    if answer in ['y', 'yes']:
        try:
            print("🔄 既存ファイルを検索中...")
            new_files = monitor.check_for_new_files()
            
            if not new_files:
                print("📝 処理対象の新しいファイルはありません")
                return True
            
            print(f"🎯 {len(new_files)}個のファイルを処理開始")
            
            for file_info in new_files:
                try:
                    print(f"⚙️ 処理中: {file_info['name']}")
                    success = processor.process_file(file_info)
                    if success:
                        print(f"✅ 完了: {file_info['name']}")
                    else:
                        print(f"❌ 失敗: {file_info['name']}")
                except Exception as e:
                    print(f"❌ エラー: {file_info['name']} - {str(e)}")
            
            return True
            
        except Exception as e:
            print(f"❌ 既存ファイル処理エラー: {e}")
            return False
    else:
        print("⏭️ スキップしました")
        return True


def main():
    """メインテスト実行"""
    print("🚀 Google-Drive-AutoSync 統合テスト開始（PyDrive2版）")
    print(f"⏰ 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ログレベルを警告以上に設定（情報ログを抑制）
    logging.getLogger().setLevel(logging.WARNING)
    
    tests = [
        ("環境チェック", test_environment),
        ("ディレクトリ構造", test_directory_structure),
        ("認証ファイル", test_credentials),
    ]
    
    # 基本テスト実行
    for test_name, test_func in tests:
        try:
            if not test_func():
                print(f"\n❌ {test_name}テスト失敗 - テストを中断します")
                return False
        except Exception as e:
            print(f"\n❌ {test_name}テスト中にエラー: {e}")
            return False
    
    # 設定ファイルテスト
    config_ok, config = test_config_file()
    if not config_ok:
        print("\n❌ 設定ファイルテスト失敗 - テストを中断します")
        return False
    
    # PyDrive2接続テスト
    drive_ok, monitor = test_drive_connection(config)
    if not drive_ok:
        print("\n❌ PyDrive2接続テスト失敗")
        print("💡 初回認証の場合、ブラウザでの認証が必要です")
        return False
    
    # FileProcessorテスト
    if not test_file_processor(config):
        print("\n❌ FileProcessorテスト失敗")
        return False
    
    # Google Driveフォルダ診断
    if not diagnose_drive_folder(monitor, config):
        print("\n⚠️ フォルダ診断で問題が見つかりました")
    
    # 既存ファイル処理オプション
    processor = FileProcessor(config)
    process_existing_files(monitor, processor)
    
    print(f"\n{'='*50}")
    print("🎉 全てのテストが完了しました！")
    print("💡 PyDrive2移行完了 - 次の手順:")
    print("   1. 手動実行: python main.py")
    print("   2. Task Scheduler設定で自動実行")
    print("   3. 古いファイル（token.pickle, page_token.txt）を削除可能")
    print(f"{'='*50}")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)