import cv2
import numpy as np
import random

lander_width, lander_height = 40, 100
trajectory_points = []

class Obstacle:
    def __init__(self, width, height):
        self.radius = random.randint(10, 20)
        corners = [(0, 0), (width, 10), (10, height), (width, height)]
        self.x, self.y = random.choice(corners)
        angle = random.uniform(np.pi / 4, 3 * np.pi / 4) if self.y == 0 else random.uniform(-np.pi / 4, -3 * np.pi / 4)
        speed = random.uniform(0.5, 1.5)
        self.vx = speed * np.cos(angle)
        self.vy = speed * np.sin(angle)

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, frame):
        cv2.circle(frame, (int(self.x), int(self.y)), self.radius, (0, 0, 255), -1)

    def collides_with(self, lx, ly):
        return np.hypot(self.x - lx, self.y - ly) < self.radius + max(lander_width, lander_height) / 2

def draw_lander(frame, x, y, angle, thrusting):
    M = cv2.getRotationMatrix2D((x, y), angle, 1.0)
    canvas = np.zeros_like(frame)

    body_color = (200, 200, 200)
    cv2.ellipse(canvas, (x, y - lander_height // 4), (lander_width // 2, lander_height // 3), 0, 0, 360, body_color, -1)
    cv2.circle(canvas, (x, y - lander_height // 2), 20, (0, 0, 255), -1)
    cv2.circle(canvas, (x, y - lander_height // 2), 15, (255, 255, 255), 2)
    cv2.rectangle(canvas, (x - lander_width // 2, y), (x + lander_width // 2, y + lander_height // 4), (150, 150, 150), -1)
    cv2.line(canvas, (x - lander_width // 2, y + lander_height // 4), (x - lander_width, y + lander_height // 2), (255, 255, 255), 3)
    cv2.line(canvas, (x + lander_width // 2, y + lander_height // 4), (x + lander_width, y + lander_height // 2), (255, 255, 255), 3)
    cv2.line(canvas, (x - lander_width // 4, y + lander_height // 4), (x - lander_width // 4, y + lander_height // 2), (0, 255, 255), 3)
    cv2.line(canvas, (x + lander_width // 4, y + lander_height // 4), (x + lander_width // 4, y + lander_height // 2), (0, 255, 255), 3)
    if thrusting:
        flame_color = (0, 165, 255)
        cv2.line(canvas, (x - lander_width // 4, y + lander_height // 2), (x - lander_width // 4, y + lander_height // 2 + 30), flame_color, 10)
        cv2.line(canvas, (x + lander_width // 4, y + lander_height // 2), (x + lander_width // 4, y + lander_height // 2 + 30), flame_color, 10)
    rotated = cv2.warpAffine(canvas, M, (frame.shape[1], frame.shape[0]))
    frame[:] = cv2.add(frame, rotated)

def get_phase(altitude):
    if altitude > 400:
        return "Rough Braking Phase"
    elif altitude > 250:
        return "Altitude Hold Phase"
    elif altitude > 100:
        return "Fine Braking Phase"
    elif altitude > 20:
        return "Terminal Descent Phase"
    else:
        return "Touchdown"

def auto_thrust(altitude):
    if altitude > 400:
        return 100
    elif altitude > 250:
        return 80
    elif altitude > 100:
        return 60
    elif altitude > 20:
        return 40
    else:
        return 0

def draw_simulation(fuel, temperature):
    width, height = 1000, 800
    lander_x, lander_y = 200, 100
    vx, vy = 1.5, 0.0
    gravity = 0.1
    angle = -30
    obstacles = []

    while True:
        frame_bg = cv2.imread("moon.jpg")
        frame = cv2.resize(frame_bg, (width, height))

        altitude = height - lander_y - 150
        phase = get_phase(altitude)
        thrust = auto_thrust(altitude)
        thrusting = fuel > 0 and thrust > gravity * 100

        acceleration = gravity-(thrust / 100)
        if fuel > 0:
            vy += acceleration
            fuel -= 0.3
        else:
            vy += gravity

        vy = max(min(vy, 2), -1)

        lander_y += int(vy)

        if altitude < 100:
            angle += 2
            angle = min(angle, 0)

        trajectory_points.append((lander_x, lander_y))
        for pt in trajectory_points:
            cv2.circle(frame, pt, 2, (0, 255, 255), -1)

        if random.random() < 0.1:
            obstacles.append(Obstacle(width, height))

        avoidance_force = 0
        danger_radius = 100

        for ob in obstacles:
            ob.update()
            dx = ob.x - lander_x
            dy = ob.y - lander_y
            distance = np.hypot(dx, dy)
            if distance < danger_radius:
                force = (danger_radius - distance) / danger_radius
                if dx > 0:
                    avoidance_force -= force
                else:
                    avoidance_force += force
            ob.draw(frame)
            if ob.collides_with(lander_x, lander_y):
                cv2.putText(frame, "Crashed into obstacle!", (width//2 - 250, height//2),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
                cv2.imshow("Moon Lander Simulation", frame)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                return

        vx += avoidance_force
        lander_x += int(vx)

        draw_lander(frame, lander_x, lander_y, angle, thrusting)

        bar_x = width - 50
        bar_top = 50
        bar_bottom = height - 150
        bar_height = bar_bottom - bar_top
        altitude_ratio = max(min(altitude / (height - 150), 1), 0)
        bar_fill_height = int(bar_height * altitude_ratio)
        bar_fill_top = bar_bottom - bar_fill_height

        cv2.rectangle(frame, (bar_x, bar_top), (bar_x + 20, bar_bottom), (100, 100, 100), 2)
        bar_color = (0, 255, 0) if altitude > 100 else (0, 0, 255)
        cv2.rectangle(frame, (bar_x, bar_fill_top), (bar_x + 20, bar_bottom), bar_color, -1)
        cv2.putText(frame, "ALTITUDE", (bar_x - 30, bar_top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        cv2.putText(frame, f"Fuel: {int(fuel)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Temperature: {temperature} C", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Altitude: {altitude}KM", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"V Velocity: {vy:.2f}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"H Velocity: {vx:.2f}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Phase: {phase}", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        if lander_y >= height - 150:
            if abs(vy) <= 2 and abs(vx) <= 2:
                cv2.putText(frame, "Landed Safely!", (width//2 - 200, height//2),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
            else:
                cv2.putText(frame, "Crashed!", (width//2 - 100, height//2),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
            cv2.imshow("Moon Lander Simulation", frame)
            cv2.waitKey(0)
            break

        cv2.imshow("Moon Lander Simulation", frame)
        if cv2.waitKey(100) == 27:
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    fuel = int(input("Enter initial fuel level: "))
    temperature = int(input("Enter temperature (-100 to +100 °C): "))
    draw_simulation(fuel, temperature)
