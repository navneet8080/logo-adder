import os
from PIL import Image
import sys

# Helper function to find bundled resources in PyInstaller
def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temporary folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def add_logo_to_images(input_folder, output_folder, logo_path, logo_percentage, message_callback=None):
    """
    Adds a logo to the top-left corner of every image in a given input folder.

    Args:
        input_folder (str): The path to the folder containing the original images.
        output_folder (str): The path to the folder where the new images with the logo will be saved.
        logo_path (str): The path to the logo image.
        logo_percentage (int): The desired width of the logo as a percentage of the image's width.
        message_callback (callable, optional): A function to call with progress messages.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        if message_callback:
            message_callback(f"Created output folder: {output_folder}")

    try:
        base_logo = Image.open(logo_path).convert("RGBA")
    except FileNotFoundError:
        if message_callback:
            message_callback(f"Error: Logo file not found at {logo_path}")
        return
    except Exception as e:
        if message_callback:
            message_callback(f"Error loading logo: {e}")
        return

    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
    total_images = len(image_files)
    if total_images == 0:
        if message_callback:
            message_callback("No supported image files found in the input folder.")
        return

    for i, filename in enumerate(image_files):
        image_path = os.path.join(input_folder, filename)
        try:
            with Image.open(image_path).convert("RGBA") as img:
                img_width, img_height = img.size
                logo_width_resized = int(img_width * (logo_percentage / 100))
                
                logo_height_resized = int(base_logo.height * (logo_width_resized / base_logo.width))
                
                if logo_width_resized == 0 or logo_height_resized == 0:
                     if message_callback:
                        message_callback(f"Warning: Logo for {filename} would be too small. Skipping logo for this image.")
                     logo_resized = base_logo 
                else:
                    logo_resized = base_logo.resize((logo_width_resized, logo_height_resized), Image.LANCZOS)
                
                position = (10, 10)
                
                if position[0] + logo_resized.width > img_width or \
                   position[1] + logo_resized.height > img_height:
                    if message_callback:
                        message_callback(f"Warning: Logo for {filename} would extend beyond image boundaries. Skipping logo for this image.")
                    composite_img = img
                else:
                    composite_img = Image.new('RGBA', img.size)
                    composite_img.paste(img, (0, 0))
                    composite_img.paste(logo_resized, position, logo_resized)

                output_path = os.path.join(output_folder, filename)
                
                if output_path.lower().endswith(('.png')):
                    composite_img.save(output_path)
                else:
                    composite_img.convert('RGB').save(output_path)
                
                if message_callback:
                    message_callback(f"Processed {filename} ({i+1}/{total_images})")

        except Exception as e:
            if message_callback:
                message_callback(f"Error processing {filename}: {e}")

# This part is only for standalone testing, not for the GUI
if __name__ == "__main__":
    input_folder = "input_images"
    output_folder = "output_images"
    logo_path = get_resource_path(os.path.join("assets", "logo.png"))
    logo_percentage = 15
    add_logo_to_images(input_folder, output_folder, logo_path, logo_percentage, print)