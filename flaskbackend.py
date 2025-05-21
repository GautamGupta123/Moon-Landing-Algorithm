from flask import Flask, Response, request
import cv2
import numpy as np

app = Flask(__name__)

# Simulation Parameters
width, height = 1000, 1000
gravity = 0.1
thrust = -0.2
fuel_consumed = 1
lander_x, lander_y = width // 2, 20
velocity = 0
fuel = 300
lander_width, lander_height = 40, 100
ground_level = height - 350
thrusting = False

def draw_lander(frame, x, y):
    body_color = (200, 200, 200)
    cv2.ellipse(frame, (x, y - lander_height // 4), (lander_width // 2, lander_height // 3), 
                0, 0, 360, body_color, -1)
    hatch_color = (0, 0, 255)
    cv2.circle(frame, (x, y - lander_height // 2), 20, hatch_color, -1)
    cv2.circle(frame, (x, y - lander_height // 2), 15, (255, 255, 255), 2)  # Hatch border

    # Body bottom: Rectangular base
    base_color = (150, 150, 150)
    cv2.rectangle(frame, (x - lander_width // 2, y), 
                  (x + lander_width // 2, y + lander_height // 4), base_color, -1)

    # Legs: Triangular supports
    leg_color = (255, 255, 255)
    cv2.line(frame, (x - lander_width // 2, y + lander_height // 4), 
             (x - lander_width, y + lander_height // 2), leg_color, 3)
    cv2.line(frame, (x + lander_width // 2, y + lander_height // 4), 
             (x + lander_width, y + lander_height // 2), leg_color, 3)

    # Thrusters: Triangles at the base
    thruster_color = (0, 255, 255)
    cv2.line(frame, (x - lander_width // 4, y + lander_height // 4), 
             (x - lander_width // 4, y + lander_height // 2), thruster_color, 3)
    cv2.line(frame, (x + lander_width // 4, y + lander_height // 4), 
             (x + lander_width // 4, y + lander_height // 2), thruster_color, 3)

@app.route('/video_feed')
def video_feed():
    def generate_frames():
        global lander_y, velocity, fuel, thrusting

        while True:
            # Background
            frame = np.zeros((height, width, 3), dtype=np.uint8)

            # Update Lander position and velocity
            velocity += gravity
            if thrusting and fuel > 0:
                velocity += thrust
                fuel -= fuel_consumed
            lander_y += int(velocity)

            # Draw Lander
            draw_lander(frame, lander_x, lander_y)

            # Collision Detection
            if lander_y + lander_height // 2 >= ground_level:
                if abs(velocity) < 4:
                    cv2.putText(frame, "Landed Safely!", (width // 2 - 100, height // 2),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    cv2.putText(frame, "Crashed!", (width // 2 - 100, height // 2),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # Convert to JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            frame_data = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/control', methods=['POST'])
def control():
    global lander_y, velocity, fuel, thrusting

    data = request.json
    if data['action'] == 'restart':
        lander_y, velocity, fuel = 20, 0, 300
    elif data['action'] == 'thrust':
        thrusting = data['state']
    elif data['action'] == 'close':
        exit(0)
    return {'status': 'success'}

if __name__ == "__main__":
    app.run(debug=True)
