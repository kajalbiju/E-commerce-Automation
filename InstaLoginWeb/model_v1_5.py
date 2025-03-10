import os
import pandas as pd
from PIL import Image
import cv2
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch
from paddleocr import PaddleOCR
from mistralai import Mistral
import re
import glob
import time
import subprocess
import webbrowser
import requests

# Step 1: Run the Flask app.py in the InstaLoginWeb directory
flask_app_path = os.path.join("InstaLoginWeb", "app.py")
flask_process = subprocess.Popen(["python", flask_app_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Step 2: Open Flask app in Chrome
flask_url = "http://127.0.0.1:5000"
chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"  # Adjust path if needed
webbrowser.get(chrome_path).open(flask_url)

print("Flask server started in Chrome. Please input information on the website.")

# Step 3: Wait for 'instagram_content_*_*' folder to appear
base_path = '.'  # Parent directory where 'instagram_content_*_*' should appear
base_dir = None

while not base_dir:
    matching_dirs = [d for d in glob.glob(os.path.join(base_path, "instagram_content*")) 
                     if re.match(r"^instagram_content_\d+_\d+$", os.path.basename(d))]
    
    if matching_dirs:
        base_dir = matching_dirs[0]
        print(f"Found directory: {base_dir}")
        time.sleep(20)  # Check every 5 seconds
        break
    else:
        print("Waiting for 'instagram_content_*_*' directory...")
        time.sleep(5)  # Check every 5 seconds

# Step 4: Initialize models after detecting the folder
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
processor = BlipProcessor.from_pretrained("noamrot/FuseCap")
model1 = BlipForConditionalGeneration.from_pretrained("noamrot/FuseCap").to(device)
ocr_model = PaddleOCR(lang='en')

# Initialize Mistral client with API key (ensure you set your API key as an environment variable for security)
api_key = "iBGDfsGLNlGIr26A09CCttgSkaCjDwEM"
model = "mistral-large-latest"
client = Mistral(api_key=api_key)

# Define paths within the detected 'instagram_content_*_*' directory
photos_dir = os.path.join(base_dir, "photos")
captions_dir = os.path.join(base_dir, "captions")
csv_path = os.path.join(base_dir, "metadata.csv")

# Load CSV
df = pd.read_csv(csv_path)

# Process each post (rest of your code follows as usual)
for idx, row in df.iterrows():
    post_name = f"{row['timestamp']}_{row['id']}"
    image_path = os.path.join(photos_dir, f"{post_name}.jpg")
    caption_path = os.path.join(captions_dir, f"{post_name}.txt")
    print("POST: " + post_name)
    
    # Check if files exist
    if not os.path.exists(image_path) or not os.path.exists(caption_path):
        print(f"Files for post {post_name} not found. Skipping.")
        continue

    # Load Image
    raw_image = cv2.imread(image_path)

    # Load Caption Text from CSV
    instagram_caption = row['caption']

    # Step 5: Generate Image Caption with BLIP
    text = "describe the image"
    inputs = processor(raw_image, text, return_tensors="pt").to(device)
    out = model1.generate(**inputs, num_beams=3)
    blip_caption = processor.decode(out[0], skip_special_tokens=True)

    # Step 6: Extract Text from Image using OCR
    ocr_result = ocr_model.ocr(image_path)
    ocr_text = []
    if ocr_result[0] is not None:
        for item in ocr_result[0]:
            ocr_text.append(item[1][0])
    ocr_text = ' '.join(ocr_text)

    # Step 7: Use Mistral API for Classification
    chat_response = client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {
                "role": "user",
                "content": (
                    "You are a product classifier chatbot. Given the following inputs, identify if it describes a product, "
                    "and if so, provide the product details including name, price, size, weight, description, and subcategory.\n\n"
                    f"1. OCR Text: {ocr_text}\n"
                    f"2. Image Caption: {blip_caption}\n"
                    f"3. Instagram Caption: {instagram_caption}\n\n"
                    "If it is a product, respond with the following format:\n"
                    "name: \n"
                    "colour: \n"
                    "price: \n"
                    "size: \n"
                    "weight: \n"
                    "description: \n"
                    "subcategory: \n\n"
                    "If it’s not a product, simply respond 'Not a product.'"
                ),
            },
        ]
    )

    # Display or Save Output
    result_text = chat_response.choices[0].message.content
    # result_text += "\nid: 3\n"
    print(f"Output for {post_name}:\n{result_text}\n")

    # Optionally, save result to a file
    output_dir = 'output_results'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{post_name}_result.txt")

    # api_url = "http://127.0.0.1:5000/posts"  # Use HTTP instead of HTTPS

    # try:
    #     # Ensure result_text is sent as JSON
    #     response = requests.post(api_url, json=result_text)
        
    #     # Check if the request was successful
    #     if response.status_code == 200:
    #         print("Data sent successfully")
    #     else:
    #         print(f"Failed to send data: {response.status_code} - {response.text}")
    # except requests.exceptions.RequestException as e:
    #     print(f"An error occurred: {e}")

    api_url = "http://127.0.0.1:5000/posts"  # Ensure HTTP is used and endpoint is correct

    # Example data structure (adjust to match your API requirements)
    # post_data = {
    #     "id": "20241113_123708_3500244048538310039_70424899839",
    #     "name": "Comfortable and Stylish Headphones",
    #     "price": "Not specified",
    #     "description": "Headphones designed for comfort and style, suitable for every mood and occasion.",
    #     "colour": "Black",
    #     "weight": "Not specified",
    #     "subcategory": "Audio Accessories"
    # }

    # Function to parse the product information into a dictionary with error handling
    def parse_product_info(info):
        product_data = {}
        lines = info.strip().split('\n')[2:]  # Skip the first two lines
        
        try:
            for line in lines:
                # Expect each line to have a "key: value" format
                key, value = line.split(': ', 1)
                product_data[key.strip().lower()] = value.strip()
        except ValueError as e:
            print(f"Error parsing line: '{line}'. Expected format 'key: value'. Error: {e}")
            return None  # Return None or an empty dictionary to indicate parsing failure
        
        return product_data

    # Convert parsed data to the post_data format with fallback values
    parsed_data = parse_product_info(result_text)
    if parsed_data:
        post_data = {
            "id": "20241113_123708_3500244048538310039_70424899839",  # Sample ID
            "name": parsed_data.get("name", "Unknown Product"),
            "price": parsed_data.get("price", "Not specified"),
            "description": parsed_data.get("description", "No description available"),
            "colour": parsed_data.get("colour", "Not specified"),
            "weight": parsed_data.get("weight", "Not specified"),
            "subcategory": parsed_data.get("subcategory", "Miscellaneous")
        }
        print(post_data)

        try:
            response = requests.post(api_url, json=post_data)
            if response.status_code == 200:
                print("Data sent successfully")
            else:
                print(f"Failed to send data: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
    else:
        print("Failed to parse product information.")





    # try:
    #     response = requests.post(api_url, json=post_data)
    #     if response.status_code == 200:
    #         print("Data sent successfully")
    #     else:
    #         print(f"Failed to send data: {response.status_code} - {response.text}")
    # except requests.exceptions.RequestException as e:
    #     print(f"An error occurred: {e}")


    

    with open(output_file, 'w') as f:
        f.write(result_text)
