"""
설정 위젯 모듈

자계 노출 측정기의 설정을 관리하는 위젯을 정의합니다.
"""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QGridLayout,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QMessageBox,
)
from PyQt5.QtCore import Qt, pyqtSlot
import serial


class SettingsWidget(QWidget):
    """설정 위젯 클래스"""

    def __init__(self, data_manager, logger):
        """SettingsWidget 클래스 초기화

        Args:
            data_manager (DataManager): 데이터 관리 객체
            logger (Logger): 로거 객체
        """
        super().__init__()
        self.data_manager = data_manager
        self.logger = logger

        self._init_ui()
        self._load_settings()
        self._connect_signals()

    def _init_ui(self):
        """UI 초기화"""
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)

        # 연결 설정 그룹
        connection_group = QGroupBox("연결 설정")
        connection_layout = QGridLayout()

        # 포트
        connection_layout.addWidget(QLabel("포트:"), 0, 0)
        self.port_edit = QLineEdit()
        connection_layout.addWidget(self.port_edit, 0, 1)

        # 전송 속도
        connection_layout.addWidget(QLabel("전송 속도:"), 1, 0)
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        connection_layout.addWidget(self.baudrate_combo, 1, 1)

        # 데이터 비트
        connection_layout.addWidget(QLabel("데이터 비트:"), 2, 0)
        self.bytesize_combo = QComboBox()
        self.bytesize_combo.addItems(["5", "6", "7", "8"])
        connection_layout.addWidget(self.bytesize_combo, 2, 1)

        # 패리티
        connection_layout.addWidget(QLabel("패리티:"), 3, 0)
        self.parity_combo = QComboBox()
        self.parity_combo.addItems(
            ["없음 (N)", "홀수 (O)", "짝수 (E)", "마크 (M)", "스페이스 (S)"]
        )
        connection_layout.addWidget(self.parity_combo, 3, 1)

        # 정지 비트
        connection_layout.addWidget(QLabel("정지 비트:"), 4, 0)
        self.stopbits_combo = QComboBox()
        self.stopbits_combo.addItems(["1", "1.5", "2"])
        connection_layout.addWidget(self.stopbits_combo, 4, 1)

        # 타임아웃
        connection_layout.addWidget(QLabel("타임아웃 (초):"), 5, 0)
        self.timeout_spin = QDoubleSpinBox()
        self.timeout_spin.setRange(0.1, 10.0)
        self.timeout_spin.setSingleStep(0.1)
        self.timeout_spin.setValue(1.0)
        connection_layout.addWidget(self.timeout_spin, 5, 1)

        connection_group.setLayout(connection_layout)
        main_layout.addWidget(connection_group)

        # 자동 새로고침 설정 그룹
        refresh_group = QGroupBox("자동 새로고침 설정")
        refresh_layout = QGridLayout()

        # 자동 새로고침 활성화
        self.auto_refresh_check = QCheckBox("자동 새로고침 활성화")
        refresh_layout.addWidget(self.auto_refresh_check, 0, 0, 1, 2)

        # 새로고침 간격
        refresh_layout.addWidget(QLabel("새로고침 간격 (초):"), 1, 0)
        self.refresh_interval_spin = QSpinBox()
        self.refresh_interval_spin.setRange(1, 60)
        self.refresh_interval_spin.setValue(5)
        refresh_layout.addWidget(self.refresh_interval_spin, 1, 1)

        refresh_group.setLayout(refresh_layout)
        main_layout.addWidget(refresh_group)

        # 버튼 레이아웃
        button_layout = QHBoxLayout()

        # 저장 버튼
        self.save_button = QPushButton("설정 저장")
        button_layout.addWidget(self.save_button)

        # 기본값 버튼
        self.default_button = QPushButton("기본값으로 복원")
        button_layout.addWidget(self.default_button)

        main_layout.addLayout(button_layout)

        # 여백 추가
        main_layout.addStretch()

    def _connect_signals(self):
        """시그널 연결"""
        # 버튼 시그널
        self.save_button.clicked.connect(self._save_settings)
        self.default_button.clicked.connect(self._restore_defaults)

    def _load_settings(self):
        """설정 로드"""
        settings = self.data_manager.settings

        # 연결 설정
        connection = settings.get("connection", {})
        self.port_edit.setText(connection.get("port", ""))

        baudrate = connection.get("baudrate", 9600)
        index = self.baudrate_combo.findText(str(baudrate))
        if index >= 0:
            self.baudrate_combo.setCurrentIndex(index)

        bytesize = connection.get("bytesize", 8)
        index = self.bytesize_combo.findText(str(bytesize))
        if index >= 0:
            self.bytesize_combo.setCurrentIndex(index)

        parity = connection.get("parity", "N")
        parity_map = {"N": 0, "O": 1, "E": 2, "M": 3, "S": 4}
        self.parity_combo.setCurrentIndex(parity_map.get(parity, 0))

        stopbits = connection.get("stopbits", 1)
        stopbits_map = {1: 0, 1.5: 1, 2: 2}
        self.stopbits_combo.setCurrentIndex(stopbits_map.get(stopbits, 0))

        self.timeout_spin.setValue(connection.get("timeout", 1.0))

        # 자동 새로고침 설정
        auto_refresh = settings.get("auto_refresh", {})
        self.auto_refresh_check.setChecked(auto_refresh.get("enabled", False))
        self.refresh_interval_spin.setValue(auto_refresh.get("interval", 5))

        self.logger.info("설정 로드 완료")

    def _save_settings(self):
        """설정 저장"""
        # 현재 설정 가져오기
        settings = self.data_manager.settings.copy()

        # 연결 설정 업데이트
        parity_map = {0: "N", 1: "O", 2: "E", 3: "M", 4: "S"}
        stopbits_map = {0: 1, 1: 1.5, 2: 2}

        settings["connection"] = {
            "port": self.port_edit.text(),
            "baudrate": int(self.baudrate_combo.currentText()),
            "bytesize": int(self.bytesize_combo.currentText()),
            "parity": parity_map[self.parity_combo.currentIndex()],
            "stopbits": stopbits_map[self.stopbits_combo.currentIndex()],
            "timeout": self.timeout_spin.value(),
        }

        # 자동 새로고침 설정 업데이트
        settings["auto_refresh"] = {
            "enabled": self.auto_refresh_check.isChecked(),
            "interval": self.refresh_interval_spin.value(),
        }

        # 설정 저장
        success = self.data_manager.save_settings(settings)

        if success:
            QMessageBox.information(self, "설정 저장", "설정이 저장되었습니다.")
            self.logger.info("설정 저장 완료")
        else:
            QMessageBox.warning(
                self, "설정 저장 실패", "설정을 저장하는 중 오류가 발생했습니다."
            )
            self.logger.error("설정 저장 실패")

    def _restore_defaults(self):
        """기본 설정으로 복원"""
        # 확인 대화 상자
        reply = QMessageBox.question(
            self,
            "기본값으로 복원",
            "모든 설정을 기본값으로 복원하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        # 기본 설정
        default_settings = {
            "connection": {
                "port": "",
                "baudrate": 9600,
                "bytesize": 8,
                "parity": "N",
                "stopbits": 1,
                "timeout": 1.0,
            },
            "auto_refresh": {"enabled": False, "interval": 5},
        }

        # 설정 저장
        success = self.data_manager.save_settings(default_settings)

        if success:
            # UI 업데이트
            self._load_settings()

            QMessageBox.information(
                self, "기본값으로 복원", "설정이 기본값으로 복원되었습니다."
            )
            self.logger.info("설정 기본값으로 복원 완료")
        else:
            QMessageBox.warning(
                self, "복원 실패", "설정을 기본값으로 복원하는 중 오류가 발생했습니다."
            )
            self.logger.error("설정 기본값으로 복원 실패")
