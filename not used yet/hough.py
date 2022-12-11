#Goes into baddriving.process_frame()

# if detectionType == 'Hough':
#         canny = cv2.Canny(gray, threshold1=200, threshold2=300) #200/300
#         canny_blurred = cv2.GaussianBlur(canny, (5,5), 0)

#         #this draws mask poly on pic
#         draw_vertices(frame,vertices)

#         masked_road, masked_l_mirror, masked_r_mirror, total_masks = crop(canny_blurred, vertices)
        
#         # this saves an image on exit
#         #cv2.imwrite("pics/testing/total_masks.jpg", total_masks)
        
#         road_lines = cv2.HoughLinesP(masked_road, cv2.HOUGH_PROBABILISTIC, 1*np.pi/180, 200, np.array([]), 40, 10)
#         l_mirror_lines = cv2.HoughLinesP(masked_l_mirror, cv2.HOUGH_PROBABILISTIC, 1*np.pi/180, 200, np.array([]), 2, 5)
#         r_mirror_lines = cv2.HoughLinesP(masked_r_mirror, cv2.HOUGH_PROBABILISTIC, 1*np.pi/180, 200, np.array([]), 2, 5)
    

#         all_slopes = []
#         if road_lines is not None:
#             road_slopes = get_slopes(road_lines, True)
#             all_slopes.append(road_slopes)
#         if l_mirror_lines is not None:
#             l_mirror_slopes = get_slopes(l_mirror_lines, True)
#             all_slopes.append(l_mirror_slopes)
#         if r_mirror_lines is not None:
#             r_mirror_slopes = get_slopes(r_mirror_lines, True)
#             all_slopes.append(r_mirror_slopes)


#         for slopes in all_slopes:
#             for pos_neg_horiz in slopes.keys():
                
#                 # Sets color of line for drawing
#                 if pos_neg_horiz == 'pos':
#                     color = [255,0,0] # Green
#                 if pos_neg_horiz == 'neg':
#                     color = [0,255,0] # Blue
#                 if pos_neg_horiz == 'horizontal':
#                     color = [0,0,255] # Red

#                 # Draws lines on frame
#                 for idx in slopes[pos_neg_horiz]:
#                     draw_lines(frame, slopes[pos_neg_horiz][idx][2], color)