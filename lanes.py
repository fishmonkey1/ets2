from numpy import ones,vstack
from numpy.linalg import lstsq
from statistics import mean

import traceback

import pprint
pp = pprint.PrettyPrinter(depth=6)


#    This file should take the lines found, and find which are most likely lanes.

#    Things have changed as to how we are finding and serving lines,
#    so most of the logic here needs a re-write.

#    Instead of focusing on returning two lane lines as we were originally,
#    I want to be focus on returning GOOD lines, even if there are more than two.


def find_matching_lines(line_dict):
    '''
    Goes over dict of found lines,
    For each line, looks at other lines and sees if matching slope within 20% variance.
    Creates 'final lanes' dict, 
    where Key is a slope, and Value is all lines that match for that slope

    TODO: compare values against same dict
          https://stackoverflow.com/questions/14345397/compare-a-dictionary-to-itself-in-python

          Creating a new dict for comparisons is slow and inefficient.
    '''

    final_lanes = {'pos': {},
                    'neg': {}}
    for pos_neg in line_dict.keys():
        for idx in line_dict[pos_neg]:
            final_lanes_copy = final_lanes.copy()
            
            m = line_dict[pos_neg][idx][0]
            b = line_dict[pos_neg][idx][1]
            line = line_dict[pos_neg][idx][2] # remember this is a list of xyxy coords
            
            # add initial value to empty dict
            if len(final_lanes) == 0:
                final_lanes[pos_neg][m] = [ [m,b,line] ]
                
            else:
                found_copy = False

                for other_ms in final_lanes_copy[pos_neg]:

                    if not found_copy:
                        if abs(other_ms*1.2) > abs(m) > abs(other_ms*0.8):
                            if abs(final_lanes_copy[pos_neg][other_ms][0][1]*1.2) > abs(b) > abs(final_lanes_copy[pos_neg][other_ms][0][1]*0.8):
                                final_lanes[pos_neg][other_ms].append([m,b,line])
                                found_copy = True
                                break
                        else:
                            final_lanes[pos_neg][m] = [ [m,b,line] ]

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

def driving_lanes(final_lanes):

    '''
    Takes final lanes and gets two slopes with the most lines
    TODO: get best pos and neg slope, not just any slopes
    '''
    
    lanes = []

    line_counter = {}
    for pos_neg in final_lanes.keys():
        temp = []
        for lanes in final_lanes[pos_neg]:
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
        if len(top_lanes) != 0:
            lane1_id = top_lanes[0][0]  # 1st best line
            temp.append(lane1_id)
        if len(top_lanes) > 1:
            lane2_id = top_lanes[1][0]  # 2nd best line
            temp.append(lane2_id)

        lanes.append(temp)    

    return lanes

#def lanes(lines):
    # TODO: if no line, don't run function 
    # if this fails, no line found
    #try:
        
        # Dict with slope/bias info for all lines
        #line_dict, disqualified = get_slopes(lines)
        #print(f"disqualified: {disqualified}")
        #print(f"number of pos lines: {len(line_dict['pos'])}")
        # if len(line_dict['neg']) > 0:
        #     print(f"number of neg lines: {len(line_dict['neg'])}")

        # Dict with possible lines narrowed down
        # based on matching slopes
        #final_lanes = find_matching_lines(line_dict)
        #print(f"number of good pos lanes: {len(final_lanes['pos'])}")
        #print(f"number of good neg lanes: {len(final_lanes['neg'])}")
        
        # [ [lane1_id, lane2_id], [lane1_id, lane2_id] ]

        #id_list = driving_lanes(final_lanes)
        #print(id_list)

        # lane1_id = driving_lanes(final_lanes)
        # print(f"lane1_id: {lane1_id}")
        # lane2_id = driving_lanes(neg_final_lanes)
        # print(f"lane2_id: {lane2_id}")
        
        # l1_x1, l1_y1, l1_x2, l1_y2 = final_average_lanes(pos_final_lanes[lane1_id])
        # l2_x1, l2_y1, l2_x2, l2_y2 = final_average_lanes(neg_final_lanes[lane2_id])


        # return [l1_x1, l1_y1, l1_x2, l1_y2], [l2_x1, l2_y1, l2_x2, l2_y2]
    #except Exception as e:
        #traceback.print_exc()
        #print(str(e), "No lanes found this frame")
        #pass
