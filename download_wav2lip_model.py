import os
import requests
from tqdm import tqdm

def download_file(url, filename):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filename, 'wb') as f, tqdm(
        desc=filename,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            pbar.update(size)

def main():
    # Create checkpoints directory
    os.makedirs('Wav2Lip/checkpoints', exist_ok=True)
    
    # Model URL (from Hugging Face)
    model_url = "https://huggingface.co/datasets/amitkumarjaiswal/wav2lip/resolve/main/wav2lip_gan.pth"
    output_path = 'Wav2Lip/checkpoints/wav2lip_gan.pth'
    
    print(f"Downloading Wav2Lip model to {output_path}...")
    try:
        download_file(model_url, output_path)
        print("Download complete!")
        
        # Verify file size
        size = os.path.getsize(output_path)
        print(f"Model file size: {size / 1024 / 1024:.2f} MB")
        
        if size < 1000000:  # Less than 1MB
            print("Warning: File seems too small, might be corrupted")
            return False
            
        return True
        
    except Exception as e:
        print(f"Error downloading model: {str(e)}")
        return False

if __name__ == "__main__":
    main()
