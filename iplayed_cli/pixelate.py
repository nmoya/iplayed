import numpy as np
from PIL import Image
from skimage import io


def download_image(url):
    image = io.imread(url)
    return image


def apply_pixelation(image_array: np.ndarray, scale_factor: float) -> np.ndarray:
    if not (0 < scale_factor <= 1.0):
        raise ValueError("scale_factor must be between 0 and 1")

    img = Image.fromarray(image_array)
    original_size = img.size
    new_size = (max(1, int(original_size[0] * scale_factor)), max(1, int(original_size[1] * scale_factor)))

    # Downscale and upscale using NEAREST neighbor interpolation
    img_small = img.resize(new_size, resample=Image.NEAREST)
    img_pixelated = img_small.resize(original_size, resample=Image.NEAREST)

    return np.array(img_pixelated)


def save_image(image, filename):
    io.imsave(filename, image)
    print(f"Image saved as {filename}")


if __name__ == "__main__":
    original = download_image("https://images.igdb.com/igdb/image/upload/t_cover_big/co670h.jpg")
    pixelated_image = apply_pixelation(original, 0.25)
    save_image(pixelated_image, "pixelated_image.png")
