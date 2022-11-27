import win32gui, win32con

def windowData(hwnd, extra):
    windowRect = win32gui.GetWindowRect(hwnd) #outer window bounds 
    window_x = windowRect[0]
    window_y = windowRect[1]
    window_w = windowRect[2] - window_x
    window_h = windowRect[3] - window_y
    print("Window %s:" % win32gui.GetWindowText(hwnd))
    print("\tLocation: (%d, %d)" % (window_x, window_y))
    print("\t    Size: (%d, %d)" % (window_w, window_h))

    clientRect = win32gui.GetClientRect(hwnd) #inner game bounds
    game_x = clientRect[0]
    game_y = clientRect[1]
    game_w = clientRect[2] - game_x
    game_h = clientRect[3] - game_y
    print("Client %s:" % win32gui.GetWindowText(hwnd))
    print("\tLocation: (%d, %d)" % (game_x, game_y))
    print("\t    Size: (%d, %d)" % (game_w, game_h))

    # Windows 10 has an invisible window padding on left/right/bottom of windows
    invisible_win10_padding = int((window_w-game_w) / 2)
    title_bar_height = window_h - invisible_win10_padding - game_h
    print("padding px: ", invisible_win10_padding, " and title ", title_bar_height)
    
    

    return window_w, window_h, invisible_win10_padding, title_bar_height
 


if __name__ == "__main__":
    # window ID of game 
    hwnd = win32gui.FindWindow(None, "Euro Truck Simulator 2",)

    if hwnd == 0:
        raise Exception("Could not find ETS2 window, please make sure it is launched.")

    else:
        print(f'ETS2 window found ({hwnd}), setting to upper-left corner')
        width, height, window_padding, title = windowData(hwnd, None)

        #COMMENT THIS OUT IF YOU DON'T WANT TO SEE TITLE BAR
        # Currently handling for having the title bar there, so don't touch this yet
        # TODO: handle for title bar not being there
        title = 0
        
        #                                                     X             Y
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0-window_padding, 0-title, width, height, 0)
