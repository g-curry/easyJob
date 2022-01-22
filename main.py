import os
import serial
import tkinter as tk
import serial.tools.list_ports
import pyautogui as pg
import time
import random

mserial = None

# ch9329 键值对
key_map = {
    'A': 0x4,
    'B': 0x5,
    'C': 0x6,
    'D': 0x7,
    'E': 0x8,
    'F': 0x9,
    'G': 0xA,
    'H': 0xB,
    'I': 0xC,
    'J': 0xD,
    'K': 0xE,
    'L': 0xF,
    'M': 0x10,
    'N': 0x11,
    'O': 0x12,
    'P': 0x13,
    'Q': 0x14,
    'R': 0x15,
    'S': 0x16,
    'T': 0x17,
    'U': 0x18,
    'V': 0x19,
    'W': 0x1A,
    'X': 0x1B,
    'Y': 0x1C,
    'Z': 0x1D,

    '1': 0x1E,
    '2': 0x1F,
    '3': 0x20,
    '4': 0x21,
    '5': 0x22,
    '6': 0x23,
    '7': 0x24,
    '8': 0x25,
    '9': 0x26,
    '0': 0x27,

    ';': 0x33,
    '‘': 0x34,
    '`': 0x35,
    ',': 0x36,
    '.': 0x37,
    '/': 0x38,

    'TAB': 0x2B,
    ' ': 0x2C,
    '-': 0x2D,
    '+': 0x2E,
    '[': 0x2F,
    ']': 0x30,
    '\\': 0x31,

    'ESC': 0x29,
    'DELETE': 0x4C,
    'ENTER': 0x28,

    'UP': 0x4F,
    'DOWN': 0x50,
    'LEFT': 0x51,
    'RIGHT': 0x52,
    '*': 0x55,

}
# ch9329 控制键offset
control_key_map = {
    'CTRL': 0,
    'SHIFT': 1,
    'CLT': 2,
    'WIN': 3,
}


def hang_out():
    # 在棋盘小范围内随机游荡，防止鼠标指针挡住关卡图片导致检测不到3-2关卡
    x = random.randint(400, 1500)
    y = random.randint(100, 700)

    # 随机点击2-5下鼠标右键
    for i in range(random.randint(2, 5)):
        hard_click(x, y, button=pg.RIGHT)
        time.sleep(0.1)

    return True


def get_button_val(button):
    if button == pg.LEFT:
        return 0
    if button == pg.RIGHT:
        return 1
    if button == pg.MIDDLE:
        return 2


def hard_click(x, y, clicks=1, interval=0.0, button=pg.LEFT, duration=0.0):
    global mserial
    nx = int(x * 4096 / 1920)
    ny = int(y * 4096 / 1080)
    # 鼠标绝对坐标命令
    cmd = [0x57, 0xAB, 0x00, 0x04, 0x07, 0x02]
    button_val = 1 << get_button_val(button)
    low_x = nx & 0xFF
    high_x = (nx >> 8) & 0xFF
    low_y = ny & 0xFF
    high_y = (ny >> 8) & 0xFF
    scroll = 0x00
    data = [button_val, low_x, high_x, low_y, high_y, scroll]
    sum_val = (sum(cmd) + sum(data)) & 0xFF
    data.append(sum_val)
    # 按下
    press = cmd + data
    # 释放
    release = press.copy()
    release[6] = 0x0
    sum_val = sum(release[:-1]) & 0xFF
    release[len(release) - 1] = sum_val

    while clicks > 0:
        # 移动并按下键
        mserial.write(bytes(press))
        # 延时50ms
        time.sleep(50 / 1000)
        # mserial.readall()
        # 释放键
        mserial.write(bytes(release))
        time.sleep(50 / 1000)
        # mserial.readall()
        clicks -= 1
        if clicks > 0:
            time.sleep(interval)

    mserial.flushInput()

    return True


def get_available_serial():
    l = list(serial.tools.list_ports.comports())
    if len(l) < 1:
        return False
    port_list = list(l[0])
    port = port_list[0]
    return port


