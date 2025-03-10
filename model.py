# %% [markdown] # ## Image Captioning



# %%
import requests
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch
import cv2
from mistralai import Mistral
from paddleocr import PaddleOCR, draw_ocr # main OCR dependencies
from matplotlib import pyplot as plt # plot images
import cv2 #opencv
import os # folder directory navigation

import re
import glob

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)
processor = BlipProcessor.from_pretrained("noamrot/FuseCap")
model1 = BlipForConditionalGeneration.from_pretrained("noamrot/FuseCap").to(device)

# %%
# img_url="https://cdn.dribbble.com/users/5054637/screenshots/14026155/media/7cc1339278e8a82be1cd66a7f9c5f6d2.jpeg"
# raw_image = Image.open(requests.get(img_url, stream=True).raw).convert('RGB')

# raw_image=cv2.imread("WIN_20241113_16_35_15_Pro.jpg")
raw_image=cv2.imread("Images/3.jpg")
text = "describe the image"
inputs = processor(raw_image, text, return_tensors="pt").to(device)

out = model1.generate(**inputs, num_beams = 3)
corpus1= processor.decode(out[0], skip_special_tokens=True)
print(corpus1)

ocr_model = PaddleOCR(lang='en')
result=ocr_model.ocr("Images/3.jpg")
corpus = []
if result[0]!=None:
    for item in result[0]:
        text = item[1][0]  # Access the text part in each tuple
        corpus.append(text) # Append to corpus list

    # Join the list items into a single string for the corpus if needed
    corpus_text = ' '.join(corpus)
else:
    corpus_text=''

corpus_text

coprus3="get your coke at flat 50 off today"

api_key = "iBGDfsGLNlGIr26A09CCttgSkaCjDwEM"
model = "mistral-large-latest"
client = Mistral(api_key=api_key)

chat_response = client.chat.complete(
    model=model,
    messages=[
        {
            "role": "user",
            "content": (
                "You are a product classifier chatbot. Given the following inputs, identify if it describes a product, "
                "and if so, provide the product details including name, price, size, weight, description, and subcategory.\n\n"
                f"1. OCR Text: {corpus1}\n"
                f"2. Image Caption: {corpus_text}\n"
                f"3. Instagram Caption: {coprus3}\n\n"
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


print(chat_response.choices[0].message.content)




