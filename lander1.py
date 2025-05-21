import cv2
import numpy as np

lander_width, lander_height = 40, 100
thrusting=False

def draw_lander(frame, x, y):
    body_color = (200, 200, 200)
    cv2.ellipse(frame, (x, y - lander_height // 4), (lander_width // 2, lander_height // 3), 
                0, 0, 360, body_color, -1)

    hatch_color = (0, 0, 255)
    cv2.circle(frame, (x, y - lander_height // 2), 20, hatch_color, -1)
    cv2.circle(frame, (x, y - lander_height // 2), 15, (255, 255, 255), 2)  # Hatch border

    base_color = (150, 150, 150)
    cv2.rectangle(frame, (x - lander_width // 2, y), 
                  (x + lander_width // 2, y + lander_height // 4), base_color, -1)

    leg_color = (255, 255, 255)
    cv2.line(frame, (x - lander_width // 2, y + lander_height // 4), 
             (x - lander_width, y + lander_height // 2), leg_color, 3)
    cv2.line(frame, (x + lander_width // 2, y + lander_height // 4), 
             (x + lander_width, y + lander_height // 2), leg_color, 3)

    thruster_color = (0, 255, 255)
    cv2.line(frame, (x-lander_width//4, y+lander_height//4), 
             (x-lander_width//4, y+lander_height//2), thruster_color, 3)
    cv2.line(frame, (x+lander_width//4,y+lander_height//4), 
             (x+lander_width//4, y + lander_height//2), thruster_color, 3)

    if thrusting and fuel > 0:
        flame_color = (0, 165, 255)
        cv2.line(frame, (x-lander_width//4, y+lander_height//2), 
                 (x-lander_width//4, y+lander_height//2+30), flame_color, 10)
        cv2.line(frame, (x+lander_width//4, y+lander_height//2), 
                 (x+lander_width//4, y+lander_height//2+30), flame_color, 10)


def draw_simulation(fuel, temperature, thrust):
    width, height = 1000, 800
    lander_x, lander_y = width // 2, height // 6
    velocity = 0
    gravity = 0.1
    # altitude=0
    
    while True:
        frame2 = cv2.imread("moon.jpg")
        frame = cv2.resize(frame2, (width, height))
    
        altitude = height-lander_y-150  # Distance from moon surface
        acceleration=(thrust/100)-gravity

        if fuel>0:
            velocity-= acceleration
            fuel-=0.9
        else:
            velocity += gravity
        
        lander_y += int(velocity)

        draw_lander(frame, lander_x, lander_y)
        
        # Display inputs
        cv2.putText(frame, f"Fuel: {fuel}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Temperature: {temperature} C", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Thrust: {thrust}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame,f"Altitude:{altitude}",(10,120),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Velocity: {velocity:.2f}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        

        if lander_y>=height-150:
             cv2.putText(frame, "Landed Safely!", (width//2-200,height//2+50),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
                
             cv2.imshow("Moon Lander Algorithm", frame)
             cv2.waitKey(0)
             break
        
        cv2.imshow("Moon Landing Simulation", frame)
        key=cv2.waitKey(100)
        
        # Exit condition
        if key == 27:
            break
   
    cv2.destroyAllWindows()

if __name__ == "__main__":
    fuel = int(input("Enter initial fuel level: "))
    temperature = int(input("Enter temperature(e.g., -100°C to +100°C): "))
    thrust = int(input("Enter thrust level: "))
    velocity=int(input("Enter Velcoity:"))

    
    draw_simulation(fuel, temperature, thrust)
