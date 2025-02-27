"""
로깅 유틸리티 모듈

애플리케이션 로깅 기능을 제공합니다.
"""
import logging
import os
from datetime import datetime


class Logger:
    """로깅 유틸리티 클래스"""
    
    # 로그 레벨
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    
    def __init__(self, name="magnetic_field_monitor", log_level=logging.INFO):
        """Logger 클래스 초기화
        
        Args:
            name (str): 로거 이름 (기본값: "magnetic_field_monitor")
            log_level (int): 로그 레벨 (기본값: logging.INFO)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # 로그 포맷 설정
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # 콘솔 핸들러 설정
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 파일 핸들러 설정
        self._setup_file_handler(formatter)
    
    def _setup_file_handler(self, formatter):
        """파일 핸들러 설정
        
        Args:
            formatter (logging.Formatter): 로그 포맷
        """
        # 로그 디렉토리 생성
        log_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # 로그 파일 이름 설정 (날짜 포함)
        log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
        
        # 파일 핸들러 설정
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def debug(self, message):
        """디버그 로그 기록
        
        Args:
            message (str): 로그 메시지
        """
        self.logger.debug(message)
    
    def info(self, message):
        """정보 로그 기록
        
        Args:
            message (str): 로그 메시지
        """
        self.logger.info(message)
    
    def warning(self, message):
        """경고 로그 기록
        
        Args:
            message (str): 로그 메시지
        """
        self.logger.warning(message)
    
    def error(self, message):
        """오류 로그 기록
        
        Args:
            message (str): 로그 메시지
        """
        self.logger.error(message)
    
    def critical(self, message):
        """심각한 오류 로그 기록
        
        Args:
            message (str): 로그 메시지
        """
        self.logger.critical(message)
    
    def set_level(self, level):
        """로그 레벨 설정
        
        Args:
            level (int): 로그 레벨
        """
        self.logger.setLevel(level) 