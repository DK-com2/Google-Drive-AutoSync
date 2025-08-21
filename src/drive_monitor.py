#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Drive監視モジュール
Changes APIを使用してシンプルで効率的な新規ファイル検出を行う

機能:
- Changes APIによる効率的な監視
- ページトークンベースの状態管理
- 音声ファイルの自動検出
- アップロード完了の簡単判定
"""

import json
import pickle
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class DriveMonitor:
    """Google Drive監視クラス"""
    
    # 必要なスコープ
    SCOPES = [
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/drive.file'
    ]
    
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
        
        # Google Drive API設定
        self.target_folder_id = config['google_drive']['target_folder_id']
        self.credentials_file = self.project_root / "config" / config['google_drive']['credentials_file']
        self.token_file = self.project_root / "config" / config['google_drive']['token_file']
        self.page_token_file = self.project_root / "config" / config['google_drive']['page_token_file']
        
        # APIサービス初期化
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Google Drive API認証"""
        creds = None
        
        # 既存のトークンファイル確認
        if self.token_file.exists():
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # 認証が必要な場合
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.logger.info("トークンを更新中...")
                creds.refresh(Request())
            else:
                self.logger.info("新規認証を実行中...")
                if not self.credentials_file.exists():
                    raise FileNotFoundError(f"認証ファイルが見つかりません: {self.credentials_file}")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_file), self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # トークンを保存
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
            
            self.logger.info("認証完了")
        
        return build('drive', 'v3', credentials=creds)
    
    def _load_page_token(self) -> Optional[str]:
        """ページトークンの読み込み"""
        try:
            if self.page_token_file.exists():
                content = self.page_token_file.read_text(encoding='utf-8').strip()
                if content:
                    return content
        except Exception as e:
            self.logger.warning(f"ページトークン読み込みエラー: {e}")
        
        return None
    
    def _save_page_token(self, token: str):
        """ページトークンの保存"""
        try:
            self.page_token_file.write_text(token, encoding='utf-8')
        except Exception as e:
            self.logger.error(f"ページトークン保存エラー: {e}")
    
    def _get_initial_page_token(self) -> str:
        """初期ページトークンの取得"""
        try:
            response = self.service.changes().getStartPageToken().execute()
            return response.get('startPageToken')
        except HttpError as e:
            self.logger.error(f"初期ページトークン取得エラー: {e}")
            raise
    
    def _is_target_file(self, file_info: dict) -> bool:
        """対象ファイルかどうかの判定"""
        if not file_info:
            return False
        
        # ファイル名確認
        name = file_info.get('name', '')
        if not name:
            return False
        
        # 拡張子確認
        file_ext = Path(name).suffix.lower()
        if file_ext not in self.AUDIO_EXTENSIONS:
            return False
        
        # 親フォルダ確認
        parents = file_info.get('parents', [])
        if self.target_folder_id not in parents:
            return False
        
        # MIMEタイプ確認（追加安全性）
        mime_type = file_info.get('mimeType', '')
        if not mime_type.startswith('audio/'):
            return False
        
        return True
    
    def _is_upload_complete(self, file_info: dict) -> bool:
        """
        アップロード完了判定（シンプル版）
        
        MD5チェックサムの存在を主要指標として使用
        """
        # MD5チェックサムが存在すれば基本的に完了
        if file_info.get('md5Checksum'):
            return True
        
        # MD5がない場合は少し待ってから再確認
        self.logger.info(f"MD5チェックサム待機中: {file_info.get('name')}")
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
            with open(processed_file, 'a', encoding='utf-8') as f:
                f.write(f"{file_id}\n")
        except Exception as e:
            self.logger.error(f"処理済みファイル追加エラー: {e}")
    
    def check_for_new_files(self) -> List[dict]:
        """
        新しいファイルのチェック
        
        Returns:
            新しい音声ファイルのリスト
        """
        try:
            # ページトークン取得
            page_token = self._load_page_token()
            if not page_token:
                self.logger.info("初回実行: フォルダ内ファイルを直接チェック")
                return self._check_existing_files_directly()
            
            # 処理済みファイルリスト取得
            processed_files = self._get_processed_files()
            
            # Changes APIで変更を取得
            self.logger.info("Google Drive変更を確認中...")
            
            response = self.service.changes().list(
                pageToken=page_token,
                includeRemoved=False,
                spaces='drive',
                fields='nextPageToken,changes(file(id,name,size,md5Checksum,parents,mimeType,modifiedTime))'
            ).execute()
            
            new_files = []
            changes = response.get('changes', [])
            
            self.logger.info(f"{len(changes)}個の変更を検出")
            
            for change in changes:
                file_info = change.get('file')
                
                # 対象ファイルか確認
                if not self._is_target_file(file_info):
                    continue
                
                file_id = file_info['id']
                file_name = file_info['name']
                
                # 既に処理済みか確認
                if file_id in processed_files:
                    self.logger.debug(f"処理済みファイルをスキップ: {file_name}")
                    continue
                
                # アップロード完了か確認
                if not self._is_upload_complete(file_info):
                    self.logger.info(f"アップロード未完了: {file_name} (後で再確認)")
                    continue
                
                new_files.append(file_info)
                self.logger.info(f"新規ファイル検出: {file_name}")
            
            # ページトークン更新
            next_token = response.get('nextPageToken')
            if next_token:
                self._save_page_token(next_token)
            
            return new_files
            
        except HttpError as e:
            self.logger.error(f"Google Drive API エラー: {e}")
            raise
        except Exception as e:
            self.logger.error(f"ファイルチェック中にエラー: {e}")
            raise
    
    def _check_existing_files_directly(self) -> List[dict]:
        """
        初回実行時の既存ファイル直接チェック
        """
        self.logger.info("フォルダ内の既存ファイルを直接チェック中...")
        
        processed_files = self._get_processed_files()
        
        response = self.service.files().list(
            q=f"'{self.target_folder_id}' in parents and trashed=false",
            fields="files(id,name,size,md5Checksum,mimeType,modifiedTime,parents)",
            orderBy="modifiedTime desc"
        ).execute()
        
        all_files = response.get('files', [])
        target_files = []
        
        for file_info in all_files:
            file_id = file_info['id']
            file_name = file_info['name']
            
            # 処理済みかチェック
            if file_id in processed_files:
                continue
            
            # 対象ファイルかチェック
            if self._is_target_file(file_info):
                if self._is_upload_complete(file_info):
                    target_files.append(file_info)
                    self.logger.info(f"新規ファイル検出: {file_name}")
        
        # 初回実行後はページトークンを作成
        if not target_files:  # 新しいファイルがない場合のみ
            self.logger.info("初回ページトークンを作成中...")
            initial_token = self._get_initial_page_token()
            self._save_page_token(initial_token)
        
        return target_files
    
    def mark_file_processed(self, file_id: str):
        """ファイルを処理済みとしてマーク"""
        self._add_processed_file(file_id)
        self.logger.debug(f"処理済みファイルに追加: {file_id}")
    
    def get_file_details(self, file_id: str) -> Optional[dict]:
        """ファイルの詳細情報を取得"""
        try:
            response = self.service.files().get(
                fileId=file_id,
                fields='id,name,size,md5Checksum,mimeType,modifiedTime,parents'
            ).execute()
            return response
        except HttpError as e:
            self.logger.error(f"ファイル詳細取得エラー: {e}")
            return None
