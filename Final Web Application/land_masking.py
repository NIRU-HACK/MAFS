import numpy as np
import cv2
from scipy.ndimage import uniform_filter

def gamma_correction(image, gamma=1.0):
    """Simple gamma correction."""
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
        for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

def refined_lee_filter(image, window_size=5, k=1.0):
    # Convert to float for calculations
    img = image.astype(np.float32)

    # Step 1: Compute local mean
    mean = uniform_filter(img, size=window_size)

    # Step 2: Compute local variance
    mean_square = uniform_filter(img**2, size=window_size)
    variance = mean_square - mean**2

    # Avoid division by zero
    variance[variance <= 0] = 1e-10

    # Step 3: Compute coefficient of variation
    cv = np.sqrt(variance) / mean

    # Step 4: Compute weighting factor
    weight = 1.0 / (1.0 + k * cv**2)

    # Step 5: Apply filter
    filtered = mean + weight * (img - mean)

    # Clip values to valid range
    filtered = np.clip(filtered, 0, 255).astype(np.uint8)

    return filtered

def compute_mask(image, combined_masks=None, invert_mask=False, bull=False, return_steps=False):
    if combined_masks is None:
        combined_masks = np.zeros_like(image, dtype=np.uint8)
        
    # 1. Load and preprocess
    img = image.copy()
    img = cv2.bilateralFilter(img, d=10, sigmaColor=256, sigmaSpace=75)
    img = cv2.bilateralFilter(img, d=10, sigmaColor=256, sigmaSpace=75)
    img = cv2.bilateralFilter(img, d=10, sigmaColor=256, sigmaSpace=75)
    
    step_1 = img.copy()
    
    # 2. Multi-stage denoising
    blurred = cv2.GaussianBlur(img, (7, 7), 0)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(blurred)
    
    step_2 = enhanced.copy()

    # 3. Combined thresholding
    _, otsu_thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    adaptive_thresh = cv2.adaptiveThreshold(enhanced, 255,
                                          cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY_INV, 21, 5)
    
    # 4. Fusion of thresholding methods
    combined = cv2.bitwise_or(otsu_thresh, adaptive_thresh)
    combined = cv2.bilateralFilter(combined, d=9, sigmaColor=256, sigmaSpace=75)
    combined = cv2.bilateralFilter(combined, d=9, sigmaColor=256, sigmaSpace=75)
    combined = cv2.bilateralFilter(combined, d=9, sigmaColor=256, sigmaSpace=75)
    _, combined = cv2.threshold(combined, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    step_3 = combined.copy()
    
    # 5. Advanced morphological processing
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    morphed = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel, iterations=3)
    morphed = cv2.morphologyEx(morphed, cv2.MORPH_OPEN, kernel, iterations=2)
    
    step_4 = morphed.copy()
    
    morphed = cv2.bitwise_or(morphed, combined_masks)
    morphed = cv2.bitwise_not(morphed)
    
    # 7. Contour filtering (remove small islands)
    contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_contour_area = 2000  # Adjust as needed
    land_mask = np.zeros_like(img)
    for cnt in contours:
        if cv2.contourArea(cnt) > min_contour_area:
            cv2.drawContours(land_mask, [cnt], -1, 255, -1)

    if invert_mask:
        land_mask = cv2.bitwise_not(land_mask)
        
    step_5 = land_mask.copy()
    
    if return_steps:
        return step_1, step_2, step_3, step_4, step_5, land_mask
    
    return land_mask

def calculate_land_percentage(mask):
    total_pixels = mask.size
    land_pixels = cv2.countNonZero(mask)
    return (land_pixels / total_pixels) * 100

def remove_land_areas(image, mask):
    inverted_mask = cv2.bitwise_not(mask)
    return cv2.bitwise_and(image, image, mask=inverted_mask)

def process_image(image, return_steps=True):
    """
    Process image for land masking.
    Expected input: Grayscale image (numpy array).
    """
    original_image = image.copy()
    
    # Step 1: Apply Lee filter for noise reduction
    filtered_image = refined_lee_filter(original_image, window_size=35, k=15)

    # Step 2: Process iteratively to remove land
    current_image = filtered_image.copy()
    masked_image = original_image.copy()
    iteration = 0
    max_iterations = 2 # Reduced for performance in web app

    mask_fin = np.zeros_like(original_image, dtype=np.uint8)
    
    steps = {}

    while iteration < max_iterations:
        iteration += 1
        
        # Create land mask
        if iteration == 1 and return_steps:
            s1, s2, s3, s4, s5, land_mask = compute_mask(current_image, mask_fin, invert_mask=True, return_steps=True)
            steps['Denoising'] = s1
            steps['Enhanced'] = s2
            steps['Thresholding'] = s3
            steps['Morphological'] = s4
            steps['Land Mask'] = s5
        else:
            land_mask = compute_mask(current_image, mask_fin, invert_mask=True, return_steps=False)
            
        land_percentage = calculate_land_percentage(land_mask)

        if land_percentage > 95:
            # Image is almost completely land
            return np.zeros_like(original_image), mask_fin, steps

        # Remove land areas
        masked_image = remove_land_areas(masked_image, land_mask)
        current_image = remove_land_areas(current_image, land_mask)
        current_image = refined_lee_filter(current_image, window_size=35, k=15)
        current_image = gamma_correction(current_image, gamma=0.9)
        current_image = cv2.convertScaleAbs(current_image, alpha=10/9, beta=0)
        mask_fin = cv2.bitwise_or(mask_fin, land_mask)

        if land_percentage < 10:
            break

    buffer_radius = 10
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (buffer_radius, buffer_radius))
    mask_fin = cv2.dilate(mask_fin, kernel, iterations=1)
    
    final_masked = remove_land_areas(original_image, mask_fin)
    
    if return_steps:
        steps['Final Result'] = final_masked
        return final_masked, mask_fin, steps
    
    return final_masked, mask_fin
