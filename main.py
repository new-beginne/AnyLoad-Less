import os
# ১. গ্রাফিক্স ফিক্স (সবার উপরে মাস্ট)
os.environ['KIVY_GRAPHICS'] = 'sdl2'

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.utils import platform

class AnyLoadApp(MDApp):
    # ডট এনিমেশনের জন্য স্ট্রিং প্রোপার্টি (Tofu □□□ এরর এড়াতে)
    dot_text = StringProperty("...")
    _dot_count = 0

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        self.title = "AnyLoad"
        # ui.kv লোড করার আগে ফোল্ডার পাথ চেক করে নেওয়া ভালো
        return Builder.load_file("ui.kv")

    def on_start(self):
        # ২. অ্যান্ড্রয়েড পারমিশন রিকোয়েস্ট (অ্যান্ড্রয়েড ১৩+ সাপোর্ট)
        if platform == "android":
            self.request_android_permissions()
        
        # ডট এনিমেশন অটো-স্টার্ট (টেস্ট করার জন্য)
        self.start_dot_animation()

    def request_android_permissions(self):
        from android.permissions import request_permissions, Permission
        # আধুনিক পারমিশন লিস্ট
        perms = [
            Permission.READ_MEDIA_VIDEO,
            Permission.READ_MEDIA_AUDIO,
            Permission.POST_NOTIFICATIONS,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE
        ]
        request_permissions(perms)

    def on_pause(self):
        return True

    def start_dot_animation(self):
        Clock.schedule_interval(self.animate_dots, 0.5)

    def animate_dots(self, dt):
        # ৩টা ডট এক এক করে বাড়বে ( . -> .. -> ... -> )
        self._dot_count = (self._dot_count + 1) % 4
        self.dot_text = "." * self._dot_count

if __name__ == "__main__":
    AnyLoadApp().run()