import os
import gdown
import torch

def download_wav2lip_model():
    os.makedirs('models', exist_ok=True)
    
    # Download Wav2Lip model
    model_url = 'https://drive.google.com/uc?id=1HYYXNYyVfUHq0B5uAkA4d7yNHGOK_6Bu'
    output_path = 'models/wav2lip_gan.pth'
    
    if not os.path.exists(output_path):
        print("Downloading Wav2Lip model...")
        gdown.download(model_url, output_path, quiet=False)
        print("Download complete!")
    else:
        print("Model file already exists.")

if __name__ == "__main__":
    download_wav2lip_model()