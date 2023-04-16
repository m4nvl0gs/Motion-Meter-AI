# Required Modules
import cv2, pyttsx3, pyaudio, smtplib, ssl
import pyfiglet as pyg
import speech_recognition as sr
from tracker import *
from moviepy.editor import VideoFileClip

#Welcome Display
res = pyg.figlet_format("Motion Meter AI", font = "slant")   
print(res)

#Constants
tracker = EuclideanDistTracker() # Used to differentiate between moving and static objects
port = 465 # Standard GMAIL Port
context = ssl.create_default_context()
name_video = str(input("Enter the filename of the video you would like to analyse: "))
cap = cv2.VideoCapture(name_video+".mp4") # filepath for the video clip to analyse

# Calculate duration of video to be analysed
clip = VideoFileClip(name_video+".mp4")
# Main Vehicle Detection 
object_detector = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=40)
try:
    # Loop till video ends (analysing frame by frame)
    while True: 
        ret, frame = cap.read()
        height, width, _ = frame.shape

        # Extract Region of interest
        roi = frame[340: 720,500: 800]

        mask = object_detector.apply(roi)
        _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        detections = []
        for cnt in contours:
            # Calculate area and remove unecessary elements
            area = cv2.contourArea(cnt)
            if area > 100:
                #cv2.drawContours(roi, [cnt], -1, (0, 255, 0), 2)
                x, y, w, h = cv2.boundingRect(cnt)
                detections.append([x, y, w, h])
        boxes_ids = tracker.update(detections)
        for box_id in boxes_ids:
            x, y, w, h, id = box_id
            cv2.putText(roi, str(id), (x, y - 15), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
            cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 3)

        cv2.imshow("roi", roi)
        cv2.imshow("Frame", frame)
        cv2.imshow("Mask", mask)

        key = cv2.waitKey(30)
        # Exit the program if the "ESC" key is pressed
        if key == 27: break
    
except AttributeError: # Marks the end of video clip
    num = boxes_ids[2][-1] # Retrieve number of vehicles
    engine = pyttsx3.init() # Initiate text to speech program
    engine.say("The program has finished, would you like me to send a copy of the results to your email address?")
    engine.runAndWait()

# Speech Recognition AI (ask user whether they want an email of the results)
r = sr.Recognizer()
with sr.Microphone() as source:
    audio_data = r.record(source, duration=5)
    text = r.recognize_google(audio_data)
    print(text)
    if "yes" in text.lower():
        email_id = input("Enter your email address: ")
        with smtplib.SMTP_SSL("smtp.gmail.com",port, context=context) as server:
            string = "The object tracking detection program successfully detected",num,"vehicles from the video clip",name_video
            duration_clip = clip.duration
            #server.login(email,password)
            #server.sendmail(from,to,string)
        print(f"The email has been sent to the email address {email_id}")
cap.release()
cv2.destroyAllWindows() # Close all windows
