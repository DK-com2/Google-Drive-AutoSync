#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本的なユニットテストケース
BirdNET AutoPipelineの主要機能をテストします
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# テスト対象モジュールのインポート
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from drive_monitor import DriveMonitor
from file_processor import FileProcessor


class TestDriveMonitor(unittest.TestCase):
    """DriveMonitorクラスのテスト"""
    
    def setUp(self):
        """テスト前の初期設定"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = {
            'google_drive': {
                'target_folder_id': 'test_folder_id',
                'credentials_file': 'credentials.json',
                'token_file': 'token.pickle',
                'page_token_file': 'page_token.txt'
            }
        }
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('drive_monitor.build')
    @patch('drive_monitor.pickle.load')
    @patch('drive_monitor.Path.exists')
    def test_authentication_with_existing_token(self, mock_exists, mock_pickle_load, mock_build):
        """既存トークンでの認証テスト"""
        # モックの設定
        mock_exists.return_value = True
        mock_creds = Mock()
        mock_creds.valid = True
        mock_pickle_load.return_value = mock_creds
        
        # テスト実行
        with patch.object(Path, 'parent', new_callable=lambda: Path(self.temp_dir)):
            monitor = DriveMonitor(self.test_config)
        
        # 検証
        mock_build.assert_called_once_with('drive', 'v3', credentials=mock_creds)
    
    def test_is_target_file_valid_audio(self):
        """有効な音声ファイルの判定テスト"""
        # テストデータ
        file_info = {
            'name': 'recording_20240620.wav',
            'parents': ['test_folder_id'],
            'mimeType': 'audio/wav'
        }
        
        # モックDriveMonitor作成
        with patch.object(DriveMonitor, '__init__', lambda x, y: None):
            monitor = DriveMonitor(None)
            monitor.target_folder_id = 'test_folder_id'
            monitor.AUDIO_EXTENSIONS = {'.wav', '.mp3', '.flac'}
            
            # テスト実行
            result = monitor._is_target_file(file_info)
            
            # 検証
            self.assertTrue(result)
    
    def test_is_target_file_invalid_extension(self):
        """無効な拡張子のファイル判定テスト"""
        # テストデータ
        file_info = {
            'name': 'document.pdf',
            'parents': ['test_folder_id'],
            'mimeType': 'application/pdf'
        }
        
        # モックDriveMonitor作成
        with patch.object(DriveMonitor, '__init__', lambda x, y: None):
            monitor = DriveMonitor(None)
            monitor.target_folder_id = 'test_folder_id'
            monitor.AUDIO_EXTENSIONS = {'.wav', '.mp3', '.flac'}
            
            # テスト実行
            result = monitor._is_target_file(file_info)
            
            # 検証
            self.assertFalse(result)
    
    def test_is_upload_complete_with_md5(self):
        """MD5チェックサム有りのアップロード完了判定テスト"""
        file_info = {
            'name': 'test.wav',
            'md5Checksum': 'abcd1234567890'
        }
        
        with patch.object(DriveMonitor, '__init__', lambda x, y: None):
            monitor = DriveMonitor(None)
            
            # テスト実行
            result = monitor._is_upload_complete(file_info)
            
            # 検証
            self.assertTrue(result)
    
    def test_is_upload_complete_without_md5(self):
        """MD5チェックサム無しのアップロード完了判定テスト"""
        file_info = {
            'name': 'test.wav',
            'md5Checksum': None
        }
        
        with patch.object(DriveMonitor, '__init__', lambda x, y: None):
            monitor = DriveMonitor(None)
            monitor.logger = Mock()
            
            # テスト実行
            result = monitor._is_upload_complete(file_info)
            
            # 検証
            self.assertFalse(result)


class TestFileProcessor(unittest.TestCase):
    """FileProcessorクラスのテスト"""
    
    def setUp(self):
        """テスト前の初期設定"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = {
            'file_processing': {
                'download_path': self.temp_dir,
                'chunk_size_mb': 5,
                'min_free_space_gb': 1
            }
        }
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('file_processor.os.statvfs')
    def test_check_disk_space_sufficient(self, mock_statvfs):
        """十分なディスク容量がある場合のテスト"""
        # モックの設定（十分な空き容量）
        mock_stat = Mock()
        mock_stat.f_frsize = 4096
        mock_stat.f_bavail = 1000000  # 4GB相当
        mock_statvfs.return_value = mock_stat
        
        with patch.object(FileProcessor, '__init__', lambda x, y: None):
            processor = FileProcessor(None)
            processor.min_free_space = 1024 * 1024 * 1024  # 1GB
            processor.download_path = Path(self.temp_dir)
            processor.logger = Mock()
            
            # テスト実行（50MB必要）
            result = processor._check_disk_space(50 * 1024 * 1024)
            
            # 検証
            self.assertTrue(result)
    
    @patch('file_processor.os.statvfs')
    def test_check_disk_space_insufficient(self, mock_statvfs):
        """ディスク容量不足の場合のテスト"""
        # モックの設定（容量不足）
        mock_stat = Mock()
        mock_stat.f_frsize = 4096
        mock_stat.f_bavail = 1000  # 4MB相当
        mock_statvfs.return_value = mock_stat
        
        with patch.object(FileProcessor, '__init__', lambda x, y: None):
            processor = FileProcessor(None)
            processor.min_free_space = 1024 * 1024 * 1024  # 1GB
            processor.download_path = Path(self.temp_dir)
            processor.logger = Mock()
            
            # テスト実行（50MB必要）
            result = processor._check_disk_space(50 * 1024 * 1024)
            
            # 検証
            self.assertFalse(result)
    
    def test_calculate_md5(self):
        """MD5計算のテスト"""
        # テストファイル作成
        test_file = Path(self.temp_dir) / "test.txt"
        test_content = b"Hello, BirdNET!"
        test_file.write_bytes(test_content)
        
        with patch.object(FileProcessor, '__init__', lambda x, y: None):
            processor = FileProcessor(None)
            processor.logger = Mock()
            
            # テスト実行
            result = processor._calculate_md5(test_file)
            
            # 検証（期待するMD5ハッシュ値）
            import hashlib
            expected_md5 = hashlib.md5(test_content).hexdigest()
            self.assertEqual(result, expected_md5)
    
    def test_verify_file_integrity_success(self):
        """ファイル整合性確認成功のテスト"""
        # テストファイル作成
        test_file = Path(self.temp_dir) / "test.wav"
        test_content = b"RIFF" + b"0" * 100  # 簡単なWAVファイルもどき
        test_file.write_bytes(test_content)
        
        import hashlib
        expected_md5 = hashlib.md5(test_content).hexdigest()
        expected_size = len(test_content)
        
        with patch.object(FileProcessor, '__init__', lambda x, y: None):
            processor = FileProcessor(None)
            processor.logger = Mock()
            
            # テスト実行
            result = processor._verify_file_integrity(test_file, expected_md5, expected_size)
            
            # 検証
            self.assertTrue(result)
    
    def test_verify_file_integrity_size_mismatch(self):
        """ファイルサイズ不一致のテスト"""
        # テストファイル作成
        test_file = Path(self.temp_dir) / "test.wav"
        test_content = b"RIFF" + b"0" * 100
        test_file.write_bytes(test_content)
        
        import hashlib
        expected_md5 = hashlib.md5(test_content).hexdigest()
        wrong_size = 999  # 間違ったサイズ
        
        with patch.object(FileProcessor, '__init__', lambda x, y: None):
            processor = FileProcessor(None)
            processor.logger = Mock()
            
            # テスト実行
            result = processor._verify_file_integrity(test_file, expected_md5, wrong_size)
            
            # 検証
            self.assertFalse(result)
    
    def test_analyze_audio_dummy_result(self):
        """音声解析ダミー結果のテスト"""
        # テストファイル作成
        test_file = Path(self.temp_dir) / "test.wav"
        test_file.write_bytes(b"dummy audio content")
        
        with patch.object(FileProcessor, '__init__', lambda x, y: None):
            processor = FileProcessor(None)
            processor.logger = Mock()
            
            # テスト実行
            result = processor.analyze_audio(test_file)
            
            # 検証
            self.assertIsNotNone(result)
            self.assertIn('file_name', result)
            self.assertIn('segments', result)
            self.assertIn('summary', result)
            self.assertEqual(result['file_name'], 'test.wav')
            self.assertIsInstance(result['segments'], list)
    
    def test_save_analysis_result(self):
        """解析結果保存のテスト"""
        # テスト結果データ
        test_result = {
            'file_name': 'test.wav',
            'segments': [],
            'summary': {'total_segments': 0}
        }
        
        with patch.object(FileProcessor, '__init__', lambda x, y: None):
            processor = FileProcessor(None)
            processor.results_path = Path(self.temp_dir)
            processor.logger = Mock()
            
            # テスト実行
            result_file = processor.save_analysis_result(test_result, 'test.wav')
            
            # 検証
            self.assertTrue(result_file.exists())
            self.assertTrue(result_file.name.startswith('analysis_'))
            self.assertTrue(result_file.name.endswith('_test.json'))
            
            # 保存内容の確認
            with open(result_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            self.assertEqual(saved_data['file_name'], 'test.wav')


class TestIntegration(unittest.TestCase):
    """統合テスト"""
    
    def setUp(self):
        """テスト前の初期設定"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = {
            'google_drive': {
                'target_folder_id': 'test_folder_id',
                'credentials_file': 'credentials.json',
                'token_file': 'token.pickle',
                'page_token_file': 'page_token.txt'
            },
            'file_processing': {
                'download_path': self.temp_dir,
                'chunk_size_mb': 5,
                'min_free_space_gb': 1
            }
        }
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('drive_monitor.build')
    @patch('drive_monitor.pickle.load')
    @patch('drive_monitor.Path.exists')
    def test_config_loading(self, mock_exists, mock_pickle_load, mock_build):
        """設定読み込みの統合テスト"""
        # モックの設定
        mock_exists.return_value = True
        mock_creds = Mock()
        mock_creds.valid = True
        mock_pickle_load.return_value = mock_creds
        
        # テスト実行
        with patch.object(Path, 'parent', new_callable=lambda: Path(self.temp_dir)):
            monitor = DriveMonitor(self.test_config)
            processor = FileProcessor(self.test_config)
        
        # 検証
        self.assertEqual(monitor.target_folder_id, 'test_folder_id')
        self.assertEqual(str(processor.download_path), self.temp_dir)


if __name__ == '__main__':
    # テスト実行
    unittest.main(verbosity=2)
