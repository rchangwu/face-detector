import numpy as np
import cv2
import sys
from scipy.spatial import distance
import dlib
import io
import base64
from PIL import Image
import re
from urlparse import unquote
from models import *

class SessionManager:
    def __init__(self):
        self.sessions = {}

    def check_exists(self, clientId):
        return clientId in self.sessions

    def create_session(self, clientId):
        self.sessions[clientId] = Session(clientId)

    def check_locked(self, clientId):
        return self.sessions[clientId].locked

    def lock_session(self, clientId):
        self.sessions[clientId].locked = True

    def unlock_session(self, clientId):
        self.sessions[clientId].locked = False

    def get_session(self, clientId):
        return self.sessions[clientId]

class JsonDeserializer:
    def get_clientid(self, json):
        return json['clientId'].encode('ascii','ignore')

    def get_subjectid(self, json):
        return json['subject'].encode('ascii','ignore')

    def get_nparray_image(self, json):
        res = re.search(r'base64,(.*)', unquote(json['dataUrl']))
        if (res == None):
            return None
        imgstr = res.group(1)
        image_bytes = io.BytesIO(base64.b64decode(imgstr))
        im = Image.open(image_bytes)
        return np.array(im)

class PersonSerializer:

    def serialize(self, person):
        return {
            "boundingBox": {
                "left": person.boundingBox.left,
                "top": person.boundingBox.top,
                "right": person.boundingBox.right,
                "bottom": person.boundingBox.bottom
            },
            "name": person.name,
            "image": self.convertToDataUrl(person.image)
        }

    def convertToDataUrl(self, arr):
        DATA_URL_PREFIX = "data:image/jpeg;base64,"
        pil_img = Image.fromarray(arr)
        buff = io.BytesIO()
        pil_img.save(buff, format="JPEG")
        base64EncodedImage = base64.b64encode(buff.getvalue()).decode("utf-8")
        return DATA_URL_PREFIX + base64EncodedImage



class FaceDetectorService:
    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()
        self.sp = dlib.shape_predictor('shape_predictor_5_face_landmarks.dat')
        self.facerec = dlib.face_recognition_model_v1('dlib_face_recognition_resnet_model_v1.dat')

    def detect_people(self, frame, subjects, recognition_threshold):

        last_sub = 0
        for subject in subjects:
            curr_sub = int(subject[-2:])
            if curr_sub > last_sub:
                last_sub = curr_sub

        subject_number = last_sub

        img = frame
        dets = self.detector(img, 1)
        people = []
        for d in dets:

            if d.top() <= 0 or d.bottom() <= 0 or d.left() <= 0 or d.right() <= 0:
                continue

            shape = self.sp(img, d)

            face_descriptor = self.facerec.compute_face_descriptor(img, shape)

            subject_name = 'Unknown'
            face_image = img[d.top():d.bottom(), d.left():d.right()]
            try:
                face_image = cv2.resize(face_image, dsize=(64, 64))
            except:
                print d.top(), d.bottom(), d.left(), d.right()
                print face_image.shape

            if subjects == {}:
                subject_number += 1
                name = 'subject' + str(subject_number).zfill(2)
                subjects[name] = {'descriptor': face_descriptor, 'image': face_image}
                subject_name = name
            else:
                top_candidate = None
                shortest_dist = float('inf')
                for subject in subjects:
                    dist = distance.euclidean(face_descriptor, subjects[subject]['descriptor'])
                    if dist < recognition_threshold and dist < shortest_dist:
                        top_candidate = subject
                        shortest_dist = dist
                
                if top_candidate == None:
                    subject_number += 1
                    name = 'subject' + str(subject_number).zfill(2)
                    subjects[name] = {'descriptor': face_descriptor, 'image': face_image}
                    subject_name = name
                else:
                    subject_name = top_candidate

            boundingBox = BoundingBox(d.left(), d.top(), d.right(), d.bottom())
            person = Person(boundingBox, subject_name, face_image)
            people.append(person)
        
        return people