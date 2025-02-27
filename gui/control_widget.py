"""
제어 위젯 모듈

자계 노출 측정기를 제어하는 위젯을 정의합니다.
"""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QGridLayout,
    QRadioButton,
    QButtonGroup,
    QMessageBox,
)
from PyQt5.QtCore import Qt, pyqtSlot


class ControlWidget(QWidget):
    """제어 위젯 클래스"""

    def __init__(self, command_handler, logger):
        """ControlWidget 클래스 초기화

        Args:
            command_handler (CommandHandler): 명령 처리 관리 객체
            logger (Logger): 로거 객체
        """
        super().__init__()
        self.command_handler = command_handler
        self.logger = logger

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """UI 초기화"""
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)

        # 자계 제어 그룹
        field_group = QGroupBox("자계 제어")
        field_layout = QGridLayout()

        # 자계 On/Off 라디오 버튼
        field_layout.addWidget(QLabel("자계 상태:"), 0, 0)
        self.field_on_radio = QRadioButton("ON")
        self.field_off_radio = QRadioButton("OFF")
        self.field_button_group = QButtonGroup()
        self.field_button_group.addButton(self.field_on_radio, 0)
        self.field_button_group.addButton(self.field_off_radio, 1)
        field_layout.addWidget(self.field_on_radio, 0, 1)
        field_layout.addWidget(self.field_off_radio, 0, 2)

        # 자계 제어 버튼
        self.field_control_button = QPushButton("자계 제어")
        field_layout.addWidget(self.field_control_button, 0, 3)

        field_group.setLayout(field_layout)
        main_layout.addWidget(field_group)

        # 감지 제어 그룹
        detection_group = QGroupBox("감지 제어")
        detection_layout = QGridLayout()

        # 감지 모드 라디오 버튼
        detection_layout.addWidget(QLabel("감지 모드:"), 0, 0)
        self.live_mode_radio = QRadioButton("LIVE")
        self.max_mode_radio = QRadioButton("MAX")
        self.detection_button_group = QButtonGroup()
        self.detection_button_group.addButton(self.live_mode_radio, 0)
        self.detection_button_group.addButton(self.max_mode_radio, 1)
        detection_layout.addWidget(self.live_mode_radio, 0, 1)
        detection_layout.addWidget(self.max_mode_radio, 0, 2)

        # 감지 제어 버튼
        self.detection_control_button = QPushButton("감지 모드 설정")
        detection_layout.addWidget(self.detection_control_button, 0, 3)

        detection_group.setLayout(detection_layout)
        main_layout.addWidget(detection_group)

        # 단위 설정 그룹
        unit_group = QGroupBox("단위 설정")
        unit_layout = QGridLayout()

        # 단위 라디오 버튼
        unit_layout.addWidget(QLabel("단위:"), 0, 0)
        self.ut_radio = QRadioButton("μT")
        self.mg_radio = QRadioButton("mG")
        self.unit_button_group = QButtonGroup()
        self.unit_button_group.addButton(self.ut_radio, 0)
        self.unit_button_group.addButton(self.mg_radio, 1)
        unit_layout.addWidget(self.ut_radio, 0, 1)
        unit_layout.addWidget(self.mg_radio, 0, 2)

        # 단위 설정 버튼
        self.unit_control_button = QPushButton("단위 설정")
        unit_layout.addWidget(self.unit_control_button, 0, 3)

        unit_group.setLayout(unit_layout)
        main_layout.addWidget(unit_group)

        # 여백 추가
        main_layout.addStretch()

    def _connect_signals(self):
        """시그널 연결"""
        # 버튼 시그널
        self.field_control_button.clicked.connect(self._control_field)
        self.detection_control_button.clicked.connect(self._control_detection)
        self.unit_control_button.clicked.connect(self._set_unit)

    @pyqtSlot()
    def _control_field(self):
        """자계 제어"""
        # 선택된 상태 확인
        field_on = self.field_on_radio.isChecked()

        # 자계 제어 명령 전송
        self.logger.debug(f"자계 {'활성화' if field_on else '비활성화'} 요청")
        success = self.command_handler.control_b_field(field_on)

        # 결과 처리
        if success:
            QMessageBox.information(
                self,
                "자계 제어",
                f"자계가 {'활성화' if field_on else '비활성화'}되었습니다.",
            )
            self.logger.info(f"자계 {'활성화' if field_on else '비활성화'} 성공")
        else:
            QMessageBox.warning(
                self,
                "자계 제어",
                f"자계 {'활성화' if field_on else '비활성화'} 실패",
            )
            self.logger.error(f"자계 {'활성화' if field_on else '비활성화'} 실패")

    @pyqtSlot()
    def _control_detection(self):
        """감지 제어"""
        # 선택된 모드 확인
        live_mode = self.live_mode_radio.isChecked()

        # 감지 제어 명령 전송
        self.logger.debug(f"감지 모드 {'LIVE' if live_mode else 'MAX'} 설정 요청")
        success = self.command_handler.control_detection(live_mode)

        # 결과 처리
        if success:
            QMessageBox.information(
                self,
                "감지 모드 설정",
                f"감지 모드가 {'LIVE' if live_mode else 'MAX'}로 설정되었습니다.",
            )
            self.logger.info(f"감지 모드 {'LIVE' if live_mode else 'MAX'} 설정 성공")
        else:
            QMessageBox.warning(
                self,
                "감지 모드 설정",
                f"감지 모드 {'LIVE' if live_mode else 'MAX'} 설정 실패",
            )
            self.logger.error(f"감지 모드 {'LIVE' if live_mode else 'MAX'} 설정 실패")

    @pyqtSlot()
    def _set_unit(self):
        """단위 설정"""
        # 선택된 단위 확인
        use_ut = self.ut_radio.isChecked()

        # 단위 설정 명령 전송
        self.logger.debug(f"단위 {'μT' if use_ut else 'mG'} 설정 요청")
        success = self.command_handler.set_unit(use_ut)

        # 결과 처리
        if success:
            QMessageBox.information(
                self,
                "단위 설정",
                f"단위가 {'μT' if use_ut else 'mG'}로 설정되었습니다.",
            )
            self.logger.info(f"단위 {'μT' if use_ut else 'mG'} 설정 성공")
        else:
            QMessageBox.warning(
                self,
                "단위 설정",
                f"단위 {'μT' if use_ut else 'mG'} 설정 실패",
            )
            self.logger.error(f"단위 {'μT' if use_ut else 'mG'} 설정 실패")

    @pyqtSlot(str, bool)
    def update_control_status(self, control_type, status):
        """제어 상태 업데이트

        Args:
            control_type (str): 제어 타입 ('b_field', 'detection', 'unit')
            status (bool): 상태 값
        """
        if control_type == "b_field":
            # 자계 상태 업데이트
            self.field_on_radio.setChecked(status)
            self.field_off_radio.setChecked(not status)
            self.logger.debug(f"자계 상태 UI 업데이트: {'ON' if status else 'OFF'}")
        elif control_type == "detection":
            # 감지 모드 업데이트
            self.live_mode_radio.setChecked(status)
            self.max_mode_radio.setChecked(not status)
            self.logger.debug(f"감지 모드 UI 업데이트: {'LIVE' if status else 'MAX'}")
        elif control_type == "unit":
            # 단위 업데이트
            self.ut_radio.setChecked(status)
            self.mg_radio.setChecked(not status)
            self.logger.debug(f"단위 UI 업데이트: {'μT' if status else 'mG'}")

    def update_from_status(self, status_info):
        """상태 정보로부터 UI 업데이트

        Args:
            status_info (dict): 상태 정보
        """
        if not status_info:
            return

        # 자계 상태 업데이트
        b_field_on = status_info["status"]["b_field"] == "ON"
        self.field_on_radio.setChecked(b_field_on)
        self.field_off_radio.setChecked(not b_field_on)

        # 감지 모드 업데이트
        live_mode = status_info["status"]["detection"] == "LIVE"
        self.live_mode_radio.setChecked(live_mode)
        self.max_mode_radio.setChecked(not live_mode)

        # 단위 업데이트
        use_ut = status_info["status"]["unit"] == "uT"
        self.ut_radio.setChecked(use_ut)
        self.mg_radio.setChecked(not use_ut)

        self.logger.debug("제어 UI 상태 업데이트 완료")
