#Copyright (c) 2022, Rüdiger Lück
#All rights reserved.
 

# ++ Import Modules ++

import cv2 # module for computer vision
import os # module for accessing operating system
from PIL import Image # module for image processing
from fpdf import FPDF # module for creating pdf files
from guizero import App, PushButton, Text, TextBox, Box # Python GUI


# ++ Functions ++

def B1_pressed():
    global file_name
    if file_name:
        message_B1.value = 'File selected.'
    else:
        message_B1.value = 'No file selected.'

def B2_pressed():
    global vidSuccess
    if vidSuccess == True:
        message_B2.value = 'Video converted successfully.'
    else:
        message_B2.value = 'Video not converted.'

def B3_pressed():
    message_B3.value = 'PDF created successfully.'

def getFile():
    global file_name
    file_returned = app.select_file(filetypes=[['Video', '*.mp4'], ['All files', '*.*']])
    file_name = file_returned
    B1_pressed()
    return file_name

def getFrame():
    
    global img_folder, vidSuccess
    
    # defining local variable
    count = 1
    
    # reading variables from TextBox
    time = float(time_val.value) # time shift
    frameRate = float(frameR_val.value) # capture image each n-th minutes
    comp = float(comp_val.value)
    
    # creating a folder named Images    
    vid_path = os.path.dirname(file_name)
    img_folder = os.path.join(vid_path, 'Images').replace("\\","/")

    try: 
        if not os.path.exists(img_folder): 
            os.makedirs(img_folder) 
    # if not created then raise error 
    except OSError: 
        print ('Error: Creating Image directory')
    
    # read the video
    try:    
        vidcap = cv2.VideoCapture(file_name)
        if (vidcap.isOpened() == False):
            print('Error opening the video file.')
        else:
            print('Video loaded sucessfully')
            hasFrames,image = vidcap.read()
            while hasFrames:
                vidcap.set(cv2.CAP_PROP_POS_MSEC,time*1000*60)
                hasFrames,image = vidcap.read()
                
                # add time stamp to each image
                font = cv2.FONT_HERSHEY_SIMPLEX # choose font
                if time >= 0:
                    tstamp = 'Time elapsed: ' + str(time-float(time_val.value)) + ' min'
                else:
                    tstamp = 'Time elapsed: ' + '[ ]' + ' min'
                image = cv2.putText(image, tstamp, (50, 60), font, 2, (10, 255, 10), 5, cv2.LINE_8)
                
                cv2.imwrite(img_folder+'./image'+str(count)+".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), int(comp*100)]) # save frames in folder 'Images' as JPG file
                print('Creating Image... ' + str(count))
                count = count + 1
                time = time + 1/frameRate
                time = round(time,2)
            
    except:
        if (vidcap.isOpened() == False):
            vidSuccess = False
        else:
            vidSuccess = True
        B2_pressed()
        return vidSuccess
    return img_folder

def createPDF():
    
    global img_folder
    
    # reading variables from TextBox
    zoomfactor = float(zoom_val.value) # zoom factor for pdf 
    
    pdf = FPDF()
    pdf.compress = True
    pdf_dir = img_folder
    list = os.listdir(pdf_dir) # list elements in directory
    number_images = len(list) # count number of elements
    print(str(number_images) + ' Image(s) founded.')
    
    w,h = 0,0 # initialize variables width, height
    basewidth = int(500 * zoomfactor) # basewidth in pixels
    #img = Image.open('somepic.jpg')
    #img = img.resize((basewidth,hsize), Image.ANTIALIAS)
    #img.save('somepic.jpg')
    
    for i in range(1, number_images+1):
        fname = pdf_dir + '/image%d.jpg' % i
        if os.path.exists(fname):
            if i == 1: # extract size of first image
                cover = Image.open(fname)
                w,h = cover.size
                wpercent = basewidth/w
                h_new = int(h * wpercent)
                pdf = FPDF(unit = "pt", format = [1.2*basewidth, 1.7*basewidth])
            image = fname         
            pdf.add_page()
            if w > h:
                pdf.image(image,0.1*basewidth,0.3*basewidth,basewidth,h_new) # convert image to PDF(image,x-pos,y-pos,x-format,y-format)
            else:
                pdf.image(image,0.1*basewidth,0.1*basewidth,0.75*basewidth,0.75*h_new)
        else:
            print("File not found: ", fname)
        print("Creating PDF %d" % i)
    
    # Create PDF Directory and File
    vid_path = os.path.dirname(file_name)
    pdf_folder = os.path.join(vid_path, 'PDF').replace("\\","/")
    try: 
        if not os.path.exists(pdf_folder): 
            os.makedirs(pdf_folder) 
    # if not created then raise error 
    except OSError: 
        print ('Error: Creating PDF directory')
    pdf_file = os.path.join(pdf_folder, 'PDF_convFile.pdf').replace("\\","/")
    pdf.output(pdf_file, 'F')
    B3_pressed()
    print('PDF document created successfully.')

def resetApp():
    
    # reset variables
    vidSuccess = False
    file_name = ''
    img_folder = ''
    
    # reset Text
    message_B1.value = ''
    message_B2.value = ''
    message_B3.value = ''
    
    # reset TextBox
    time_val.value = 0
    frameR_val.value = 1.0
    zoom_val.value = 1.0
    comp_val.value = 1.0
    
    # reset cv2
    cv2.destroyAllWindows()
      
    return vidSuccess, file_name, img_folder

# ++ Variables ++

#count = 1 # initial counter
vidSuccess = False
file_name = ''
img_folder = ''
pdf_dir = ''


# ++ App ++

app = App('LabVideoConverter', height=500, width=650)
intro = Text(app, text='This application is used for converting video files (*.mp4) to images (*.jpg) and/or documents (*.pdf). \n All rigths reserved by Rüdiger Lück.\n', size = 8, color = 'gray')

# manipulated variables
board = Box(app, layout='grid')

time_text = Text(board, size=10, text='Initial time: ', grid=[0,0])
time_val = TextBox(board, text='0', grid=[1,0])
time_unit = Text(board, size = 10, text='[min]', grid=[2,0])

frameR_text = Text(board, size=10, text='Frame rate: ', grid=[0,1])
frameR_val = TextBox(board, text='1.0', grid=[1,1])
frameR_unit = Text(board, size = 10, text='[fpm]', grid=[2,1])

zoom_text = Text(board, size=10, text='Zoom factor: ', grid=[0,2])
zoom_val = TextBox(board, text='1.0', grid=[1,2])
zoom_unit = Text(board, size = 10, text='[-]', grid=[2,2])

comp_text = Text(board, size=10, text='File Compression: ', grid=[0,3])
comp_val = TextBox(board, text='1.0', grid=[1,3])
comp_unit = Text(board, size = 10, text='[-]', grid=[2,3])


# Buttons
button0 = Text(app)

button1 = PushButton(app, text='Load Video from File', command=getFile) # search for .mp4 video
message_B1 = Text(app, size = 9, color='blue') # indicate selected video

button2 = PushButton(app, text='Convert Video to Images', command=getFrame) # extract .jpg images form video
message_B2 = Text(app, size = 9, color='blue') # incicate converted video

button3 = PushButton(app, text='Create PDF File', command=createPDF) # button for creating and saving .pdf file
message_B3 = Text(app, size = 9, color='blue') # incicate created .pdf file

button4 = PushButton(app, text='Reset App', command =resetApp) # button for resetting the app

# show app window
app.display()
