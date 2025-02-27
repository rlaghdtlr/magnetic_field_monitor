"""
상태 표시 위젯 모듈

자계 노출 측정기의 상태를 표시하는 위젯을 정의합니다.
"""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QGridLayout,
    QCheckBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer


class StatusWidget(QWidget):
    """상태 표시 위젯 클래스"""

    def __init__(self, command_handler, logger):
        """StatusWidget 클래스 초기화

        Args:
            command_handler (CommandHandler): 명령 처리 관리 객체
            logger (Logger): 로거 객체
        """
        super().__init__()
        self.command_handler = command_handler
        self.logger = logger
        self.auto_refresh_timer = None
        self.auto_refresh_interval = 1000  # 1초

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """UI 초기화"""
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)

        # 장치 정보 그룹
        device_group = QGroupBox("장치 정보")
        device_layout = QGridLayout()

        # 펌웨어 버전
        device_layout.addWidget(QLabel("펌웨어 버전:"), 0, 0)
        self.firmware_version_label = QLabel("-")
        device_layout.addWidget(self.firmware_version_label, 0, 1)

        # 시리얼 번호
        device_layout.addWidget(QLabel("시리얼 번호:"), 1, 0)
        self.serial_number_label = QLabel("-")
        device_layout.addWidget(self.serial_number_label, 1, 1)

        # 배터리 상태
        device_layout.addWidget(QLabel("배터리 상태:"), 2, 0)
        self.battery_status_label = QLabel("-")
        device_layout.addWidget(self.battery_status_label, 2, 1)

        # 온도
        device_layout.addWidget(QLabel("온도:"), 3, 0)
        self.temperature_label = QLabel("-")
        device_layout.addWidget(self.temperature_label, 3, 1)

        device_group.setLayout(device_layout)
        main_layout.addWidget(device_group)

        # 상태 그룹
        status_group = QGroupBox("장치 상태")
        status_layout = QGridLayout()

        # 자계 상태
        status_layout.addWidget(QLabel("자계 상태:"), 0, 0)
        self.b_field_status_label = QLabel("-")
        status_layout.addWidget(self.b_field_status_label, 0, 1)

        # 자계 값
        status_layout.addWidget(QLabel("자계 값:"), 1, 0)
        self.b_field_value_label = QLabel("-")
        status_layout.addWidget(self.b_field_value_label, 1, 1)

        # 감지 모드
        status_layout.addWidget(QLabel("감지 모드:"), 2, 0)
        self.detection_mode_label = QLabel("-")
        status_layout.addWidget(self.detection_mode_label, 2, 1)

        # 단위
        status_layout.addWidget(QLabel("단위:"), 3, 0)
        self.unit_label = QLabel("-")
        status_layout.addWidget(self.unit_label, 3, 1)

        # GPS 상태
        status_layout.addWidget(QLabel("GPS 상태:"), 4, 0)
        self.gps_status_label = QLabel("-")
        status_layout.addWidget(self.gps_status_label, 4, 1)

        # GPS 수신 상태
        status_layout.addWidget(QLabel("GPS 수신:"), 5, 0)
        self.gps_reception_label = QLabel("-")
        status_layout.addWidget(self.gps_reception_label, 5, 1)

        # 시계 소스
        status_layout.addWidget(QLabel("시계 소스:"), 6, 0)
        self.rt_clock_source_label = QLabel("-")
        status_layout.addWidget(self.rt_clock_source_label, 6, 1)

        # 디스플레이 상태
        status_layout.addWidget(QLabel("디스플레이:"), 7, 0)
        self.display_status_label = QLabel("-")
        status_layout.addWidget(self.display_status_label, 7, 1)

        # 조명 상태
        status_layout.addWidget(QLabel("조명:"), 8, 0)
        self.light_status_label = QLabel("-")
        status_layout.addWidget(self.light_status_label, 8, 1)

        # 로그 상태
        status_layout.addWidget(QLabel("로그:"), 9, 0)
        self.log_status_label = QLabel("-")
        status_layout.addWidget(self.log_status_label, 9, 1)

        # 로그 동작 모드
        status_layout.addWidget(QLabel("로그 동작:"), 10, 0)
        self.log_operation_label = QLabel("-")
        status_layout.addWidget(self.log_operation_label, 10, 1)

        # 로그 시간 간격
        status_layout.addWidget(QLabel("로그 간격:"), 11, 0)
        self.log_interval_label = QLabel("-")
        status_layout.addWidget(self.log_interval_label, 11, 1)

        # 측지계
        status_layout.addWidget(QLabel("측지계:"), 12, 0)
        self.datum_status_label = QLabel("-")
        status_layout.addWidget(self.datum_status_label, 12, 1)

        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)

        # GPS 정보 그룹
        gps_group = QGroupBox("GPS 정보")
        gps_layout = QGridLayout()

        # 위도
        gps_layout.addWidget(QLabel("위도:"), 0, 0)
        self.latitude_label = QLabel("-")
        gps_layout.addWidget(self.latitude_label, 0, 1)

        # 경도
        gps_layout.addWidget(QLabel("경도:"), 1, 0)
        self.longitude_label = QLabel("-")
        gps_layout.addWidget(self.longitude_label, 1, 1)

        # 고도
        gps_layout.addWidget(QLabel("고도:"), 2, 0)
        self.altitude_label = QLabel("-")
        gps_layout.addWidget(self.altitude_label, 2, 1)

        gps_group.setLayout(gps_layout)
        main_layout.addWidget(gps_group)

        # 날짜/시간 그룹
        datetime_group = QGroupBox("날짜/시간")
        datetime_layout = QGridLayout()

        # 날짜/시간
        datetime_layout.addWidget(QLabel("날짜/시간:"), 0, 0)
        self.datetime_label = QLabel("-")
        datetime_layout.addWidget(self.datetime_label, 0, 1)

        datetime_group.setLayout(datetime_layout)
        main_layout.addWidget(datetime_group)

        # 제어 그룹
        control_group = QGroupBox("상태 제어")
        control_layout = QHBoxLayout()

        # 상태 갱신 버튼
        self.refresh_button = QPushButton("상태 갱신")
        control_layout.addWidget(self.refresh_button)

        # 자동 갱신 체크박스
        self.auto_refresh_checkbox = QCheckBox("자동 갱신")
        control_layout.addWidget(self.auto_refresh_checkbox)

        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)

        # 여백 추가
        main_layout.addStretch()

    def _connect_signals(self):
        """시그널 연결"""
        # 버튼 시그널
        self.refresh_button.clicked.connect(self._refresh_status)

        # 체크박스 시그널
        self.auto_refresh_checkbox.stateChanged.connect(self._toggle_auto_refresh)

        # 자동 갱신 타이머 설정
        self.auto_refresh_timer = QTimer(self)
        self.auto_refresh_timer.timeout.connect(self._refresh_status)

    @pyqtSlot()
    def _refresh_status(self):
        """상태 정보 갱신"""
        self.logger.debug("상태 정보 갱신 요청")
        status_info = self.command_handler.query_status()
        if status_info:
            self._update_status_display(status_info)
        else:
            self.logger.error("상태 정보 갱신 실패")

    @pyqtSlot(int)
    def _toggle_auto_refresh(self, state):
        """자동 갱신 토글

        Args:
            state (int): 체크박스 상태
        """
        if state == Qt.Checked:
            self.auto_refresh_timer.start(self.auto_refresh_interval)
            self.logger.debug(f"자동 갱신 시작 (간격: {self.auto_refresh_interval}ms)")
        else:
            self.auto_refresh_timer.stop()
            self.logger.debug("자동 갱신 중지")

    @pyqtSlot(dict)
    def update_status(self, status_info):
        """상태 정보 업데이트

        Args:
            status_info (dict): 상태 정보
        """
        self._update_status_display(status_info)

    def _update_status_display(self, status_info):
        """상태 표시 업데이트

        Args:
            status_info (dict): 상태 정보
        """
        # 장치 정보
        self.firmware_version_label.setText(status_info["firmware_version"])
        self.serial_number_label.setText(str(status_info["serial_number"]))
        self.battery_status_label.setText(status_info["battery"]["description"])
        self.temperature_label.setText(status_info["temperature"]["formatted"])

        # 상태 정보
        self.b_field_status_label.setText(status_info["status"]["b_field"])
        self.b_field_value_label.setText(
            f"{status_info['b_field']['value']} {status_info['b_field']['unit']}"
        )
        self.detection_mode_label.setText(status_info["status"]["detection"])
        self.unit_label.setText(status_info["status"]["unit"])
        self.gps_status_label.setText(status_info["status"]["gps"])
        self.gps_reception_label.setText(status_info["status"]["gps_reception"])
        self.rt_clock_source_label.setText(status_info["status"]["rt_clock_source"])
        self.display_status_label.setText(status_info["status"]["display"])
        self.light_status_label.setText(status_info["status"]["light"])
        self.log_status_label.setText(status_info["status"]["log"])
        self.log_operation_label.setText(status_info["status"]["log_operation"])
        self.log_interval_label.setText(status_info["log_interval"]["formatted"])
        self.datum_status_label.setText(status_info["status"]["datum"])

        # GPS 정보
        self.latitude_label.setText(status_info["gps"]["latitude"]["formatted"])
        self.longitude_label.setText(status_info["gps"]["longitude"]["formatted"])
        self.altitude_label.setText(f"{status_info['gps']['altitude']} m")

        # 날짜/시간
        self.datetime_label.setText(status_info["datetime"]["formatted"])

        self.logger.debug("상태 표시 업데이트 완료")
