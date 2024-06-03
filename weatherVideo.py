import os
import cv2
import time
from datetime import datetime
from glob import glob
from weather_secrets import secrets


def get_most_recent_files(directory, file_extension, count):
    # Get the list of files with the given extension in the directory
    files = glob(os.path.join(directory, f"*.{file_extension}"))
    
    # Extract datetime from filenames and sort files by datetime in ascending order
    files.sort(key=lambda x: datetime.strptime(os.path.basename(x).replace('~', ':').replace(f'.{file_extension}', ''), '%Y-%m-%d_%H:%M:%S'), reverse=True)
    
    # Return the most recent 'count' files
    return files[:count]  # Take the last 'count' files

def display_video_from_images(image_files, frame_rate=1):
    # Read and display each image in reverse order
    for file in reversed(image_files):
        img = cv2.imread(file)
        
        # Extract datetime from the filename
        basename = os.path.basename(file).replace('~', ':').replace('.png', '')
        timestamp = datetime.strptime(basename, '%Y-%m-%d_%H:%M:%S')
        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')

        # Add timestamp to the image
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        color = (0, 0, 0)  # Black color
        thickness = 2
        position = (10, 30)  # Bottom-left corner of the image

        img = cv2.putText(img, timestamp_str, position, font, font_scale, color, thickness, cv2.LINE_AA)
        
        # Display the image
        cv2.imshow('Video Feed', img)
        if cv2.waitKey(int(1000 / frame_rate)) & 0xFF == ord('q'):
            return False
    return True

def display_video_from_images_old(image_files, frame_rate=1):
    # Read and display each image
    for file in image_files:
        img = cv2.imread(file)
        cv2.imshow('Video Feed', img)
        if cv2.waitKey(int(1000 / frame_rate)) & 0xFF == ord('q'):
            return False
    return True

# Define the directory containing the images
directory = os.path.join(os.getcwd(), 'Images', 'Omaha', secrets['layer'])

# Frame rate for displaying images (frames per second)
frame_rate = 1

# Number of most recent files to include in the video feed
file_count = 10

while True:

    # Get the most recent 'file_count' PNG files based on their name
    recent_files = get_most_recent_files(directory, 'png', file_count)
    
    if recent_files:
        # Display the video from the recent files
        if not display_video_from_images(recent_files, frame_rate):
            break
    
    # Wait for a certain amount of time before checking for new files again
    time.sleep(1)  # Check for new images every 1 second

# Release resources
cv2.destroyAllWindows()

