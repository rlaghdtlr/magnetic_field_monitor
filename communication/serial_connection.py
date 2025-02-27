"""
시리얼 통신 관리 모듈

RS-232C 통신을 통해 자계 노출 측정기와의 연결을 관리합니다.
"""

import serial
import time
from PyQt5.QtCore import QObject, pyqtSignal


class SerialConnection(QObject):
    """시리얼 통신 연결을 관리하는 클래스"""

    # 시그널 정의
    connected = pyqtSignal(bool)
    data_received = pyqtSignal(bytes)
    error_occurred = pyqtSignal(str)
    connection_changed = pyqtSignal(bool)
    status_updated = pyqtSignal(dict)
    control_updated = pyqtSignal(str, bool)

    def __init__(self, logger):
        """SerialConnection 클래스 초기화

        Args:
            logger (Logger): 로거 객체
        """
        super().__init__()
        self.logger = logger
        self.serial = None
        self._is_connected = False
        self.port = ""
        self.baudrate = 9600
        self.bytesize = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.timeout = 1

    def connect(
        self,
        port,
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1,
    ):
        """시리얼 포트에 연결

        Args:
            port (str): 시리얼 포트 이름
            baudrate (int): 통신 속도 (기본값: 9600)
            bytesize (int): 데이터 비트 (기본값: 8)
            parity (str): 패리티 비트 (기본값: 없음)
            stopbits (float): 정지 비트 (기본값: 1)
            timeout (float): 타임아웃 (초) (기본값: 1)

        Returns:
            bool: 연결 성공 여부
        """
        try:
            self.port = port
            self.baudrate = baudrate
            self.bytesize = bytesize
            self.parity = parity
            self.stopbits = stopbits
            self.timeout = timeout

            self.serial = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=bytesize,
                parity=parity,
                stopbits=stopbits,
                timeout=timeout,
            )

            self._is_connected = True
            self.connection_changed.emit(True)
            self.logger.info(f"포트 {port}에 연결되었습니다.")
            return True

        except serial.SerialException as e:
            self.error_occurred.emit(f"연결 오류: {str(e)}")
            self._is_connected = False
            self.connection_changed.emit(False)
            self.logger.error(f"연결 오류: {str(e)}")
            return False

    def disconnect(self):
        """시리얼 포트 연결 해제"""
        if self.serial and self.serial.is_open:
            self.serial.close()

        self._is_connected = False
        self.connection_changed.emit(False)
        self.logger.info("연결이 해제되었습니다.")

    def send_data(self, data):
        """데이터 전송

        Args:
            data (bytes): 전송할 데이터

        Returns:
            bool: 전송 성공 여부
        """
        if not self._is_connected or not self.serial:
            self.error_occurred.emit(
                "연결되지 않은 상태에서 데이터를 전송할 수 없습니다."
            )
            self.logger.error("연결되지 않은 상태에서 데이터 전송 시도")
            return False

        try:
            self.serial.write(data)
            # 전송 데이터 로깅 추가
            self.logger.debug(f"데이터 전송: {data.hex()}")
            return True

        except serial.SerialException as e:
            self.error_occurred.emit(f"데이터 전송 오류: {str(e)}")
            self.logger.error(f"데이터 전송 오류: {str(e)}")
            return False

    def read_data(self, size=1024):
        """데이터 수신

        Args:
            size (int): 읽을 최대 바이트 수 (기본값: 1024)

        Returns:
            bytes: 수신된 데이터 또는 None (오류 발생 시)
        """
        if not self._is_connected or not self.serial:
            self.error_occurred.emit(
                "연결되지 않은 상태에서 데이터를 수신할 수 없습니다."
            )
            self.logger.error("연결되지 않은 상태에서 데이터 수신 시도")
            return None

        try:
            data = self.serial.read(size)
            if data:
                self.data_received.emit(data)
            return data

        except serial.SerialException as e:
            self.error_occurred.emit(f"데이터 수신 오류: {str(e)}")
            self.logger.error(f"데이터 수신 오류: {str(e)}")
            return None

    def get_available_ports(self):
        """사용 가능한 시리얼 포트 목록 반환

        Returns:
            list: 사용 가능한 시리얼 포트 목록
        """
        import serial.tools.list_ports

        return [port.device for port in serial.tools.list_ports.comports()]

    def receive_data(self, timeout=3.0):
        """응답 데이터 수신

        Args:
            timeout (float): 타임아웃 (초) (기본값: 3.0)

        Returns:
            bytes: 수신된 데이터 또는 None (오류 발생 시)
        """
        if not self._is_connected or not self.serial:
            self.error_occurred.emit(
                "연결되지 않은 상태에서 데이터를 수신할 수 없습니다."
            )
            self.logger.error("연결되지 않은 상태에서 데이터 수신 시도")
            return None

        try:
            # 타임아웃 설정
            start_time = time.time()
            buffer = bytearray()

            # 디버깅 정보 추가
            self.logger.debug(f"데이터 수신 대기 시작 (타임아웃: {timeout}초)")

            # 데이터 수신 대기
            while (time.time() - start_time) < timeout:
                if self.serial.in_waiting > 0:
                    # 데이터 읽기
                    data = self.serial.read(self.serial.in_waiting)
                    buffer.extend(data)

                    # 디버깅 정보 추가
                    self.logger.debug(
                        f"데이터 수신: {data.hex()}, 버퍼 크기: {len(buffer)}"
                    )

                    # STX와 ETX를 찾아 완전한 프레임 확인
                    from communication.protocol import Protocol

                    # 버퍼에서 STX 위치 찾기
                    stx_index = -1
                    for i in range(len(buffer)):
                        if buffer[i] == Protocol.STX:
                            stx_index = i
                            break

                    # STX가 없으면 계속 대기
                    if stx_index == -1:
                        continue

                    # 불필요한 데이터 제거
                    if stx_index > 0:
                        buffer = buffer[stx_index:]

                    # ETX 위치 찾기
                    etx_index = -1
                    for i in range(1, len(buffer)):
                        if buffer[i] == Protocol.ETX:
                            etx_index = i
                            break

                    # 완전한 프레임이 있으면 반환
                    if etx_index > 0:
                        # 완전한 프레임 추출 (STX부터 ETX까지)
                        frame = buffer[: etx_index + 1]

                        # 최소 프레임 길이 확인 (STX + TYPE(2) + CRC(4) + ETX = 최소 8바이트)
                        if len(frame) >= 8:
                            # bytearray를 bytes로 변환하여 emit
                            self.data_received.emit(bytes(frame))
                            self.logger.debug(f"완전한 프레임 수신: {frame.hex()}")
                            return bytes(frame)

                # 잠시 대기
                time.sleep(0.01)

            # 타임아웃 발생
            elapsed = time.time() - start_time
            if buffer:
                self.logger.warning(
                    f"불완전한 데이터 수신 (경과 시간: {elapsed:.2f}초): {buffer.hex()}"
                )
                return bytes(buffer)  # 불완전한 데이터라도 반환
            else:
                self.logger.warning(f"응답 타임아웃 (경과 시간: {elapsed:.2f}초)")
                return None

        except serial.SerialException as e:
            self.error_occurred.emit(f"데이터 수신 오류: {str(e)}")
            self.logger.error(f"데이터 수신 오류: {str(e)}")
            return None

    def is_connected(self):
        """연결 상태 확인

        Returns:
            bool: 연결 상태
        """
        return self._is_connected
