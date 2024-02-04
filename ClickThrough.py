import time
import threading
import win32gui
import win32con
from pynput import mouse

click_times = []
double_click_threshold = 0.5
sem = threading.Semaphore(0)

def on_click(x, y, button, pressed):
    if button == mouse.Button.left and pressed:
        now = time.time()
        if click_times and (now - click_times[-1] < double_click_threshold):
            time.sleep(0.5)
            sem.release()
            click_times.clear()
        else:
            click_times.append(now)

def set_window_attributes(hwnd, transparency, click_through):
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    if click_through:
        style |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
    else:
        style &= ~win32con.WS_EX_TRANSPARENT
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)
    win32gui.SetLayeredWindowAttributes(hwnd, 0, transparency, win32con.LWA_ALPHA)

def is_excluded_window(hwnd):
    excluded_classes = ['Progman', 'WorkerW', 'Shell_TrayWnd']
    class_name = win32gui.GetClassName(hwnd)
    return class_name in excluded_classes or    win32gui.IsIconic(hwnd) or not win32gui.IsWindowVisible(hwnd)

def process_windows(transparency, click_through):
    def callback(hwnd, extra):
        if not is_excluded_window(hwnd):
            set_window_attributes(hwnd, transparency, click_through)
        return True
    win32gui.EnumWindows(callback, None)

if __name__ == "__main__":
    process_windows(20, True)

    mouse.Listener(on_click=on_click).start()
    sem.acquire()

    process_windows(255, False)

