import cv2

def faceBox(faceNet,frame):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (227,227),MODEL_MEAN_VALUES,swapRB=False, crop=False)
    faceNet.setInput(blob)
    detection=faceNet.forward()
    bboxs=[]
    for i in range(detection.shape[2]):
        confidence = detection[0, 0, i, 2]
        if confidence > 0.7:
            x1 = int(detection[0, 0, i, 3] * frameWidth)
            y1 = int(detection[0, 0, i, 4] * frameHeight)
            x2 = int(detection[0, 0, i, 5] * frameWidth)
            y2 = int(detection[0, 0, i, 6] * frameHeight)
            bboxs.append([x1, y1, x2, y2])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
    return frame, bboxs
    


faceProto="opencv_face_detector.pbtxt"
faceModel="opencv_face_detector_uint8.pb"

agePropto="age_deploy.prototxt"
ageModel="age_net.caffemodel"

genderPropto="gender_deploy.prototxt"
genderModel="gender_net.caffemodel"

faceNet=cv2.dnn.readNet(faceModel,faceProto)
ageNet=cv2.dnn.readNet(ageModel,agePropto)
genderNet=cv2.dnn.readNet(genderModel,genderPropto)


MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
ageList=["(0-2)", "(4-6)", "(8-12)", "(15-20)", "(25-32)", "(38-43)", "(48-53)", "(60-100)"]
genderList=['Male','Female']

video = cv2.VideoCapture(0, cv2.CAP_DSHOW) 
video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  
video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) 

padding = 20

if not video.isOpened():
    print("Error: Camera not accessible")
else:
    print("Camera initialized successfully")

while True:
    ret, frame = video.read()
    frame,bboxs=faceBox(faceNet,frame)
    if not ret:
        print("Failed to grab frame")
        break
    for bbox in bboxs:
        face=frame[bbox[1]:bbox[3], bbox[0]:bbox[2]]
        blob=cv2.dnn.blobFromImage(face,1.0,(227,227),MODEL_MEAN_VALUES,swapRB=False,crop=False)
        genderNet.setInput(blob)
        genderPred=genderNet.forward()
        gender=genderList[genderPred[0].argmax()]
        
        ageNet.setInput(blob)
        agePred=ageNet.forward()
        age=ageList[agePred[0].argmax()]
        
        label="{},{}".format(gender,age)
        cv2.rectangle(frame,(bbox[0],bbox[1]-30),(bbox[2],bbox[1]),(0,255,0),-1)
        cv2.putText(frame,label,(bbox[0],bbox[1]-10),cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,255),2,cv2.LINE_AA)

    cv2.imshow("Age-Gender", frame)
    k = cv2.waitKey(1)
    if k == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
