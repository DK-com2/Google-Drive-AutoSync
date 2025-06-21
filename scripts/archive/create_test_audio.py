#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
テスト用音声ファイル作成スクリプト
Google Driveでテストするための簡単な音声ファイルを作成します
"""

import wave
import numpy as np
from pathlib import Path

def create_test_audio_file(filename, duration=10, sample_rate=22050):
    """
    テスト用の音声ファイルを作成
    
    Args:
        filename: 出力ファイル名
        duration: 長さ（秒）
        sample_rate: サンプリングレート
    """
    # 正弦波を生成（鳥の鳴き声のような音）
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # 複数の周波数を組み合わせて鳥の鳴き声風に
    frequency1 = 2000  # 2kHz
    frequency2 = 3000  # 3kHz
    frequency3 = 1500  # 1.5kHz
    
    # 音声波形生成
    audio = (np.sin(2 * np.pi * frequency1 * t) * 0.3 +
             np.sin(2 * np.pi * frequency2 * t) * 0.2 +
             np.sin(2 * np.pi * frequency3 * t) * 0.2)
    
    # 音量調整（-32768 to 32767の範囲）
    audio = (audio * 16384).astype(np.int16)
    
    # WAVファイルとして保存
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # モノラル
        wav_file.setsampwidth(2)  # 16bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio.tobytes())

def main():
    """テスト音声ファイル作成"""
    output_dir = Path("test_audio")
    output_dir.mkdir(exist_ok=True)
    
    # 複数のテストファイルを作成
    test_files = [
        ("test_bird_recording_1.wav", 15),
        ("test_bird_recording_2.wav", 20),
        ("test_bird_recording_3.wav", 10)
    ]
    
    print("🎵 テスト用音声ファイルを作成中...")
    
    for filename, duration in test_files:
        filepath = output_dir / filename
        create_test_audio_file(str(filepath), duration)
        file_size = filepath.stat().st_size
        print(f"✅ 作成完了: {filename} ({file_size/1024:.1f}KB, {duration}秒)")
    
    print(f"\n📁 作成されたファイルは {output_dir} フォルダにあります")
    print("📤 これらのファイルをGoogle Driveの対象フォルダにアップロードしてテストしてください")

if __name__ == "__main__":
    try:
        main()
    except ImportError:
        print("❌ numpy が必要です。以下のコマンドでインストールしてください:")
        print("pip install numpy")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
