#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
環境状況確認スクリプト
現在のファイル状況と処理状態を表示
"""

import os
import json
from datetime import datetime
from pathlib import Path

def check_environment():
    """環境状況の確認"""
    print("🔍 BirdNET AutoPipeline 環境状況確認")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    
    # ダウンロードファイル確認
    downloads_dir = project_root / "data" / "downloads"
    if downloads_dir.exists():
        download_files = list(downloads_dir.glob("*"))
        audio_files = [f for f in download_files if f.suffix.lower() in ['.mp3', '.wav', '.flac', '.aac']]
        print(f"📁 ダウンロードファイル: {len(audio_files)}個")
        for file in audio_files[:5]:  # 最初の5個だけ表示
            size_mb = file.stat().st_size / 1024 / 1024
            print(f"   - {file.name} ({size_mb:.1f}MB)")
        if len(audio_files) > 5:
            print(f"   ... 他 {len(audio_files) - 5}個")
    else:
        print("📁 ダウンロードファイル: 0個")
    
    print()
    
    # 解析結果確認
    results_dir = project_root / "data" / "results"
    if results_dir.exists():
        result_files = list(results_dir.glob("*.json"))
        print(f"📊 解析結果: {len(result_files)}個")
        for file in sorted(result_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            print(f"   - {file.name} ({mtime.strftime('%m-%d %H:%M')})")
        if len(result_files) > 3:
            print(f"   ... 他 {len(result_files) - 3}個")
    else:
        print("📊 解析結果: 0個")
    
    print()
    
    # ログファイル確認
    logs_dir = project_root / "logs"
    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.log"))
        print(f"📝 ログファイル: {len(log_files)}個")
        for file in sorted(log_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
            size_kb = file.stat().st_size / 1024
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            print(f"   - {file.name} ({size_kb:.1f}KB, {mtime.strftime('%m-%d %H:%M')})")
    else:
        print("📝 ログファイル: 0個")
    
    print()
    
    # 状態ファイル確認
    print("⚙️ システム状態:")
    
    state_files = {
        'processed_files.txt': '処理済みファイルリスト',
        'page_token.txt': 'Google Drive監視位置',
        'last_run.txt': '最終実行時刻',
        'error_flag.txt': 'エラーフラグ',
        'token.pickle': 'Google認証トークン'
    }
    
    for filename, description in state_files.items():
        filepath = project_root / "data" / filename
        if filepath.exists():
            if filename == 'processed_files.txt':
                try:
                    lines = filepath.read_text(encoding='utf-8').strip().split('\n')
                    count = len([line for line in lines if line.strip()])
                    print(f"   ✅ {description}: {count}個")
                except:
                    print(f"   ✅ {description}: あり")
            elif filename == 'last_run.txt':
                try:
                    content = filepath.read_text(encoding='utf-8').strip()
                    dt = datetime.fromisoformat(content)
                    print(f"   ✅ {description}: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                except:
                    print(f"   ✅ {description}: あり")
            elif filename == 'error_flag.txt':
                try:
                    content = filepath.read_text(encoding='utf-8').strip()
                    print(f"   ⚠️ {description}: {content}")
                except:
                    print(f"   ⚠️ {description}: あり")
            else:
                print(f"   ✅ {description}: あり")
        else:
            if filename == 'error_flag.txt':
                print(f"   ✅ {description}: なし（正常）")
            else:
                print(f"   ❌ {description}: なし")
    
    print()
    
    # 設定ファイル確認
    print("🔧 設定ファイル:")
    config_file = project_root / "config" / "config.json"
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            folder_id = config.get('google_drive', {}).get('target_folder_id', 'Unknown')
            print(f"   ✅ 設定ファイル: あり")
            print(f"   📁 監視フォルダID: {folder_id}")
        except:
            print("   ⚠️ 設定ファイル: 読み込みエラー")
    else:
        print("   ❌ 設定ファイル: なし")
    
    creds_file = project_root / "config" / "credentials.json"
    if creds_file.exists():
        print("   ✅ Google認証ファイル: あり")
    else:
        print("   ❌ Google認証ファイル: なし")
    
    print()
    print("=" * 50)
    
    # 総容量計算
    total_size = 0
    if downloads_dir.exists():
        for file in downloads_dir.rglob('*'):
            if file.is_file():
                total_size += file.stat().st_size
    
    if results_dir.exists():
        for file in results_dir.rglob('*'):
            if file.is_file():
                total_size += file.stat().st_size
    
    if logs_dir.exists():
        for file in logs_dir.rglob('*'):
            if file.is_file():
                total_size += file.stat().st_size
    
    print(f"💾 データ総サイズ: {total_size / 1024 / 1024:.1f}MB")
    
    # リセット推奨判定
    download_count = len(list(downloads_dir.glob("*"))) if downloads_dir.exists() else 0
    result_count = len(list(results_dir.glob("*"))) if results_dir.exists() else 0
    
    if download_count > 0 or result_count > 0:
        print()
        print("🧹 リセット実行:")
        print("   scripts\\reset_environment.bat または")
        print("   scripts\\reset_environment.ps1 を実行してください")


if __name__ == "__main__":
    try:
        check_environment()
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
    
    input("\nEnterキーを押して終了...")
