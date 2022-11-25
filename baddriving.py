from grabscreen import grab_screen
import GameWindow
from lanes import lanes
import cv2
import numpy as np
import keys as k
import time


keys = k.Keys()

def pathing(minimap):
    pass

def mirrors_roi(mirrors):
    pass

def lanes_roi(image, vertices):
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, vertices, 255)
    masked = cv2.bitwise_and(image, mask)
    return masked

def draw_lines(image, lines):
    try:
        for coords in lines:
            #coords = line[0]
            cv2.line(image, (coords[0], coords[1]), (coords[2], coords[3]), [255,0,0], 2)
    except:
        pass

def process_frame(frame):
    #Lanes
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    canny = cv2.Canny(gray, threshold1=200, threshold2=300) #200/300
    canny_blurred = cv2.GaussianBlur(canny, (5,5), 0)

    #old vertices
    #vertices = np.array([[300,507], [1024,507], [1024,375], [840,375], [840,275], [300,275]])
    
    #trying a narrower window to catch less lines far ahead
    vertices = np.array([[300,507], [840,507], [840,375], [300,275]])
    processed_lane_image = lanes_roi(canny_blurred, [vertices])
    
    #                                 edges                                              minLineLength, maxLineGap
    #found_lines = cv2.HoughLinesP(processed_lane_image, 1, 1*np.pi/180, 200, np.array([]), 13,              5)
    found_lines = cv2.HoughLinesP(processed_lane_image, cv2.HOUGH_PROBABILISTIC, 1*np.pi/180, 200, np.array([]), 40, 10)

    processed_lane_image = cv2.cvtColor(processed_lane_image, cv2.COLOR_GRAY2BGR) #need to color to see lines

    fuck = lanes(found_lines)

    draw_lines(frame, fuck)

  
    return frame

#runtime = "GAME"
runtime = "VIDEO"

if runtime == "GAME":
    
    # just a countdown so you can click on game and bring to focus
    for i in range(5):
        print(i)
        time.sleep(1)

    #run for just 150 frames.
    for i in range(150):
        screen = grab_screen(region=(0,0,1024,768))
        screen = process_frame(screen)
        screen = cv2.resize(screen, (896,500))
        cv2.imshow("lines", screen)   
        #cv2.moveWindow("cv2screen",1025,0)  #move window so we can see it next to game
        cv2.moveWindow("lines",875,0)
        #cv2.waitKey(1) #this is needed to keep py kernel from crashing
        if cv2.waitKey(1) == ord('q'):
            break


if runtime == "VIDEO":

    video = cv2.VideoCapture("pics/ETS2video.mp4")
    
    # uncomment if video output wanted
    #out = cv2.VideoWriter('lane_test2.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 60, (896,500))
    
    while video.isOpened():
        ret, screen = video.read()

        if not ret:
            print("Can't find frame. Exiting")
            break  
               
        screen_with_lines = process_frame(screen)
        screen_with_lines = cv2.resize(screen_with_lines, (896,500))

        # uncomment if video output wanted
        #out.write(screen_with_lines) #for saving video results

        cv2.imshow("lines", screen_with_lines)   
        cv2.moveWindow("lines",875,0)
        
        if cv2.waitKey(1) == ord('q'): #press q to quit
            break

# uncomment if video output wanted
#out.release()
cv2.destroyAllWindows()

