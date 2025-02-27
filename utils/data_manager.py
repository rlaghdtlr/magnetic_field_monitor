"""
데이터 관리 모듈

로그 데이터 저장 및 설정 관리 기능을 제공합니다.
"""
import os
import json
import csv
from datetime import datetime


class DataManager:
    """데이터 저장 및 관리 클래스"""
    
    def __init__(self):
        """DataManager 클래스 초기화"""
        # 데이터 디렉토리 생성
        self.data_dir = os.path.join(os.getcwd(), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 로그 데이터 디렉토리 생성
        self.log_data_dir = os.path.join(self.data_dir, "logs")
        os.makedirs(self.log_data_dir, exist_ok=True)
        
        # 설정 파일 경로
        self.settings_file = os.path.join(self.data_dir, "settings.json")
        
        # 기본 설정 로드
        self.settings = self._load_settings()
    
    def _load_settings(self):
        """설정 파일 로드
        
        Returns:
            dict: 설정 데이터
        """
        default_settings = {
            "serial": {
                "port": "",
                "baudrate": 9600,
                "bytesize": 8,
                "parity": "N",
                "stopbits": 1,
                "timeout": 1
            },
            "ui": {
                "theme": "light",
                "language": "ko",
                "font_size": 10
            },
            "logging": {
                "level": "INFO",
                "max_log_files": 10
            }
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                return settings
            except (json.JSONDecodeError, IOError):
                return default_settings
        else:
            return default_settings
    
    def save_settings(self):
        """설정 파일 저장"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            return True
        except IOError:
            return False
    
    def update_settings(self, section, key, value):
        """설정 업데이트
        
        Args:
            section (str): 설정 섹션
            key (str): 설정 키
            value: 설정 값
            
        Returns:
            bool: 업데이트 성공 여부
        """
        if section in self.settings and key in self.settings[section]:
            self.settings[section][key] = value
            return self.save_settings()
        return False
    
    def get_setting(self, section, key, default=None):
        """설정 값 가져오기
        
        Args:
            section (str): 설정 섹션
            key (str): 설정 키
            default: 기본값 (설정이 없는 경우)
            
        Returns:
            설정 값 또는 기본값
        """
        if section in self.settings and key in self.settings[section]:
            return self.settings[section][key]
        return default
    
    def save_log_data(self, log_data, filename=None):
        """로그 데이터 저장
        
        Args:
            log_data (list): 로그 데이터 (딕셔너리 리스트)
            filename (str): 파일 이름 (기본값: 현재 날짜와 시간)
            
        Returns:
            str: 저장된 파일 경로 또는 None (저장 실패 시)
        """
        if not filename:
            filename = f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        file_path = os.path.join(self.log_data_dir, filename)
        
        try:
            if log_data and isinstance(log_data, list) and isinstance(log_data[0], dict):
                fieldnames = log_data[0].keys()
                
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(log_data)
                
                return file_path
            return None
        except IOError:
            return None
    
    def load_log_data(self, filename):
        """로그 데이터 로드
        
        Args:
            filename (str): 파일 이름
            
        Returns:
            list: 로그 데이터 (딕셔너리 리스트) 또는 None (로드 실패 시)
        """
        file_path = os.path.join(self.log_data_dir, filename)
        
        if not os.path.exists(file_path):
            return None
        
        try:
            log_data = []
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    log_data.append(row)
            
            return log_data
        except IOError:
            return None
    
    def get_log_files(self):
        """로그 파일 목록 가져오기
        
        Returns:
            list: 로그 파일 목록
        """
        if not os.path.exists(self.log_data_dir):
            return []
        
        return [f for f in os.listdir(self.log_data_dir) if f.endswith('.csv')] 