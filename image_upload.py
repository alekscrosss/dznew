# файл image_upload.py

import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()  #

cloudinary.config(
  cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'),
  api_key = os.getenv('CLOUDINARY_API_KEY'),
  api_secret = os.getenv('CLOUDINARY_API_SECRET')
)


def upload_image(image_file):
    """
    Uploads an image file to Cloudinary.

    This function takes an image file and uploads it to Cloudinary using the credentials
    configured from environment variables. It returns the URL to the uploaded image.

    Args:
        image_file (file-like object): The image file to upload.

    Returns:
        str: The URL of the uploaded image.

    Raises:
        cloudinary.exceptions.Error: An error occurred while uploading the image to Cloudinary.
    """

    result = cloudinary.uploader.upload(image_file)
    return result['url']