from multiprocessing import Process
import time

def asRun():
    for i in range(5):
        print("asrun: {}".format(i))
        time.sleep(1)

def run():
    time.sleep(1.5)
    print("ran")

if __name__ == "__main__":
    asProcess = Process(target=asRun)
    #process = Process(target=run)
    asProcess.start()
    #process.run()
    run()