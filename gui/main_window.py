"""
메인 윈도우 모듈

자계 노출 측정기 모니터링 시스템의 메인 윈도우를 정의합니다.
"""

import os
import sys
from PyQt5.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QAction,
    QMessageBox,
    QFileDialog,
    QApplication,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
import logging

from gui.connection_widget import ConnectionWidget
from gui.status_widget import StatusWidget
from gui.control_widget import ControlWidget
from gui.log_widget import LogWidget
from gui.settings_widget import SettingsWidget

from communication.serial_connection import SerialConnection
from commands.command_handler import CommandHandler
from data.data_manager import DataManager
from utils.logger import Logger


class MainWindow(QMainWindow):
    """메인 윈도우 클래스"""

    def __init__(self):
        """MainWindow 클래스 초기화"""
        super().__init__()

        # 애플리케이션 정보
        self.app_title = "자계 노출 측정기 모니터링 시스템"
        self.app_version = "1.0.0"
        self.app_copyright = "Copyright © 2025 PAPKY. All rights reserved."

        # 데이터 디렉토리 설정
        self.data_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
        )
        os.makedirs(self.data_dir, exist_ok=True)

        # 로거 초기화
        self.logger = Logger("magnetic_field_monitor", logging.DEBUG)
        self.logger.info(f"{self.app_title} v{self.app_version} 시작")

        # 데이터 관리자 초기화
        self.data_manager = DataManager(self.data_dir, self.logger)

        # 시리얼 연결 초기화
        self.serial_connection = SerialConnection(self.logger)

        # 명령 처리기 초기화
        self.command_handler = CommandHandler(
            self.serial_connection, self.logger, self.data_manager
        )

        # UI 초기화
        self._init_ui()

        # 시그널 연결
        self._connect_signals()

        # 상태 업데이트 타이머
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)

    def _init_ui(self):
        """UI 초기화"""
        # 윈도우 설정
        self.setWindowTitle(self.app_title)
        self.setMinimumSize(800, 600)
        self.setWindowIcon(QIcon("resources/icon.png"))

        # 탭 위젯 생성
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # 연결 탭
        self.connection_widget = ConnectionWidget(
            self.serial_connection, self.data_manager, self.logger
        )
        self.tab_widget.addTab(self.connection_widget, "연결")

        # 상태 탭
        self.status_widget = StatusWidget(self.command_handler, self.logger)
        self.tab_widget.addTab(self.status_widget, "상태")

        # 제어 탭
        self.control_widget = ControlWidget(self.command_handler, self.logger)
        self.tab_widget.addTab(self.control_widget, "제어")

        # 로그 탭
        self.log_widget = LogWidget(self.data_manager, self.logger)
        self.tab_widget.addTab(self.log_widget, "로그")

        # 설정 탭
        self.settings_widget = SettingsWidget(self.data_manager, self.logger)
        self.tab_widget.addTab(self.settings_widget, "설정")

        # 메뉴바 생성
        self._create_menu_bar()

        # 상태바 생성
        self.statusBar().showMessage("준비")

    def _create_menu_bar(self):
        """메뉴바 생성"""
        # 메뉴바
        menubar = self.menuBar()

        # 파일 메뉴
        file_menu = menubar.addMenu("파일")

        # 연결 메뉴 항목
        connect_action = QAction("연결", self)
        connect_action.setShortcut("Ctrl+C")
        connect_action.triggered.connect(self._connect_device)
        file_menu.addAction(connect_action)

        # 연결 해제 메뉴 항목
        disconnect_action = QAction("연결 해제", self)
        disconnect_action.setShortcut("Ctrl+D")
        disconnect_action.triggered.connect(self._disconnect_device)
        file_menu.addAction(disconnect_action)

        file_menu.addSeparator()

        # 종료 메뉴 항목
        exit_action = QAction("종료", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 도구 메뉴
        tools_menu = menubar.addMenu("도구")

        # 로그 내보내기 메뉴 항목
        export_logs_action = QAction("로그 내보내기", self)
        export_logs_action.triggered.connect(self._export_logs)
        tools_menu.addAction(export_logs_action)

        # 설정 메뉴 항목
        settings_action = QAction("설정", self)
        settings_action.triggered.connect(self._show_settings)
        tools_menu.addAction(settings_action)

        # 도움말 메뉴
        help_menu = menubar.addMenu("도움말")

        # 정보 메뉴 항목
        about_action = QAction("정보", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _connect_signals(self):
        """시그널 연결"""
        # 연결 상태 변경 시그널
        self.serial_connection.connection_changed.connect(self._on_connection_changed)

        # 상태 업데이트 시그널
        self.serial_connection.status_updated.connect(self._on_status_updated)

        # 제어 상태 업데이트 시그널
        self.serial_connection.control_updated.connect(self._on_control_updated)

    def _connect_device(self):
        """장치 연결"""
        # 연결 탭으로 이동
        self.tab_widget.setCurrentWidget(self.connection_widget)
        # 연결 버튼 클릭
        self.connection_widget.connect_button.click()

    def _disconnect_device(self):
        """장치 연결 해제"""
        # 연결 탭으로 이동
        self.tab_widget.setCurrentWidget(self.connection_widget)
        # 연결 해제 버튼 클릭
        self.connection_widget.disconnect_button.click()

    def _export_logs(self):
        """로그 내보내기"""
        # 로그 탭으로 이동
        self.tab_widget.setCurrentWidget(self.log_widget)
        # 내보내기 버튼 클릭
        self.log_widget.export_button.click()

    def _show_settings(self):
        """설정 표시"""
        # 설정 탭으로 이동
        self.tab_widget.setCurrentWidget(self.settings_widget)

    def _show_about(self):
        """정보 대화 상자 표시"""
        about_text = f"""
        <h2>{self.app_title}</h2>
        <p>버전: {self.app_version}</p>
        <p>{self.app_copyright}</p>
        <p>자계 노출 측정기와 통신하여 상태를 모니터링하고 제어하는 시스템입니다.</p>
        """
        QMessageBox.about(self, "정보", about_text)

    def _on_connection_changed(self, connected):
        """연결 상태 변경 처리

        Args:
            connected (bool): 연결 상태
        """
        if connected:
            self.statusBar().showMessage("장치 연결됨")
            self.logger.info("장치 연결됨")

            # 자동 상태 업데이트 시작
            auto_refresh = self.data_manager.settings.get("auto_refresh", {})
            if auto_refresh.get("enabled", False):
                interval = auto_refresh.get("interval", 5) * 1000  # 밀리초 단위로 변환
                self.status_timer.start(interval)
                self.logger.debug(f"자동 상태 업데이트 시작 (간격: {interval}ms)")
        else:
            self.statusBar().showMessage("장치 연결 해제됨")
            self.logger.info("장치 연결 해제됨")

            # 자동 상태 업데이트 중지
            if self.status_timer.isActive():
                self.status_timer.stop()
                self.logger.debug("자동 상태 업데이트 중지")

    def _update_status(self):
        """상태 업데이트"""
        if self.serial_connection.is_connected():
            # 상태 쿼리 요청
            self.command_handler.query_status()
            self.logger.debug("자동 상태 업데이트 요청")

    def _on_status_updated(self, status_info):
        """상태 업데이트 처리

        Args:
            status_info (dict): 상태 정보
        """
        # 상태 위젯 업데이트
        self.status_widget.update_status(status_info)

        # 제어 위젯 업데이트
        self.control_widget.update_from_status(status_info)

        # 로그 추가
        log_data = self.data_manager.add_log(status_info)
        if log_data:
            self.log_widget.add_log_entry(log_data)

        self.logger.debug("상태 정보 업데이트 완료")

    def _on_control_updated(self, control_type, status):
        """제어 상태 업데이트 처리

        Args:
            control_type (str): 제어 타입
            status (bool): 상태 값
        """
        # 제어 위젯 업데이트
        self.control_widget.update_control_status(control_type, status)
        self.logger.debug(f"제어 상태 업데이트: {control_type}={status}")

    def closeEvent(self, event):
        """윈도우 종료 이벤트 처리

        Args:
            event: 종료 이벤트
        """
        # 연결 해제
        if self.serial_connection.is_connected():
            self.serial_connection.disconnect()

        # 타이머 중지
        if self.status_timer.isActive():
            self.status_timer.stop()

        self.logger.info(f"{self.app_title} 종료")
        event.accept()
