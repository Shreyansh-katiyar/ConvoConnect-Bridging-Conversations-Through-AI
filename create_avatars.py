import numpy as np
import cv2

def create_avatar(color, filename):
    # Create a 200x200 image with the specified color
    img = np.ones((200, 200, 3), dtype=np.uint8) * 255
    
    # Draw a circle for the head
    cv2.circle(img, (100, 100), 80, color, -1)
    
    # Draw eyes
    cv2.circle(img, (70, 80), 10, (255, 255, 255), -1)
    cv2.circle(img, (130, 80), 10, (255, 255, 255), -1)
    
    # Draw smile
    cv2.ellipse(img, (100, 110), (40, 30), 0, 0, 180, (255, 255, 255), 2)
    
    # Save the image
    cv2.imwrite(filename, img)

if __name__ == "__main__":
    # Create interviewer avatar (blue)
    create_avatar((255, 150, 0), "interviewer-avatar.png")
    
    # Create interviewee avatar (green)
    create_avatar((0, 150, 0), "interviewee-avatar.png")
