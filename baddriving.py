import cv2
import numpy as np
import time

from numpy import ones,vstack
from numpy.linalg import lstsq
from statistics import mean

import pprint
pp = pprint.PrettyPrinter(depth=6)


'''
# not using these yet
import keyboardkeys as k
buttons = k.Keys()
from grabscreen import grab_screen
import GameWindow
import lanes
'''
# venv\Scripts\activate

def roi(image,vertices):
    # revisit later, might not be nessecary? trying to set no color for masking
    # channel_count = image.shape[0]  # i.e. 3 or 4 depending on your image?
    # color = (255,)*channel_count #this makes the mask clear

    color = 255

    # TODO: Refactor:
    #       loop and put masks into dict
    #       return single dict

    mask = np.zeros_like(image) # empty array of zeros (empty pixels) in same shape as frame
    cv2.fillPoly(mask, vertices["road_vertices"], color) # create polygon shape (mask)
    masked_road = cv2.bitwise_and(image, mask) # show only area of original image that is mask shape

    mask = np.zeros_like(image)
    cv2.fillPoly(mask, vertices["l_mirror_vertices"], color)
    masked_L_mirror = cv2.bitwise_and(image, mask)

    mask = np.zeros_like(image)
    cv2.fillPoly(mask, vertices["r_mirror_vertices"], color)
    masked_R_mirror = cv2.bitwise_and(image, mask)
    
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, vertices["road_vertices"], color)
    cv2.fillPoly(mask, vertices["l_mirror_vertices"], color)
    cv2.fillPoly(mask, vertices["r_mirror_vertices"], color)
    total_masks = cv2.bitwise_and(image, mask)

    return masked_road, masked_L_mirror, masked_R_mirror, total_masks

def get_slopes(lines, include_horizontal=False):
    '''
    Finds slope(m) and y-intercept(b)
    Creates dict of all lines... slope, y-intercept, [x,y,x2,y2]

    TODO: Change horizontal --> horizontal
    
    '''

    line_dict = {'pos': {},
                'neg': {}}
    # line_dict['pos']['innerkey1] = 'value'             

    added = 0
    horizontal = 0
    for idx,i in enumerate(lines):
        for xyxy in i:

            # These four lines:
            # modified from http://stackoverflow.com/questions/21565994/method-to-return-the-equation-of-a-straight-line-given-two-points
            # Used to calculate the definition of a line, given two sets of coords.
            x_coords = (xyxy[0],xyxy[2])
            y_coords = (xyxy[1],xyxy[3])
            A = vstack([x_coords,ones(len(x_coords))]).T
            m, b = lstsq(A, y_coords)[0]

            # TODO: we can calculate this shit ourselves,
            #       you lazy fuck
            #       you don't need to use least squares
            #       to calculate y = mx+b
            #       you were just tired and looking for the easy way 

            # #This skips over horizontal lines
            if 0.15> m > -0.15:
                horizontal +=1
                if include_horizontal:
                    if 'horizontal' not in line_dict:
                        line_dict['horizontal'] = {}
                    line_dict['horizontal'][idx] = [m,b,[xyxy[0], xyxy[1], xyxy[2], xyxy[3]]]
                    added +=1
                continue
            
            if m > 0:
                line_dict['pos'][idx] = [m,b,[xyxy[0], xyxy[1], xyxy[2], xyxy[3]]]
                added +=1

            if m < 0:
                line_dict['neg'][idx] = [m,b,[xyxy[0], xyxy[1], xyxy[2], xyxy[3]]]
                added +=1
      
    return line_dict 



def draw_lines(image, coords, color):
             #coords = line[0]
    cv2.line(image, (coords[0], coords[1]), (coords[2], coords[3]), color, 2)
    

def draw_vertices(frame, vertices):

    for key in vertices.keys():
        vert = vertices[key]
        isClosed = True

        color = (255, 0, 255) #pink
        thickness = 1

        frame = cv2.polylines(frame, vert, isClosed, color, thickness)
        
    #cv2.imwrite("pics/testing/vertices.jpg", frame)

def process_frame(frame):
    '''
    TODO:
    https://stackoverflow.com/questions/45127421/when-applying-the-canny-function-can-you-apply-the-mask-first
    Doing masking before edge detection results in detecting edge border around mask.
    need to mask larger polygon, then canny edge detect, then mask actual size again to get rid of border...
    make preprocessing func to do this.
    '''
    
    #gets full frame ready for edge detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    canny = cv2.Canny(gray, threshold1=200, threshold2=300) #200/300
    canny_blurred = cv2.GaussianBlur(canny, (5,5), 0)

    # vertices of parts of screen for individual line detection  
    vertices = {"road_vertices":     [np.array([[300,508], [340,508], [390,475], [460,445], [560,445], [630,475], [685,508], [840,508], [840,350], [300,350]], dtype=np.int32)],
                "l_mirror_vertices": [np.array([[18,285], [169,285], [169,362], [18,362]], dtype=np.int32)],
                "r_mirror_vertices": [np.array([[852,285], [1003,285], [1003,362], [852,362]], dtype=np.int32)]}

    #this draws mask poly on pic
    draw_vertices(frame,vertices)

    masked_road, masked_l_mirror, masked_r_mirror, total_masks = roi(canny_blurred, vertices)
    
    # this saves an image on exit
    cv2.imwrite("pics/testing/total_masks.jpg", total_masks)

    road_lines = cv2.HoughLinesP(masked_road, cv2.HOUGH_PROBABILISTIC, 1*np.pi/180, 200, np.array([]), 40, 10)
    l_mirror_lines = cv2.HoughLinesP(masked_l_mirror, cv2.HOUGH_PROBABILISTIC, 1*np.pi/180, 200, np.array([]), 2, 5)
    r_mirror_lines = cv2.HoughLinesP(masked_r_mirror, cv2.HOUGH_PROBABILISTIC, 1*np.pi/180, 200, np.array([]), 2, 5)
    

    if l_mirror_lines is not None:
        print(len(l_mirror_lines))
    if r_mirror_lines is not None:
        print(len(r_mirror_lines))
    

    all_slopes = []
    if road_lines is not None:
        road_slopes = get_slopes(road_lines, True)
        all_slopes.append(road_slopes)
    if l_mirror_lines is not None:
        l_mirror_slopes = get_slopes(l_mirror_lines, True)
        all_slopes.append(l_mirror_slopes)
    if r_mirror_lines is not None:
        r_mirror_slopes = get_slopes(r_mirror_lines, True)
        all_slopes.append(r_mirror_slopes)


    for slopes in all_slopes:
        for pos_neg_horiz in slopes.keys():
            
            # Sets color of line for drawing
            if pos_neg_horiz == 'pos':
                color = [255,0,0] # Green
            if pos_neg_horiz == 'neg':
                color = [0,255,0] # Blue
            if pos_neg_horiz == 'horizontal':
                color = [0,0,255] # Red

            # Draws lines on frame
            for idx in slopes[pos_neg_horiz]:
                draw_lines(frame, slopes[pos_neg_horiz][idx][2], color)
                
    return frame

#runtime = "GAME" # don't think this is working quite yet
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

