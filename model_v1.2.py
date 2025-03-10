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

# Initialize models
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
processor = BlipProcessor.from_pretrained("noamrot/FuseCap")
model1 = BlipForConditionalGeneration.from_pretrained("noamrot/FuseCap").to(device)
ocr_model = PaddleOCR(lang='en')

# Initialize Mistral client with API key (ensure you set your API key as an environment variable for security)
api_key = "iBGDfsGLNlGIr26A09CCttgSkaCjDwEM"
model = "mistral-large-latest"
client = Mistral(api_key=api_key)


# Paths
# Define the base path where directories are located
base_path = 'InstaLoginWeb'  # Adjust to the actual parent directory path if needed

# Use a regular expression to find the directory starting with "instagram_content"
matching_dirs = [d for d in glob.glob(os.path.join(base_path, "instagram_content*")) if re.match(r"^instagram_content_\d+_\d+$", os.path.basename(d))]

if matching_dirs:
    base_dir = matching_dirs[0]  # Use the first match, or modify as needed
else:
    raise FileNotFoundError("No directory matching the pattern 'instagram_content_*_*' was found.")

print("Base directory selected:", base_dir)

photos_dir = os.path.join(base_dir, "photos")
captions_dir = os.path.join(base_dir, "captions")
csv_path = os.path.join(base_dir, "metadata.csv")

# Load CSV
df = pd.read_csv(csv_path)

# Process each post
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

    # Step 1: Generate Image Caption with BLIP
    text = "describe the image"
    inputs = processor(raw_image, text, return_tensors="pt").to(device)
    out = model1.generate(**inputs, num_beams=3)
    blip_caption = processor.decode(out[0], skip_special_tokens=True)

    # Step 2: Extract Text from Image using OCR
    ocr_result = ocr_model.ocr(image_path)
    ocr_text = []
    if ocr_result[0] is not None:
        for item in ocr_result[0]:
            ocr_text.append(item[1][0])
    ocr_text = ' '.join(ocr_text)

    # Step 3: Use Mistral API for Classification
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
                    "- **Product Name**: \n"
                    "- **Colour**: \n"
                    "- **Price**: \n"
                    "- **Size**: \n"
                    "- **Weight**: \n"
                    "- **Description**: \n"
                    "- **Subcategory**: \n\n"
                    "If it’s not a product, simply respond 'Not a product.'"
                ),
            },
        ]
    )

    # Display or Save Output
    result_text = chat_response.choices[0].message.content
    print(f"Output for {post_name}:\n{result_text}\n")

    # Optionally, save result to a file
    output_dir = 'output_results'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{post_name}_result.txt")
    with open(output_file, 'w') as f:
        f.write(result_text)
