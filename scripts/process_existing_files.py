#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
既存ファイル処理スクリプト
フォルダ内の既存音声ファイルを直接検出して処理します
"""

import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from drive_monitor import DriveMonitor
from file_processor import FileProcessor

def setup_logging():
    """ログ設定の初期化"""
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"existing_files_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('ExistingFileProcessor')

def process_existing_files():
    """既存ファイルの処理"""
    logger = setup_logging()
    logger.info("=== 既存ファイル処理開始 ===")
    
    try:
        # 設定読み込み
        config_file = project_root / "config" / "config.json"
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # モニターとプロセッサ初期化
        monitor = DriveMonitor(config)
        processor = FileProcessor(config)
        folder_id = config['google_drive']['target_folder_id']
        
        logger.info(f"対象フォルダID: {folder_id}")
        
        # 処理済みファイルリスト取得
        processed_files = monitor._get_processed_files()
        logger.info(f"処理済みファイル数: {len(processed_files)}")
        
        # フォルダ内の全ファイルを直接取得
        logger.info("フォルダ内ファイルを直接取得中...")
        
        response = monitor.service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id,name,size,md5Checksum,mimeType,modifiedTime,parents)",
            orderBy="modifiedTime desc"
        ).execute()
        
        all_files = response.get('files', [])
        logger.info(f"フォルダ内総ファイル数: {len(all_files)}")
        
        # 対象ファイルを抽出
        target_files = []
        for file_info in all_files:
            file_id = file_info['id']
            file_name = file_info['name']
            
            # 既に処理済みかチェック
            if file_id in processed_files:
                logger.debug(f"処理済みファイルをスキップ: {file_name}")
                continue
            
            # 対象ファイルかチェック
            if monitor._is_target_file(file_info):
                # アップロード完了チェック
                if monitor._is_upload_complete(file_info):
                    target_files.append(file_info)
                    logger.info(f"処理対象ファイル発見: {file_name}")
                else:
                    logger.warning(f"アップロード未完了: {file_name}")
            else:
                logger.debug(f"対象外ファイル: {file_name}")
        
        if not target_files:
            logger.info("処理対象の音声ファイルはありません")
            return
        
        # ファイル処理実行
        logger.info(f"{len(target_files)}個のファイルを処理開始")
        processed_count = 0
        
        for file_info in target_files:
            file_name = file_info['name']
            file_size = file_info.get('size', 0)
            
            try:
                logger.info(f"処理開始: {file_name} ({int(file_size)/1024/1024:.1f}MB)")
                
                success = processor.process_file(file_info)
                if success:
                    processed_count += 1
                    logger.info(f"✅ 処理完了: {file_name}")
                else:
                    logger.error(f"❌ 処理失敗: {file_name}")
                    
            except Exception as e:
                logger.error(f"❌ 処理エラー: {file_name} - {str(e)}")
                continue
        
        # 処理結果まとめ
        logger.info(f"=== 処理結果: {processed_count}/{len(target_files)}個のファイル処理完了 ===")
        
        if processed_count > 0:
            results_dir = project_root / "data" / "results"
            logger.info(f"解析結果は {results_dir} フォルダを確認してください")
        
    except Exception as e:
        logger.error(f"システムエラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    logger.info("=== 既存ファイル処理終了 ===")
    return True

if __name__ == "__main__":
    success = process_existing_files()
    if success:
        print("\n🎉 処理が完了しました！")
        print("📁 解析結果: data/results/ フォルダを確認してください")
    else:
        print("\n❌ 処理中にエラーが発生しました")
        print("📄 ログ: logs/ フォルダを確認してください")
