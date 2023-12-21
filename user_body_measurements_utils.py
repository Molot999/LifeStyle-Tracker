class BodyMeasurements:
    def __init__(self, id, user_id, shoulders=None, forearms=None, biceps=None, chest=None, waist=None, thighs=None, calves=None, neck=None, datetime=None):
        self.number = None
        self.id = id
        self.user_id = user_id
        self.shoulders = shoulders
        self.forearms = forearms
        self.biceps = biceps
        self.chest = chest
        self.waist = waist
        self.thighs = thighs
        self.calves = calves
        self.neck = neck
        self.datetime = datetime