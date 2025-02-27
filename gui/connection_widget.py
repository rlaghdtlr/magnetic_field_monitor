"""
연결 설정 위젯 모듈

자계 노출 측정기와의 연결을 설정하고 관리하는 위젯을 정의합니다.
"""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QGridLayout,
    QComboBox,
    QSpinBox,
    QMessageBox,
)
from PyQt5.QtCore import Qt, pyqtSlot
import serial
from utils.crc import calculate_crc16


class ConnectionWidget(QWidget):
    """연결 설정 위젯 클래스"""

    def __init__(self, serial_connection, data_manager, logger):
        """ConnectionWidget 클래스 초기화

        Args:
            serial_connection (SerialConnection): 시리얼 연결 객체
            data_manager (DataManager): 데이터 관리 객체
            logger (Logger): 로거 객체
        """
        super().__init__()

        self.serial_connection = serial_connection
        self.data_manager = data_manager
        self.logger = logger

        # UI 초기화
        self._init_ui()

        # 시그널 연결
        self._connect_signals()

        # 설정 로드
        self._load_settings()

    def _init_ui(self):
        """UI 초기화"""
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)

        # 연결 설정 그룹
        connection_group = QGroupBox("연결 설정")
        connection_layout = QGridLayout()

        # 포트 선택
        connection_layout.addWidget(QLabel("포트:"), 0, 0)
        self.port_combo = QComboBox()
        connection_layout.addWidget(self.port_combo, 0, 1)

        # 포트 새로고침 버튼
        self.refresh_button = QPushButton("새로고침")
        connection_layout.addWidget(self.refresh_button, 0, 2)

        # 통신 속도 선택
        connection_layout.addWidget(QLabel("통신 속도:"), 1, 0)
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        connection_layout.addWidget(self.baudrate_combo, 1, 1, 1, 2)

        # 데이터 비트 선택
        connection_layout.addWidget(QLabel("데이터 비트:"), 2, 0)
        self.bytesize_combo = QComboBox()
        self.bytesize_combo.addItems(["5", "6", "7", "8"])
        self.bytesize_combo.setCurrentText("8")
        connection_layout.addWidget(self.bytesize_combo, 2, 1, 1, 2)

        # 패리티 비트 선택
        connection_layout.addWidget(QLabel("패리티:"), 3, 0)
        self.parity_combo = QComboBox()
        self.parity_combo.addItems(["없음", "홀수", "짝수", "마크", "스페이스"])
        connection_layout.addWidget(self.parity_combo, 3, 1, 1, 2)

        # 정지 비트 선택
        connection_layout.addWidget(QLabel("정지 비트:"), 4, 0)
        self.stopbits_combo = QComboBox()
        self.stopbits_combo.addItems(["1", "1.5", "2"])
        connection_layout.addWidget(self.stopbits_combo, 4, 1, 1, 2)

        # 타임아웃 설정
        connection_layout.addWidget(QLabel("타임아웃 (초):"), 5, 0)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 10)
        self.timeout_spin.setValue(1)
        connection_layout.addWidget(self.timeout_spin, 5, 1, 1, 2)

        connection_group.setLayout(connection_layout)
        main_layout.addWidget(connection_group)

        # 연결 버튼 그룹
        button_group = QGroupBox("연결 제어")
        button_layout = QHBoxLayout()

        # 연결/연결 해제 버튼
        self.connect_button = QPushButton("연결")
        button_layout.addWidget(self.connect_button)

        # 연결 해제 버튼
        self.disconnect_button = QPushButton("연결 해제")
        self.disconnect_button.setEnabled(False)
        button_layout.addWidget(self.disconnect_button)

        # 테스트 버튼 추가
        self.test_button = QPushButton("통신 테스트")
        self.test_button.setEnabled(False)
        button_layout.addWidget(self.test_button)

        button_group.setLayout(button_layout)
        main_layout.addWidget(button_group)

        # 연결 상태 그룹
        status_group = QGroupBox("연결 상태")
        status_layout = QGridLayout()

        # 연결 상태 표시
        status_layout.addWidget(QLabel("상태:"), 0, 0)
        self.status_label = QLabel("연결되지 않음")
        status_layout.addWidget(self.status_label, 0, 1)

        # 포트 정보 표시
        status_layout.addWidget(QLabel("포트 정보:"), 1, 0)
        self.port_info_label = QLabel("-")
        status_layout.addWidget(self.port_info_label, 1, 1)

        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)

        # 여백 추가
        main_layout.addStretch()

    def _connect_signals(self):
        """시그널 연결"""
        # 버튼 시그널
        self.refresh_button.clicked.connect(self._refresh_ports)
        self.connect_button.clicked.connect(self._connect)
        self.disconnect_button.clicked.connect(self._disconnect)
        self.test_button.clicked.connect(self._test_communication)

        # 시리얼 연결 시그널
        self.serial_connection.connection_changed.connect(
            self._update_connection_status
        )
        self.serial_connection.error_occurred.connect(self._show_error)

    def _load_settings(self):
        """설정 로드"""
        # 포트 목록 로드
        self._refresh_ports()

        # 저장된 설정 로드
        settings = self.data_manager.settings.get("connection", {})

        port = settings.get("port", "")
        if port and port in [
            self.port_combo.itemText(i) for i in range(self.port_combo.count())
        ]:
            self.port_combo.setCurrentText(port)

        baudrate = str(settings.get("baudrate", 9600))
        if baudrate in [
            self.baudrate_combo.itemText(i) for i in range(self.baudrate_combo.count())
        ]:
            self.baudrate_combo.setCurrentText(baudrate)

        bytesize = str(settings.get("bytesize", 8))
        if bytesize in [
            self.bytesize_combo.itemText(i) for i in range(self.bytesize_combo.count())
        ]:
            self.bytesize_combo.setCurrentText(bytesize)

        parity_map = {
            "N": "없음",
            "O": "홀수",
            "E": "짝수",
            "M": "마크",
            "S": "스페이스",
        }
        parity = settings.get("parity", "N")
        self.parity_combo.setCurrentText(parity_map.get(parity, "없음"))

        stopbits = str(settings.get("stopbits", 1))
        if stopbits in [
            self.stopbits_combo.itemText(i) for i in range(self.stopbits_combo.count())
        ]:
            self.stopbits_combo.setCurrentText(stopbits)

        timeout = settings.get("timeout", 1)
        self.timeout_spin.setValue(int(timeout))

        self.logger.debug("연결 설정 로드 완료")

    def _save_settings(self):
        """설정 저장"""
        # 현재 설정 저장
        settings = self.data_manager.settings.copy()

        # 연결 설정 업데이트
        parity_map = {
            "없음": "N",
            "홀수": "O",
            "짝수": "E",
            "마크": "M",
            "스페이스": "S",
        }
        stopbits_map = {"1": 1, "1.5": 1.5, "2": 2}

        settings["connection"] = {
            "port": self.port_combo.currentText(),
            "baudrate": int(self.baudrate_combo.currentText()),
            "bytesize": int(self.bytesize_combo.currentText()),
            "parity": parity_map.get(self.parity_combo.currentText(), "N"),
            "stopbits": stopbits_map.get(self.stopbits_combo.currentText(), 1),
            "timeout": self.timeout_spin.value(),
        }

        # 설정 저장
        success = self.data_manager.save_settings(settings)
        if success:
            self.logger.debug("연결 설정 저장 완료")
        else:
            self.logger.error("연결 설정 저장 실패")

    @pyqtSlot()
    def _refresh_ports(self):
        """포트 목록 새로고침"""
        # 현재 선택된 포트 저장
        current_port = self.port_combo.currentText()

        # 포트 목록 가져오기
        ports = self.serial_connection.get_available_ports()

        # 포트 목록 업데이트
        self.port_combo.clear()
        self.port_combo.addItems(ports)

        # 이전에 선택된 포트가 있으면 다시 선택
        if current_port and current_port in ports:
            self.port_combo.setCurrentText(current_port)

        self.logger.debug(f"포트 목록 새로고침: {len(ports)}개 발견")

    @pyqtSlot()
    def _connect(self):
        """장치 연결"""
        # 연결 설정 가져오기
        port = self.port_combo.currentText()
        if not port:
            QMessageBox.warning(self, "경고", "연결할 포트를 선택해주세요.")
            return

        baudrate = int(self.baudrate_combo.currentText())
        bytesize_map = {
            "5": serial.FIVEBITS,
            "6": serial.SIXBITS,
            "7": serial.SEVENBITS,
            "8": serial.EIGHTBITS,
        }
        bytesize = bytesize_map.get(self.bytesize_combo.currentText(), serial.EIGHTBITS)

        parity_map = {
            "없음": serial.PARITY_NONE,
            "홀수": serial.PARITY_ODD,
            "짝수": serial.PARITY_EVEN,
            "마크": serial.PARITY_MARK,
            "스페이스": serial.PARITY_SPACE,
        }
        parity = parity_map.get(self.parity_combo.currentText(), serial.PARITY_NONE)

        stopbits_map = {
            "1": serial.STOPBITS_ONE,
            "1.5": serial.STOPBITS_ONE_POINT_FIVE,
            "2": serial.STOPBITS_TWO,
        }
        stopbits = stopbits_map.get(
            self.stopbits_combo.currentText(), serial.STOPBITS_ONE
        )

        timeout = self.timeout_spin.value()

        # 연결 시도
        self.logger.info(f"포트 {port}에 연결 시도 중...")
        success = self.serial_connection.connect(
            port, baudrate, bytesize, parity, stopbits, timeout
        )

        if success:
            # 설정 저장
            self._save_settings()

            # UI 업데이트
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
            self.port_combo.setEnabled(False)
            self.baudrate_combo.setEnabled(False)
            self.bytesize_combo.setEnabled(False)
            self.parity_combo.setEnabled(False)
            self.stopbits_combo.setEnabled(False)
            self.timeout_spin.setEnabled(False)

            self.logger.info(f"포트 {port}에 연결 성공")
            QMessageBox.information(self, "연결 성공", f"포트 {port}에 연결되었습니다.")
        else:
            self.logger.error(f"포트 {port}에 연결 실패")

    @pyqtSlot()
    def _disconnect(self):
        """장치 연결 해제"""
        if self.serial_connection.is_connected():
            self.serial_connection.disconnect()
            self.logger.info("장치 연결 해제")

            # UI 업데이트
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)
            self.port_combo.setEnabled(True)
            self.baudrate_combo.setEnabled(True)
            self.bytesize_combo.setEnabled(True)
            self.parity_combo.setEnabled(True)
            self.stopbits_combo.setEnabled(True)
            self.timeout_spin.setEnabled(True)

    @pyqtSlot(bool)
    def _update_connection_status(self, connected):
        """연결 상태 업데이트

        Args:
            connected (bool): 연결 상태
        """
        if connected:
            self.status_label.setText("연결됨")
            self.port_info_label.setText(
                f"{self.port_combo.currentText()}, {self.baudrate_combo.currentText()} bps"
            )

            # UI 업데이트
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
            self.port_combo.setEnabled(False)
            self.baudrate_combo.setEnabled(False)
            self.bytesize_combo.setEnabled(False)
            self.parity_combo.setEnabled(False)
            self.stopbits_combo.setEnabled(False)
            self.timeout_spin.setEnabled(False)
            self.test_button.setEnabled(True)
        else:
            self.status_label.setText("연결되지 않음")
            self.port_info_label.setText("-")

            # UI 업데이트
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)
            self.port_combo.setEnabled(True)
            self.baudrate_combo.setEnabled(True)
            self.bytesize_combo.setEnabled(True)
            self.parity_combo.setEnabled(True)
            self.stopbits_combo.setEnabled(True)
            self.timeout_spin.setEnabled(True)
            self.test_button.setEnabled(False)

        self.logger.debug(
            f"연결 상태 업데이트: {'연결됨' if connected else '연결되지 않음'}"
        )

    @pyqtSlot(str)
    def _show_error(self, error_message):
        """오류 메시지 표시

        Args:
            error_message (str): 오류 메시지
        """
        QMessageBox.critical(self, "오류", error_message)
        self.logger.error(f"연결 오류: {error_message}")

    @pyqtSlot()
    def _test_communication(self):
        """통신 테스트"""
        if not self.serial_connection.is_connected():
            QMessageBox.warning(self, "경고", "장치가 연결되어 있지 않습니다.")
            return

        self.logger.info("통신 테스트 시작...")

        # 상태 조회 명령 생성
        from communication.protocol import Protocol

        protocol = Protocol()

        # 상태 조회 명령 생성 (TYPE 0x00)
        command = protocol.create_frame(Protocol.TYPE_STATUS, b"")

        # 명령 전송 전 로그
        self.logger.debug(f"테스트 명령 생성: {command.hex()}")
        self.logger.debug(f"- STX: 0x{command[0]:02X}")
        self.logger.debug(f"- TYPE: {command[1:3].decode('ascii')}")
        self.logger.debug(f"- ETX: 0x{command[-1]:02X}")

        # 명령 전송
        success = self.serial_connection.send_data(command)

        if not success:
            QMessageBox.critical(self, "오류", "테스트 명령 전송 실패")
            self.logger.error("테스트 명령 전송 실패")
            return

        # 응답 수신 (타임아웃 10초로 증가)
        self.logger.debug("테스트 응답 대기 중...")
        response = self.serial_connection.receive_data(timeout=10.0)

        if not response:
            QMessageBox.warning(self, "경고", "테스트 응답 수신 실패 (타임아웃)")
            self.logger.warning("테스트 응답 수신 실패 (타임아웃)")

            # 추가 디버깅 정보
            QMessageBox.information(
                self,
                "디버깅 정보",
                "장치가 응답하지 않습니다. 다음을 확인하세요:\n"
                "1. 장치가 켜져 있는지 확인\n"
                "2. 케이블이 올바르게 연결되어 있는지 확인\n"
                "3. 통신 설정(baudrate, bytesize 등)이 올바른지 확인\n"
                "4. 다른 프로그램이 COM 포트를 사용 중인지 확인\n"
                "5. 프로토콜 문서에 따라 STX는 0x02, ETX는 0x03이며, TYPE/DATA는 ASCII 코드로 전송됩니다.",
            )
            return

        # 응답 파싱
        self.logger.debug(f"테스트 응답 수신: {response.hex()}")

        # 응답 상세 로깅
        try:
            self.logger.debug(f"- STX: 0x{response[0]:02X}")
            self.logger.debug(f"- TYPE: {response[1:3].decode('ascii')}")
            self.logger.debug(f"- DATA 길이: {len(response[3:-1])} 바이트")
            self.logger.debug(f"- ETX: 0x{response[-1]:02X}")
        except Exception as e:
            self.logger.error(f"응답 로깅 오류: {str(e)}")

        parsed = protocol.parse_frame(response)

        if not parsed:
            QMessageBox.warning(self, "경고", "테스트 응답 파싱 실패")
            self.logger.warning("테스트 응답 파싱 실패")
            return

        frame_type, data, is_valid = parsed

        # 성공 메시지
        QMessageBox.information(
            self,
            "성공",
            f"통신 테스트 성공!\n"
            f"응답 타입: 0x{frame_type:02X}\n"
            f"데이터 길이: {len(data)} 바이트\n\n"
            f"프레임 구조:\n"
            f"- STX: 0x{response[0]:02X}\n"
            f"- TYPE: {response[1:3].decode('ascii')} (0x{frame_type:02X})\n"
            f"- DATA: {len(data)} 바이트\n"
            f"- ETX: 0x{response[-1]:02X}",
        )
        self.logger.info("통신 테스트 성공")
