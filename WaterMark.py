import os
from PIL import Image

def add_logo_to_images(input_folder, output_folder, logo_path, position=(0, 0)):
    """
    Adds a logo to the top-left corner of every image in a given input folder.

    Args:
        input_folder (str): The path to the folder containing the original images.
        output_folder (str): The path to the folder where the new images with the logo will be saved.
        logo_path (str): The path to the logo image.
        position (tuple): The position to paste the logo. Default is (0, 0) for the top-left corner.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    try:
        logo = Image.open(logo_path).convert("RGBA")
    except FileNotFoundError:
        print(f"Error: Logo file not found at {logo_path}")
        return

    # Resize logo if needed (optional)
    # logo = logo.resize((100, 100))

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            image_path = os.path.join(input_folder, filename)
            try:
                with Image.open(image_path).convert("RGBA") as img:
                    # Resize logo based on image dimensions
                    # Let's make the logo's width 15% of the image's width
                    logo_width_resized = int(img.width * 0.15)
                    ratio = logo_width_resized / logo.width
                    logo_resized = logo.resize((logo_width_resized, int(logo.height * ratio)), Image.LANCZOS)
                    
                    # Define position for top-left corner
                    # You can add padding here, e.g., (10, 10)
                    position = (10, 10)
                    
                    # Create a new blank image with the same size as the main image
                    # This is a safe way to handle transparency and overlays
                    composite_img = Image.new('RGBA', img.size)
                    composite_img.paste(img)
                    composite_img.paste(logo_resized, position, logo_resized)

                    output_path = os.path.join(output_folder, filename)
                    
                    # Save as PNG to preserve transparency, or convert to RGB for JPG
                    if output_path.lower().endswith(('.png')):
                        composite_img.save(output_path)
                    else:
                        composite_img.convert('RGB').save(output_path)
                    
                    print(f"Successfully added logo to {filename} and saved to {output_path}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

# Example usage
if __name__ == "__main__":
    # Define your folder paths and logo path
    input_folder = "input_images"
    output_folder = "output_images"
    logo_path = "assets/logo.png"  # Make sure this path is correct

    # Run the function
    add_logo_to_images(input_folder, output_folder, logo_path)