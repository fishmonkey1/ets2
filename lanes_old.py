from numpy import ones,vstack
from numpy.linalg import lstsq
from statistics import mean

import pprint
pp = pprint.PrettyPrinter(depth=6)

def lanes(lines):

    # if this fails, go with some default line
    try:

        # finds the maximum y value for a lane marker 
        # (since we cannot assume the horizon will always be at the same point.)

        ys = []  
        for group in lines:
            for xyxy in group:
                ys += [xyxy[1],xyxy[3]]
        min_y = min(ys)
        max_y = 760
        line_dict = {}


        '''
        Finds slope(m) and y-intercept(b)
        Creates dict of all lines... slope, y-intercept, [x,y,x2,y2]
        '''
        for idx,i in enumerate(lines):
            for xyxy in i:
                # These four lines:
                # modified from http://stackoverflow.com/questions/21565994/method-to-return-the-equation-of-a-straight-line-given-two-points
                # Used to calculate the definition of a line, given two sets of coords.
                x_coords = (xyxy[0],xyxy[2])
                y_coords = (xyxy[1],xyxy[3])
                A = vstack([x_coords,ones(len(x_coords))]).T
                m, b = lstsq(A, y_coords)[0]

                # Calculating our new, and improved, xs
                # in order to get longer lines?
                x1 = (min_y-b) / m
                x2 = (max_y-b) / m

                #this should get rid of horizontal lines
                if 0.25> m > -0.25:
                    continue

                #print (m)
                line_dict[idx] = [m,b,[xyxy[0], xyxy[1], xyxy[2], xyxy[3]]]
                

        '''
        Goes over improved dict
        for each line, looks at other lines and sees if matching slope within 20% variance
        creates 'final lanes' dict

        '''

        final_lanes = {}
        for idx in line_dict:
            final_lanes_copy = final_lanes.copy()
            m = line_dict[idx][0]
            b = line_dict[idx][1]
            line = line_dict[idx][2] # remember this is a list of xyxy coords
            
            # add initial value to empty dict
            if len(final_lanes) == 0:
                final_lanes[m] = [ [m,b,line] ]
                
            else:
                found_copy = False

                for other_ms in final_lanes_copy:

                    if not found_copy:
                        if abs(other_ms*1.2) > abs(m) > abs(other_ms*0.8):
                            if abs(final_lanes_copy[other_ms][0][1]*1.2) > abs(b) > abs(final_lanes_copy[other_ms][0][1]*0.8):
                                final_lanes[other_ms].append([m,b,line])
                                found_copy = True
                                break
                        else:
                            final_lanes[m] = [ [m,b,line] ]

        pp.pprint(final_lanes)
        print(" ")

        line_counter = {}

        for lanes in final_lanes:
            line_counter[lanes] = len(final_lanes[lanes])

        

        top_lanes = sorted(line_counter.items(), key=lambda item: item[1])[::-1][:2]

        print(top_lanes)

        lane1_id = top_lanes[0][0]
        lane2_id = top_lanes[1][0]

        def average_lane(lane_data):
            x1s = []
            y1s = []
            x2s = []
            y2s = []
            for data in lane_data:
                x1s.append(data[2][0])
                y1s.append(data[2][1])
                x2s.append(data[2][2])
                y2s.append(data[2][3])
            return int(mean(x1s)), int(mean(y1s)), int(mean(x2s)), int(mean(y2s)) 

        l1_x1, l1_y1, l1_x2, l1_y2 = average_lane(final_lanes[lane1_id])
        l2_x1, l2_y1, l2_x2, l2_y2 = average_lane(final_lanes[lane2_id])

        return [l1_x1, l1_y1, l1_x2, l1_y2], [l2_x1, l2_y1, l2_x2, l2_y2]
    except Exception as e:
        print(str(e), "No lanes found")
