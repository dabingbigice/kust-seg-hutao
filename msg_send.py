import serial
import time
import binascii


def send_to_stm32(port='COM7', baudrate=9600, message="0"):
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            print(f"已连接 {ser.name}")

            # 核心修改：将 "0"/"1" 转换为 0x00/0x01
            if message == "0":
                hex_data = b'\x00'  # 二进制0
            elif message == "1":
                hex_data = b'\x01'  # 二进制1
            else:
                hex_data = message.encode('gbk')  # 其他内容仍用GBK编码

            ser.write(hex_data)
            print(f"发送HEX: {binascii.hexlify(hex_data).decode()}")

            # 接收响应（假设ESP32返回HEX）
            time.sleep(0.5)
            if ser.in_waiting > 0:
                response = ser.read_all()
                print(f"响应HEX: {binascii.hexlify(response).decode()}")

    except Exception as e:
        print(f"错误: {str(e)}")


# 测试
if __name__ == "__main__":
    # send_to_stm32(message="0")  # 发送 0x00
    send_to_stm32(message="1")  # 发送 0x01