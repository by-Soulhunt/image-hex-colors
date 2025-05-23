import numpy as np
from PIL import Image
from collections import Counter
from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, redirect, url_for, request
from typing import Optional
import os


# Main logic class
class ImageToHex:
    """
    Class for processing an image and extracting the most common colors as HEX codes.

    Attributes:
        image (PIL.Image): Loaded image object.
        most_common_hex_colors (dict): Dictionary storing HEX colors and their counts.
        img_path (Optional[str]): Path to the image file. None if not yet set.
        number_of_colors (list): List of possible numbers of colors to extract.

    Methods:
        open_image(): Opens the image file.
        img_to_hex(number_of_colors): Converts the image pixels to HEX colors.
        rgb_to_hex(rgb_tuple): Converts RGB tuple to HEX string.

    """

    def __init__(self):
        self.image = None
        self.most_common_hex_colors = {}
        self.img_path: Optional[str] = None
        self.number_of_colors = [1, 2, 3, 4, 5, 10, 20, 50]

    @staticmethod
    def rgb_to_hex(rgb):
        """
        Convert RGB color into HEX
        :param rgb: RGB color
        :return: HEX string in format "#000000"
        """
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

    def open_image(self):
        """
        Open image and save into self.image
        :return: None
        """
        self.image = Image.open(self.img_path).convert("RGB")

    def img_to_hex(self, number_of_colors):
        """
        Convert an image to a dictionary of the most common HEX color codes.
        :param number_of_colors: Number of top colors to extract (from UI dropdown)
        :return: None
        """
        img_array = np.array(self.image) # Convert image to array
        pixels = img_array.reshape(-1, 3) # Flatten image to list of RGB pixels
        pixels_tuple = [tuple(int(x) for x in pixel) for pixel in pixels] # Create RGB tuples
        colour_counts = Counter(pixels_tuple) # Count frequency of each color
        # Get most common colors based on number_of_colors
        most_common_colors = colour_counts.most_common(number_of_colors)

        # Convert RGB tuples to HEX and store them
        for color, count in most_common_colors:
            hex_color = self.rgb_to_hex(color)
            self.most_common_hex_colors[hex_color] = count


# Flask configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("FLASK_KEY")
Bootstrap5(app)


# Routs
@app.route("/")
def index():
    """
    Main page
    :return: index.html
    """
    return render_template("index.html")


@app.route("/convert", methods=["GET", "POST"])
def convert():
    """
    Handles image upload and conversion to a color palette.

    GET: Displays the upload form.
    POST: Processes the uploaded image, converts it to HEX colors,
          and displays the result.

    Form parameters:
    - image_file: the uploaded image file
    - color: number of colors to output
    :return: template with a form to upload a file or information with HEX codes after processing
    """

    # Create class object
    data = ImageToHex()
    # If Upload button pressed
    if request.method == "POST":
        file = request.files.get("image_file")
        number_of_colors = request.form.get("color")

        # Convert str into int
        try:
            number_of_colors = int(number_of_colors)
        except (TypeError, ValueError):
            number_of_colors = 5

        # Save file
        if file and file.filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
            save_path = "static/tmp/new_img.jpg"
            file.save(save_path)
            data.img_path = save_path

            # Get HEX codes
            data.open_image()
            data.img_to_hex(number_of_colors)

            return render_template("convert.html",  image_is_open=True,
                                   data=data.most_common_hex_colors,
                                   image=data.img_path.replace("static", ""))

    return render_template("convert.html", image_is_open=False,
                           number_of_colors=data.number_of_colors)


if __name__ == "__main__":
    app.run(debug=True, port=5009)