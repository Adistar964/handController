

import cv2, numpy as np, math, mediapipe as mp, pyautogui

video = cv2.VideoCapture(0) # 0 means accessng first webcam

hand_object = mp.solutions.hands.Hands(max_num_hands=1) # this will be used to detect our hand!

# Now for controlling volume, we will use pycaw
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
vol = interface.QueryInterface(IAudioEndpointVolume)
volume_range = vol.GetVolumeRange()
min_volume = volume_range[0]
max_volume = volume_range[1]

while True:
    status, image = video.read()
    image = cv2.flip(image, 1) # flipping it horizontally as my webcam by default mirrors my video

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # as we need rgb image to process with mediapipe
    processed_object = hand_object.process(rgb_image) # this will process our video and give out cordinates for our detected hands

    if processed_object.multi_hand_landmarks != None: # if it successfully detected our hand
        handLandmarks = processed_object.multi_hand_landmarks[0] # getting landmarks of the first hand detected (our model only detects one hand!)
        mp.solutions.drawing_utils.draw_landmarks( image, handLandmarks, mp.solutions.hands.HAND_CONNECTIONS ) # this will enable us to draw the landmarks of the detected hands with connecting lines

        landmarks = [] # we will have all cordinates/landmarks of the points here
        for pointNumber, landmark in enumerate(handLandmarks.landmark): # for accessing the detected landmarks/cordinates manually so that we could highlight some of these with our needs 
            image_height, image_width, _ = image.shape # to get image dimensions
            x = int(image_width*landmark.x) # our landmark.x is not in pixels form, so we convert it to pixels form
            y = int(image_height*landmark.y) # same here
            landmarks.append( (x,y) )

        # Now we will do the programming for our handController
        # we first define various variables each defining a certain condition
        middle_finger_opened = landmarks[12][1] < landmarks[10][1]
        middle_finger_closed = not middle_finger_opened
        thumb_finger_closed = landmarks[4][0] > landmarks[5][0]
        thumb_finger_opened = not thumb_finger_closed
        ring_finger_closed = landmarks[16][1] > landmarks[14][1]
        ring_finger_opened = not ring_finger_closed
        pinky_finger_closed = landmarks[20][1] > landmarks[18][1]
        pinky_finger_opened = not pinky_finger_closed
        index_finger_opened = landmarks[8][1] < landmarks[6][1]

        if (index_finger_opened and middle_finger_closed and ring_finger_closed and pinky_finger_closed and thumb_finger_closed):
            cv2.circle(image, landmarks[8], 9, (0,255,255), cv2.FILLED)
            landmark_x,landmark_y = landmarks[8][0], landmarks[8][1]
            image_height, image_width, _ = image.shape # to get image dimensions
            screen_width, screen_height = pyautogui.size()
            x = np.interp(landmark_x, [0,image_width-200], [0,screen_width])
            y = np.interp(landmark_y, [0,image_height-200], [0,screen_height])
            pyautogui.moveTo(x,y)
        elif (index_finger_opened and middle_finger_opened and ring_finger_closed and pinky_finger_closed and thumb_finger_closed):
            # we will make sure that we do the operations if these fingers are close enough
            x1, y1 = landmarks[8]
            x2, y2 = landmarks[12]
            distance = math.pow( math.pow((x1-x2) , 2)+math.pow((y1-y2) , 2) , 0.5 ) # we use the distance formula
            if distance <= 30: # if the fingers are almost touching or actually touching
                cv2.circle(image, landmarks[8], 9, (0,128,255), cv2.FILLED)
                cv2.circle(image, landmarks[12], 9, (0,128,255), cv2.FILLED)
                pyautogui.leftClick()
        elif (index_finger_opened and middle_finger_closed and ring_finger_closed and pinky_finger_closed and thumb_finger_opened):
            # we will make sure that we do the operations if these fingers are close enough
            x1, y1 = landmarks[8]
            x2, y2 = landmarks[4]
            distance = math.pow( math.pow((x1-x2) , 2)+math.pow((y1-y2) , 2) , 0.5 ) # we use the distance formula
            if distance <= 30: # if the fingers are almost touching or actually touching
                cv2.circle(image, landmarks[8], 9, (255,102,102), cv2.FILLED)
                cv2.circle(image, landmarks[4], 9, (255,102,102), cv2.FILLED)
                pyautogui.rightClick()
        elif (index_finger_opened and middle_finger_opened and ring_finger_opened and pinky_finger_opened and thumb_finger_opened):
            # we will make sure that we do the operations if these fingers are close enough
            x1, y1 = landmarks[8]
            x2, y2 = landmarks[4]
            distance = math.pow( math.pow((x1-x2) , 2)+math.pow((y1-y2) , 2) , 0.5 ) # we use the distance formula
            cv2.line(image, (x1,y1), (x2,y2), (102,0,204), 4)
            cv2.circle(image, (x1,y1), 8, (102,0,204), cv2.FILLED)
            cv2.circle(image, (x2,y2), 8, (102,0,204), cv2.FILLED)
            # now we will get the volume from this distance
            volumeBetweenFingers = np.interp(distance, (30,300), (min_volume,max_volume)) # our thumb and index can go upto 30 to 300 distance in puxels
            vol.SetMasterVolumeLevel(volumeBetweenFingers, None)

    cv2.imshow("Hand Controller",image) # for displaying the video with window-title "Hand Controller"

    if cv2.waitKey(1) == ord('w'): # press "w" key to exit the program!
        break

cv2.destroyAllWindows() # to make sure that the the program is completely closed!