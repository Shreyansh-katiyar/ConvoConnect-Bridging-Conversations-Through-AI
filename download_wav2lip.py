import os
import torch
import urllib.request

def download_wav2lip_model():
    # Create checkpoints directory
    os.makedirs('Wav2Lip/checkpoints', exist_ok=True)
    
    # Model URL
    model_url = 'https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip_gan.pth'
    output_path = 'Wav2Lip/checkpoints/wav2lip_gan.pth'
    
    print(f"Downloading Wav2Lip model to {output_path}...")
    try:
        urllib.request.urlretrieve(model_url, output_path)
        print("Download complete!")
        
        # Verify file size
        size = os.path.getsize(output_path)
        print(f"Model file size: {size / 1024 / 1024:.2f} MB")
        
    except Exception as e:
        print(f"Error downloading model: {str(e)}")
        raise

if __name__ == "__main__":
    download_wav2lip_model()
