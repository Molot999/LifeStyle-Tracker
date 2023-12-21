from typing import List

class UserWeightDiaryEntry:
    def __init__(self, id, user_id, weight, datetime) -> None:
        self.number = None
        self.id = id
        self.user_id = user_id
        self.weight = weight
        self.datetime = datetime