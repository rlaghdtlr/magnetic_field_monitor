"""
명령 처리 관리 모듈

자계 노출 측정기와의 명령 처리를 관리합니다.
"""

from communication.protocol import Protocol
from commands.status_commands import StatusCommands
from commands.control_commands import ControlCommands


class CommandHandler:
    """명령 처리 관리 클래스"""

    def __init__(self, serial_connection, logger, data_manager):
        """CommandHandler 클래스 초기화

        Args:
            serial_connection (SerialConnection): 시리얼 연결 객체
            logger (Logger): 로거 객체
            data_manager (DataManager): 데이터 관리 객체
        """
        self.serial_connection = serial_connection
        self.logger = logger
        self.data_manager = data_manager

        # 명령 객체 초기화
        self.status_commands = StatusCommands(serial_connection, logger)
        self.control_commands = ControlCommands(serial_connection, logger)

        # 응답 핸들러 등록
        self.response_handlers = {}
        self._register_response_handlers()

        # 최근 상태 정보
        self.latest_status = None

    def _register_response_handlers(self):
        """응답 핸들러 등록"""
        # 상태 응답 핸들러
        self.register_response_handler(
            Protocol.TYPE_STATUS_RESPONSE, self._handle_status_response
        )

        # 제어 응답 핸들러
        self.register_response_handler(
            Protocol.TYPE_FIELD_CONTROL_RESPONSE, self._handle_field_control_response
        )
        self.register_response_handler(
            Protocol.TYPE_DETECTION_CONTROL_RESPONSE,
            self._handle_detection_control_response,
        )
        self.register_response_handler(
            Protocol.TYPE_UNIT_SET_RESPONSE, self._handle_unit_set_response
        )

    def register_response_handler(self, response_type, handler):
        """응답 핸들러 등록

        Args:
            response_type (int): 응답 타입
            handler (callable): 핸들러 함수
        """
        self.response_handlers[response_type] = handler

    def handle_response(self, response):
        """응답 처리

        Args:
            response (bytes): 수신된 응답 데이터

        Returns:
            bool: 처리 성공 여부
        """
        # 응답 파싱
        parsed = Protocol().parse_frame(response)
        if not parsed:
            self.logger.error("응답 파싱 실패")
            return False

        frame_type, data, is_valid = parsed
        if not is_valid:
            self.logger.error("응답 CRC 오류")
            return False

        # 핸들러 호출
        handler = self.response_handlers.get(frame_type)
        if handler:
            return handler(data)
        else:
            self.logger.warning(f"알 수 없는 응답 타입: {frame_type}")
            return False

    def _handle_status_response(self, data):
        """상태 응답 처리

        Args:
            data (bytes): 응답 데이터

        Returns:
            bool: 처리 성공 여부
        """
        # 상태 정보 파싱
        status_info = self.status_commands._parse_status_response(data)
        if not status_info:
            return False

        # 최근 상태 정보 업데이트
        self.latest_status = status_info

        # 상태 변경 이벤트 발생
        self.serial_connection.status_updated.emit(status_info)

        return True

    def _handle_field_control_response(self, data):
        """B Field 제어 응답 처리

        Args:
            data (bytes): 응답 데이터

        Returns:
            bool: 처리 성공 여부
        """
        try:
            # ASCII 데이터를 HEX로 변환
            status = int(data.decode("ascii"), 16)

            # 상태 변경 이벤트 발생
            self.serial_connection.control_updated.emit("b_field", status == 0x00)

            return True
        except Exception as e:
            self.logger.error(f"B Field 제어 응답 처리 오류: {e}")
            return False

    def _handle_detection_control_response(self, data):
        """Detection 제어 응답 처리

        Args:
            data (bytes): 응답 데이터

        Returns:
            bool: 처리 성공 여부
        """
        try:
            # ASCII 데이터를 HEX로 변환
            status = int(data.decode("ascii"), 16)

            # 상태 변경 이벤트 발생
            self.serial_connection.control_updated.emit("detection", status == 0x00)

            return True
        except Exception as e:
            self.logger.error(f"Detection 제어 응답 처리 오류: {e}")
            return False

    def _handle_unit_set_response(self, data):
        """Unit 설정 응답 처리

        Args:
            data (bytes): 응답 데이터

        Returns:
            bool: 처리 성공 여부
        """
        try:
            # ASCII 데이터를 HEX로 변환
            status = int(data.decode("ascii"), 16)

            # 상태 변경 이벤트 발생
            self.serial_connection.control_updated.emit("unit", status == 0x00)

            return True
        except Exception as e:
            self.logger.error(f"Unit 설정 응답 처리 오류: {e}")
            return False

    def query_status(self):
        """장치 상태 조회

        Returns:
            dict: 상태 정보 또는 None (실패 시)
        """
        return self.status_commands.query_status()

    def control_b_field(self, on):
        """B Field On/Off 제어

        Args:
            on (bool): True: ON, False: OFF

        Returns:
            bool: 제어 성공 여부
        """
        return self.control_commands.control_b_field(on)

    def control_detection(self, live_mode):
        """Detection 제어

        Args:
            live_mode (bool): True: LIVE 모드, False: MAX 모드

        Returns:
            bool: 제어 성공 여부
        """
        return self.control_commands.control_detection(live_mode)

    def set_unit(self, use_ut):
        """Unit 설정

        Args:
            use_ut (bool): True: uT 단위 사용, False: mG 단위 사용

        Returns:
            bool: 제어 성공 여부
        """
        return self.control_commands.set_unit(use_ut)

    def get_latest_status(self):
        """최근 상태 정보 반환

        Returns:
            dict: 최근 상태 정보 또는 None
        """
        return self.latest_status
