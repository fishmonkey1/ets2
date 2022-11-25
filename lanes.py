from numpy import ones,vstack
from numpy.linalg import lstsq
from statistics import mean

import traceback

import pprint
pp = pprint.PrettyPrinter(depth=6)

def lanes(lines):
    
    def get_slopes(lines):
        '''
        Finds slope(m) and y-intercept(b)
        Creates dict of all lines... slope, y-intercept, [x,y,x2,y2]
        Removes lines with horizontal slope
        '''

        line_dict = {}

        for idx,i in enumerate(lines):
            for xyxy in i:
                # These four lines:
                # modified from http://stackoverflow.com/questions/21565994/method-to-return-the-equation-of-a-straight-line-given-two-points
                # Used to calculate the definition of a line, given two sets of coords.
                x_coords = (xyxy[0],xyxy[2])
                y_coords = (xyxy[1],xyxy[3])
                A = vstack([x_coords,ones(len(x_coords))]).T
                m, b = lstsq(A, y_coords)[0]

                #This skips over horizontal lines
                if 0.25> m > -0.25:
                    continue

                line_dict[idx] = [m,b,[xyxy[0], xyxy[1], xyxy[2], xyxy[3]]]

        return line_dict   

    def find_matching_lines(line_dict):
        '''
        Goes over improved dict
        for each line, looks at other lines and sees if matching slope within 20% variance
        creates 'final lanes' dict where Key is a slope, and Value is
        all lines that match for that slope

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

        return final_lanes


    def final_average_lanes(lane_data):
            '''
            Of those two slopes:
            gets the average of the many lines that slope has
            
            Returns two lines
            '''
        
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




    # TODO: if no line, don't run function 
    # if this fails, no line found
    try:
        
        # Dict with slope/bias info for all lines
        line_dict = get_slopes(lines)

        # Dict with possible lines narrowed down
        # based on matching slopes
        final_lanes = find_matching_lines(line_dict)
        
        '''
        Takes final lanes and gets two slopes with the most lines
        TODO: get best pos and neg slope, not just any slopes
        '''
        line_counter = {}
        for lanes in final_lanes:
            line_counter[lanes] = len(final_lanes[lanes])

        # top_lanes = [slope, number of lines]
        # sort by "slope that has most lines"
        top_lanes = sorted(line_counter.items(), key=lambda item: item[1])[::-1][:2]

        '''
        TODO: `lane2_id` does not always exist because
              only one best line found...
              this throws exception because
              we are always looking for two lines...
              try/except catches, but find better solution...
        '''
        lane1_id = top_lanes[0][0]  # 1st best line
        lane2_id = top_lanes[1][0]  # 2nd best line

        
        l1_x1, l1_y1, l1_x2, l1_y2 = final_average_lanes(final_lanes[lane1_id])
        l2_x1, l2_y1, l2_x2, l2_y2 = final_average_lanes(final_lanes[lane2_id])

        return [l1_x1, l1_y1, l1_x2, l1_y2], [l2_x1, l2_y1, l2_x2, l2_y2]
    except Exception as e:
        #traceback.print_exc()
        #print(str(e), "No lanes found this frame")
        pass
