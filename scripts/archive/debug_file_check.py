#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ファイル判定の詳細デバッグスクリプト
対象ファイル判定の各ステップを詳しく確認します
"""

import sys
import json
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from drive_monitor import DriveMonitor

def debug_file_check():
    """ファイル判定の詳細デバッグ"""
    print("🐛 ファイル判定デバッグ開始")
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
        print(f"🎵 音声拡張子: {monitor.AUDIO_EXTENSIONS}")
        
        # フォルダ内のファイル一覧を取得
        response = monitor.service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id,name,size,mimeType,md5Checksum,modifiedTime,parents)",
            orderBy="modifiedTime desc"
        ).execute()
        
        files = response.get('files', [])
        
        for file_info in files:
            name = file_info.get('name', '')
            print(f"\n🔍 ファイル詳細チェック: {name}")
            print("-" * 30)
            
            # 各条件を個別にチェック
            print("📄 ファイル情報:")
            for key, value in file_info.items():
                print(f"   {key}: {value}")
            
            print("\n✅ 判定ステップ:")
            
            # 1. ファイル名チェック
            if not name:
                print("❌ 1. ファイル名なし")
                continue
            else:
                print(f"✅ 1. ファイル名: {name}")
            
            # 2. 拡張子チェック
            file_ext = Path(name).suffix.lower()
            if file_ext not in monitor.AUDIO_EXTENSIONS:
                print(f"❌ 2. 拡張子: {file_ext} (対象外)")
                continue
            else:
                print(f"✅ 2. 拡張子: {file_ext} (対象)")
            
            # 3. 親フォルダチェック
            parents = file_info.get('parents', [])
            print(f"📂 ファイルの親フォルダ: {parents}")
            print(f"📂 対象フォルダID: {folder_id}")
            
            if folder_id not in parents:
                print(f"❌ 3. 親フォルダ: {parents} (対象フォルダにない)")
                continue
            else:
                print(f"✅ 3. 親フォルダ: 対象フォルダ内")
            
            # 4. MIMEタイプチェック
            mime_type = file_info.get('mimeType', '')
            if not mime_type.startswith('audio/'):
                print(f"❌ 4. MIMEタイプ: {mime_type} (音声ファイルではない)")
                continue
            else:
                print(f"✅ 4. MIMEタイプ: {mime_type} (音声ファイル)")
            
            # 最終判定
            is_target = monitor._is_target_file(file_info)
            print(f"\n🎯 最終判定: {'✅ 対象ファイル' if is_target else '❌ 対象外'}")
            
            if not is_target:
                print("❓ 全条件を満たしているのに対象外の理由を調査中...")
                
                # _is_target_fileメソッドを詳細に実行
                print("\n🔬 _is_target_file詳細実行:")
                
                # 実際のメソッドのステップを再現
                if not file_info:
                    print("❌ file_info が None または空")
                    continue
                
                name_check = file_info.get('name', '')
                if not name_check:
                    print("❌ ファイル名が空")
                    continue
                    
                ext_check = Path(name_check).suffix.lower()
                if ext_check not in monitor.AUDIO_EXTENSIONS:
                    print(f"❌ 拡張子チェック失敗: {ext_check}")
                    continue
                
                parents_check = file_info.get('parents', [])
                if monitor.target_folder_id not in parents_check:
                    print(f"❌ 親フォルダチェック失敗: {parents_check}")
                    continue
                
                mime_check = file_info.get('mimeType', '')
                if not mime_check.startswith('audio/'):
                    print(f"❌ MIMEタイプチェック失敗: {mime_check}")
                    continue
                
                print("🤔 すべての条件を満たしているのに対象外...")
                print("💡 コードに問題がある可能性があります")
        
    except Exception as e:
        print(f"❌ デバッグ中にエラーが発生: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_file_check()
