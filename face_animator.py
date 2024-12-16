import cv2
import numpy as np
import dlib
from scipy.spatial import Delaunay
import soundfile as sf
import librosa
import logging
import streamlit as st
import os

class FaceAnimator:
    def __init__(self):
        # Initialize face detector and facial landmarks predictor
        st.info("Initializing face detector...")
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        
        # Indices for mouth landmarks
        self.mouth_indices = list(range(48, 68))
        st.info("Face detector initialized successfully")
        
    def resize_frame(self, frame, target_width=960):
        """Resize frame while maintaining aspect ratio"""
        height, width = frame.shape[:2]
        ratio = target_width / float(width)
        target_height = int(height * ratio)
        return cv2.resize(frame, (target_width, target_height))
        
    def get_landmarks(self, image):
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.detector(gray)
        if len(faces) == 0:
            st.warning("No faces detected in the frame")
            return None
            
        # Get facial landmarks
        landmarks = self.predictor(gray, faces[0])
        points = np.array([[p.x, p.y] for p in landmarks.parts()])
        
        return points
        
    def get_mouth_mask(self, image, landmarks):
        # Get mouth landmarks
        mouth_points = landmarks[self.mouth_indices]
        
        # Create mask
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        hull = cv2.convexHull(mouth_points)
        cv2.fillConvexPoly(mask, hull, 255)
        
        return mask
        
    def animate_frame(self, frame, audio_features, frame_idx):
        # Resize frame for faster processing
        small_frame = self.resize_frame(frame)
        
        # Get landmarks on small frame
        landmarks = self.get_landmarks(small_frame)
        if landmarks is None:
            return frame
            
        # Scale landmarks back to original size
        scale_factor = frame.shape[1] / small_frame.shape[1]
        landmarks = (landmarks * scale_factor).astype(np.int32)
        
        # Get mouth mask
        mouth_mask = self.get_mouth_mask(frame, landmarks)
        
        # Calculate mouth opening based on audio
        if len(audio_features) > frame_idx:
            energy = audio_features[frame_idx]
            opening = int(energy * 20)  # Scale factor for mouth opening
            
            # Modify mouth points based on audio energy
            mouth_points = landmarks[self.mouth_indices].copy()
            mouth_center = mouth_points.mean(axis=0)
            
            for i in range(len(mouth_points)):
                vector = mouth_points[i] - mouth_center
                mouth_points[i] = mouth_center + vector * (1 + opening * 0.1)
            
            # Create new mask with modified mouth
            new_mask = np.zeros_like(mouth_mask)
            hull = cv2.convexHull(mouth_points.astype(np.int32))
            cv2.fillConvexPoly(new_mask, hull, 255)
            
            # Blend the original and modified mouth
            result = frame.copy()
            mouth_region = cv2.bitwise_and(frame, frame, mask=new_mask)
            result = cv2.add(result, mouth_region)
            
            return result
            
        return frame
        
    def process_audio(self, audio_path):
        st.info(f"Processing audio from: {audio_path}")
        # Load audio and extract features
        y, sr = librosa.load(audio_path)
        
        # Get audio energy
        hop_length = int(sr / 30)  # For 30 fps video
        energy = librosa.feature.rms(y=y, hop_length=hop_length)[0]
        
        st.info(f"Audio processed: {len(energy)} frames")
        return energy
        
    def animate_video(self, video_path, audio_path, output_path):
        st.info(f"Starting video animation: {video_path}")
        # Load video
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Calculate output dimensions (960p max width)
        output_width = min(width, 960)
        output_height = int(height * (output_width / width))
        
        st.info(f"Processing video: {width}x{height} -> {output_width}x{output_height} @ {fps}fps")
        
        # Process audio
        audio_features = self.process_audio(audio_path)
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (output_width, output_height))
        
        frame_idx = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Resize frame for output
                frame = cv2.resize(frame, (output_width, output_height))
                
                # Animate frame
                animated_frame = self.animate_frame(frame, audio_features, frame_idx)
                out.write(animated_frame)
                
                # Update progress
                progress = int((frame_idx / total_frames) * 100)
                progress_bar.progress(progress)
                status_text.text(f"Processing frame {frame_idx + 1}/{total_frames}")
                
                frame_idx += 1
                
            st.info("Video processing completed successfully")
            
        except Exception as e:
            st.error(f"Error processing video: {str(e)}")
            logging.error("Video processing error", exc_info=True)
            
        finally:
            cap.release()
            out.release()
            
        if os.path.exists(output_path):
            st.info(f"Animation completed: {output_path}")
            return output_path
        else:
            st.error("Failed to create output video")
            return None
