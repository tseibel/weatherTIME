import cv2
import numpy as np

# Read the image
img = cv2.imread('Images/Omaha/2024-05-27_20~55~55.png')

# Convert the image to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply non-local means denoising filter
denoised_gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

# Apply Gaussian blurring
denoised = cv2.GaussianBlur(denoised_gray, (5, 5), 0)

# Show the denoised image
cv2.imshow('Denoised Image', denoised)
cv2.waitKey(0)
cv2.destroyAllWindows()