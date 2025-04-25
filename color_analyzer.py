from sklearn.cluster import KMeans
import webcolors
import cv2
import numpy as np

class ColorAnalyzer:
 def detect_clothing_color(image, torso_location):
    """Detect the dominant color in the clothing area"""
    x, y, w, h = torso_location
    clothing_roi = image[y:y + h, x:x + w]
    clothing_roi = cv2.resize(clothing_roi, (100, 100), interpolation=cv2.INTER_AREA)

    pixels = clothing_roi.reshape(-1, 3)
    kmeans = KMeans(n_clusters=3, n_init=10)
    kmeans.fit(pixels)

    dominant_color = kmeans.cluster_centers_[np.argmax(np.bincount(kmeans.labels_))]
    b, g, r = dominant_color

    return get_color_name((int(r), int(g), int(b))), (int(r), int(g), int(b))


def get_color_name(rgb):
    """Convert RGB values to the closest color name"""
    min_distance = float('inf')
    closest_color = None

    for hex_code, color_name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(hex_code)
        distance = (r_c - rgb[0]) ** 2 + (g_c - rgb[1]) ** 2 + (b_c - rgb[2]) ** 2

        if distance < min_distance:
            min_distance = distance
            closest_color = color_name

    return closest_color