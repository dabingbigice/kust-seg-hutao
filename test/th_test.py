import threading
import time

import cv2

shared_photo_frame_0 = []
shared_photo_ret_0 = []
shared_photo_frame_1 = []
shared_photo_ret_1 = []

th_flag = True


# 定义线程要执行的函数
def add_data(shared_list_frame, shared_list_ret, value, cap):
    while th_flag:
        time.sleep(30)
        start1 = time.time()
        ret, frame = cap.read()
        start2 = time.time()
        print(f'cap号摄像头读取照片时间{(start2 - start1) * 1000}ms')
        shared_list_frame.append(frame)
        shared_list_ret.append(ret)
        print(f"Added {value} by {threading.current_thread().name} to{cap}")



# 创建共享集合（这里用列表演示）
shared_list = []
if __name__ == "__main__":
    # 创建并启动新线程
    thread = threading.Thread(target=add_data, args=(shared_photo_frame_0,shared_photo_ret_0, "Hello World!",cv2.VideoCapture(0)),name="DelayThread-1")
    thread.start()

    # 等待线程执行完成
    thread.join()

    print("Final list:", shared_list)
