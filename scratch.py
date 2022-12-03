import cv2
import numpy as np

vertices = {"road_vertices":     np.array([[300,508], [340,508], [390,475], [460,445], [560,445], [630,475], [685,508], [840,508], [840,350], [300,350]], dtype=np.int32),
            "l_mirror_vertices": np.array([[18,285], [169,285], [169,362], [18,362]], dtype=np.int32),
            "r_mirror_vertices": [np.array([[852,285], [1003,285], [1003,362], [852,362]], dtype=np.int32)]}

import pprint
pp = pprint.PrettyPrinter(depth=6)

def draw_lines(image, color, LSD=None):
    for xyxy in LSD:
        cv2.line(image, (int(xyxy[0][0]), int(xyxy[0][1])), (int(xyxy[0][2]),int(xyxy[0][3])), color, 2)
 

def roi(image,vertices):
    color = 255

    mask = np.zeros_like(image) # empty array of zeros (empty pixels) in same shape as frame
    cv2.fillPoly(mask, [vertices["road_vertices"]], color) # create polygon shape (mask)
    masked_road = cv2.bitwise_and(image, mask) # show only area of original image that is mask shape

    mask = np.zeros_like(image)
    cv2.fillPoly(mask, [vertices["l_mirror_vertices"]], color)
    masked_L_mirror = cv2.bitwise_and(image, mask)

    mask = np.zeros_like(image)
    cv2.fillPoly(mask, vertices["r_mirror_vertices"], color)
    masked_R_mirror = cv2.bitwise_and(image, mask)
    
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, [vertices["road_vertices"]], color)
    cv2.fillPoly(mask, [vertices["l_mirror_vertices"]], color)
    cv2.fillPoly(mask, vertices["r_mirror_vertices"], color)
    total_masks = cv2.bitwise_and(image, mask)

    return masked_road, masked_L_mirror, masked_R_mirror, total_masks

def process_frame(frame):
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    lsd = cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD)       
                                                            #need to pass in grayscale
    masked_road, masked_l_mirror, masked_r_mirror, total_masks = roi(gray, vertices)

    cv2.imwrite("masked_road.jpg", masked_road)


    road_lines = lsd.detect(masked_road)[0]
    print(len(road_lines))
    # l_mirror_lines = lsd.detect(masked_l_mirror)[0]
    # r_mirror_lines = lsd.detect(masked_r_mirror)[0]
    #total_lines = lsd.detect(total_masks,)[0]

    
    

    
    

    # yes I am aware of lsd.drawSegments()
    # this is just a more customizeable way to draw the lines
    #draw_lines(frame, color=[255,0,0], LSD=total_lines)
    lsd.drawSegments(frame, road_lines)
    return frame

path = 'pics/cabin1.png'
frame = cv2.imread(path)

screen_with_lines = process_frame(frame)
cv2.imwrite("pics/testing/output.jpg", screen_with_lines)
