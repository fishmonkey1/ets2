from grabscreen import grab_screen
import GameWindow
import lanes
import cv2
import numpy as np
import keys as k
import time

import pprint
pp = pprint.PrettyPrinter(depth=6)


keys = k.Keys()

def pathing(minimap):
    pass

def mirrors_analysis(l_mirror_vertices, r_mirror_vertices):
    pass

def roi(image, road_vertices,l_mirror_vertices,r_mirror_vertices):

    #empty array of zeros (empty pixels) in same shape as frame
    mask = np.zeros_like(image)
    #create polygon shape (mask)
    cv2.fillPoly(mask, road_vertices, 255)
    # show only area that is mask
    masked_road = cv2.bitwise_and(image, mask)

    mask = np.zeros_like(image)
    cv2.fillPoly(mask, l_mirror_vertices, 255)
    masked_L_mirror = cv2.bitwise_and(image, mask)

    mask = np.zeros_like(image)
    cv2.fillPoly(mask, r_mirror_vertices, 255)
    masked_R_mirror = cv2.bitwise_and(image, mask)
    
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, road_vertices, 255)
    cv2.fillPoly(mask, l_mirror_vertices, 255)
    cv2.fillPoly(mask, r_mirror_vertices, 255)
    total_masks = cv2.bitwise_and(image, mask)
    
    
    # show only area that is mask

    cv2.imwrite("pics/testing/masked_road.jpg", masked_road)
    cv2.imwrite("pics/testing/masked_L_mirror.jpg", masked_L_mirror)
    cv2.imwrite("pics/testing/masked_R_mirror.jpg", masked_R_mirror)
    cv2.imwrite("pics/testing/total_masks.jpg", total_masks)

    return masked_road, masked_L_mirror, masked_R_mirror, total_masks

def draw_lines(image, lines, color):
    coords = lines
    #         #coords = line[0]
    cv2.line(image, (coords[0], coords[1]), (coords[2], coords[3]), color, 2)
    
    # try:
    #     for coords in lines:
    #         #coords = line[0]
    #         cv2.line(image, (coords[0], coords[1]), (coords[2], coords[3]), [255,0,0], 5)
    # except:
    #     print("uhhhh")
    #     pass

def process_frame(frame):

    #gets full frame ready for edge detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    canny = cv2.Canny(gray, threshold1=200, threshold2=300) #200/300
    canny_blurred = cv2.GaussianBlur(canny, (5,5), 0)

    # vertices of parts of screen for individual line detection
    road_vertices = np.array([[300,507], [840,507], [840,350], [300,350]], dtype=np.int32)
    l_mirror_vertices = np.array([[18,156], [169,156], [169,362], [18,362]], dtype=np.int32)
    r_mirror_vertices = np.array([[852,156], [1003,156], [1003,362], [852,362]], dtype=np.int32)
    masked_road, masked_l_mirror, masked_r_mirror, total_masks = roi(canny_blurred, [road_vertices], [l_mirror_vertices], [r_mirror_vertices])

    #cv2.imwrite('test.jpg', masked_frame)
    
    road_lines = cv2.HoughLinesP(masked_road, cv2.HOUGH_PROBABILISTIC, 1*np.pi/180, 200, np.array([]), 40, 10)
    l_mirror_lines = cv2.HoughLinesP(masked_l_mirror, cv2.HOUGH_PROBABILISTIC, 1*np.pi/180, 200, np.array([]), 40, 10)
    r_mirror_lines = cv2.HoughLinesP(masked_r_mirror, cv2.HOUGH_PROBABILISTIC, 1*np.pi/180, 200, np.array([]), 40, 10)
    # print(len(road_lines),len(l_mirror_lines),len(r_mirror_lines),)

    all_slopes = []
    if road_lines is not None:
        road_slopes = lanes.get_slopes(road_lines, True)
        all_slopes.append(road_slopes)
    if l_mirror_lines is not None:
        l_mirror_slopes = lanes.get_slopes(l_mirror_lines, True)
        all_slopes.append(l_mirror_slopes)
    if r_mirror_lines is not None:
        r_mirror_slopes = lanes.get_slopes(r_mirror_lines, True)
        all_slopes.append(r_mirror_slopes)
    # all_slopes = [road_slopes]

    for slopes in all_slopes:
        for pos_neg_disq in slopes.keys():
            if pos_neg_disq == 'pos':
                color = [255,0,0]
            if pos_neg_disq == 'neg':
                color = [0,255,0]
            if pos_neg_disq == 'disqualified':
                color = [0,0,255]
            for idx in slopes[pos_neg_disq]:

                #draw_lines(frame, slopes[pos_neg_disq][idx][2], color)
                # masked_frame = cv2.cvtColor(total_masks, cv2.COLOR_GRAY2BGR)

                '''
                This draws calculated lines directly on frame that was passed in
                '''
                draw_lines(frame, slopes[pos_neg_disq][idx][2], color)

    #return masked_frame
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
        
        if cv2.waitKey(5) == ord('q'): #press q to quit
            break

# uncomment if video output wanted
#out.release()
cv2.destroyAllWindows()

