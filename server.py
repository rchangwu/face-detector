# Rafael Chang Wu

from flask import Flask, request, Response
from flask_socketio import SocketIO, emit
from models import *
from services import *

app = Flask(__name__)
socketio = SocketIO(app)

recognition_threshold = 0.6

person_serializer = PersonSerializer()
face_detector_service = FaceDetectorService()
json_deserializer = JsonDeserializer()
session_manager = SessionManager()


@app.route('/')
def index():
    return Response(open('./static/index.html').read(), mimetype="text/html")

@socketio.on('delete_subject')
def delete_subject(json):
    clientId = json_deserializer.get_clientid(json)
    session = session_manager.get_session(clientId)
    session.delete_subject(json_deserializer.get_subjectid(json))

@socketio.on('webcam_image')
def handle_webcam_image(json):

    clientId = json_deserializer.get_clientid(json)

    if not session_manager.check_exists(clientId):
        session_manager.create_session(clientId)
    elif session_manager.check_locked(clientId):
        return

    session_manager.lock_session(clientId)
    arr = json_deserializer.get_nparray_image(json)
    if arr is None:
        return

    session = session_manager.get_session(clientId)
    people = face_detector_service.detect_people(arr, session.learned_subjects, recognition_threshold)
    session_manager.unlock_session(clientId)
    emit('people', {'people': map(person_serializer.serialize, people)})


@socketio.on('custom_image')
def handle_custom_image(json):

    clientId = json_deserializer.get_clientid(json)

    if not session_manager.check_exists(clientId):
        session_manager.create_session(clientId)
    elif session_manager.check_locked(clientId):
        return

    session_manager.lock_session(clientId)
    arr = json_deserializer.get_nparray_image(json)
    if arr is None:
        return

    session = session_manager.get_session(clientId)
    people = face_detector_service.detect_people(arr, session.learned_subjects, recognition_threshold)
    session_manager.unlock_session(clientId)
    emit('people', {'people': map(person_serializer.serialize, people)})

if __name__ == '__main__':
    print "starting"

