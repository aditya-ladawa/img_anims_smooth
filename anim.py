import os
import subprocess
import imageio
import math
import random
import numpy as np
from PIL import Image, ImageFilter

def ease_out_cubic(x):
    return 1 - (1 - x) ** 3
    
class Animations:
    def __init__(
        self,
        screen_width=1080,
        screen_height=1920,
        illustration_height_percent=0.4,
        padding_percent=0.01,
        duration=0.3,
        output_path="./"
    ):
        """
        :param output_path: directory where .webm files will be saved
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.top_area_height = int(screen_height * illustration_height_percent)
        self.padding_top = int(screen_height * padding_percent)
        self.default_duration = duration
        self.current_duration = duration
        self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)

        self.frame_generator = None
        self.last_effect = None

    def load_image(self, image_path):
        self.image_path = image_path
        self.orig_img = Image.open(image_path).convert("RGBA")
        max_w, max_h = self.screen_width, self.top_area_height - self.padding_top
        iw, ih = self.orig_img.size
        scale = min(max_w / iw, max_h / ih, 1)
        self.target_width = int(iw * scale)
        self.target_height = int(ih * scale)

    def _prepare(self, image_path, duration):
        self.load_image(image_path)
        # clamp duration to avoid extremely long or unwanted lengths
        self.current_duration = duration if duration is not None else self.default_duration
        self.last_effect = None

    # -- animation methods --
    def bubble_pop(self, image_path, duration=None):
        self._prepare(image_path, duration)
        self.last_effect = "bubble_pop"
        def frame(t):
            p = min(max(t / self.current_duration, 0), 1)
            w = max(1, int(self.target_width * p))
            h = max(1, int(self.target_height * p))
            img = self.orig_img.resize((w, h), Image.LANCZOS)
            bg = Image.new("RGBA", (self.screen_width, self.screen_height), (0,0,0,0))
            x = (self.screen_width - w)//2
            y = self.padding_top + (self.top_area_height - self.padding_top - h)//2
            bg.paste(img, (x,y), img)
            return np.array(bg)
        self.frame_generator = frame

    def slide_in(self, image_path, direction="left", duration=None):
        self._prepare(image_path, duration)
        self.last_effect = "slide_in"
        def frame(t):
            linear = min(max(t / self.current_duration, 0), 1)
            p = ease_out_cubic(linear)
            img = self.orig_img.resize((self.target_width, self.target_height), Image.LANCZOS)
            bg = Image.new("RGBA", (self.screen_width, self.screen_height), (0,0,0,0))
            y = self.padding_top + (self.top_area_height - self.padding_top - self.target_height)//2
            end_x = (self.screen_width - self.target_width)/2
            start_x = -self.target_width if direction == "left" else self.screen_width
            x = int(round(start_x + p * (end_x - start_x)))
            bg.paste(img, (x,y), img)
            return np.array(bg)
        self.frame_generator = frame

    def slide_in_overshoot(self, image_path, direction="left", duration=None, overshoot=100, overshoot_ratio=0.7):
        """
        Slides in past center by 'overshoot' pixels, then returns to center.
        :param overshoot: extra pixels past center before spring-back
        :param overshoot_ratio: portion of duration to reach overshoot
        """
        self._prepare(image_path, duration)
        def frame(t):
            p = min(max(t / self.current_duration, 0), 1)
            img = self.orig_img.resize((self.target_width, self.target_height), Image.LANCZOS)
            bg = Image.new("RGBA", (self.screen_width, self.screen_height), (0,0,0,0))
            y = self.padding_top + (self.top_area_height - self.padding_top - self.target_height)//2
            start_x = -self.target_width if direction == "left" else self.screen_width
            center_x = (self.screen_width - self.target_width)//2
            # overshoot position
            if direction == "left":
                over_x = center_x + overshoot
            else:
                over_x = center_x - overshoot
            if p < overshoot_ratio:
                # move from start to overshoot
                x = start_x + (p/overshoot_ratio) * (over_x - start_x)
            else:
                # spring back from overshoot to center
                q = (p - overshoot_ratio) / (1 - overshoot_ratio)
                x = over_x + q * (center_x - over_x)
            bg.paste(img, (int(x), y), img)
            return np.array(bg)
        self.frame_generator = frame

    def fade_in(self, image_path, duration=None):
        self._prepare(image_path, duration)
        def frame(t):
            p = min(max(t / self.current_duration, 0), 1)
            e = 1 - (1-p)**3
            img = self.orig_img.resize((self.target_width, self.target_height), Image.LANCZOS)
            alpha = img.split()[3].point(lambda p: p*e)
            img.putalpha(alpha)
            bg = Image.new("RGBA", (self.screen_width, self.screen_height), (0,0,0,0))
            x = (self.screen_width - self.target_width)//2
            y = self.padding_top + (self.top_area_height - self.padding_top - self.target_height)//2
            bg.paste(img, (x,y), img)
            return np.array(bg)
        self.frame_generator = frame

    def blur_in(self, image_path, duration=None, max_blur_radius=15):
        self._prepare(image_path, duration)
        def frame(t):
            p = min(max(t / self.current_duration, 0), 1)
            e = 1 - (1-p)**3
            r = max_blur_radius * (1-e)
            img = self.orig_img.resize((self.target_width, self.target_height), Image.LANCZOS)
            img = img.filter(ImageFilter.GaussianBlur(radius=r))
            bg = Image.new("RGBA", (self.screen_width, self.screen_height), (0,0,0,0))
            x = (self.screen_width - self.target_width)//2
            y = self.padding_top + (self.top_area_height - self.padding_top - self.target_height)//2
            bg.paste(img, (x,y), img)
            return np.array(bg)
        self.frame_generator = frame

    def drop(self, image_path, duration=None):
        self._prepare(image_path, duration)
        def frame(t):
            p = min(max(t / self.current_duration, 0), 1)
            e = 1 - (1-p)**3
            img = self.orig_img.resize((self.target_width, self.target_height), Image.LANCZOS)
            start_y = -self.target_height
            end_y = self.padding_top + (self.top_area_height - self.padding_top - self.target_height)//2
            y = int(round(start_y + e*(end_y - start_y)))
            x = (self.screen_width - self.target_width)//2
            bg = Image.new("RGBA", (self.screen_width, self.screen_height), (0,0,0,0))
            bg.paste(img, (x,y), img)
            return np.array(bg)
        self.frame_generator = frame

    def shake(self, image_path, intensity=15, frequency=25, duration=None):
        self._prepare(image_path, duration)
        def frame(t):
            p = min(max(t/self.current_duration,0),1)
            center_x = (self.screen_width - self.target_width)//2
            y = self.padding_top + (self.top_area_height - self.padding_top - self.target_height)//2
            offset = int(intensity*math.sin(2*math.pi*frequency*t) + random.uniform(-intensity/3, intensity/3))
            img = self.orig_img.resize((self.target_width, self.target_height), Image.LANCZOS)
            bg = Image.new("RGBA", (self.screen_width, self.screen_height), (0,0,0,0))
            bg.paste(img, (center_x+offset, y), img)
            return np.array(bg)
        self.frame_generator = frame

    def bounce(self, image_path, bounce_height=150, duration=None):
        self._prepare(image_path, duration)
        def frame(t):
            p = min(max(t/self.current_duration,0),1)
            bounce = 1 - (math.cos(4.5*math.pi*p) * math.exp(-6*p))
            img = self.orig_img.resize((self.target_width, self.target_height), Image.LANCZOS)
            x = (self.screen_width - self.target_width)//2
            target_y = self.padding_top + (self.top_area_height - self.padding_top - self.target_height)//2
            y = int(target_y - bounce_height*(1 - bounce))
            bg = Image.new("RGBA", (self.screen_width, self.screen_height), (0,0,0,0))
            bg.paste(img, (x,y), img)
            return np.array(bg)
        self.frame_generator = frame

    def blur_in_shake(self, image_path, max_blur_radius=15, intensity=15, frequency=25, duration=None):
        self._prepare(image_path, duration)
        def frame(t):
            p = min(max(t/self.current_duration,0),1)
            e = 1 - (1-p)**3
            r = max_blur_radius*(1-e)
            offset = int(intensity*math.sin(2*math.pi*frequency*t) + random.uniform(-intensity/3, intensity/3))
            img = self.orig_img.resize((self.target_width, self.target_height), Image.LANCZOS)
            img = img.filter(ImageFilter.GaussianBlur(radius=r))
            x = (self.screen_width - self.target_width)//2 + offset
            y = self.padding_top + (self.top_area_height - self.padding_top - self.target_height)//2
            bg = Image.new("RGBA", (self.screen_width, self.screen_height), (0,0,0,0))
            bg.paste(img, (x,y), img)
            return np.array(bg)
        self.frame_generator = frame

    def rotate_3d_page_flip(self, image_path, duration=None):
        self._prepare(image_path, duration)
        base = self.orig_img.resize((self.target_width, self.target_height), Image.LANCZOS)
        w, h = self.target_width, self.target_height
        def frame(t):
            def ease(t): return t*t*(3-2*t)
            p = ease(min(max(t/self.current_duration,0),1))
            ang = p * math.pi
            scale = abs(math.cos(ang))
            cw = max(1, int(w*scale))
            img = base if ang<=math.pi else base.transpose(Image.FLIP_LEFT_RIGHT)
            img = img.resize((cw,h), Image.LANCZOS)
            x = (self.screen_width-cw)//2
            y = self.padding_top + (self.top_area_height - self.padding_top - h)//2
            bg = Image.new("RGBA", (self.screen_width, self.screen_height), (0,0,0,0))
            bg.paste(img, (x,y), img)
            return np.array(bg)
        self.frame_generator = frame

    def bounce_pop_animation(self, image_path, duration=None):
        self._prepare(image_path, duration)
        base = self.orig_img.resize((self.target_width, self.target_height), Image.LANCZOS)
        w, h = self.target_width, self.target_height
        def osc(t): return 1 + (math.exp(-5*t) * math.cos(8*math.pi*t)) * 0.2
        def frame(t):
            p = min(max(t/self.current_duration,0),1)
            scale = osc(p)
            cw = max(1,int(w*scale)); ch = max(1,int(h*scale))
            img = base.resize((cw,ch), Image.LANCZOS)
            x = (self.screen_width-cw)//2
            y = self.padding_top + (self.top_area_height - self.padding_top - ch)//2
            bg = Image.new("RGBA", (self.screen_width, self.screen_height), (0,0,0,0))
            bg.paste(img, (x,y), img)
            return np.array(bg)
        self.frame_generator = frame

    def bubble_bounce_pop(self, image_path, duration=None):
        self._prepare(image_path, duration)
        def bounce_ease(t):
            n1,d1=7.5625,2.75
            if t<1/d1: return n1*t*t
            elif t<2/d1: t-=1.5/d1; return n1*t*t+0.75
            elif t<2.5/d1: t-=2.25/d1; return n1*t*t+0.9375
            else: t-=2.625/d1; return n1*t*t+0.984375
        def frame(t):
            p = min(max(t/self.current_duration,0),1)
            bv = bounce_ease(p)
            scale = bv/1.05*1.2
            if p>0.95:
                ep=(p-0.95)/0.05
                scale=scale*(1-ep)+1*ep
            w,h=self.target_width,self.target_height
            cw=max(1,int(w*scale)); ch=max(1,int(h*scale))
            img = self.orig_img.resize((cw,ch), Image.LANCZOS)
            x = (self.screen_width-cw)//2
            y = self.padding_top + (self.top_area_height - self.padding_top - ch)//2
            bg = Image.new("RGBA", (self.screen_width, self.screen_height), (0,0,0,0))
            bg.paste(img, (x,y), img)
            return np.array(bg)
        self.frame_generator = frame


    def transparent_in(self, image_path, duration=None):
        self.load_image(image_path)
        self.current_duration = duration or self.default_duration
        self.last_effect = "transparent_in"

        def frame(t):
            t = min(t, self.current_duration)
            p = min(max(t / self.current_duration, 0), 1)
            alpha = int(p * 255)
            faded_img = self.orig_img.copy()
            faded_img.putalpha(alpha)
            bg = Image.new("RGBA", (self.screen_width, self.screen_height), (0, 0, 0, 0))
            x = (self.screen_width - self.target_width) // 2
            y = self.padding_top + (self.top_area_height - self.padding_top - self.target_height) // 2
            faded_img = faded_img.resize((self.target_width, self.target_height), Image.LANCZOS)
            bg.paste(faded_img, (x, y), faded_img)
            return np.array(bg)

        self.frame_generator = frame



    def place_in_y(self, image_path, duration=None):
        self.load_image(image_path)
        self.current_duration = duration or self.default_duration
        self.last_effect = "place_in_y"

        # Starting scale larger than normal to simulate "closer to viewer"
        start_scale = 1.5  # 150% size at start, can tweak this
        end_scale = 1.0    # normal size at end

        # Starting position outside screen (e.g., above or in front, here top)
        # We'll move from above screen down to center.
        start_y = -int(self.target_height * start_scale)  # start fully above visible area
        end_y = self.padding_top + (self.top_area_height - self.padding_top - self.target_height) // 2

        def frame(t):
            t = min(t, self.current_duration)
            p = min(max(t / self.current_duration, 0), 1)  # progress 0->1

            # Interpolate scale and alpha
            scale = start_scale + (end_scale - start_scale) * p
            alpha = int(255 * p)

            # Calculate image size and position
            w = int(self.target_width * scale)
            h = int(self.target_height * scale)

            # Linear interpolate y position from start_y to end_y
            y = int(start_y + (end_y - start_y) * p)

            # Center horizontally
            x = (self.screen_width - w) // 2

            # Resize and set alpha
            img = self.orig_img.copy().resize((w, h), Image.LANCZOS)
            img.putalpha(alpha)

            # Create transparent background and paste image on it
            bg = Image.new("RGBA", (self.screen_width, self.screen_height), (0, 0, 0, 0))
            bg.paste(img, (x, y), img)

            return np.array(bg)

        self.frame_generator = frame


    def place_in_z(self, image_path, duration=None):
        self.load_image(image_path)
        self.current_duration = duration or self.default_duration
        self.last_effect = "place_in_z"

        start_scale = 1.5
        end_scale = 1.0

        def frame(t):
            t = min(t, self.current_duration)
            linear_p = min(max(t / self.current_duration, 0), 1)
            p = ease_out_cubic(linear_p)  # easing progress

            scale = start_scale + (end_scale - start_scale) * p
            alpha = int(255 * p)

            w = int(self.target_width * scale)
            h = int(self.target_height * scale)

            x = (self.screen_width - w) // 2
            y = self.padding_top + (self.top_area_height - self.padding_top - h) // 2

            img = self.orig_img.copy().resize((w, h), Image.LANCZOS)
            img.putalpha(alpha)

            bg = Image.new("RGBA", (self.screen_width, self.screen_height), (0, 0, 0, 0))
            bg.paste(img, (x, y), img)

            return np.array(bg)

        self.frame_generator = frame    

    def render_gif(self, filename, fps=60):
        if not self.frame_generator:
            raise RuntimeError("No animation selected. Call an effect method first.")
        # Temporary GIF
        temp_gif = os.path.join(self.output_path, "temp.gif")
        frames = int(self.current_duration * fps)
        with imageio.get_writer(temp_gif, mode='I', duration=1/fps, loop=0, disposal=2) as writer:
            for i in range(frames):
                t = (i + 0.5) / fps  # sample mid-frame for smoother timing
                writer.append_data(self.frame_generator(t))
        output_webm = os.path.join(self.output_path, filename)
        # Convert with explicit input & output FPS
        cmd = [
            'ffmpeg', '-y',
            '-r', str(fps),              # treat input as fps
            '-i', temp_gif,
            '-c:v', 'libvpx-vp9', '-auto-alt-ref', '0',
            '-pix_fmt', 'yuva420p',
            '-r', str(fps),              # force output fps
            output_webm
        ]
        subprocess.run(cmd, check=True)
        os.remove(temp_gif)

# Usage remains unchanged, calling each animation with duration=0.3 and fps=60















# if __name__ == '__main__':
#     impath = 'src/open_deep_research/files/ais_clever_paths/illustrations/mcts_own.png'
#     anim = Animations(output_path='./webms')

#     # Bubble pop animation
#     anim.bubble_pop(impath, duration=0.3)
#     anim.render_gif('bubble_pop.webm', fps=60)

#     # Slide in from left (default)
#     anim.slide_in(impath, direction='left', duration=0.3)
#     anim.render_gif('slide_in_left.webm', fps=60)

#     # Slide in from right
#     anim.slide_in(impath, direction='right', duration=0.3)
#     anim.render_gif('slide_in_right.webm', fps=60)

#     # Slide in overshoot from left
#     anim.slide_in_overshoot(impath, direction='left', duration=0.3)
#     anim.render_gif('slide_in_overshoot_left.webm', fps=60)

#     # Slide in overshoot from right
#     anim.slide_in_overshoot(impath, direction='right', duration=0.3)
#     anim.render_gif('slide_in_overshoot_right.webm', fps=60)

#     # Fade in
#     anim.fade_in(impath, duration=0.3)
#     anim.render_gif('fade_in.webm', fps=60)

#     # Blur in
#     anim.blur_in(impath, duration=0.3)
#     anim.render_gif('blur_in.webm', fps=60)

#     # Drop animation
#     anim.drop(impath, duration=0.3)
#     anim.render_gif('drop.webm', fps=60)

#     # Shake animation
#     anim.shake(impath, intensity=15, frequency=25, duration=0.3)
#     anim.render_gif('shake.webm', fps=60)

#     # Bounce animation
#     anim.bounce(impath, bounce_height=150, duration=0.3)
#     anim.render_gif('bounce.webm', fps=60)

#     # Blur in + shake combined
#     anim.blur_in_shake(impath, max_blur_radius=15, intensity=15, frequency=25, duration=0.3)
#     anim.render_gif('blur_in_shake.webm', fps=60)

#     # 3D page flip rotate
#     anim.rotate_3d_page_flip(impath, duration=0.3)
#     anim.render_gif('rotate_3d_page_flip.webm', fps=60)

#     # Bounce pop animation
#     anim.bounce_pop_animation(impath, duration=0.3)
#     anim.render_gif('bounce_pop_animation.webm', fps=60)

#     # Bubble bounce pop animation
#     anim.bubble_bounce_pop(impath, duration=0.3)
#     anim.render_gif('bubble_bounce_pop.webm', fps=60)

#     # Transparent in animation
#     anim.transparent_in(impath, duration=0.3)
#     anim.render_gif('transparent_in.webm', fps=60)

#     # Place in Y (scale + move down)
#     anim.place_in_y(impath, duration=0.3)
#     anim.render_gif('place_in_y.webm', fps=60)

#     # Place in Z (scale + fade in)
#     anim.place_in_z(impath, duration=0.3)
#     anim.render_gif('place_in_z.webm', fps=60)


animations_simple_fx = [
    {"animation": "bubble_pop",          "duration": 0.15, "sfx": "pop"},
    {"animation": "slide_in_left",       "duration": 0.3, "sfx": "whoosh"},
    {"animation": "slide_in_right",      "duration": 0.3, "sfx": "whoosh"},
    {"animation": "slide_in_overshoot",  "duration": 0.5, "sfx": "spring"},
    {"animation": "fade_in",             "duration": 0.5, "sfx": "chime"},
    {"animation": "blur_in",             "duration": 0.5, "sfx": "whoosh"},
    {"animation": "drop",                "duration": 0.5, "sfx": "thud"},
    {"animation": "shake",               "duration": 0.3, "sfx": "shake"},
    {"animation": "bounce",              "duration": 0.3, "sfx": "boing"},
    {"animation": "blur_in_shake",       "duration": 0.3, "sfx": "whoosh"},
    {"animation": "rotate_3d_page_flip", "duration": 0.5, "sfx": "page_flip"},
    {"animation": "bounce_pop_animation","duration": 0.5, "sfx": "pop"},
    {"animation": "bubble_bounce_pop",   "duration": 0.5, "sfx": "pop"},
    {"animation": "transparent_in",      "duration": 0.5, "sfx": "shimmer"},
    {"animation": "place_in_y",          "duration": 0.5, "sfx": "whoosh"},
    {"animation": "place_in_z",          "duration": 0.5, "sfx": "zoom"},
]
