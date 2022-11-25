import win32gui, win32con

def windowData(hwnd, extra):
    windowRect = win32gui.GetWindowRect(hwnd) #outer window bounds 
    win_x = windowRect[0]
    win_y = windowRect[1]
    win_w = windowRect[2] - win_x
    win_h = windowRect[3] - win_y
    print("Window %s:" % win32gui.GetWindowText(hwnd))
    print("\tLocation: (%d, %d)" % (win_x, win_y))
    print("\t    Size: (%d, %d)" % (win_w, win_h))

    clientRect = win32gui.GetClientRect(hwnd) #inner game bounds
    client_x = clientRect[0]
    client_y = clientRect[1]
    client_w = clientRect[2] - client_x
    client_h = clientRect[3] - client_y
    print("Client %s:" % win32gui.GetWindowText(hwnd))
    print("\tLocation: (%d, %d)" % (client_x, client_y))
    print("\t    Size: (%d, %d)" % (client_w, client_h))

    invisible_win10_padding = int((win_w-client_w) / 2)
    title = win_h - invisible_win10_padding - client_h
    print("padding px: ", invisible_win10_padding, " and title ", title)
    
    #COMMENT THIS OUT IF YOU DON'T WANT TO SEE TITLE BAR!!!
    title = 0

    return win_w, win_h, invisible_win10_padding, title
 
hwnd = win32gui.FindWindow(None, "Euro Truck Simulator 2",)

if __name__ == "__main__":
    if hwnd == 0:
        raise Exception("Could not find ETS2 window, please make sure it is launched.")

    else:
        print(f'ETS2 window found ({hwnd}), setting to upper-left corner')
        width, height, window_padding, title = windowData(hwnd, None)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0-window_padding, 0-title, width, height, 0)
