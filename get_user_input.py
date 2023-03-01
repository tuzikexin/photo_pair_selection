import PySimpleGUI as sg

# # Define the layout of the window
def user_select_folder():
    background_image = None
    # Define the PySimpleGUI layout
    layout = [[sg.Text('Select a directory:')],
              [sg.InputText('/Users/kexin/Desktop/t/fundamakeovers/'),
               sg.FolderBrowse()],
              [sg.Submit(), sg.Cancel()]]
    
    # Create the PySimpleGUI window
    window = sg.Window('Directory Selector', layout)
    
    # Loop until the user closes the window or clicks the Submit or Cancel button
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel':
            break
        elif event == 'Submit':
            background_image = values[0]
            print(f'Selected directory: {background_image}')
            break
    
    # Close the PySimpleGUI window
    window.close()
    return background_image


def user_do_pair(bg_png):
    # Create the image element with your background image
    image = sg.Image(filename=bg_png)
    # Get the size of the image

    # Define your layout, including the image element as the first element
    w_layout = [[image],
                
                [sg.Text("Enter the pair photo, negative number indicate that"
                         " paired photo as raw photo(save to train_a)"),
                 sg.InputText(),
                 sg.Button("Pair Submit")],
                
                [sg.Button("move to next one"),
                 sg.Button("Check folder"),
                 sg.Button("First Photo as")
                 ],

                [sg.Column(
                    [[sg.Button('Open all folders'),
                      sg.Button("To Other folder")]],
                    justification='left', element_justification='top')]
                ]

    # Create the window using your custom layout
    window = sg.Window("Input Box Example", w_layout, finalize=True)
    # Run the event loop to wait for user interaction
    select_nr = None
    continue_pair = True
    while True:
        user_event, value = window.read()
        if user_event == sg.WIN_CLOSED:
            # If the user closed the window, exit the event loop
            continue_pair = False
            break
        elif user_event == "Pair Submit":
            try:
                select_nr = int(value[1])
                if abs(select_nr) > 16:
                    sg.popup('Please enter a number small than 16.')
                else:
                    break
            except ValueError:
                sg.popup('Please enter a number small than 16.')
                
        elif user_event =='First Photo as':
            try:
                select_nr = int(value[1])
                if select_nr > 16 or select_nr < 1:
                    sg.popup('Please enter a number between 1 and 16.')
                else:
                    break
            except ValueError:
                sg.popup('Please enter a number between 1 and 16.')
        
        elif user_event == "Check folder":
            break
        elif user_event == "Open all folders":
            break
        elif user_event == "move to next one":
            break
        elif user_event == "To Other folder":
            break
    # Close the window when done
    window.close()
    return continue_pair, user_event, select_nr


def finish_windows():
    layout = [
        [sg.Text('NO MORE Folder !')],
        [sg.Button('Byebye')]
    ]
    
    window = sg.Window('My Window', layout)
    
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Byebye':
            break
    window.close()
