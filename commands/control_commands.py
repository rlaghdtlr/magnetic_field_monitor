"""
제어 명령 모듈

자계 노출 측정기를 제어하는 명령을 처리합니다.
"""

from communication.protocol import Protocol


class ControlCommands:
    """제어 명령 클래스"""

    def __init__(self, serial_connection, logger):
        """ControlCommands 클래스 초기화

        Args:
            serial_connection (SerialConnection): 시리얼 연결 객체
            logger (Logger): 로거 객체
        """
        self.serial_connection = serial_connection
        self.logger = logger
        self.protocol = Protocol()

    def control_b_field(self, on):
        """B Field On/Off 제어

        Args:
            on (bool): True: ON, False: OFF

        Returns:
            bool: 제어 성공 여부
        """
        # 데이터 생성 (0x00: ON, 0x01: OFF)
        data = "00" if on else "01"

        # 명령 생성
        command = self.protocol.create_frame(Protocol.TYPE_FIELD_CONTROL, data)

        # 명령 전송
        self.logger.debug(f"B Field 제어 명령 전송: {command.hex()}")
        success = self.serial_connection.send_data(command)
        if not success:
            self.logger.error("B Field 제어 명령 전송 실패")
            return False

        # 응답 수신
        response = self.serial_connection.receive_data()
        if not response:
            self.logger.error("B Field 제어 응답 수신 실패")
            return False

        # 응답 파싱
        parsed = self.protocol.parse_frame(response)
        if not parsed:
            self.logger.error("B Field 제어 응답 파싱 실패")
            return False

        frame_type, data, is_valid = parsed
        if not is_valid:
            self.logger.error("B Field 제어 응답 CRC 오류")
            return False

        # 응답 타입 확인
        if frame_type != Protocol.TYPE_FIELD_CONTROL_RESPONSE:
            self.logger.error(f"B Field 제어 응답 타입 오류: {frame_type}")
            return False

        # 응답 데이터 확인
        try:
            # ASCII 데이터를 HEX로 변환
            status = int(data.decode("ascii"), 16)
            return status == (0x01 if not on else 0x00)
        except Exception as e:
            self.logger.error(f"B Field 제어 응답 데이터 파싱 오류: {e}")
            return False

    def control_detection(self, live_mode):
        """Detection 제어

        Args:
            live_mode (bool): True: LIVE 모드, False: MAX 모드

        Returns:
            bool: 제어 성공 여부
        """
        # 데이터 생성 (0x00: LIVE, 0x01: MAX)
        data = "00" if live_mode else "01"

        # 명령 생성
        command = self.protocol.create_frame(Protocol.TYPE_DETECTION_CONTROL, data)

        # 명령 전송
        self.logger.debug(f"Detection 제어 명령 전송: {command.hex()}")
        success = self.serial_connection.send_data(command)
        if not success:
            self.logger.error("Detection 제어 명령 전송 실패")
            return False

        # 응답 수신
        response = self.serial_connection.receive_data()
        if not response:
            self.logger.error("Detection 제어 응답 수신 실패")
            return False

        # 응답 파싱
        parsed = self.protocol.parse_frame(response)
        if not parsed:
            self.logger.error("Detection 제어 응답 파싱 실패")
            return False

        frame_type, data, is_valid = parsed
        if not is_valid:
            self.logger.error("Detection 제어 응답 CRC 오류")
            return False

        # 응답 타입 확인
        if frame_type != Protocol.TYPE_DETECTION_CONTROL_RESPONSE:
            self.logger.error(f"Detection 제어 응답 타입 오류: {frame_type}")
            return False

        # 응답 데이터 확인
        try:
            # ASCII 데이터를 HEX로 변환
            status = int(data.decode("ascii"), 16)
            return status == (0x01 if not live_mode else 0x00)
        except Exception as e:
            self.logger.error(f"Detection 제어 응답 데이터 파싱 오류: {e}")
            return False

    def set_unit(self, use_ut):
        """Unit 설정

        Args:
            use_ut (bool): True: uT 단위 사용, False: mG 단위 사용

        Returns:
            bool: 제어 성공 여부
        """
        # 데이터 생성 (0x00: uT, 0x01: mG)
        data = "00" if use_ut else "01"

        # 명령 생성
        command = self.protocol.create_frame(Protocol.TYPE_UNIT_SET, data)

        # 명령 전송
        self.logger.debug(f"Unit 설정 명령 전송: {command.hex()}")
        success = self.serial_connection.send_data(command)
        if not success:
            self.logger.error("Unit 설정 명령 전송 실패")
            return False

        # 응답 수신
        response = self.serial_connection.receive_data()
        if not response:
            self.logger.error("Unit 설정 응답 수신 실패")
            return False

        # 응답 파싱
        parsed = self.protocol.parse_frame(response)
        if not parsed:
            self.logger.error("Unit 설정 응답 파싱 실패")
            return False

        frame_type, data, is_valid = parsed
        if not is_valid:
            self.logger.error("Unit 설정 응답 CRC 오류")
            return False

        # 응답 타입 확인
        if frame_type != Protocol.TYPE_UNIT_SET_RESPONSE:
            self.logger.error(f"Unit 설정 응답 타입 오류: {frame_type}")
            return False

        # 응답 데이터 확인
        try:
            # ASCII 데이터를 HEX로 변환
            status = int(data.decode("ascii"), 16)
            return status == (0x01 if not use_ut else 0x00)
        except Exception as e:
            self.logger.error(f"Unit 설정 응답 데이터 파싱 오류: {e}")
            return False
