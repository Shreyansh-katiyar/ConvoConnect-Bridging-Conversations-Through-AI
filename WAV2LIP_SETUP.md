# Wav2Lip Checkpoint Setup

## Manual Download Instructions

1. **Download the Checkpoint**:
   - Visit: https://github.com/Rudrabha/Wav2Lip/releases
   - Download `wav2lip_gan.pth`

2. **Checkpoint Placement**:
   - Create directory: `Wav2Lip/checkpoints/`
   - Place `wav2lip_gan.pth` in this directory

## Alternative Download Links

1. Google Drive Mirror:
   - [Wav2Lip Checkpoint](https://drive.google.com/file/d/1i2LFmq1zLo-ETEPaY5Br_krkm4mKmzVq/view)

## Installation Dependencies

```bash
pip install -r requirements_wav2lip.txt
```

## Troubleshooting

- Ensure Python 3.7+ is installed
- Check CUDA compatibility for GPU acceleration
- Verify all dependencies are correctly installed

## Model Requirements

- Input video: Clear frontal face
- Recommended resolution: 720p-1080p
- Stable lighting conditions
