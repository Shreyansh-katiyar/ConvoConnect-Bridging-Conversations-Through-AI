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
    model_url = "https://github.com/davisking/dlib-models/raw/master/shape_predictor_68_face_landmarks.dat.bz2"
    compressed_file = "shape_predictor_68_face_landmarks.dat.bz2"
    output_file = "shape_predictor_68_face_landmarks.dat"
    
    print(f"Downloading face landmark model...")
    try:
        # Download compressed file
        download_file(model_url, compressed_file)
        
        # Decompress file
        import bz2
        with bz2.BZ2File(compressed_file) as fr, open(output_file, 'wb') as fw:
            fw.write(fr.read())
            
        # Remove compressed file
        os.remove(compressed_file)
        
        print("Download and extraction complete!")
        return True
        
    except Exception as e:
        print(f"Error downloading model: {str(e)}")
        return False

if __name__ == "__main__":
    main()
