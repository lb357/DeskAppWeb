import pyautogui
import threading
import time
from PIL import ImageOps, ImageDraw
import io
import tornado.web
import tornado.websocket
import tornado.ioloop
import json
import pydirectinput
import os

# URL = "6.tcp.eu.ngrok.io:16351"
# IP = "localhost"
URL = "192.168.100.29"
IP = "192.168.100.29"
PORT = 80

class configurator:
    def __init__(self, config_file = "config.json"):
        self.use_pos_handler = True
        self.handler_mode = 1
        self.region = (0, 0, 1280, 720)
        self.grayscale = True
        self.ip = "127.0.0.1"
        self.url = "localhost"
        self.port = 80

        with open(config_file) as file:
            config_json = json.load(file)

        for param in config_json:
            if param == "UsePosHandler":
                self.use_pos_handler = bool(config_json[param])
            elif param == "HandlerMode":
                self.handler_mode = int(config_json[param])
            elif param == "CaptureArea":
                self.region = tuple(config_json[param])
            elif param == "Grayscale":
                self.grayscale = bool(config_json[param])
            elif param == "IP":
                self.ip = str(config_json[param])
            elif param == "URL":
                self.url = str(config_json[param])
            elif param == "PORT":
                self.port = int(config_json[param])
            else:
                print(f"Unknown param: {param}")
        print("PARAMS:", self.use_pos_handler, self.handler_mode,
              self.region, self.grayscale, self.ip, self.url, self.port)



class ScreenCapture:
    def __init__(self, region=(0, 0, 1280, 720), grayscale=True):
        self.data = []
        self.region = region
        self.time = 0
        self.x, self.y = region[0], region[1]
        self.threads_list = []
        self.grayscale = grayscale

    def get_image(self):
        pil_img = pyautogui.screenshot(region=self.region)
        draw = ImageDraw.Draw(pil_img)
        mx, my = pyautogui.position()
        mx -= self.x
        my -= self.y
        ms = 3
        draw.ellipse((mx - ms - 1, my - ms - 1, mx + ms + 1, my + ms + 1), fill=(0, 0, 0, 0))
        draw.ellipse((mx - ms, my - ms, mx + ms, my + ms), fill=(255, 255, 255, 0))
        if self.grayscale:
            pil_img = ImageOps.grayscale(pil_img)
        img_bytes = io.BytesIO()
        pil_img.save(img_bytes, format="JPEG")
        data_temp = img_bytes.getvalue()
        cur_time = time.time()
        if cur_time > self.time:
            self.time = cur_time
            self.data = data_temp

    def handler(self):
        while True:
            self.get_image()

    def start(self, count=1):
        for i in range(count):
            thread = threading.Thread(target=self.handler)
            thread.start()
            self.threads_list.append(thread)


