import cv2
import numpy as np

# Load a simulated lunar surface image
terrain_image = cv2.imread("moon_surface.jpg", 0)  # Load in grayscale

# Resize for display
terrain_image = cv2.resize(terrain_image, (800, 800))

# Parameters for simulation
altitude = 500  # Initial altitude (meters)
vertical_velocity = -2  # Descent speed (m/s)
camera_window_size = 200  # Size of the "camera" viewport
current_position = 0  # Start of the viewport

# Hazard detection function
def detect_hazards(terrain):
    edges = cv2.Canny(terrain, 50, 150)  # Detect edges
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return edges, contours

while altitude > 0:
    # Simulate descent by moving the viewport
    current_position += abs(vertical_velocity)
    if current_position + camera_window_size > terrain_image.shape[0]:
        current_position = terrain_image.shape[0] - camera_window_size

    # Crop the current "camera view" from the terrain
    camera_view = terrain_image[current_position:current_position + camera_window_size, :]
    camera_view_color = cv2.cvtColor(camera_view, cv2.COLOR_GRAY2BGR)

    # Hazard detection
    hazards, contours = detect_hazards(camera_view)
    for contour in contours:
        cv2.drawContours(camera_view_color, [contour], -1, (0, 0, 255), 1)

    # Overlay data
    cv2.putText(camera_view_color, f"Altitude: {altitude} m", (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(camera_view_color, f"Velocity: {vertical_velocity} m/s", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Show the "camera view"
    cv2.imshow("Lunar Lander Camera", camera_view_color)

    # Update parameters
    altitude += vertical_velocity

    # Break if 'q' is pressed
    if cv2.waitKey(100) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
