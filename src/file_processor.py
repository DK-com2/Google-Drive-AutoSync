#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ファイル処理モジュール
Google Driveからのダウンロード、BirdNET解析、クリーンアップを実行

機能:
- 安全なファイルダウンロード
- ディスク容量管理
- ファイル整合性確認
- BirdNET解析（将来実装）
- 自動クリーンアップ
"""

import os
import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError


class FileProcessor:
    """ファイル処理クラス"""
    
    def __init__(self, config: Dict):
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
        self.results_path = self.project_root / "data" / "results"
        
        # 処理設定
        self.chunk_size = config['file_processing']['chunk_size_mb'] * 1024 * 1024
        self.min_free_space = config['file_processing']['min_free_space_gb'] * 1024 * 1024 * 1024
        
        # ディレクトリ作成
        self.download_path.mkdir(parents=True, exist_ok=True)
        self.temp_path.mkdir(parents=True, exist_ok=True)
        self.results_path.mkdir(parents=True, exist_ok=True)
    
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
            
            # Windows対応: shutil.disk_usageを使用
            import shutil
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
            
            # MD5ハッシュ確認
            actual_md5 = self._calculate_md5(file_path)
            if actual_md5 != expected_md5:
                self.logger.error(f"MD5ハッシュ不一致: 期待={expected_md5}, 実際={actual_md5}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"整合性確認エラー: {e}")
            return False
    
    def download_file(self, service, file_info: Dict) -> Optional[Path]:
        """
        Google Driveからファイルをダウンロード
        
        Args:
            service: Google Drive APIサービス
            file_info: ファイル情報
            
        Returns:
            ダウンロード成功時はファイルパス、失敗時はNone
        """
        file_id = file_info['id']
        file_name = file_info['name']
        file_size = int(file_info.get('size', 0))
        expected_md5 = file_info.get('md5Checksum')
        
        self.logger.info(f"ダウンロード開始: {file_name} ({file_size/1024/1024:.1f}MB)")
        
        # ディスク容量チェック
        if not self._check_disk_space(file_size):
            return None
        
        # 一時ファイルパス
        temp_file = self.temp_path / f"{file_name}.downloading"
        final_file = self.download_path / file_name
        
        try:
            # ダウンロード実行
            request = service.files().get_media(fileId=file_id)
            
            with open(temp_file, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request, chunksize=self.chunk_size)
                done = False
                
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        progress = int(status.progress() * 100)
                        if progress % 20 == 0:  # 20%ごとに表示
                            self.logger.info(f"ダウンロード進捗: {progress}%")
            
            # ファイル整合性確認
            if expected_md5 and not self._verify_file_integrity(temp_file, expected_md5, file_size):
                self.logger.error(f"ファイル整合性確認失敗: {file_name}")
                temp_file.unlink(missing_ok=True)
                return None
            
            # 最終ファイルに移動
            temp_file.rename(final_file)
            self.logger.info(f"ダウンロード完了: {file_name}")
            
            return final_file
            
        except HttpError as e:
            self.logger.error(f"ダウンロードエラー: {file_name} - {e}")
            temp_file.unlink(missing_ok=True)
            return None
        except Exception as e:
            self.logger.error(f"ダウンロード中の予期しないエラー: {file_name} - {e}")
            temp_file.unlink(missing_ok=True)
            return None
    
    def analyze_audio(self, file_path: Path) -> Optional[Dict]:
        """
        BirdNET音声解析（将来実装）
        
        Args:
            file_path: 音声ファイルパス
            
        Returns:
            解析結果辞書
        """
        # TODO: BirdNET解析の実装
        # 現在はダミーデータを返す
        
        self.logger.info(f"音声解析実行: {file_path.name}")
        
        # ダミー解析結果
        dummy_result = {
            'file_name': file_path.name,
            'file_size': file_path.stat().st_size,
            'analyzed_at': datetime.now().isoformat(),
            'segments': [
                {
                    'start_time': 0.0,
                    'end_time': 3.0,
                    'species': 'Turdus migratorius',
                    'confidence': 0.85,
                    'quality_score': 0.78
                },
                {
                    'start_time': 6.0,
                    'end_time': 9.0,
                    'species': 'Turdus migratorius',
                    'confidence': 0.92,
                    'quality_score': 0.89
                }
            ],
            'summary': {
                'total_segments': 2,
                'species_detected': ['Turdus migratorius'],
                'average_confidence': 0.885,
                'processing_time_seconds': 12.5
            }
        }
        
        return dummy_result
    
    def save_analysis_result(self, result: Dict, file_name: str) -> Path:
        """
        解析結果の保存
        
        Args:
            result: 解析結果
            file_name: 元のファイル名
            
        Returns:
            結果ファイルのパス
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = self.results_path / f"analysis_{timestamp}_{Path(file_name).stem}.json"
        
        try:
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"解析結果保存: {result_file.name}")
            return result_file
            
        except Exception as e:
            self.logger.error(f"解析結果保存エラー: {e}")
            raise
    
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
    
    def delete_from_drive(self, service, file_id: str, file_name: str):
        """
        Google Driveからファイルを削除
        
        Args:
            service: Google Drive APIサービス
            file_id: ファイルID
            file_name: ファイル名
        """
        try:
            service.files().delete(fileId=file_id).execute()
            self.logger.info(f"Google Driveからファイル削除: {file_name}")
        except HttpError as e:
            self.logger.error(f"Google Driveファイル削除エラー: {file_name} - {e}")
            raise
        except Exception as e:
            self.logger.error(f"ファイル削除中の予期しないエラー: {file_name} - {e}")
            raise
    
    def process_file(self, file_info: Dict) -> bool:
        """
        ファイルの完全処理（ダウンロード→解析→クリーンアップ）
        
        Args:
            file_info: ファイル情報
            
        Returns:
            処理成功時True、失敗時False
        """
        file_id = file_info['id']
        file_name = file_info['name']
        
        try:
            # Google Drive APIサービスを取得（drive_monitorから）
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent))
            from drive_monitor import DriveMonitor
            monitor = DriveMonitor(self.config)
            service = monitor.service
            
            # 1. ファイルダウンロード
            downloaded_file = self.download_file(service, file_info)
            if not downloaded_file:
                return False
            
            # 2. 音声解析実行
            analysis_result = self.analyze_audio(downloaded_file)
            if not analysis_result:
                self.logger.error(f"音声解析失敗: {file_name}")
                self.cleanup_file(downloaded_file)
                return False
            
            # 3. 解析結果保存
            result_file = self.save_analysis_result(analysis_result, file_name)
            
            # 4. Google Driveからファイル削除（オプション）
            try:
                self.delete_from_drive(service, file_id, file_name)
            except Exception as e:
                self.logger.warning(f"Google Driveファイル削除をスキップ: {file_name} - {str(e)}")
                # 削除失敗しても処理は継続
            
            # 5. ローカルファイルクリーンアップ（オプション）
            # 注意: ファイルを保持したい場合はコメントアウト
            # self.cleanup_file(downloaded_file)
            self.logger.info(f"ダウンロードファイルを保持: {downloaded_file}")
            
            # 6. 処理済みマーク
            monitor.mark_file_processed(file_id)
            
            self.logger.info(f"ファイル処理完了: {file_name} -> {result_file.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"ファイル処理中にエラー: {file_name} - {e}")
            # エラー時はローカルファイルだけクリーンアップ
            if 'downloaded_file' in locals() and downloaded_file:
                self.cleanup_file(downloaded_file)
            return False
