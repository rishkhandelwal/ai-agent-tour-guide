import openai
import requests
import pandas as pd
import xlsxwriter
import os
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import time

# Set your API keys
openai.api_key = 'YOUR_OPENAI_API_KEY'
google_generativeai_api_key = 'YOUR_GOOGLE_GENERATIVEAI_API_KEY'
limewire_api_key = 'YOUR_LIMEWIRE_API_KEY'
google_places_api_key = 'your-google-places-api-key'

# Configure Google Generative AI
genai.configure(api_key=google_generativeai_api_key)

# Create the model configuration for Generative AI
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}
safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
]

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  safety_settings=safety_settings,
  generation_config=generation_config,
)

# Function to get description from ChatGPT
def get_chatgpt_description(attraction_name):
    try:
        response = openai.Completion.create(
            engine="text-davinci-004",
            prompt=f"Provide a detailed description of {attraction_name}.",
            max_tokens=300
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Function to get description from Google Generative AI (Gemini)
def get_gemini_description(attraction_name):
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(f"Provide a detailed description of {attraction_name}.")
    return response.text

# Function to combine unique points from both descriptions
def combine_descriptions(chatgpt_desc, gemini_desc):
    return f"ChatGPT: {chatgpt_desc}\n\nGemini: {gemini_desc}"

# Function to fetch attractions (hardcoded for demonstration)
def get_attractions(country, city):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=tourist+attractions+in+{city}+{country}&key={google_places_api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        attractions = response.json().get('results', [])
        return [attraction['name'] for attraction in attractions]
    else:
        return []
# Function to generate images using LimeWire API
def generate_image(attraction_name):
    url = "https://api.limewire.com/api/image/generation"

    payload = {
      "prompt": attraction_name,
      "negative_prompt": "darkness, fog",
      "samples": 1,
      "quality": "LOW",
      "guidance_scale": 50,
      "aspect_ratio": "1:1",
      "style": "PHOTOREALISTIC"
    }

    headers = {
      "Content-Type": "application/json",
      "X-Api-Version": "v1",
      "Accept": "application/json",
      "Authorization": f"Bearer {limewire_api_key}"
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    if response.status_code == 200 and data['status'] == 'COMPLETED':
        image_url = data['data'][0]['asset_url']
        return image_url
    else:
        return None

# Function to download an image from a URL and save it locally
def download_image(image_url, file_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        img.save(file_path)

# Main function to execute the script
def main():
    # Collecting user input
    country = input("Enter the country: ")
    city = input("Enter the city: ")

    # Fetch attractions
    attractions = get_attractions(country, city)
    if not attractions:
        print("No attractions found.")
        return

    print(f"Found {len(attractions)} attractions in {city}, {country}.")

    # Initialize an empty list to store results
    results = []

    # Directory to save images
    os.makedirs('images', exist_ok=True)

    # Process each attraction
    for attraction in attractions:
        chatgpt_desc = get_chatgpt_description(attraction)
        gemini_desc = get_gemini_description(attraction)
        combined_desc = combine_descriptions(chatgpt_desc, gemini_desc)
        image_url = generate_image(attraction)

        if image_url:
            image_file_path = f"images/{attraction.replace(' ', '_')}.jpg"
            download_image(image_url, image_file_path)
        else:
            image_file_path = None

        results.append({
            "Country": country,
            "City": city,
            "Attraction Name": attraction,
            "ChatGPT Description": chatgpt_desc,
            "Gemini Description": gemini_desc,
            "Combined Description": combined_desc,
            "Image Path": image_file_path
        })

        # Sleep for 20 seconds to avoid hitting rate limits
        time.sleep(20)

    # Convert results to a DataFrame
    df = pd.DataFrame(results)
    df.to_excel('tourdata.xlsx')
    # Export to Excel
    with pd.ExcelWriter('tourist_attractions.xlsx', engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Attractions')
        worksheet = writer.sheets['Attractions']

        for idx, row in df.iterrows():
            image_path = row['Image Path']
            if image_path and os.path.exists(image_path):
                worksheet.insert_image(idx + 1, len(df.columns) - 1, image_path, {'x_scale': 0.5, 'y_scale': 0.5})

    print("Excel file created successfully.")

# Execute the main function
if __name__ == "__main__":
    main()
