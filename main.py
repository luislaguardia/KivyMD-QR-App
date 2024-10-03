import qrcode
import cv2
import imutils
from io import BytesIO
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.graphics.texture import Texture

from kivy.core.window import Window
Window.size = (412, 732)

camera_id = 0
delay = 1
window_name = 'OpenCV QR Code'

qcd = cv2.QRCodeDetector()
cap = cv2.VideoCapture(camera_id)

class LoginScreen(Screen):
    pass

class SignupScreen(Screen):
    pass

class DashboardScreen(Screen):
    pass

class ReceiveScreen(Screen):
    pass

class QRScreen(Screen):
    pass

class CameraScreen(Screen):
    pass

class SuccessScreen(Screen):
    pass

class MyApp(MDApp):

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.username = None
        self.capture = None
        return Builder.load_file('main.kv')

    def login(self):
        login_screen = self.root.get_screen('login')
        self.username = login_screen.ids.login_email.text
        self.root.current = 'dashboard'

    def sign_up(self):
        signup_screen = self.root.get_screen('signup')
        self.username = signup_screen.ids.signup_email.text
        self.root.current = 'dashboard'

    def animate_button(self, button):
        if button.text == "Login":
            self.root.current = 'dashboard'
            img = qrcode.make('Some data here')
            img.save("some_file.png")
        elif button.text == "Sign Up":
            self.root.current = 'dashboard'

    def send(self):
        print("Send button clicked")

    def on_cam_click(self):
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.load_camera_frame, 1.0 / 30.0)

    def load_camera_frame(self, dt):
        ret, frame = self.capture.read()
        if ret:
            ret_qr, decoded_info, points, _ = qcd.detectAndDecodeMulti(frame)
            if ret_qr:
                for s, p in zip(decoded_info, points):
                    if s:
                        print(f"QR Code detected: {s}")
                        self.capture.release()
                        Clock.unschedule(self.load_camera_frame)
                        self.root.current = 'success'
                        return
                    else:
                        color = (0, 0, 255)
                    frame = cv2.polylines(frame, [p.astype(int)], True, color, 8)
            frame = imutils.resize(frame, width=375, height=200)
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring()
            image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            img = self.root.get_screen('camera').ids.img
            img.texture = image_texture

    def generate_qr(self, amount):
        data = f'{self.username} received {amount}'
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        qr_image = CoreImage(BytesIO(buf.read()), ext="png").texture
        qr_screen = self.root.get_screen('qr')
        qr_screen.ids.qr_code_img.texture = qr_image
        self.root.current = 'qr'

    def on_stop(self):
        if self.capture:
            self.capture.release()

if __name__ == '__main__':
    MyApp().run()