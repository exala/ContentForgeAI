# File: /content_automation/content_system/wordpress_publisher.py

import os
import requests
import json
import base64
from dotenv import load_dotenv

load_dotenv()  # take environment variables

# --- WordPress Configuration ---
# IMPORTANT: Load these from environment variables for security in a real application.
# For this example, we'll define them here.
WP_URL = os.getenv("WP_URL")
WP_USER = os.getenv("WP_USER")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
# WP_URL = "https://gigantichistory.s3-tastewp.com"  # Replace with your WordPress site URL
# WP_USER = "admin"        # Replace with your WordPress username
# WP_APP_PASSWORD = "EkRC uvGd qJ1Y 6JKK t8wi s68L" # Replace with the Application Password you generated

API_BASE = f"{WP_URL}/wp-json/wp/v2"

# Prepare the credentials for Basic Authentication
credentials = f"{WP_USER}:{WP_APP_PASSWORD}"
token = base64.b64encode(credentials.encode())
HEADERS = {'Authorization': f'Basic {token.decode("utf-8")}'}


# async def upload_image_to_wordpress(image_path: str, article_title: str) -> int | None:
#     """
#     Uploads an image to the WordPress Media Library and returns its ID.

#     Args:
#         image_path: The absolute local path to the image file.
#         article_title: The title of the article, used for image alt text.
#     """
#     if not image_path or not os.path.exists(image_path):
#         print("   [WP] Image path not provided or file does not exist. Skipping image upload.")
#         return None

#     media_url = f"{API_BASE}/media"
#     filename = os.path.basename(image_path)

#     try:
#         with open(image_path, 'rb') as f:
#             image_data = f.read()

#         # Set headers for the file upload
#         file_headers = HEADERS.copy()
#         file_headers['Content-Disposition'] = f'attachment; filename={filename}'
#         file_headers['Content-Type'] = 'image/png' # Or jpeg, etc.

#         print(f"   [WP] Uploading {filename} to WordPress Media Library...")
#         response = requests.post(media_url, headers=file_headers, data=image_data, timeout=60)
#         response.raise_for_status() # Raise an exception for bad status codes

#         media_id = response.json()['id']
#         alt_text = article_title

#         # Optional: Update the alt text for the image for better SEO
#         update_url = f"{API_BASE}/media/{media_id}"
#         update_payload = {'alt_text': alt_text, 'title': article_title}
#         requests.post(update_url, headers=HEADERS, json=update_payload)

#         print(f"   [WP] Image uploaded successfully. Media ID: {media_id}")
#         return media_id

#     except requests.exceptions.RequestException as e:
#         print(f"   [WP] Error uploading image to WordPress: {e}")
#         return None

# async def create_wordpress_post(title: str, content: str, status: str, featured_media_id: int | None) -> bool:
#     """
#     Creates a new post in WordPress.

#     Args:
#         title: The post title.
#         content: The full HTML content of the post.
#         status: The post status ('publish', 'draft', 'pending').
#         featured_media_id: The ID of the image to set as the featured image.
#     """
#     posts_url = f"{API_BASE}/posts"

#     payload = {
#         'title': title,
#         'content': content,
#         'status': status
#     }

#     if featured_media_id:
#         payload['featured_media'] = featured_media_id

#     try:
#         print(f"   [WP] Creating post '{title}' as a '{status}'...")
#         response = requests.post(posts_url, headers=HEADERS, json=payload, timeout=60)
#         response.raise_for_status()

#         print(f"   [WP] Successfully created post. Post ID: {response.json()['id']}")
#         return True

#     except requests.exceptions.RequestException as e:
#         print(f"   [WP] Error creating post in WordPress: {e}")
#         print(f"   [WP] Response Body: {e.response.text if e.response else 'No Response'}")
#         return False

################################ TESTING
def upload_image_to_wordpress(image_path: str, article_title: str) -> int | None:
    """
    Uploads an image to the WordPress Media Library and returns its ID.

    Args:
        image_path: The absolute local path to the image file.
        article_title: The title of the article, used for image alt text.
    """
    image_path = "D:\Ghazanfer Projects\2025\Modexis\font.PNG"
    print(os.path.exists(image_path))
    if not image_path or not os.path.exists(image_path):
        print("   [WP] Image path not provided or file does not exist. Skipping image upload.")
        return None

    media_url = f"{API_BASE}/media"
    filename = os.path.basename(image_path)

    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()

        # Set headers for the file upload
        file_headers = HEADERS.copy()
        file_headers['Content-Disposition'] = f'attachment; filename={filename}'
        file_headers['Content-Type'] = 'image/png' # Or jpeg, etc.

        print(f"   [WP] Uploading {filename} to WordPress Media Library...")
        response = requests.post(media_url, headers=file_headers, data=image_data, timeout=60)
        response.raise_for_status() # Raise an exception for bad status codes

        media_id = response.json()['id']
        alt_text = article_title

        # Optional: Update the alt text for the image for better SEO
        update_url = f"{API_BASE}/media/{media_id}"
        update_payload = {'alt_text': alt_text, 'title': article_title}
        requests.post(update_url, headers=HEADERS, json=update_payload)

        print(f"   [WP] Image uploaded successfully. Media ID: {media_id}")
        return media_id

    except requests.exceptions.RequestException as e:
        print(f"   [WP] Error uploading image to WordPress: {e}")
        return None

def create_wordpress_post(title: str, content: str, status: str, featured_media_id: int | None) -> bool:
    """
    Creates a new post in WordPress.

    Args:
        title: The post title.
        content: The full HTML content of the post.
        status: The post status ('publish', 'draft', 'pending').
        featured_media_id: The ID of the image to set as the featured image.
    """
    posts_url = f"{API_BASE}/posts"

    payload = {
        'title': title,
        'content': content,
        'status': status
    }

    if featured_media_id:
        payload['featured_media'] = featured_media_id

    try:
        print(f"   [WP] Creating post '{title}' as a '{status}'...")
        response = requests.post(posts_url, headers=HEADERS, json=payload, timeout=60, verify=False)
        response.raise_for_status()

        print(f"   [WP] Successfully created post. Post ID: {response.json()['id']}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"   [WP] Error creating post in WordPress: {e}")
        print(f"   [WP] Response Body: {e.response.text if e.response else 'No Response'}")
        return False