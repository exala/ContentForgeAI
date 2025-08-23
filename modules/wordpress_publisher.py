# File: modules/wordpress_publisher.py

import os
import requests
import json
import base64
from dotenv import load_dotenv

# It's still good practice to have this for local testing if you use a .env file
load_dotenv()


def get_wp_config():
    """Reads WordPress configuration from environment variables."""
    WP_URL = os.getenv("WP_URL")
    WP_USER = os.getenv("WP_USER")
    # In your Streamlit app, you named the password key 'wp_password'
    # but your .env probably uses WP_APP_PASSWORD. Let's check for both.
    WP_APP_PASSWORD = os.getenv("WP_PASSWORD") or os.getenv("WP_APP_PASSWORD")

    if not all([WP_URL, WP_USER, WP_APP_PASSWORD]):
        # This provides a more graceful failure if credentials are not set
        raise ValueError(
            "WordPress credentials (WP_URL, WP_USER, WP_PASSWORD/WP_APP_PASSWORD) are not set in the environment.")

    api_base = f"{WP_URL}/wp-json/wp/v2"
    credentials = f"{WP_USER}:{WP_APP_PASSWORD}"
    token = base64.b64encode(credentials.encode())
    headers = {'Authorization': f'Basic {token.decode("utf-8")}'}

    return api_base, headers


def upload_image_to_wordpress(image_path: str, article_title: str) -> int | None:
    """
    Uploads an image to the WordPress Media Library and returns its ID.
    """
    if not image_path or not os.path.exists(image_path):
        print("   [WP] Image path not provided or file does not exist. Skipping image upload.")
        return None

    try:
        api_base, headers = get_wp_config()
        media_url = f"{api_base}/media"
        filename = os.path.basename(image_path)

        with open(image_path, 'rb') as f:
            image_data = f.read()

        file_headers = headers.copy()
        file_headers['Content-Disposition'] = f'attachment; filename={filename}'
        file_headers['Content-Type'] = 'image/png'

        print(f"   [WP] Uploading {filename} to WordPress...")
        response = requests.post(media_url, headers=file_headers, data=image_data, timeout=60, verify=False)
        response.raise_for_status()

        media_id = response.json()['id']

        # Optional: Update the alt text
        update_url = f"{api_base}/media/{media_id}"
        update_payload = {'alt_text': article_title, 'title': article_title}
        requests.post(update_url, headers=headers, json=update_payload, verify=False)

        print(f"   [WP] Image uploaded successfully. Media ID: {media_id}")
        return media_id

    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"   [WP] Error uploading image to WordPress: {e}")
        return None


def create_wordpress_post(title: str, content: str, status: str, featured_media_id: int | None) -> bool:
    """
    Creates a new post in WordPress.
    """
    try:
        # Get the latest credentials EVERY time the function is called
        api_base, headers = get_wp_config()
        posts_url = f"{api_base}/posts"

        payload = {
            'title': title,
            'content': content,
            'status': status
        }

        if featured_media_id:
            payload['featured_media'] = featured_media_id

        print(f"   [WP] Creating post '{title}' as a '{status}'...")
        # Note: verify=False suppresses the InsecureRequestWarning. This is okay for TasteWP.
        response = requests.post(posts_url, headers=headers, json=payload, timeout=60, verify=False)
        response.raise_for_status()

        # Check if the response contains JSON before trying to parse it
        if response.text:
            post_id = response.json().get('id', 'N/A')
            print(f"   [WP] Successfully created post. Post ID: {post_id}")
            return True
        else:
            print("[WP] Error: Post was created but response was empty.")
            return False  # Or True, depending on how you want to handle this case

    except (requests.exceptions.RequestException, ValueError, json.JSONDecodeError) as e:
        error_message = str(e)
        # Handle the specific JSON decode error
        if isinstance(e, json.JSONDecodeError):
            error_message = "Expecting JSON but got empty or invalid response from server."

        print(f"   [WP] Error creating post in WordPress: {error_message}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   [WP] Response Body: {e.response.text if e.response.text else 'No Response'}")
        return False