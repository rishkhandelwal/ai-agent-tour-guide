# ai-agent-tour-guide
Developed a AI agent which can give details about tourist attraction and also generate AI image for destination.

# Tourist Attractions App

This application collects information about tourist attractions from a specified country and city, generates detailed descriptions using ChatGPT and Google Generative AI (Gemini), and creates an AI-generated image of each attraction. The results are presented in an Excel sheet.

## Dockerfile Details

### Base Image

We use the official `python:3.9-slim` image, which is a lightweight version of Python 3.9.

### Working Directory

We set the working directory to `/app`.

### Copy requirements.txt

We copy the `requirements.txt` file to the working directory.

### Install Dependencies

We install the required Python packages listed in `requirements.txt`.

### Copy Application Code

We copy the rest of the application code into the container.

### Set Environment Variables

We set the API keys as environment variables. You should replace `your_openai_api_key`, `your_google_generativeai_api_key`, and `your_limewire_api_key` with your actual API keys.

### Run the Script

We specify the command to run the script (`tourist_attraction_agent.py`).

## Building and Running the Docker Container

### Build the Docker Image

```bash
docker build -t tourist-attractions-app .

### Run the docker Container

```bash
docker run -e OPENAI_API_KEY=your_openai_api_key -e GOOGLE_GENERATIVEAI_API_KEY=your_google_generativeai_api_key -e LIMEWIRE_API_KEY=your_limewire_api_key tourist-attractions-app


