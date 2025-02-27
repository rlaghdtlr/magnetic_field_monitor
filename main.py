#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
자계 노출 측정기 모니터링 시스템

자계 노출 측정기와 통신하여 상태를 모니터링하고 제어하는 시스템입니다.
"""

import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

from gui.main_window import MainWindow


def exception_hook(exctype, value, tb):
    """
    예외 처리 훅 함수

    Args:
        exctype: 예외 타입
        value: 예외 값
        tb: 트레이스백 객체
    """
    # 콘솔에 예외 출력
    traceback.print_exception(exctype, value, tb)

    # 예외 메시지 생성
    error_msg = "".join(traceback.format_exception(exctype, value, tb))

    # 오류 대화 상자 표시
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle("오류 발생")
    msg_box.setText("애플리케이션에서 오류가 발생했습니다.")
    msg_box.setDetailedText(error_msg)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()


def main():
    """
    메인 함수
    """
    # 예외 처리 훅 설정
    sys.excepthook = exception_hook

    # 애플리케이션 생성
    app = QApplication(sys.argv)

    # 애플리케이션 스타일 설정
    app.setStyle("Fusion")

    # 메인 윈도우 생성 및 표시
    main_window = MainWindow()
    main_window.show()

    # 애플리케이션 실행
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
