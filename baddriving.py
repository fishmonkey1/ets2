import cv2
import numpy as np
import time
from math import dist

from numpy import ones,vstack
from numpy.linalg import lstsq
from statistics import mean

import pprint
pp = pprint.PrettyPrinter(depth=5)

from GameWindow import screen_width, screen_height


'''
# not using these yet
import keyboardkeys as k
buttons = k.Keys()
from grabscreen import grab_screen
import GameWindow

'''
# venv\Scripts\activate


# vertices of parts of screen for individual line detection  
vertices = {"road_vertices":     np.array([[300,508], [840,508], [840,350], [300,350]], dtype=np.int32),
            "l_mirror_vertices": np.array([[18,285], [169,285], [169,362], [18,362]], dtype=np.int32),
            "r_mirror_vertices": np.array([[852,285], [1003,285], [1003,362], [852,362]], dtype=np.int32)}

vertices_bounds = {"road_bounding": cv2.boundingRect(vertices["road_vertices"]),
                   "l_mirror_bounding": cv2.boundingRect(vertices["l_mirror_vertices"]),
                   "r_mirror_bounding": cv2.boundingRect(vertices["r_mirror_vertices"])}


def crop(frame):
    x,y,w,h = vertices_bounds['road_bounding']
    cropped_road = frame[y:y+h, x:x+w]

    x,y,w,h = vertices_bounds['l_mirror_bounding']
    cropped_l_mirror = frame[y:y+h, x:x+w]

    x,y,w,h = vertices_bounds['r_mirror_bounding']
    cropped_r_mirror = frame[y:y+h, x:x+w]

    return cropped_road, cropped_l_mirror, cropped_r_mirror


def transformPoints(cropped_lines, ROI_bounding_box):
    '''
    Takes in found lines from cropped image,
    Increases x/y values so they are back
    in their original place on the frame.
    '''

    x_offset, y_offset,_,_ = ROI_bounding_box
    for arr in cropped_lines:
        for xyxy in arr:
 
            xyxy[0] = xyxy[0] + x_offset
            xyxy[1] = xyxy[1] + y_offset
            xyxy[2] = xyxy[2] + x_offset
            xyxy[3] = xyxy[3] + y_offset
            
    return cropped_lines


def get_slopes(lines, include_horizontal=True, min_line_length = 40):
    '''
    Finds slope(m) and y-intercept(b)
    Creates dict of all lines... slope, y-intercept, [x1,y1,x2,y2]   
    '''
    line_dict = {'pos': {},
                'neg': {},
                'horizontal': {}}

    for idx,i in enumerate(lines):
        for xyxy in i:

            # TODO: more efficient calculation 
            x_coords = (xyxy[0],xyxy[2])
            y_coords = (xyxy[1],xyxy[3])
            A = vstack([x_coords,ones(len(x_coords))]).T
            m, b = lstsq(A, y_coords, rcond=None)[0]

            line_data = [m,b,[xyxy[0], xyxy[1], xyxy[2], xyxy[3]]]
            
            length = dist([xyxy[0],xyxy[1]],[xyxy[2],xyxy[3]])
            if length < min_line_length:
                continue

            # #This sorts horizontal lines
            if 0.15> m > -0.15:
                line_dict['horizontal'][idx] = line_data
                continue
            
            # positive slopes
            if m > 0:
                line_dict['pos'][idx] = line_data

            # negative slopes
            if m < 0:
                line_dict['neg'][idx] = line_data

    return line_dict 



def draw_lines(image, coords, color, LSD=None, thickness=2):
             #coords = line[0]
    if LSD is not None:
        cv2.line(image, (int(LSD[0]), int(LSD[1])), (int(LSD[2]),int(LSD[3])), color, thickness)
    else:        
        cv2.line(image, (coords[0], coords[1]), (coords[2], coords[3]), color, thickness)
    

def draw_ROI_vertices(frame, vertices):
    '''
    Draws vertices on frame for testing purposes
    '''
    for key in vertices.keys():
        vert = [vertices[key]]
        isClosed = True

        color = (255, 0, 255) #pink
        thickness = 1

        frame = cv2.polylines(frame, vert, isClosed, color, thickness)
        
    #cv2.imwrite("pics/testing/vertices.jpg", frame)


def process_frame(frame):
     
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    #this is for viewing lines only for testing
    black_mask = np.zeros_like(frame, dtype = "uint8")
    
    lsd = cv2.createLineSegmentDetector(cv2.LSD_REFINE_ADV) #LSD_REFINE_STD is normal, LSD_REFINE_ADV for advanced 

    #return cropped images for each ROI     
    cropped_road, cropped_l_mirror, cropped_r_mirror = crop(gray)

    '''
    lsd.detect() returns tuple of:
        ([Lines in image], [Widths of the regions, where the lines are found. E.g. Width of line.], [Precisions with which the lines are found.])
    if createLSD() is set to LSD_REFINE_ADV, tuple will also contain:
        Vector containing number of false alarms in the line region, with precision of 10%. The bigger the value, logarithmically better the detection.
    '''
    cropped_road_lines     = lsd.detect(cropped_road)[0]            
    cropped_l_mirror_lines = lsd.detect(cropped_l_mirror)[0]    
    cropped_r_mirror_lines = lsd.detect(cropped_r_mirror)[0]    
    
    # puts lines found from cropped images back where they came from
    road_lines     = transformPoints(cropped_road_lines, vertices_bounds['road_bounding'])
    l_mirror_lines = transformPoints(cropped_l_mirror_lines, vertices_bounds['l_mirror_bounding'])
    r_mirror_lines = transformPoints(cropped_r_mirror_lines, vertices_bounds['r_mirror_bounding'])

    # main line dicts for each ROI
    road_slopes     = get_slopes(road_lines, min_line_length = 40)
    l_mirror_slopes = get_slopes(l_mirror_lines, min_line_length = 40)
    r_mirror_slopes = get_slopes(r_mirror_lines, min_line_length = 40)

    draw_all_lines = True

    if draw_all_lines:
        for slopes in (road_slopes, l_mirror_slopes, r_mirror_slopes):
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
                    draw_lines(frame, coords=None, color=color, LSD=slopes[pos_neg_horiz][idx][2])
                    draw_lines(black_mask,coords=None, color=color, LSD=slopes[pos_neg_horiz][idx][2], thickness=1)
    else:
        '''run some sort of filtering func()'''
        pass

    draw_ROI_vertices(frame,vertices)

    #midpoint for steering, we'll use this at some point
    midpoint = 515

    #cv2.imwrite("pics/testing/output.jpg", frame)
    # cv2.imwrite("pics/testing/cropped_l_mirror.jpg", cropped_l_mirror)
    # cv2.imwrite("pics/testing/cropped_r_mirror.jpg", cropped_r_mirror)

    #draw_lines(frame, coords=None, color=[255,0,0], LSD=road_lines)


            
    return frame, black_mask

