import requests
from io import BytesIO
from PIL import Image
import logging

def fetch_image_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        return image
    except Exception as e:
        logging.error(f"Failed to fetch image from {url}: {e}")
        return None

def scan_image_for_steganography(image, detection_function):
    """
    Scan a PIL Image object for steganography using the provided detection function.
    Returns True if steganography is detected, False otherwise.
    """
    if image is None:
        return False
    return detection_function(image)

def scan_social_media_images(image_urls, detection_function):
    """
    Given a list of image URLs from social media, fetch and scan each image.
    Returns a list of URLs flagged as suspicious.
    """
    flagged_urls = []
    for url in image_urls:
        image = fetch_image_from_url(url)
        if scan_image_for_steganography(image, detection_function):
            flagged_urls.append(url)
    return flagged_urls

# Example usage (to be integrated with main tool):
# from main import extract_lsb_ratios, model
# def detection_func(image):
#     features = extract_lsb_ratios(image)
#     prediction = model.predict([features])[0]
#     return prediction == 1
#
# suspicious = scan_social_media_images(list_of_urls, detection_func)
# for url in suspicious:
#     print(f"Suspicious image detected: {url}")
