from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QThread
from PyQt5 import QtGui
from PyQt5 import QtCore

import os
import sys
import time
import random

# 부모 파일 경로, UI 파일 경로 선언
filePath = os.path.dirname(__file__)
uiPath = os.path.join(filePath, "taebo.ui")

# 클래스 UI, 객체로 생성 시 uic 모듈로 ui 로드하고 보여줌
class Ui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(uiPath)
        self.ui.setWindowTitle("절 대 태 보 해")
        #self.ui.showFullScreen()
        self.ui.show()
        # print(type(self)) # __main__.Ui
        # print(type(self.ui)) # QWidget
        
        self.worker = Worker(func=self.playTaebo, display=self.ui.display) # func로 쓰레드에 함수 넘기고 kwargs로 display 넘김
        #self.worker.signal.connect(self.ui.display.setText)
        #self.worker.statusChanged.connect()
        self.worker.start()

    def playTaebo(self, args): # 쓰레드에 넘겨주는 함수
        display = self.ui.display
        while True:
            displayString = ""
            for count in range(100):
                ascii = random.randrange(33, 126 + 1)
                displayString += chr(ascii)
            display.setText(displayString)
            time.sleep(0.01)

class Worker(QThread): # QThread 멀티 쓰레드
    #signal = QtCore.pyqtSignal(str)
    #statusChanged = QtCore.pyqtSignal(bool)

    def __init__(self, func, **kwargs):
        super(Worker, self).__init__()
        self.quit_flag = False
        self.func = func
        self.args = kwargs # kwargs로 딕셔너리 형태로 func제외 파라미터 다 받음

    def run(self):
        self.func(self.args)
        #self.func(self.signal, self.args)

# 메인 라인
if __name__ == "__main__":
    app = QApplication(sys.argv) # 애플리케이션 생성
    QtGui.QFontDatabase.addApplicationFont(os.path.join(filePath, "Galmuri9.ttf")) # 폰트 추가
    window = Ui() # UI 객체를 생성
    app.exec_() # 애플리케이션 실행