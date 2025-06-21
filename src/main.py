#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BirdNET AutoPipeline - メインプログラム
シンプルで実用的なGoogle Drive監視・ファイル処理システム

作成者: BirdNET開発チーム
最終更新: 2024-06-20
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.drive_monitor import DriveMonitor
from src.file_processor import FileProcessor


def setup_logging():
    """ログ設定の初期化"""
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"autosync_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('Google-Drive-AutoSync')


def load_config():
    """設定ファイルの読み込み"""
    config_file = project_root / "config" / "config.json"
    
    if not config_file.exists():
        raise FileNotFoundError(f"設定ファイルが見つかりません: {config_file}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return config


def create_state_files():
    """必要な状態ファイルを作成"""
    state_files = {
        'page_token.txt': '',
        'last_run.txt': datetime.now().isoformat(),
        'processed_files.txt': ''
    }
    
    for filename, default_content in state_files.items():
        filepath = project_root / "data" / filename
        if not filepath.exists():
            filepath.write_text(default_content, encoding='utf-8')


def check_error_flag():
    """エラーフラグファイルの確認"""
    error_flag = project_root / "data" / "error_flag.txt"
    if error_flag.exists():
        error_content = error_flag.read_text(encoding='utf-8')
        return f"前回エラー発生: {error_content}"
    return None


def create_error_flag(error_message):
    """エラーフラグファイルの作成"""
    error_flag = project_root / "data" / "error_flag.txt"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    error_flag.write_text(f"{timestamp} - {error_message}", encoding='utf-8')


def clear_error_flag():
    """エラーフラグファイルの削除"""
    error_flag = project_root / "data" / "error_flag.txt"
    if error_flag.exists():
        error_flag.unlink()


def cleanup_old_logs(config):
    """古いログファイルのクリーンアップ"""
    try:
        log_dir = project_root / "logs"
        if not log_dir.exists():
            return
        
        max_log_files = config.get('logging', {}).get('max_log_files', 30)
        cutoff_date = datetime.now() - timedelta(days=max_log_files)
        
        deleted_count = 0
        for log_file in log_dir.glob("autosync_*.log"):
            try:
                # ファイル名から日付を抽出 (autosync_YYYYMMDD.log)
                date_str = log_file.stem.replace('autosync_', '')
                if len(date_str) == 8 and date_str.isdigit():
                    file_date = datetime.strptime(date_str, '%Y%m%d')
                    
                    if file_date < cutoff_date:
                        log_file.unlink()
                        deleted_count += 1
                        
            except (ValueError, OSError) as e:
                # 日付解析エラーやファイル削除エラーは無視
                continue
        
        if deleted_count > 0:
            logger = logging.getLogger('Google-Drive-AutoSync')
            logger.info(f"古いログファイルを削除しました: {deleted_count}個 (保持期間: {max_log_files}日)")
                
    except Exception as e:
        # ログクリーンアップのエラーはシステム停止させない
        logger = logging.getLogger('Google-Drive-AutoSync')
        logger.warning(f"ログクリーンアップエラー: {str(e)}")


def main():
    """メイン処理"""
    logger = setup_logging()
    logger.info("=== Google Drive AutoSync 開始 ===")
    
    try:
        # 前回のエラー状態確認
        error_status = check_error_flag()
        if error_status:
            logger.warning(error_status)
        
        # 設定読み込み
        config = load_config()
        logger.info("設定ファイル読み込み完了")
        
        # 古いログファイルのクリーンアップ
        cleanup_old_logs(config)
        
        # 状態ファイル初期化
        create_state_files()
        
        # Google Drive監視システム初期化
        monitor = DriveMonitor(config)
        processor = FileProcessor(config)
        
        # 新しいファイルをチェック
        logger.info("Google Drive監視開始")
        new_files = monitor.check_for_new_files()
        
        if not new_files:
            logger.info("新しいファイルはありません")
            # 最終実行時刻を更新
            last_run_file = project_root / "data" / "last_run.txt"
            last_run_file.write_text(datetime.now().isoformat(), encoding='utf-8')
            return
        
        # ファイル処理実行
        logger.info(f"{len(new_files)}個のファイルを処理開始")
        processed_count = 0
        
        for file_info in new_files:
            try:
                success = processor.process_file(file_info)
                if success:
                    processed_count += 1
                    logger.info(f"ファイル処理完了: {file_info['name']}")
                else:
                    logger.warning(f"ファイル処理失敗: {file_info['name']}")
                    
            except Exception as e:
                logger.error(f"ファイル処理エラー: {file_info['name']} - {str(e)}")
                continue
        
        # 処理結果まとめ
        logger.info(f"処理完了: {processed_count}/{len(new_files)}個のファイル")
        
        # 成功時はエラーフラグをクリア
        clear_error_flag()
        
        # 最終実行時刻を更新
        last_run_file = project_root / "data" / "last_run.txt"
        last_run_file.write_text(datetime.now().isoformat(), encoding='utf-8')
        
    except Exception as e:
        error_message = f"システムエラー: {str(e)}"
        logger.error(error_message)
        create_error_flag(error_message)
        sys.exit(1)
    
    finally:
        logger.info("=== Google Drive AutoSync 終了 ===")


if __name__ == "__main__":
    main()
