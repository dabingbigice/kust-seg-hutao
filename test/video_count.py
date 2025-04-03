import cv2
for index in range(0, 10):
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    if cap.isOpened():
        print(f"可用摄像头编号: {index}")
        cap.release()