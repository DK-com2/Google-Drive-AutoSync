#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
機能:
- PyDrive2による安全なファイルダウンロード
- ディスク容量管理
- ファイル整合性確認
- 自動クリーンアップ
"""

import os
import hashlib
import logging
import shutil
from pathlib import Path
from typing import Optional

from pydrive2.files import GoogleDriveFile


class FileProcessor:
    """ファイル処理クラス（PyDrive2版）"""
    
    def __init__(self, config: dict):
        """
        初期化
        
        Args:
            config: 設定辞書
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.project_root = Path(__file__).parent.parent
        
        # ダウンロード設定
        self.download_path = Path(config['file_processing']['download_path'])
        self.temp_path = self.project_root / "data" / "temp"
        
        # 処理設定
        self.chunk_size = config['file_processing']['chunk_size_mb'] * 1024 * 1024
        self.min_free_space = config['file_processing']['min_free_space_gb'] * 1024 * 1024 * 1024
        
        # ディレクトリ作成
        self.download_path.mkdir(parents=True, exist_ok=True)
        self.temp_path.mkdir(parents=True, exist_ok=True)
    
    def _check_disk_space(self, required_size: int) -> bool:
        """
        ディスク容量チェック
        
        Args:
            required_size: 必要な容量（バイト）
            
        Returns:
            十分な容量があるかどうか
        """
        try:
            # 必要容量を2.5倍で計算（安全マージン + 一時ファイル）
            required_space = required_size * 2.5 + self.min_free_space
            
            # ディスク使用量を確認
            total, used, free_space = shutil.disk_usage(self.download_path)
            
            if free_space < required_space:
                self.logger.error(f"ディスク容量不足: 必要={required_space/1024/1024:.1f}MB, 使用可能={free_space/1024/1024:.1f}MB")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"ディスク容量チェックエラー: {e}")
            return False
    
    def _calculate_md5(self, file_path: Path) -> str:
        """
        ファイルのMD5チェックサムを計算
        
        Args:
            file_path: ファイルパス
            
        Returns:
            MD5ハッシュ値
        """
        hash_md5 = hashlib.md5()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.error(f"MD5計算エラー: {e}")
            raise
    
    def _verify_file_integrity(self, file_path: Path, expected_md5: str, expected_size: int) -> bool:
        """
        ファイル整合性の確認
        
        Args:
            file_path: ローカルファイルパス
            expected_md5: 期待するMD5ハッシュ
            expected_size: 期待するファイルサイズ
            
        Returns:
            整合性確認結果
        """
        try:
            # ファイルサイズ確認
            actual_size = file_path.stat().st_size
            if actual_size != expected_size:
                self.logger.error(f"ファイルサイズ不一致: 期待={expected_size}, 実際={actual_size}")
                return False
            
            # MD5ハッシュ確認（MD5が提供されている場合のみ）
            if expected_md5:
                actual_md5 = self._calculate_md5(file_path)
                if actual_md5 != expected_md5:
                    self.logger.error(f"MD5ハッシュ不一致: 期待={expected_md5}, 実際={actual_md5}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"整合性確認エラー: {e}")
            return False
    
    def download_file(self, drive_monitor, file_info: dict) -> Optional[Path]:
        """
        Google Driveからファイルをダウンロード（PyDrive2版）
        
        Args:
            drive_monitor: DriveMonitorインスタンス
            file_info: ファイル情報
            
        Returns:
            ダウンロード成功時はファイルパス、失敗時はNone
        """
        file_id = file_info['id']
        file_name = file_info['name']
        file_size = int(file_info.get('size', 0))
        expected_md5 = file_info.get('md5Checksum', '')
        
        self.logger.info(f"ダウンロード開始: {file_name} ({file_size/1024/1024:.1f}MB)")
        
        # ディスク容量チェック
        if not self._check_disk_space(file_size):
            return None
        
        # 一時ファイルパス
        temp_file = self.temp_path / f"{file_name}.downloading"
        final_file = self.download_path / file_name
        
        try:
            # PyDrive2のファイルオブジェクトを取得
            drive_file = drive_monitor.get_drive_file(file_id)
            if not drive_file:
                self.logger.error(f"ファイル取得失敗: {file_name}")
                return None
            
            # PyDrive2でダウンロード実行
            self.logger.info(f"ダウンロード中: {file_name}")
            drive_file.GetContentFile(str(temp_file))
            
            # ファイル整合性確認
            if expected_md5 and not self._verify_file_integrity(temp_file, expected_md5, file_size):
                self.logger.error(f"ファイル整合性確認失敗: {file_name}")
                temp_file.unlink(missing_ok=True)
                return None
            
            # 最終ファイルに移動
            if final_file.exists():
                final_file.unlink()  # 既存ファイルがあれば削除
            
            temp_file.rename(final_file)
            self.logger.info(f"ダウンロード完了: {file_name}")
            
            return final_file
            
        except Exception as e:
            self.logger.error(f"ダウンロードエラー: {file_name} - {e}")
            temp_file.unlink(missing_ok=True)
            return None
    
    def cleanup_file(self, file_path: Path):
        """
        処理完了後のファイルクリーンアップ
        
        Args:
            file_path: 削除するファイルパス
        """
        try:
            if file_path.exists():
                file_path.unlink()
                self.logger.info(f"ファイル削除: {file_path.name}")
        except Exception as e:
            self.logger.warning(f"ファイル削除失敗: {file_path.name} - {e}")
    
    def delete_from_drive(self, drive_monitor, file_id: str, file_name: str):
        """
        Google Driveからファイルを削除（PyDrive2版）
        
        Args:
            drive_monitor: DriveMonitorインスタンス
            file_id: ファイルID
            file_name: ファイル名
        """
        try:
            drive_file = drive_monitor.get_drive_file(file_id)
            if drive_file:
                drive_file.Delete()
                self.logger.info(f"Google Driveからファイル削除: {file_name}")
            else:
                self.logger.warning(f"削除対象ファイルが見つかりません: {file_name}")
        except Exception as e:
            self.logger.error(f"Google Driveファイル削除エラー: {file_name} - {e}")
            raise
    
    def process_file(self, file_info: dict) -> bool:
        """
        ファイルの完全処理（ダウンロード→クリーンアップ）
        
        Args:
            file_info: ファイル情報
            
        Returns:
            処理成功時True、失敗時False
        """
        file_id = file_info['id']
        file_name = file_info['name']
        
        try:
            # DriveMonitorインスタンスを取得
            from .drive_monitor import DriveMonitor
            monitor = DriveMonitor(self.config)
            
            # 1. ファイルダウンロード
            downloaded_file = self.download_file(monitor, file_info)
            if not downloaded_file:
                return False
            
            # 2. Google Driveからファイル削除（オプション）
            try:
                self.delete_from_drive(monitor, file_id, file_name)
            except Exception as e:
                self.logger.warning(f"Google Driveファイル削除をスキップ: {file_name} - {str(e)}")
                # 削除失敗しても処理は継続
            
            # 3. ローカルファイルクリーンアップ（オプション）
            # 注意: ファイルを保持したい場合はコメントアウト
            # self.cleanup_file(downloaded_file)
            self.logger.info(f"ダウンロードファイルを保持: {downloaded_file}")
            
            # 4. 処理済みマーク
            monitor.mark_file_processed(file_id)
            
            self.logger.info(f"ファイル処理完了: {file_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"ファイル処理中にエラー: {file_name} - {e}")
            # エラー時はローカルファイルだけクリーンアップ
            if 'downloaded_file' in locals() and downloaded_file:
                self.cleanup_file(downloaded_file)
            return False