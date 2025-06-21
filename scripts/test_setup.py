#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定テスト・接続確認スクリプト
BirdNET AutoPipelineの設定と接続をテストします
"""

import json
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.drive_monitor import DriveMonitor
    from src.file_processor import FileProcessor
except ImportError as e:
    print(f"❌ モジュールインポートエラー: {e}")
    sys.exit(1)


def test_config_file():
    """設定ファイルのテスト"""
    print("📁 設定ファイルテスト")
    
    config_file = project_root / "config" / "config.json"
    
    if not config_file.exists():
        print(f"❌ 設定ファイルが見つかりません: {config_file}")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✅ 設定ファイル読み込み成功")
        
        # 必要なキーの確認
        required_keys = [
            'google_drive.target_folder_id',
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
                return False
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ 設定ファイル形式エラー: {e}")
        return False


def test_credentials():
    """Google Drive認証テスト"""
    print("\n🔐 Google Drive認証テスト")
    
    credentials_file = project_root / "config" / "credentials.json"
    
    if not credentials_file.exists():
        print(f"❌ 認証ファイルが見つかりません: {credentials_file}")
        print("   Google Cloud Consoleから credentials.json をダウンロードしてください")
        return False
    
    print("✅ 認証ファイル確認")
    return True


def test_directory_structure():
    """ディレクトリ構造テスト"""
    print("\n📂 ディレクトリ構造テスト")
    
    required_dirs = [
        "src",
        "config", 
        "data",
        "data/downloads",
        "data/results",
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
            all_ok = False
    
    return all_ok


def test_drive_connection():
    """Google Drive接続テスト"""
    print("\n🌐 Google Drive接続テスト")
    
    try:
        # 設定読み込み
        config_file = project_root / "config" / "config.json"
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # DriveMonitor初期化テスト
        monitor = DriveMonitor(config)
        print("✅ DriveMonitor初期化成功")
        
        # APIサービステスト
        if monitor.service:
            print("✅ Google Drive APIサービス接続成功")
            
            # 簡単なAPI呼び出しテスト
            try:
                about = monitor.service.about().get(fields="user").execute()
                user_email = about.get('user', {}).get('emailAddress', 'Unknown')
                print(f"✅ 認証ユーザー: {user_email}")
                return True
            except Exception as e:
                print(f"❌ API呼び出しエラー: {e}")
                return False
        else:
            print("❌ APIサービス初期化失敗")
            return False
            
    except Exception as e:
        print(f"❌ 接続テストエラー: {e}")
        return False


def test_file_processor():
    """FileProcessor初期化テスト"""
    print("\n⚙️ FileProcessor初期化テスト")
    
    try:
        # 設定読み込み
        config_file = project_root / "config" / "config.json"
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # FileProcessor初期化
        processor = FileProcessor(config)
        print("✅ FileProcessor初期化成功")
        
        # ディレクトリ作成確認
        if processor.download_path.exists():
            print(f"✅ ダウンロードパス: {processor.download_path}")
        else:
            print(f"❌ ダウンロードパス作成失敗: {processor.download_path}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ FileProcessor初期化エラー: {e}")
        return False


def main():
    """メインテスト実行"""
    print("🚀 BirdNET AutoPipeline 設定テスト開始")
    print("=" * 50)
    
    tests = [
        ("設定ファイル", test_config_file),
        ("認証ファイル", test_credentials),
        ("ディレクトリ構造", test_directory_structure),
        ("FileProcessor", test_file_processor),
        ("Google Drive接続", test_drive_connection),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
            else:
                print(f"⚠️ {test_name}テスト失敗")
        except Exception as e:
            print(f"❌ {test_name}テスト中にエラー: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 テスト結果: {passed_tests}/{total_tests} 通過")
    
    if passed_tests == total_tests:
        print("🎉 すべてのテストが通過しました！")
        print("   run_pipeline.bat または run_pipeline.ps1 でシステムを実行できます")
    else:
        print("⚠️ 一部のテストが失敗しました")
        print("   エラーを修正してから再度実行してください")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
