import pygame
import cv2
import threading

width, height = 1000, 1000
gravity = 1.62 #gravity of the moon
thrust = -0.5
fuel_consumed = 1
delta_t=1/30
altitude=20
temperture=2
max_temperature=9
min_temperature=-23

restart_button = {"x1": 650, "y1": 20, "x2": 770, "y2": 75}
close_button = {"x1": 800, "y1": 20, "x2": 930, "y2": 75}

lander_x, lander_y = width // 2, 20
velocity = 8
fuel = 300
lander_width, lander_height = 40, 100
ground_level = height - 250
thrusting = False
clicked_button=None

def reset_simulation():
    global lander_y, velocity, fuel, thrusting
    lander_y = 20
    velocity = 0
    fuel = 300
    thrusting = False

def handle_mouse_event(event, x, y, flags, param):
    global clicked_button
    if event == cv2.EVENT_LBUTTONDOWN: 
        if restart_button["x1"] <= x <= restart_button["x2"] and restart_button["y1"] <= y <= restart_button["y2"]:
            clicked_button = "Restart"
        elif close_button["x1"] <= x <= close_button["x2"] and close_button["y1"] <= y <= close_button["y2"]:
            clicked_button = "Close"

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


cv2.namedWindow("Moon Lander Algorithm")
cv2.setMouseCallback("Moon Lander Algorithm",handle_mouse_event)

def play_music():
     pygame.mixer.music.play(-1)

is_alert=False
while True:
    if temperture < min_temperature or temperture > max_temperature:
        if not is_alert:
            threading.Thread(target=play_music)
            is_alert_playing = True
    else:
        if is_alert:
            pygame.mixer.music.stop() 
            is_alert_playing = False
    
   
    frame2 = cv2.imread("moon.jpg")
    frame = cv2.resize(frame2, (width, height))

    cv2.rectangle(frame, (restart_button["x1"], restart_button["y1"]),
                  (restart_button["x2"], restart_button["y2"]), (0, 255, 0), -1)
    cv2.putText(frame, "Restart", (restart_button["x1"] + 20, restart_button["y1"] + 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    cv2.rectangle(frame, (close_button["x1"], close_button["y1"]),
                  (close_button["x2"], close_button["y2"]), (0, 0, 255), -1)
    cv2.putText(frame, "Close", (close_button["x1"] + 35, close_button["y1"] + 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Check for key inputs
    key = cv2.waitKey(30) & 0xFF
    if key == ord('q'):  # Quit
        break
    elif clicked_button=="Restart":
        reset_simulation()
        clicked_button=None

    elif clicked_button=="Close":
        break
    elif key == ord('w') and fuel > 0 and temperture>min_temperature and temperture<max_temperature:  # Apply thrust
        thrusting = True
        lander_y-=int(velocity)
        altitude+=thrust*0.01
        velocity += thrust
        fuel -= fuel_consumed
    else:
        thrusting = False
        velocity+=gravity*5/3600
        altitude-=velocity*0.02
    
    if temperture>min_temperature and temperture<max_temperature:
         velocity += gravity*delta_t
         velocity = max(velocity, 1)
         altitude=max(altitude,0)
         lander_y += int(velocity)

    mouse_pos = [650,770]
    if restart_button["x1"] <= mouse_pos[0] <= restart_button["x2"] and restart_button["y1"] <= mouse_pos[1] <= restart_button["y2"]:
        reset_simulation()

    if lander_y + lander_height//2 >= ground_level:
        if abs(velocity) < 3:
            cv2.putText(frame, "Landed Safely!", (width//2-200,height//2-200),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
            draw_lander(frame,500,1000-290)
            cv2.putText(frame, f"Fuel: {fuel}Kg", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255, 255), 2)
            cv2.putText(frame, f"Velocity: {velocity:.2f} m/s", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame,f"Altitude:{0.000}m", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame,f"Temperature:{temperture}C",(10,120),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),2)
        else:
            cv2.putText(frame, "Crashed!", (width//2-130,height//2-200),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)

        cv2.imshow("Moon Lander Algorithm", frame)
        cv2.waitKey(0)
        break

    mouse_pos=[650,770]
    if restart_button["x1"] <= mouse_pos[0] <= restart_button["x2"] and restart_button["y1"] <= mouse_pos[1] <= restart_button["y2"]:
                  reset_simulation()

    if temperture<min_temperature or temperture>max_temperature:
        pygame.mixer.init()
        pygame.mixer.music.load("sound_effects/alert.mp3")
        cv2.putText(frame,"Alert:Unsafe Temperture!",(300,280),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        cv2.putText(frame,f"Not Suitable for Landing",(350,320),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
        cv2.putText(frame,f"Temperature:{temperture}C",(10,120),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),2)
    elif fuel<50:
        draw_lander(frame, lander_x, lander_y)
        cv2.putText(frame, f"Fuel: {fuel}Kg", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0, 255), 2)
        cv2.putText(frame, f"Velocity: {velocity:.2f} m/s", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame,f"Altitude:{altitude:.3f}KM", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame,f"Temperature:{temperture}C",(10,120),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),2)
    elif altitude<1:
        draw_lander(frame, lander_x, lander_y)
        cv2.putText(frame, f"Fuel: {fuel}Kg", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255, 255), 2)
        cv2.putText(frame, f"Velocity: {velocity:.2f} m/s", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame,f"Altitude:{altitude:.3f}m", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame,f"Temperature:{temperture}C",(10,120),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),2)
    else:
        draw_lander(frame, lander_x, lander_y)
        cv2.putText(frame, f"Fuel: {fuel}Kg", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Velocity: {velocity:.2f} m/s", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame,f"Altitude:{altitude:.3f}KM", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame,f"Temperature:{temperture}C",(10,120),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),2)
    cv2.imshow("Moon Lander Algorithm", frame)


cv2.destroyAllWindows()
