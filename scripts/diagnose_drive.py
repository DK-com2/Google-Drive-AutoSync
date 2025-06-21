#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Drive診断スクリプト
フォルダ内のファイル一覧と状態を確認します
"""

import sys
import json
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from drive_monitor import DriveMonitor

def diagnose_drive_folder():
    """Google Driveフォルダの診断"""
    print("🔍 Google Drive フォルダ診断開始")
    print("=" * 50)
    
    try:
        # 設定読み込み
        config_file = project_root / "config" / "config.json"
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # DriveMonitor初期化
        monitor = DriveMonitor(config)
        folder_id = config['google_drive']['target_folder_id']
        
        print(f"📁 対象フォルダID: {folder_id}")
        
        # フォルダ内のファイル一覧を取得
        print("\n📋 フォルダ内ファイル一覧:")
        
        response = monitor.service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id,name,size,mimeType,md5Checksum,modifiedTime)",
            orderBy="modifiedTime desc"
        ).execute()
        
        files = response.get('files', [])
        
        if not files:
            print("❌ フォルダ内にファイルがありません")
            print("   以下を確認してください:")
            print("   1. フォルダIDが正しいか")
            print("   2. フォルダにファイルがアップロードされているか")
            print("   3. フォルダへのアクセス権限があるか")
            return
        
        print(f"✅ {len(files)}個のファイルを発見")
        print()
        
        for i, file_info in enumerate(files, 1):
            name = file_info.get('name', 'Unknown')
            size = file_info.get('size', 'Unknown')
            mime_type = file_info.get('mimeType', 'Unknown')
            md5 = file_info.get('md5Checksum', 'None')
            modified = file_info.get('modifiedTime', 'Unknown')
            
            print(f"  {i}. 📄 {name}")
            print(f"     💾 サイズ: {size} bytes")
            print(f"     🎭 MIMEタイプ: {mime_type}")
            print(f"     🔐 MD5: {md5[:8]}..." if md5 != 'None' else "     🔐 MD5: なし")
            print(f"     ⏰ 更新日時: {modified}")
            
            # ターゲットファイル判定
            is_target = monitor._is_target_file(file_info)
            print(f"     🎯 対象ファイル: {'✅ YES' if is_target else '❌ NO'}")
            
            if not is_target:
                # 理由を詳しく説明
                name_ext = Path(name).suffix.lower()
                if name_ext not in monitor.AUDIO_EXTENSIONS:
                    print(f"        理由: 拡張子 '{name_ext}' は対象外")
                elif not mime_type.startswith('audio/'):
                    print(f"        理由: MIMEタイプ '{mime_type}' は音声ファイルではない")
                else:
                    print("        理由: その他の条件")
            
            print()
        
        # 処理済みファイルの確認
        print("📝 処理済みファイル確認:")
        processed_files = monitor._get_processed_files()
        if processed_files:
            print(f"   {len(processed_files)}個のファイルが処理済み")
            for file_id in list(processed_files)[:5]:  # 最初の5個だけ表示
                print(f"   - {file_id}")
            if len(processed_files) > 5:
                print(f"   ... 他 {len(processed_files) - 5}個")
        else:
            print("   処理済みファイルはありません")
        
        # ページトークンの確認
        print("\n🎫 ページトークン状態:")
        page_token = monitor._load_page_token()
        if page_token:
            print(f"   現在のトークン: {page_token[:20]}...")
        else:
            print("   トークンなし（初回実行または削除済み）")
        
    except Exception as e:
        print(f"❌ 診断中にエラーが発生: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_drive_folder()