#runtime = "GAME" # don't think this is working quite yet
#runtime = "VIDEO"
def main(runtime, lineDetectionType):
    if runtime == "GAME":
        
        # just a countdown so you can click on game and bring to focus
        for i in range(5):
            print(i)
            time.sleep(1)

        #run for just 150 frames.
        for i in range(150):
            # screen = grab_screen(region=(0,0,1024,768))
            screen = process_frame(screen)
            screen = cv2.resize(screen, (896,500))
            cv2.imshow("lines", screen)   
            #cv2.moveWindow("cv2screen",1025,0)  #move window so we can see it next to game
            cv2.moveWindow("lines",875,0)
            #cv2.waitKey(1) #this is needed to keep py kernel from crashing
            if cv2.waitKey(1) == ord('q'):
                break
    if runtime == "VIDEO":
        video_output = False
        if video_output:
            out = cv2.VideoWriter('pics/final_output/new test.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 60, (896,500))

        video_in = cv2.VideoCapture("pics/input/ETS2video.mp4")
        
        # frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        paused = False

        while video_in.isOpened():
            ret, screen = video_in.read()
            if not ret:
                print("Can't find frame. Exiting")
                break  
                
            screen_with_lines, black_with_lines = process_frame(screen)
            
            screen_with_lines = cv2.resize(screen_with_lines, (896,500))
            black_with_lines = cv2.resize(black_with_lines, (896,500))

            if video_output:
                out.write(screen_with_lines) #for saving video results

            cv2.imshow("lines", screen_with_lines)   
            cv2.moveWindow("lines",875,0)

            cv2.imshow("perspective", black_with_lines)
            cv2.moveWindow("perspective",0,0)

            '''
            During playback:
                'q' to quit
                'p' to pause/unpause

            While paused:
                'right/left' arrow keys to go forward/back frame-by-frame
            '''

            if paused:
                key = cv2.waitKeyEx(0) # waitKeyEx instead of waitKey
                                    # to get arrow keys

                #print(key) # uncomment to print numcodes for keys on press
                            # in case current numcodes don't work for you

                # forward frame
                if key == 2555904: # right arrow key
                    continue
                
                # back frame
                if key == 2424832: # left arrow key
                    cur_frame_number = video_in.get(cv2.CAP_PROP_POS_FRAMES)
                    #print(cur_frame_number)
                    prev_frame = cur_frame_number - 1
                    if cur_frame_number > 1:
                        prev_frame -= 1
                    video_in.set(cv2.CAP_PROP_POS_FRAMES, prev_frame)

                if key == ord('p'): #press p to unpause
                    paused = False
                    continue

                if key == ord('q'): #press q to quit
                    paused = False
                    break
            else:
                key = cv2.waitKey(5)
                if key == ord('q'): #press q to quit
                    break
                if key == ord('p'): #press p to pause
                    paused = True
        if video_output:
            out.release()
        video_in.release()
        cv2.destroyAllWindows()            

    if runtime == "PICTURE":
        path = 'pics/cabin1.png'
        frame = cv2.imread(path)
        
        screen_with_lines = process_frame(frame, lineDetectionType)

        cv2.imwrite("pics/final_output/output.jpg", screen_with_lines)
            

   
    


#####################################
'''
TODO: 
        - Get monitor size from GameWndow
          (in fact, could have it default to using the VIDEO runtime if ETS2 not found.)

            - Use that to implement a modified imshow function,
              which can size/position each window so that we can
              nicely display multiple videos at once without overlapping.

        - "Line Segment Detection (LSD)" vs. HoughLinesP for line detection...
          https://www.researchgate.net/figure/Comparison-of-LSD-and-HoughLines-a-and-d-are-the-sample-images-b-e-result-of_fig2_322005775
          
          https://docs.opencv.org/3.4/db/d73/classcv_1_1LineSegmentDetector.html#a1816a3c27f7c9b8d8acffec14451d4c4
          https://stackoverflow.com/questions/41329665/linesegmentdetector-in-opencv-3-with-python
'''
# show_frame_with_lines = True
# show_canny = False


runtime = 'VIDEO'          #  Can be 'VIDEO' or 'GAME' or "PICTURE"
lineDetectionType = 'LSD'  #  Can be 'LSD' or 'Hough'

if __name__ == '__main__':
    main(runtime, lineDetectionType)