import requests
import os

def download_file(url, filename):
    # Send a GET request to the URL
    response = requests.get(url, stream=True)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Open the file in write-binary mode
        with open(filename, 'wb') as file:
            # Iterate over the response data in chunks
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Successfully downloaded {filename}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

# URL of the Wav2Lip checkpoint
checkpoint_url = "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.1/wav2lip_gan.pth"
checkpoint_path = "Wav2Lip/checkpoints/wav2lip_gan.pth"

# Ensure the directory exists
os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)

# Download the checkpoint
download_file(checkpoint_url, checkpoint_path)
