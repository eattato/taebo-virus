from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QThread
from PyQt5 import QtGui
from PyQt5 import QtCore

import os
import sys
import time
import math

# 부모 파일 경로, UI 파일 경로 선언
filePath = os.path.dirname(__file__)
uiPath = os.path.join(filePath, "taebo.ui")

# 클래스 UI, 객체로 생성 시 uic 모듈로 ui 로드하고 보여줌
class Ui(QMainWindow):
    def __init__(self, timing):
        super().__init__()
        self.timing = timing
        self.ui = uic.loadUi(uiPath)
        self.ui.setWindowTitle("절 대 태 보 해")
        self.ui.showFullScreen()
        
        # 1. Worker 객체로 다른 쓰레드 생성해 playTaebo를 돌림
        # 2. Worker의 signal을 이 메인 쓰레드의 self.ui.display.setText()에 연결,
        # 3. Worker 쓰레드에서는 받은 func 함수에 아까 연결된 자신의 signal을 매개 변수로 넘김
        # 4. func 함수가 받은 signal에서 emit을 호출해서 원격으로 메인 쓰레드의 요소를 수정
        self.worker = Worker(func=self.playTaebo) # func로 쓰레드에 함수 넘김
        self.worker.signal.connect(self.ui.display.setText) # Worker 쓰레드의 signal과 디스플레이의 setText 연결
        self.worker.start()

    def playTaebo(self, signal, args): # 쓰레드에 넘겨주는 함수
        motionIndex = 0
        repeatCount = 2
        taeboMotion = [
            [ # 모션팩 1
                "@(^0^ )@",
                "@=(^0^ )@",
                "@==(^0^ )@",
                "@=(^0^ )@",
                "@(^0^ )@",
            ],
            [ # 모션팩 2
                "@( ^0^)@",
                "@( ^0^)=@",
                "@( ^0^)==@",
                "@( ^0^)=@",
                "@( ^0^)@",
            ]
        ]

        packCount = len(taeboMotion) # 모션팩 갯수
        countPerPack = len(taeboMotion[0]) # 모션팩 별 내용물 갯수
        countPerRepeat = packCount * countPerPack # 한 루프 당 몇 번 돌리는지
        totalCount = countPerRepeat * packCount # 모든 팩과 루프를 다 돌리면 몇 번 돌리는지

        while True:
            repeatIndex = math.floor(motionIndex / countPerPack) # 몇 번째 루프인지
            packIndex = math.floor(motionIndex / countPerRepeat) # 몇 번째 모션팩인지
            packMotionIndex = motionIndex - repeatIndex * countPerPack # 모션팩 & 루프 수를 제외한 motionIndex
            signal.emit(taeboMotion[packIndex][packMotionIndex]) # Worker의 signal을 받아 작동, 메인 쓰레드에 연결된 setText 함수 실행
            motionIndex += 1
            if motionIndex >= totalCount:
                motionIndex = 0

            time.sleep(self.timing)

    def resize(self, width, height): # 디스플레이 크기 조정
        self.ui.display.resize(width, height)

# QThread 멀티 쓰레드
class Worker(QThread):
    signal = QtCore.pyqtSignal(str)
    #statusChanged = QtCore.pyqtSignal(bool)

    def __init__(self, func, **kwargs):
        super(Worker, self).__init__()
        self.quit_flag = False
        self.func = func
        self.args = kwargs # kwargs로 딕셔너리 형태로 func제외 파라미터 다 받음

    def run(self):
        self.func(self.signal, self.args)

# 메인 라인
if __name__ == "__main__":
    app = QApplication(sys.argv) # 애플리케이션 생성

    # 크기 조정
    screen = app.primaryScreen()
    QtGui.QFontDatabase.addApplicationFont(os.path.join(filePath, "malgun.ttf")) # 폰트 추가
    window = Ui(0.1) # UI 객체를 생성
    window.resize(screen.size().width(), screen.size().height())

    app.exec_() # 애플리케이션 실행