def open_serial():
    global mserial
    port = get_available_serial()
    if not port:
        return False
    # mserial = serial.Serial("COM3", 115200, timeout=1)
    mserial = serial.Serial(port, 9600, timeout=1)

    return True


def hard_key_write(keys):
    global key_map, control_key_map
    l_keys = keys.split('+')
    # print(l_keys[0], l_keys[1])
    v = []
    c = []
    for k in l_keys:
        k = k.upper()
        if k in key_map:
            v.append(key_map[k])
        if k in control_key_map:
            c.append(control_key_map[k])

    cmd = [0x57, 0xab, 0x00, 0x02, 0x08]
    data = []

    ctl_byte = 0x0
    for i in c:
        ctl_byte += 1 << i
    data.append(ctl_byte)  # 1
    data.append(0x00)  # 2
    data += v[:6]  # 3-8
    data += [0] * (8 - len(data))

    press = cmd + data
    press.append(sum(press) & 0xFF)

    release = [0x57, 0xab, 0x00, 0x02, 0x08] + [0x00] * 8 + [0x0c]

    mserial.write(bytes(press))
    # 延时50ms
    time.sleep(50 / 1000)
    # 释放键
    mserial.write(bytes(release))
    time.sleep(50 / 1000)

    mserial.flushInput()

    return True


def check_input(input):
    time.sleep(5)
    while True:
        for k in input:
            # 大写
            if k.isupper():
                hard_key_write(k + '+shift')
                time.sleep(random.random())
                continue

            if k == '{':
                hard_key_write('[+shift')
                time.sleep(random.random())
                continue

            if k == '}':
                hard_key_write(']+shift')
                time.sleep(random.random())
                continue

            if k == '(':
                hard_key_write('9+shift')
                time.sleep(random.random())
                continue

            if k == ')':
                hard_key_write('0+shift')
                time.sleep(random.random())
                continue

            if k == '_':
                hard_key_write('-+shift')
                time.sleep(random.random())
                continue

            if k == '?':
                hard_key_write('/+shift')
                time.sleep(random.random())
                continue

            if k == '\n':
                hard_key_write('ENTER')
                time.sleep(random.random())
                continue

            if k == '\t':
                hard_key_write('TAB')
                time.sleep(random.random())
                continue

            # if k == '”' or k == '“' or k == '"':
            #    hard_key_write('‘+shift')
            #    time.sleep(random.random())
            #    continue

            k = k.upper()
            if k in key_map:
                if k == ' ':
                    time.sleep(5)
                hard_key_write(k)
                time.sleep(random.random())
        time.sleep(5)


def tk_init():
    # 第1步，建立窗口window
    window = tk.Tk()  # 建立窗口window
    # 第2步，给窗口起名称
    window.title('示例1')  # 窗口名称
    # 第3步，设定窗口的大小(长＊宽)
    window.geometry("400x240")  # 窗口大小(长＊宽)
    # 第4步，在图形化界面上设定一个文本框
    textExample = tk.Text(window, height=10)  # 创建文本输入框
    # 第5步，安置文本框
    textExample.pack()  # 把Text放在window上面，显示Text这个控件

    # Tkinter 文本框控件中第一个字符的位置是 1.0，可以用数字 1.0 或字符串"1.0"来表示。
    # "end"表示它将读取直到文本框的结尾的输入。我们也可以在这里使用 tk.END 代替字符串"end"。
    def getTextInput():
        result = textExample.get("1.0", "end")  # 获取文本输入框的内容
        print(result)  # 输出结果
        check_input(result)

    # 第7步，在图形化界面上设定一个button按钮（#command绑定获取文本框内容的方法）
    # def shutdown():
    #     os._exit(0)
    btnRead = tk.Button(window, height=1, width=10, text="Read", command=getTextInput)  # command绑定获取文本框内容的方法
    # btnShutdown = tk.Button(window, height=1, width=10, text="shutdown", command=shutdown)  # command绑定获取文本框内容的方法
    # 第8步，安置按钮
    btnRead.pack()  # 显示按钮
    # btnShutdown.pack()
    # 第9步，
    window.mainloop()  # 显示窗口


if __name__ == '__main__':
    open_serial()
    tk_init()
