"""
로그 위젯 모듈

자계 노출 측정기의 로그 데이터를 표시하는 위젯을 정의합니다.
"""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QLabel,
    QDateTimeEdit,
    QGroupBox,
)
from PyQt5.QtCore import Qt, QDateTime, pyqtSlot
import csv
import os


class LogWidget(QWidget):
    """로그 위젯 클래스"""

    def __init__(self, data_manager, logger):
        """LogWidget 클래스 초기화

        Args:
            data_manager (DataManager): 데이터 관리 객체
            logger (Logger): 로거 객체
        """
        super().__init__()
        self.data_manager = data_manager
        self.logger = logger

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """UI 초기화"""
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)

        # 필터 그룹
        filter_group = QGroupBox("로그 필터")
        filter_layout = QHBoxLayout()

        # 시작 날짜/시간
        filter_layout.addWidget(QLabel("시작:"))
        self.start_datetime = QDateTimeEdit(QDateTime.currentDateTime().addDays(-7))
        self.start_datetime.setCalendarPopup(True)
        filter_layout.addWidget(self.start_datetime)

        # 종료 날짜/시간
        filter_layout.addWidget(QLabel("종료:"))
        self.end_datetime = QDateTimeEdit(QDateTime.currentDateTime())
        self.end_datetime.setCalendarPopup(True)
        filter_layout.addWidget(self.end_datetime)

        # 필터 적용 버튼
        self.apply_filter_button = QPushButton("필터 적용")
        filter_layout.addWidget(self.apply_filter_button)

        filter_group.setLayout(filter_layout)
        main_layout.addWidget(filter_group)

        # 로그 테이블
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(5)
        self.log_table.setHorizontalHeaderLabels(
            ["시간", "자계 상태", "감지 모드", "단위", "측정값"]
        )
        self.log_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.log_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.log_table.setAlternatingRowColors(True)
        self.log_table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.log_table)

        # 버튼 레이아웃
        button_layout = QHBoxLayout()

        # 새로고침 버튼
        self.refresh_button = QPushButton("새로고침")
        button_layout.addWidget(self.refresh_button)

        # 내보내기 버튼
        self.export_button = QPushButton("CSV로 내보내기")
        button_layout.addWidget(self.export_button)

        # 삭제 버튼
        self.delete_button = QPushButton("선택 항목 삭제")
        button_layout.addWidget(self.delete_button)

        # 전체 삭제 버튼
        self.clear_button = QPushButton("전체 삭제")
        button_layout.addWidget(self.clear_button)

        main_layout.addLayout(button_layout)

    def _connect_signals(self):
        """시그널 연결"""
        # 버튼 시그널
        self.refresh_button.clicked.connect(self._refresh_logs)
        self.export_button.clicked.connect(self._export_logs)
        self.delete_button.clicked.connect(self._delete_selected_logs)
        self.clear_button.clicked.connect(self._clear_logs)
        self.apply_filter_button.clicked.connect(self._refresh_logs)

    def _refresh_logs(self):
        """로그 데이터 새로고침"""
        self.logger.debug("로그 데이터 새로고침 요청")

        # 필터 날짜 가져오기
        start_date = self.start_datetime.dateTime().toPyDateTime()
        end_date = self.end_datetime.dateTime().toPyDateTime()

        # 로그 데이터 가져오기
        logs = self.data_manager.get_logs(start_date, end_date)

        # 테이블 초기화
        self.log_table.setRowCount(0)

        # 로그 데이터 표시
        for log in logs:
            row_position = self.log_table.rowCount()
            self.log_table.insertRow(row_position)

            # 시간
            self.log_table.setItem(
                row_position,
                0,
                QTableWidgetItem(log["timestamp"].strftime("%Y-%m-%d %H:%M:%S")),
            )

            # 자계 상태
            self.log_table.setItem(row_position, 1, QTableWidgetItem(log["b_field"]))

            # 감지 모드
            self.log_table.setItem(row_position, 2, QTableWidgetItem(log["detection"]))

            # 단위
            self.log_table.setItem(row_position, 3, QTableWidgetItem(log["unit"]))

            # 측정값
            self.log_table.setItem(row_position, 4, QTableWidgetItem(str(log["value"])))

        self.logger.info(f"{len(logs)}개의 로그 데이터 로드 완료")

    def _export_logs(self):
        """로그 데이터 CSV로 내보내기"""
        self.logger.debug("로그 데이터 내보내기 요청")

        # 파일 저장 대화 상자
        file_path, _ = QFileDialog.getSaveFileName(
            self, "CSV 파일 저장", "", "CSV 파일 (*.csv)"
        )

        if not file_path:
            return

        try:
            # 필터 날짜 가져오기
            start_date = self.start_datetime.dateTime().toPyDateTime()
            end_date = self.end_datetime.dateTime().toPyDateTime()

            # 로그 데이터 가져오기
            logs = self.data_manager.get_logs(start_date, end_date)

            # CSV 파일로 저장
            with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)

                # 헤더 작성
                writer.writerow(["시간", "자계 상태", "감지 모드", "단위", "측정값"])

                # 데이터 작성
                for log in logs:
                    writer.writerow(
                        [
                            log["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                            log["b_field"],
                            log["detection"],
                            log["unit"],
                            log["value"],
                        ]
                    )

            self.logger.info(f"{len(logs)}개의 로그 데이터를 {file_path}에 저장 완료")
            QMessageBox.information(
                self, "내보내기 완료", f"{len(logs)}개의 로그 데이터를 저장했습니다."
            )

        except Exception as e:
            self.logger.error(f"로그 데이터 내보내기 실패: {str(e)}")
            QMessageBox.warning(
                self,
                "내보내기 실패",
                f"로그 데이터를 저장하는 중 오류가 발생했습니다: {str(e)}",
            )

    def _delete_selected_logs(self):
        """선택된 로그 항목 삭제"""
        selected_rows = set()
        for item in self.log_table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            QMessageBox.information(self, "알림", "삭제할 항목을 선택해주세요.")
            return

        # 확인 대화 상자
        reply = QMessageBox.question(
            self,
            "로그 삭제",
            f"선택한 {len(selected_rows)}개의 로그 항목을 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        # 선택된 로그의 타임스탬프 수집
        timestamps = []
        for row in sorted(selected_rows, reverse=True):
            timestamp_str = self.log_table.item(row, 0).text()
            timestamps.append(timestamp_str)

            # UI에서 행 제거
            self.log_table.removeRow(row)

        # 데이터베이스에서 삭제
        self.data_manager.delete_logs_by_timestamps(timestamps)

        self.logger.info(f"{len(selected_rows)}개의 로그 항목 삭제 완료")
        QMessageBox.information(
            self, "삭제 완료", f"{len(selected_rows)}개의 로그 항목을 삭제했습니다."
        )

    def _clear_logs(self):
        """모든 로그 항목 삭제"""
        # 확인 대화 상자
        reply = QMessageBox.question(
            self,
            "로그 전체 삭제",
            "모든 로그 항목을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        # 필터 날짜 가져오기
        start_date = self.start_datetime.dateTime().toPyDateTime()
        end_date = self.end_datetime.dateTime().toPyDateTime()

        # 데이터베이스에서 삭제
        count = self.data_manager.clear_logs(start_date, end_date)

        # UI 업데이트
        self.log_table.setRowCount(0)

        self.logger.info(f"{count}개의 로그 항목 전체 삭제 완료")
        QMessageBox.information(
            self, "삭제 완료", f"{count}개의 로그 항목을 삭제했습니다."
        )

    def add_log_entry(self, log_data):
        """새 로그 항목 추가

        Args:
            log_data (dict): 로그 데이터
        """
        # 현재 필터 범위 내에 있는지 확인
        log_time = log_data["timestamp"]
        start_date = self.start_datetime.dateTime().toPyDateTime()
        end_date = self.end_datetime.dateTime().toPyDateTime()

        if not (start_date <= log_time <= end_date):
            return

        # 테이블에 새 행 추가
        row_position = 0
        self.log_table.insertRow(row_position)

        # 시간
        self.log_table.setItem(
            row_position, 0, QTableWidgetItem(log_time.strftime("%Y-%m-%d %H:%M:%S"))
        )

        # 자계 상태
        self.log_table.setItem(row_position, 1, QTableWidgetItem(log_data["b_field"]))

        # 감지 모드
        self.log_table.setItem(row_position, 2, QTableWidgetItem(log_data["detection"]))

        # 단위
        self.log_table.setItem(row_position, 3, QTableWidgetItem(log_data["unit"]))

        # 측정값
        self.log_table.setItem(
            row_position, 4, QTableWidgetItem(str(log_data["value"]))
        )
