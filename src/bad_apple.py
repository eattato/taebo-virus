from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QThread
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from moviepy.editor import VideoFileClip

import os
import sys
import time
import math

import cv2

# 부모 파일 경로, UI 파일 경로 선언
filePath = os.path.dirname(__file__)
uiPath = os.path.join(filePath, "taebo.ui")

def asciiConvert(frame, widthTo): # 프레임을 아스키 아트로 바꿔줌
    result = []
    grayScaleDisplay = ["⠀", "⠄", "⠆", "⠖", "⠶", "⡶", "⣩", "⣪", "⣫", "⣾", "⣿"]
    #grayScaleDisplay = [" ", ".", ",", ":", ";", "+", "*", "?", "%", "S", "#", "@"]
    grayScaleDisplay.reverse()

    # 이미지 종횡비 계산
    width = frame.shape[1]
    height = frame.shape[0]
    scale = widthTo / width
    dim = (int(width * scale), int(height * scale)) # 조정될 이미지 크기

    frame = cv2.resize(frame, dim) # 이미지 크기 조정
    grayScaled = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # 그레이 스케일 변환

    # 픽셀 데이터 1차원으로 변환 후 아스키 형태로 변환
    result = ""
    for col in range(0, dim[1]):
        for row in range(0, dim[0]):
            pixelData = grayScaled.item(col, row)
            result += grayScaleDisplay[pixelData // 25]
        result += "\n"
    return result

# 클래스 UI, 객체로 생성 시 uic 모듈로 ui 로드하고 보여줌
class Ui(QMainWindow):
    def __init__(self, timing, fontSize, width, vidPath):
        super().__init__()
        self.timing = timing
        self.ui = uic.loadUi(uiPath)
        self.ui.setWindowTitle("절 대 태 보 해")
        self.ui.showFullScreen()
        self.ui.display.setFont(QtGui.QFont("malgun", fontSize))
        self.player = QMediaPlayer()
        self.screenSize = width
        self.vidPath = vidPath
        
        # 1. Worker 객체로 다른 쓰레드 생성해 playTaebo를 돌림
        # 2. Worker의 signal을 이 메인 쓰레드의 self.ui.display.setText()에 연결,
        # 3. Worker 쓰레드에서는 받은 func 함수에 아까 연결된 자신의 signal을 매개 변수로 넘김
        # 4. func 함수가 받은 signal에서 emit을 호출해서 원격으로 메인 쓰레드의 요소를 수정
        self.worker = Worker(func=self.playBadApple) # func로 쓰레드에 함수 넘김
        self.worker.signal.connect(self.ui.display.setText) # Worker 쓰레드의 signal과 디스플레이의 setText 연결
        #self.worker.createSignal("player", None)
        self.worker.start()

    def playBadApple(self, signal, args): # 쓰레드에 넘겨주는 함수
        signal.emit("opening..")
        caps = cv2.VideoCapture(self.vidPath + ".mp4")
        if caps.isOpened():
            signal.emit("video opened.")
            #caps.set(cv2.CAP_PROP_MODE, cv2.CAP_MODE_GRAY) # 그레이 스케일 변환
            results = []

            fps = caps.get(cv2.CAP_PROP_FPS)
            frameCount = int(caps.get(cv2.CAP_PROP_FRAME_COUNT))
            totalTime = frameCount / fps
            print("fps: {}, got {} frames in total.".format(fps, frameCount))

            # 프레임 골라내기
            signal.emit("picking frames..")
            currentTime = 0
            targetFrames = []
            while currentTime <= totalTime:
                currentFrame = math.floor(currentTime * fps)# / frameCount
                targetFrames.append(currentFrame)
                currentTime += self.timing
                #caps.set(cv2.CAP_PROP_POS_FRAMES, currentFrame) # 0부터 시작하는 프레임 인덱스 셀렉터 - 오류로 안 씀
            signal.emit("frame picking done.")
                
            # 아스키 아트 저장
            signal.emit("ascii converting..")
            print("ascii converting..")
            for ind in range(0, frameCount):
                signal.emit("ascii converting.. ({} / {})".format(ind, frameCount))
                ret, frame = caps.read() # 프레임 읽기
                if ind in targetFrames:
                    results.append(asciiConvert(frame, self.screenSize)) # 프레임을 width 120짜리 아스키 아트로 변경
            print("ascii convert done.")
            signal.emit("ascii converting done.")

            # 오디오 추출
            self.playSound(signal)

            # 재생
            print("playing..")
            currentTime = 0
            for ascii in results:
                signal.emit(ascii)
                time.sleep(self.timing)
            signal.emit("NO SIGNAL")
            print("done.")
        else:
            print("wrong video!")
            signal.emit("이런! 영상을 불러오지 못했어요.")

    def resize(self, width, height): # 디스플레이 크기 조정
        self.ui.display.resize(width, height)

    def playSound(self, signal):
        signal.emit("audio converting..")
        video = VideoFileClip(self.vidPath + ".mp4")
        audio = video.audio
        audio.write_audiofile(self.vidPath + ".mp3")
        audio.close()
        video.close()
        signal.emit("audio convert done.")

        fileUrl = QtCore.QUrl.fromLocalFile(self.vidPath + ".mp3")
        content = QMediaContent(fileUrl)
        self.player.setMedia(content)
        self.player.play()

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

    def createSignal(self, name, signalType): # 시그널 만들어도 안 써짐 아 ㅋㅋ
        if signalType == None:
            self.signals[name] = QtCore.pyqtSignal()
        else:
            self.signals[name] = QtCore.pyqtSignal(signalType)

# 메인 라인
if __name__ == "__main__":
    app = QApplication(sys.argv) # 애플리케이션 생성

    # 크기 조정
    screen = app.primaryScreen()
    QtGui.QFontDatabase.addApplicationFont(os.path.join(filePath, "malgun.ttf")) # 폰트 추가
    window = Ui(0.1, 10, 120, os.path.join(filePath, "badapple")) # UI 객체를 생성
    window.resize(screen.size().width(), screen.size().height())

    app.exec_() # 애플리케이션 실행