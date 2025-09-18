#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
機能:
- PyDrive2による簡素化された認証
- 定期的なフォルダ監視
- 音声ファイルの自動検出
- 処理済みファイル管理
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pydrive2.files import GoogleDriveFile


class DriveMonitor:
    """Google Drive監視クラス（PyDrive2版）"""
    
    # 対象ファイル形式
    AUDIO_EXTENSIONS = {'.wav', '.mp3', '.flac', '.aac'}
    
    def __init__(self, config: dict):
        """
        初期化
        
        Args:
            config: 設定辞書
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.project_root = Path(__file__).parent.parent
        
        # Google Drive設定
        self.target_folder_id = config['google_drive']['target_folder_id']
        self.client_secrets_file = self.project_root / "config" / config['google_drive']['client_secrets_file']
        self.credentials_file = self.project_root / "config" / config['google_drive']['credentials_file']
        
        # Google Drive認証
        self.drive = self._authenticate()
    
    def _authenticate(self):
        """PyDrive2による認証"""
        try:
            # settings.yamlファイルのパス
            settings_file = self.project_root / "config" / "settings.yaml"
            
            # client_secrets.jsonの確認
            if not self.client_secrets_file.exists():
                raise FileNotFoundError(f"client_secrets.jsonが見つかりません: {self.client_secrets_file}")
            
            # settings.yamlの確認
            if not settings_file.exists():
                raise FileNotFoundError(f"settings.yamlが見つかりません: {settings_file}")
            
            # PyDrive2認証（settings.yamlを使用）
            gauth = GoogleAuth(str(settings_file))
            
            # 既存の認証情報確認
            if self.credentials_file.exists():
                self.logger.info("既存の認証情報を読み込み中...")
                gauth.LoadCredentialsFile(str(self.credentials_file))
            
            # 認証情報が無効または存在しない場合
            if gauth.credentials is None:
                self.logger.info("新規認証を実行中...")
                gauth.LocalWebserverAuth()
            elif gauth.access_token_expired:
                self.logger.info("トークンを更新中...")
                gauth.Refresh()
            else:
                self.logger.info("既存の認証情報を使用")
                gauth.Authorize()
            
            # 認証情報を保存
            gauth.SaveCredentialsFile(str(self.credentials_file))
            
            # Google Driveオブジェクトを作成
            drive = GoogleDrive(gauth)
            self.logger.info("Google Drive認証完了")
            
            return drive
            
        except Exception as e:
            self.logger.error(f"Google Drive認証エラー: {e}")
            raise
    
    def _is_target_file(self, file_obj: GoogleDriveFile) -> bool:
        """対象ファイルかどうかの判定"""
        try:
            # ファイル名確認
            file_title = file_obj.get('title', '')
            if not file_title:
                return False
            
            # 拡張子確認
            file_ext = Path(file_title).suffix.lower()
            if file_ext not in self.AUDIO_EXTENSIONS:
                return False
            
            # 親フォルダ確認
            parents = file_obj.get('parents', [])
            if not parents:
                return False
            
            # 対象フォルダに存在するかチェック
            for parent in parents:
                if parent['id'] == self.target_folder_id:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"ファイル判定エラー: {e}")
            return False
    
    def _is_upload_complete(self, file_obj: GoogleDriveFile) -> bool:
        """
        アップロード完了判定
        
        PyDrive2では基本的に取得できるファイルは完了済み
        """
        # ファイルサイズが存在すれば完了とみなす
        file_size = file_obj.get('fileSize')
        if file_size and int(file_size) > 0:
            return True
        
        # MD5チェックサムが存在すれば完了
        md5_checksum = file_obj.get('md5Checksum')
        if md5_checksum:
            return True
        
        self.logger.info(f"アップロード完了待機中: {file_obj.get('title', 'Unknown')}")
        return False
    
    def _get_processed_files(self) -> set:
        """処理済みファイルIDリストの取得"""
        processed_file = self.project_root / "data" / "processed_files.txt"
        
        try:
            if processed_file.exists():
                content = processed_file.read_text(encoding='utf-8')
                return set(line.strip() for line in content.splitlines() if line.strip())
        except Exception as e:
            self.logger.warning(f"処理済みファイル読み込みエラー: {e}")
        
        return set()
    
    def _add_processed_file(self, file_id: str):
        """処理済みファイルIDを追加"""
        processed_file = self.project_root / "data" / "processed_files.txt"
        
        try:
            # dataディレクトリを確保
            processed_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(processed_file, 'a', encoding='utf-8') as f:
                f.write(f"{file_id}\n")
        except Exception as e:
            self.logger.error(f"処理済みファイル追加エラー: {e}")
    
    def check_for_new_files(self) -> List[dict]:
        """
        新しいファイルのチェック
        
        Returns:
            新しい音声ファイルのリスト（辞書形式）
        """
        try:
            self.logger.info("Google Driveフォルダを監視中...")
            
            # 処理済みファイルリスト取得
            processed_files = self._get_processed_files()
            
            # 対象フォルダ内のファイル一覧を取得
            query = f"'{self.target_folder_id}' in parents and trashed=false"
            file_list = self.drive.ListFile({'q': query}).GetList()
            
            new_files = []
            self.logger.info(f"{len(file_list)}個のファイルを検出")
            
            for file_obj in file_list:
                file_id = file_obj['id']
                file_title = file_obj.get('title', '')
                
                # 既に処理済みか確認
                if file_id in processed_files:
                    self.logger.debug(f"処理済みファイルをスキップ: {file_title}")
                    continue
                
                # 対象ファイルか確認
                if not self._is_target_file(file_obj):
                    continue
                
                # アップロード完了か確認
                if not self._is_upload_complete(file_obj):
                    self.logger.info(f"アップロード未完了: {file_title} (後で再確認)")
                    continue
                
                # ファイル情報を辞書形式で格納
                file_info = {
                    'id': file_id,
                    'name': file_title,
                    'size': file_obj.get('fileSize', '0'),
                    'md5Checksum': file_obj.get('md5Checksum', ''),
                    'mimeType': file_obj.get('mimeType', ''),
                    'modifiedTime': file_obj.get('modifiedDate', ''),
                    'parents': [{'id': parent['id']} for parent in file_obj.get('parents', [])]
                }
                
                new_files.append(file_info)
                self.logger.info(f"新規ファイル検出: {file_title}")
            
            return new_files
            
        except Exception as e:
            self.logger.error(f"ファイルチェック中にエラー: {e}")
            raise
    
    def mark_file_processed(self, file_id: str):
        """ファイルを処理済みとしてマーク"""
        self._add_processed_file(file_id)
        self.logger.debug(f"処理済みファイルに追加: {file_id}")
    
    def get_file_details(self, file_id: str) -> Optional[dict]:
        """ファイルの詳細情報を取得"""
        try:
            file_obj = self.drive.CreateFile({'id': file_id})
            file_obj.FetchMetadata()
            
            return {
                'id': file_obj['id'],
                'name': file_obj.get('title', ''),
                'size': file_obj.get('fileSize', '0'),
                'md5Checksum': file_obj.get('md5Checksum', ''),
                'mimeType': file_obj.get('mimeType', ''),
                'modifiedTime': file_obj.get('modifiedDate', ''),
                'parents': [{'id': parent['id']} for parent in file_obj.get('parents', [])]
            }
        except Exception as e:
            self.logger.error(f"ファイル詳細取得エラー: {e}")
            return None
    
    def get_drive_file(self, file_id: str) -> Optional[GoogleDriveFile]:
        """PyDrive2のファイルオブジェクトを取得"""
        try:
            file_obj = self.drive.CreateFile({'id': file_id})
            file_obj.FetchMetadata()
            return file_obj
        except Exception as e:
            self.logger.error(f"Driveファイル取得エラー: {e}")
            return None