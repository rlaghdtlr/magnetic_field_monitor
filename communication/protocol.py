"""
프로토콜 처리 모듈

자계 노출 측정기와의 통신 프로토콜을 처리합니다.
프레임 형식: STX + TYPE + DATA + CRC + ETX
* STX항목과 ETX항목은 HEX code로 전송되고 나머지(TYPE,DATA,CRC)항목은 ASCII code로 전송한다.
"""

from utils.crc import calculate_crc16


class Protocol:
    """통신 프로토콜 처리 클래스"""

    # 프레임 상수
    STX = 0x02  # 시작 문자
    ETX = 0x03  # 종료 문자

    # 명령 타입 (HEX 값)
    TYPE_STATUS = 0x00  # 상태 조회
    TYPE_STATUS_RESPONSE = 0x81  # 상태 조회 응답
    TYPE_FIELD_CONTROL = 0x02  # B Field On/Off 제어
    TYPE_FIELD_CONTROL_RESPONSE = 0x83  # B Field On/Off 제어 응답
    TYPE_DETECTION_CONTROL = 0x04  # Detection 제어
    TYPE_DETECTION_CONTROL_RESPONSE = 0x85  # Detection 제어 응답
    TYPE_UNIT_SET = 0x06  # Unit Set 제어
    TYPE_UNIT_SET_RESPONSE = 0x87  # Unit Set 제어 응답

    def __init__(self):
        """Protocol 클래스 초기화"""
        pass

    @staticmethod
    def create_frame(frame_type, data):
        """프레임 생성

        Args:
            frame_type (int): 프레임 타입 (HEX 값)
            data (bytes 또는 str): 데이터 부분

        Returns:
            bytes: 생성된 프레임
        """
        # 데이터가 문자열인 경우 바이트로 변환
        if isinstance(data, str):
            data = data.encode("ascii")

        # TYPE을 ASCII로 변환 (예: 0x00 -> '00')
        type_ascii = f"{frame_type:02X}".encode("ascii")

        # 간단한 프레임 구성: STX + TYPE(ASCII) + DATA(ASCII) + ETX
        # 문서에 따르면 STX와 ETX는 HEX 코드로, 나머지는 ASCII 코드로 전송
        simple_frame = bytes([Protocol.STX]) + type_ascii + data + bytes([Protocol.ETX])

        return simple_frame

    @staticmethod
    def parse_frame(frame):
        """수신된 프레임 파싱

        Args:
            frame (bytes): 수신된 프레임

        Returns:
            tuple: (frame_type, data, is_valid) 또는 None (유효하지 않은 프레임)
        """
        # 프레임 길이 검사 (STX + TYPE(2) + ETX = 최소 4바이트)
        if len(frame) < 4:
            return None

        # STX, ETX 검사
        if frame[0] != Protocol.STX or frame[-1] != Protocol.ETX:
            return None

        # 프레임 타입 추출 (ASCII -> HEX)
        try:
            frame_type = int(frame[1:3].decode("ascii"), 16)
        except (ValueError, UnicodeDecodeError):
            return None

        # 데이터 추출 (TYPE 이후부터 ETX 이전까지)
        data = frame[3:-1]

        # 간단한 형식에서는 CRC 검증을 생략하고 항상 유효하다고 간주
        is_valid = True

        return (frame_type, data, is_valid)

    @staticmethod
    def is_complete_frame(buffer):
        """버퍼에 완전한 프레임이 있는지 확인

        Args:
            buffer (bytes): 수신 버퍼

        Returns:
            int: 완전한 프레임의 길이 또는 0 (완전한 프레임이 없는 경우)
        """
        # STX 찾기
        stx_index = -1
        for i in range(len(buffer)):
            if buffer[i] == Protocol.STX:
                stx_index = i
                break

        if stx_index == -1:
            return 0

        # ETX 찾기
        for i in range(stx_index + 1, len(buffer)):
            if buffer[i] == Protocol.ETX:
                return i - stx_index + 1

        return 0
