
class BoundingBox:
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

class Person:
    def __init__(self, boundingBox, name, image):
        self.boundingBox = boundingBox
        self.name = name
        self.image = image

class Session:
    def __init__(self, clientId):
        self.clientId = clientId
        self.learned_subjects = {}
        self.locked = False

    def delete_subject(self, subjectId):
        del self.learned_subjects[subjectId]