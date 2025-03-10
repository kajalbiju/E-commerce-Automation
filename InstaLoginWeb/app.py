from flask import Flask, render_template, request, redirect, url_for, flash
from instagram_private_api import Client, ClientCompatPatch
import ssl
import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path
import pandas as pd
import certifi
import traceback

app = Flask(__name__, template_folder='templates')

app.secret_key = 'a3f5e9b4567d8e2c1a9c0e4b3f9a1d3f'

# Disable SSL verification for testing
ssl._create_default_https_context = ssl._create_unverified_context

from flask import Flask, request, jsonify
from flask_cors import CORS

# app = Flask(__name__)
CORS(app)  # Allow CORS for cross-origin requests

# In-memory storage for demonstration (use a database in production)
products = []
next_id = 1  # Start ID counter from 1

@app.route('/posts', methods=['POST'])
def add_product():
    global next_id
    data = request.json

    # Assign an incremental ID
    data["id"] = next_id
    next_id += 1  # Increment the counter

    products.append(data)
    return jsonify({"message": "Product added successfully", "product": data}), 200

@app.route('/posts', methods=['GET'])
def get_products():
    return jsonify(products), 200





def create_folder_structure(base_path):
    """Create folder structure for content"""
    folders = {
        'photos': base_path / 'photos',
        'videos': base_path / 'videos',
        'captions': base_path / 'captions'
    }
    for folder in folders.values():
        folder.mkdir(parents=True, exist_ok=True)
    return folders


def login_to_instagram(username, password):
    """Login to Instagram"""
    try:
        api = Client(username, password, timeout=15, verify=certifi.where())
        return api
    except Exception as e:
        traceback.print_exc()
        flash("Failed to login. Check credentials.", "error")
        return None


def get_user_media(api):
    """Fetch all media from user's account"""
    try:
        user_feed = api.self_feed()
        items = []
        while True:
            items.extend(user_feed['items'])
            if not user_feed.get('more_available'):
                break
            max_id = user_feed['next_max_id']
            user_feed = api.self_feed(max_id=max_id)
            time.sleep(2)  # Respect rate limits
        return items
    except Exception as e:
        flash("Error fetching media: " + str(e), "error")
        return []


def download_file(url, filepath):
    """Download a file from URL"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
        return False


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get credentials from the form
        username = request.form['username']
        password = request.form['password']

        # Set up base folder
        base_folder = Path(f"instagram_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        folders = create_folder_structure(base_folder)

        # Login to Instagram
        api = login_to_instagram(username, password)
        if not api:
            return redirect(url_for('index'))

        # Get all media
        flash("Fetching your media items...", "info")
        media_items = get_user_media(api)

        if not media_items:
            flash("No media items found.", "warning")
            return redirect(url_for('index'))

        # Process each media item
        media_metadata = []
        for item in media_items:
            try:
                media_info = extract_media_info(item)

                # Download media files
                for idx, (media_type, url) in enumerate(media_info['urls']):
                    filename = f"{media_info['timestamp']}_{media_info['id']}_{idx + 1}" if len(
                        media_info['urls']) > 1 else f"{media_info['timestamp']}_{media_info['id']}"
                    filepath = folders['photos'] / f"{filename}.jpg" if media_type == 'photo' else folders[
                                                                                                       'videos'] / f"{filename}.mp4"
                    if download_file(url, filepath):
                        print(f"Downloaded {media_type}: {filepath.name}")

                # Save caption
                caption_file = folders['captions'] / f"{media_info['timestamp']}_{media_info['id']}.txt"
                if media_info['caption']:
                    with open(caption_file, 'w', encoding='utf-8') as f:
                        f.write(media_info['caption'])

                # Add to metadata
                media_metadata.append({
                    'id': media_info['id'],
                    'timestamp': media_info['timestamp'],
                    'type': media_info['type'],
                    'caption': media_info['caption']
                })
                time.sleep(2)  # Respect rate limits
            except Exception as e:
                print(f"Error processing item: {str(e)}")
                continue

        # Save metadata to CSV
        metadata_df = pd.DataFrame(media_metadata)
        metadata_df.to_csv(base_folder / 'metadata.csv', index=False)

        flash("Download completed! Content saved in: " + str(base_folder), "success")
    return render_template('index.html')


def extract_media_info(item):
    """Extract relevant information from media item"""
    info = {
        'id': item['id'],
        'timestamp': datetime.fromtimestamp(item['taken_at']).strftime('%Y%m%d_%H%M%S'),
        'caption': item.get('caption', {}).get('text', '') if item.get('caption') else '',
        'type': 'carousel' if item.get('carousel_media') else item['media_type'],
        'urls': []
    }
    if info['type'] == 'carousel':
        for carousel_item in item['carousel_media']:
            if carousel_item['media_type'] == 1:
                info['urls'].append(('photo', carousel_item['image_versions2']['candidates'][0]['url']))
            elif carousel_item['media_type'] == 2:
                info['urls'].append(('video', carousel_item['video_versions'][0]['url']))
    else:
        if item['media_type'] == 1:
            info['urls'].append(('photo', item['image_versions2']['candidates'][0]['url']))
        elif item['media_type'] == 2:
            info['urls'].append(('video', item['video_versions'][0]['url']))
    return info


if __name__ == '__main__':
    app.run(debug=True)
