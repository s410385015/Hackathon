import os
import numpy as np
import cv2
import gestureCNN as myNN
from keras.models import load_model
from statistics import mode
from utils.datasets import get_labels
from utils.inference import detect_faces
from utils.inference import draw_text
from utils.inference import draw_bounding_box
from utils.inference import apply_offsets
from utils.inference import load_detection_model
from utils.preprocessor import preprocess_input

class Yolo:
    def __init__(self):
        path=os.path.split(os.path.realpath(__file__))[0]+'\\detector\\'
        with open('yolov2-tiny-voc.txt', 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]
       
        self.COLORS = np.random.uniform(0, 255, size=(len(self.classes), 3))
        self.net = cv2.dnn.readNet('yolov2-tiny-voc.weights', 'yolov2-tiny-voc.cfg')

    def get_output_layers(self,net):
        self.layer_names = self.net.getLayerNames()
        output_layers = [self.layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        return output_layers
    
    def draw_prediction(self,img, class_id, confidence, x, y, x_plus_w, y_plus_h):
        label = str(self.classes[class_id])
        color = self.COLORS[class_id]
        cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)
        cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    def get_prediction(self,image,Width,Height):
        scale = 0.00392
        blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.get_output_layers(self.net))

        class_ids = []
        confidences = []
        boxes = []
        conf_threshold = 0.5
        nms_threshold = 0.4
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0] * Width)
                    center_y = int(detection[1] * Height)
                    w = int(detection[2] * Width)
                    h = int(detection[3] * Height)
                    x = center_x - w / 2
                    y = center_y - h / 2
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])
        indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

        info=[]
        var=-1
        idx=0
        for i in indices:
            if str(self.classes[class_ids[i[0]]])=='person':
                i = i[0]
                box = boxes[i]
                if box[2]*box[3]>var:
                    idx=i
                    var=box[2]*box[3]
        
        
        if len(boxes)>0:
            box = boxes[idx]
            x = box[0]
            y = box[1]
            w = box[2]
            h = box[3]
            self.draw_prediction(image, class_ids[idx], confidences[idx], round(x), round(y), round(x+w), round(y+h))
            info=[x,y,w,h]
              
        return info
        

class Gesture:
    def __init__(self):
        self.mod=myNN.loadCNN(0)
        self.skinkernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
    def Guess(self,frame, x0, y0, width, height):
        low_range = np.array([0, 50, 80])
        upper_range = np.array([30, 200, 255])
        
        cv2.rectangle(frame, (x0,y0),(x0+width,y0+height),(0,255,0),1)
      
        roi = frame[y0:y0+height, x0:x0+width]
        
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
       
        mask = cv2.inRange(hsv, low_range, upper_range)
        
        mask = cv2.erode(mask, self.skinkernel, iterations = 1)
        mask = cv2.dilate(mask, self.skinkernel, iterations = 1)
        
       
        mask = cv2.GaussianBlur(mask, (15,15), 1)
        
       
        res = cv2.bitwise_and(roi, roi, mask = mask)

        res = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
        return myNN.guessGesture(self.mod,res)


class Emotion:
    def __init__(self):
        self.emotion_model_path = './models/emotion_model.hdf5'
        self.emotion_labels = get_labels('fer2013')
        self.frame_window = 10
        self.emotion_offsets = (20, 40)
        self.face_cascade = cv2.CascadeClassifier('./models/haarcascade_frontalface_default.xml')
        self.emotion_classifier = load_model(self.emotion_model_path)
        self.emotion_target_size = self.emotion_classifier.input_shape[1:3]

    def predict(self,image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        faces = self.face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5,minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
        emotion_window = []
        for face_coordinates in faces:
            x1, x2, y1, y2 = apply_offsets(face_coordinates, self.emotion_offsets)
            gray_face = gray_image[y1:y2, x1:x2]
            try:
                gray_face = cv2.resize(gray_face, (self.emotion_target_size))
            except:
                continue
                
            gray_face = preprocess_input(gray_face, True)
            gray_face = np.expand_dims(gray_face, 0)
            gray_face = np.expand_dims(gray_face, -1)
            emotion_prediction = self.emotion_classifier.predict(gray_face)
            emotion_probability = np.max(emotion_prediction)
            emotion_label_arg = np.argmax(emotion_prediction)
            emotion_text = self.emotion_labels[emotion_label_arg]

            

            return emotion_text,emotion_label_arg
        
        return  'null',6    
            


            
