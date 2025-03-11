import cv2


class CameraController:
    def __init__(self):
        # Windows 必须指定 CAP_DSHOW 后端
        self.capture = cv2.VideoCapture(1)

        # Linux 使用自动检测（可能需要 v4l2）
        # self.capture = cv2.VideoCapture(f"/dev/video{index}")

        if not self.capture.isOpened():
            raise RuntimeError(f"无法打开摄像头:")

    def show_preview(self):
        while True:
            ret, frame = self.capture.read()
            if not ret:
                break
            cv2.imshow('Camera Preview', frame)
            if cv2.waitKey(1) == 27:  # ESC 退出
                break
        self.capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    # 第一步：获取摄像头名称（示例代码见下文）
    # 第二步：替换下方名称
    controller = CameraController()
    controller.show_preview()