class InputHandler:
    def __init__(self, screen_capture, KeyCodesFile="KeyCodes.json", handler_mode = 1, use_pos_handler=False, ):
        self.screen_capture = screen_capture
        self.handler_mode = handler_mode
        self.use_pos_handler = use_pos_handler
        with open(KeyCodesFile) as file:
            self.key_codes = json.load(file)

    def action(self, action, data):
        #print(action,data)
        try:
            if action == 1:
                if self.use_pos_handler:
                    if self.handler_mode == 1 or self.handler_mode == 2:
                        pydirectinput.moveTo(self.screen_capture.x + data[0], None)
                    else:
                        pyautogui.moveTo(self.screen_capture.x + data[0], None)
            elif action == 2:
                if self.use_pos_handler:
                    if self.handler_mode == 1 or self.handler_mode == 2:
                        pydirectinput.moveTo(None, self.screen_capture.y + data[0])
                    else:
                        pyautogui.moveTo(None, self.screen_capture.y + data[0])
            elif action == 3:
                if data[0] == 1:
                    if self.handler_mode == 2:
                        pydirectinput.mouseDown()
                    else:
                        pyautogui.mouseDown()
                elif data[0] == 3:
                    if self.handler_mode == 2:
                        pydirectinput.mouseDown(button="right")
                    else:
                        pyautogui.mouseDown(button="right")
            elif action == 4:
                sdata = str(data[0])
                if sdata in self.key_codes:
                    if self.handler_mode == 2:
                        pydirectinput.keyDown(self.key_codes[sdata])
                    else:
                        pyautogui.keyDown(self.key_codes[sdata])
            elif action == 5:
                if data[0] == 1:
                    if self.handler_mode == 2:
                        pydirectinput.mouseUp()
                    else:
                        pyautogui.mouseUp()
                elif data[0] == 3:
                    if self.handler_mode == 2:
                        pydirectinput.mouseUp(button="right")
                    else:
                        pyautogui.mouseUp(button="right")
            elif action == 6:
                pyautogui.scroll(-data[0])
            elif action == 7:
                sdata = str(data[0])
                if sdata in self.key_codes:
                    if self.handler_mode == 2:
                        pydirectinput.keyUp(self.key_codes[sdata])
                    else:
                        pyautogui.keyUp(self.key_codes[sdata])
            elif action == 8:
                if self.use_pos_handler:
                    if self.handler_mode == 1 or self.handler_mode == 2:
                        pydirectinput.moveTo(self.screen_capture.x + data[0], self.screen_capture.y + data[1])
                    else:
                        pyautogui.moveTo(self.screen_capture.x + data[0], self.screen_capture.y + data[1])
            else:
                print("unknown action", action)
        except Exception as err:
            print("ERROR:", err)

    def handle(self, action, data):
        thread = threading.Thread(target=self.action, args=(action, data))
        thread.start()
        # pass


class WebSocketMediaHandler(tornado.websocket.WebSocketHandler):
    def initialize(self, screen_capture):
        self.screen_capture = screen_capture

    def open(self):
        print("WebSocket (media) opened")

    def on_message(self, message):
        action = int(message[0])
        if action == 0:
            self.write_message(self.screen_capture.data, True)
        else:
            print("unknown action (media)", action)

    def on_close(self):
        print("WebSocket (media) closed")


class WebSocketInputHandler(tornado.websocket.WebSocketHandler):
    def initialize(self, input_handler):
        self.input_handler = input_handler

    def open(self):
        print("WebSocket (input) opened")

    def on_message(self, message):
        action = int(message[0])
        data = list(map(int, message[1:].split("\t")))
        self.input_handler.handle(action, data)

    def on_close(self):
        print("WebSocket (input) closed")


def js_bool(value:bool):
    return str(bool(value)).lower()


class MainHandler(tornado.web.RequestHandler):
    def initialize(self, url, use_joined_pos):
        self.url = url
        self.use_joined_pos = js_bool(use_joined_pos)

    def get(self):
        self.render("static/index.html", url=self.url, use_joined_pos=self.use_joined_pos)
        print("HTML opened")


def run(**kwargs):
    config = configurator()
    pyautogui.FAILSAFE = False
    pydirectinput.FAILSAFE = False
    screen_capture = ScreenCapture(region=config.region, grayscale=config.grayscale)
    screen_capture.start()
    input_handler = InputHandler(screen_capture, handler_mode=config.handler_mode, use_pos_handler=config.use_pos_handler)
    app = tornado.web.Application([(r"/", MainHandler, dict(url=config.url, use_joined_pos=True)),
                                   (r'/media', WebSocketMediaHandler, dict(screen_capture=screen_capture)),
                                   (r'/input', WebSocketInputHandler, dict(input_handler=input_handler)),
                                   (r"/(.*)", tornado.web.StaticFileHandler,
                                    dict(path=os.path.join(os.path.dirname(__file__), "static")))])
    app.listen(address=config.ip, port=config.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    run()
