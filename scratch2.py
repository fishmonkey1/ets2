import numpy as np

import pprint
pp = pprint.PrettyPrinter(depth=6)

# vertices of parts of screen for individual line detection  
vertices = {"road_vertices":     np.array([[300,508], [340,508], [390,475], [460,445], [560,445], [630,475], [685,508], [840,508], [840,350], [300,350]], dtype=np.int32),
            "l_mirror_vertices": np.array([[18,285], [169,285], [169,362], [18,362]], dtype=np.int32),
            "r_mirror_vertices": np.array([[852,285], [1003,285], [1003,362], [852,362]], dtype=np.int32)}

slopes = []

pp.pprint(vertices['road_vertices'])
print()


def create_ROI_slopes(vertices):
        for ROI in vertices:
            roi_lines = []
            array = vertices[ROI]
            last_index = len(array) -1
            for index, xy in enumerate(array):
                if index != last_index:
                    #print(type(xy.copy()))
                    roi_lines.append([ xy[0].copy(), xy[1].copy() , array[index+1][0].copy(), array[index+1][1].copy() ])
                else:
                    #print(type(xy.copy()))
                    roi_lines.append([ xy[0].copy(), xy[1].copy() , array[0][0].copy(), array[0][1].copy() ])
            slopes.append(np.array(roi_lines, dtype=np.int32))     

create_ROI_slopes(vertices)

pp.pprint(slopes)