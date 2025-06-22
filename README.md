# Animations Library

This Python library provides various animation effects that can be applied to images. The animations are rendered as `.webm` files and include effects like slide-in, bounce, fade-in, and more.

## Features

* **Multiple Animations**: Includes animations like bubble pop, slide-in, fade-in, shake, blur, bounce, and many others.
* **Customizable**: You can adjust the duration and other parameters to fine-tune the animations to your needs.
* **Output Format**: Animations are output as `.webm` files, a popular format for web and mobile applications.

## Animations Available

Here is a list of animations available in the library:

* **bubble\_pop**: A pop effect where the image grows and fades out.
* **slide\_in\_left**: The image slides in from the left side.
* **slide\_in\_right**: The image slides in from the right side.
* **slide\_in\_overshoot\_left**: The image slides in from the left side with a slight overshoot before returning to the center.
* **slide\_in\_overshoot\_right**: Similar to `slide_in_overshoot_left`, but slides in from the right.
* **fade\_in**: The image fades in from fully transparent.
* **blur\_in**: The image fades in with a blur effect.
* **drop**: The image falls down from the top.
* **shake**: The image shakes back and forth with adjustable intensity.
* **bounce**: The image bounces up and down with a smooth oscillation.
* **blur\_in\_shake**: Combines the blur-in effect with a shake.
* **rotate\_3d\_page\_flip**: A 3D page flip animation where the image rotates in 3D space.
* **bounce\_pop\_animation**: A combination of bounce and pop effects.
* **bubble\_bounce\_pop**: A combination of bubble and bounce pop effects.
* **transparent\_in**: The image fades in from transparency.
* **place\_in\_y**: The image scales and moves into view along the vertical axis.
* **place\_in\_z**: The image scales and moves into view along the Z-axis.

## Installation

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/aditya-ladawa/img_anims_smooth.git
   ```

2. Navigate to the project directory:

   ```bash
   cd img_anims_smooth
   ```

3. Install the required dependencies:

   * Virtual environment creation

   ```bash
   python -m venv myenv
   ```

   * Activate env

   ```bash
   source myenv/bin/activate
   ```

   * install requirements.txt
   
   ```bash
   pip install -r requirements.txt
   ```

4. Install **ffmpeg** for converting GIFs to `.webm` format. On Ubuntu, you can install it with:

   ```bash
   sudo apt-get install ffmpeg
   ```

   On macOS, use Homebrew:

   ```bash
   brew install ffmpeg
   ```

## Usage

### 1. Import the Library

```python
from animations import Animations
```

### 2. Initialize the Animation Object

```python
anim = Animations(output_path='./webms')
```

### 3. Load Your Image

```python
image_path = 'path_to_your_image.png'
```

### 4. Apply an Animation

Here are some examples of applying different animations:

#### Bubble Pop Animation

```python
anim.bubble_pop(image_path, duration=0.3)
anim.render_gif('bubble_pop.webm', fps=60)
```

#### Slide In Animation (from left)

```python
anim.slide_in(image_path, direction='left', duration=0.3)
anim.render_gif('slide_in_left.webm', fps=60)
```

#### Fade In Animation

```python
anim.fade_in(image_path, duration=0.3)
anim.render_gif('fade_in.webm', fps=60)
```

#### Bounce Animation

```python
anim.bounce(image_path, bounce_height=150, duration=0.3)
anim.render_gif('bounce.webm', fps=60)
```

#### 3D Page Flip Rotation

```python
anim.rotate_3d_page_flip(image_path, duration=0.3)
anim.render_gif('rotate_3d_page_flip.webm', fps=60)
```

### 5. View Your Animation

The generated `.webm` animation files will be saved in the `output_path` directory (`./webms` by default).

## Example Output

The following sample animations are provided in the `webms` directory:

* **blur\_in\_shake.webm**: Combination of blur and shake animation.
* **place\_in\_z.webm**: The image moves into view from the Z-axis.
* **bounce\_pop\_animation.webm**: A bounce combined with a pop effect.
* **fade\_in.webm**: A smooth fade-in effect.
* **slide\_in\_left.webm**: The image slides in from the left.
* **drop.webm**: The image drops down from above.

Feel free to experiment with the parameters to create custom animations suited to your needs!

## License

This project is licensed under the MIT License - see the LICENSE file for details.
