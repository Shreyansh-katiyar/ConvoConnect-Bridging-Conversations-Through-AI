import cv2
import numpy as np
import streamlit as st
import tempfile
import os
import logging
import soundfile as sf
from face_animator import FaceAnimator

class LipSyncVideo:
    def __init__(self, video_path):
        """Initialize the lip sync video component."""
        self.video_path = video_path
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        self.face_animator = FaceAnimator()
        self.temp_dir = tempfile.mkdtemp()
        logging.info(f"Initialized LipSyncVideo with video: {video_path}")
        logging.info(f"Using temporary directory: {self.temp_dir}")
        
    def process_speech(self, audio_data, text):
        """Process TTS audio and synchronize with video."""
        try:
            # Save audio to temporary WAV file
            audio_path = os.path.join(self.temp_dir, f"speech_{hash(text)}.wav")
            logging.info(f"Saving audio to: {audio_path}")
            
            # Convert audio data to numpy array
            with open(audio_path, "wb") as f:
                f.write(audio_data)
            
            # Generate output path for video
            output_path = os.path.join(self.temp_dir, f"output_{hash(text)}.mp4")
            logging.info(f"Output video will be saved to: {output_path}")
            
            # Animate video with lip sync
            logging.info("Starting face animation...")
            self.face_animator.animate_video(self.video_path, audio_path, output_path)
            logging.info("Face animation completed")
            
            if not os.path.exists(output_path):
                raise FileNotFoundError(f"Failed to generate output video at: {output_path}")
            
            return output_path, audio_path
        except Exception as e:
            logging.error(f"Error in process_speech: {str(e)}", exc_info=True)
            raise
        
    def display_video(self, video_path):
        """Display the lip-synced video in Streamlit."""
        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
                
            # Add video container below camera feed
            st.markdown("""
                <style>
                .lip-sync-video {
                    margin-top: 20px;
                    border-radius: 16px;
                    overflow: hidden;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
                }
                </style>
            """, unsafe_allow_html=True)
            
            with st.container():
                st.markdown("### AI Interviewer Video")
                # Display video
                video_file = open(video_path, 'rb')
                video_bytes = video_file.read()
                st.video(video_bytes, use_container_width=True)
                video_file.close()
                
            logging.info(f"Successfully displayed video from: {video_path}")
        except Exception as e:
            logging.error(f"Error displaying video: {str(e)}", exc_info=True)
            st.error(f"Error displaying video: {str(e)}")
        
    def cleanup(self):
        """Clean up temporary files."""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
            logging.info(f"Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            logging.error(f"Error cleaning up: {str(e)}", exc_info=True)
