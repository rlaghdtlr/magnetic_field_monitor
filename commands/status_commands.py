"""
상태 조회 명령 모듈

자계 노출 측정기의 상태를 조회하는 명령을 처리합니다.
"""

from communication.protocol import Protocol


class StatusCommands:
    """상태 조회 명령 클래스"""

    def __init__(self, serial_connection, logger):
        """StatusCommands 클래스 초기화

        Args:
            serial_connection (SerialConnection): 시리얼 연결 객체
            logger (Logger): 로거 객체
        """
        self.serial_connection = serial_connection
        self.logger = logger
        self.protocol = Protocol()

    def query_status(self):
        """장치 상태 조회

        Returns:
            dict: 상태 정보 또는 None (실패 시)
        """
        # 상태 조회 명령 생성 (TYPE 0x00)
        command = self.protocol.create_frame(Protocol.TYPE_STATUS, b"")

        # 명령 전송
        self.logger.debug(f"상태 조회 명령 전송: {command.hex()}")
        success = self.serial_connection.send_data(command)
        if not success:
            self.logger.error("상태 조회 명령 전송 실패")
            return None

        # 응답 수신 (타임아웃 5초로 증가)
        self.logger.debug("상태 조회 응답 대기 중...")
        response = self.serial_connection.receive_data(timeout=5.0)
        if not response:
            self.logger.error("상태 조회 응답 수신 실패")
            return None

        # 응답 파싱
        self.logger.debug(f"상태 조회 응답 수신: {response.hex()}")
        parsed = self.protocol.parse_frame(response)
        if not parsed:
            self.logger.error("상태 조회 응답 파싱 실패")
            return None

        frame_type, data, is_valid = parsed

        # 응답 타입 확인
        if frame_type != Protocol.TYPE_STATUS_RESPONSE:
            self.logger.error(
                f"상태 조회 응답 타입 오류: {frame_type:02X}, 예상: {Protocol.TYPE_STATUS_RESPONSE:02X}"
            )
            return None

        # 데이터 파싱
        return self._parse_status_response(data)

    def _parse_status_response(self, data):
        """상태 응답 데이터 파싱

        Args:
            data (bytes): 응답 데이터

        Returns:
            dict: 파싱된 상태 정보 또는 None (파싱 실패 시)
        """
        try:
            # 데이터 길이 확인 (최소 길이: 56바이트)
            if len(data) < 56:
                self.logger.error(f"상태 응답 데이터 길이 오류: {len(data)}")
                return None

            # ASCII 데이터를 HEX로 변환
            # 예: '10' -> 0x10
            def ascii_to_hex(ascii_bytes):
                try:
                    return int(ascii_bytes.decode("ascii"), 16)
                except (ValueError, UnicodeDecodeError):
                    self.logger.error(f"ASCII to HEX 변환 오류: {ascii_bytes}")
                    return 0

            # 펌웨어 버전 (2바이트 ASCII -> 1바이트 HEX)
            firmware_version = ascii_to_hex(data[0:2])
            firmware_major = (firmware_version >> 4) & 0x0F
            firmware_minor = firmware_version & 0x0F

            # 시리얼 번호 (8바이트 ASCII -> 4바이트 HEX)
            serial_number = ascii_to_hex(data[2:10])

            # 상태 1 (2바이트 ASCII -> 1바이트 HEX)
            status1 = ascii_to_hex(data[10:12])
            rt_clock_source = (status1 >> 7) & 0x01  # Bit 7
            gps_reception = (status1 >> 6) & 0x01  # Bit 6
            gps_status = (status1 >> 5) & 0x01  # Bit 5
            detection_mode = (status1 >> 4) & 0x01  # Bit 4
            unit_type = (status1 >> 3) & 0x01  # Bit 3
            b_field_status = (status1 >> 2) & 0x01  # Bit 2

            # 상태 2 (2바이트 ASCII -> 1바이트 HEX)
            status2 = ascii_to_hex(data[12:14])
            light_status = (status2 >> 7) & 0x01  # Bit 7
            display_status = (status2 >> 6) & 0x01  # Bit 6
            log_operation = (status2 >> 5) & 0x01  # Bit 5
            log_status = (status2 >> 4) & 0x01  # Bit 4
            datum_status = (status2 >> 3) & 0x01  # Bit 3

            # 배터리 상태 (2바이트 ASCII -> 1바이트 HEX)
            battery_status = ascii_to_hex(data[14:16])

            # B Field 값 (4바이트 ASCII -> 2바이트 HEX)
            print("data :", data)
            print("B Field data[16:20] :", data[16:20])
            b_field_value = ascii_to_hex(data[16:20])

            # GPS 위도 (8바이트 ASCII -> 4바이트 HEX)
            latitude_deg = ascii_to_hex(data[20:22])
            latitude_min = ascii_to_hex(data[22:24])
            latitude_sec = ascii_to_hex(data[24:28])

            # GPS 경도 (8바이트 ASCII -> 4바이트 HEX)
            longitude_deg = ascii_to_hex(data[28:30])
            longitude_min = ascii_to_hex(data[30:32])
            longitude_sec = ascii_to_hex(data[32:36])

            # GPS 고도 (4바이트 ASCII -> 2바이트 HEX)
            altitude = ascii_to_hex(data[36:40])

            # 로그 시간 간격 (6바이트 ASCII -> 3바이트 HEX)
            log_hour = ascii_to_hex(data[40:42])
            log_minute = ascii_to_hex(data[42:44])
            log_second = ascii_to_hex(data[44:46])

            # 날짜/시간 (12바이트 ASCII -> 6바이트 HEX)
            year = ascii_to_hex(data[46:48])
            month = ascii_to_hex(data[48:50])
            day = ascii_to_hex(data[50:52])
            hour = ascii_to_hex(data[52:54])
            minute = ascii_to_hex(data[54:56])
            second = ascii_to_hex(data[56:58])

            # 온도 (2바이트 ASCII -> 1바이트 HEX, 부호 있음)
            temperature = ascii_to_hex(data[58:60])
            if temperature > 127:
                temperature = temperature - 256

            # 상태 정보 반환
            return {
                "firmware_version": f"{firmware_major}.{firmware_minor}",
                "serial_number": serial_number,
                "status": {
                    "rt_clock_source": "내부 RTC" if rt_clock_source else "GPS",
                    "gps_reception": "비활성" if gps_reception else "활성",
                    "gps": "OFF" if gps_status else "ON",
                    "detection": "MAX" if detection_mode else "LIVE",
                    "unit": "mG" if unit_type else "uT",
                    "b_field": "OFF" if b_field_status else "ON",
                    "light": "OFF" if light_status else "ON",
                    "display": "OFF" if display_status else "ON",
                    "log_operation": "연속" if log_operation else "단일",
                    "log": "OFF" if log_status else "ON",
                    "datum": "Tokyo" if datum_status else "WGS84",
                },
                "battery": {
                    "status": battery_status,
                    "description": self._get_battery_description(battery_status),
                },
                "b_field": {
                    "value": b_field_value / (10 if unit_type else 100),
                    "unit": "mG" if unit_type else "uT",
                },
                "gps": {
                    "latitude": {
                        "degrees": latitude_deg,
                        "minutes": latitude_min,
                        "seconds": latitude_sec / 100,
                        "formatted": f"{latitude_deg}°{latitude_min}'{latitude_sec/100:.2f}\"",
                    },
                    "longitude": {
                        "degrees": longitude_deg,
                        "minutes": longitude_min,
                        "seconds": longitude_sec / 100,
                        "formatted": f"{longitude_deg}°{longitude_min}'{longitude_sec/100:.2f}\"",
                    },
                    "altitude": altitude,
                },
                "log_interval": {
                    "hours": log_hour,
                    "minutes": log_minute,
                    "seconds": log_second,
                    "formatted": f"{log_hour:02d}:{log_minute:02d}:{log_second:02d}",
                },
                "datetime": {
                    "year": 2000 + year,
                    "month": month,
                    "day": day,
                    "hour": hour,
                    "minute": minute,
                    "second": second,
                    "formatted": f"20{year:02d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}",
                },
                "temperature": {"value": temperature, "formatted": f"{temperature}°C"},
            }
        except Exception as e:
            self.logger.error(f"상태 응답 데이터 파싱 오류: {e}")
            return None

    def _get_battery_description(self, status):
        """배터리 상태 설명 반환

        Args:
            status (int): 배터리 상태 코드

        Returns:
            str: 배터리 상태 설명
        """
        if status == 0x00:
            return "완전 충전"
        elif status == 0x01:
            return "2단계 충전"
        elif status == 0x02:
            return "1단계 충전"
        elif status == 0x03:
            return "방전"
        else:
            return "알 수 없음"
