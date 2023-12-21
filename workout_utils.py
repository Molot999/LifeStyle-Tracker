class AvailableExercise:
    def __init__(self, id, title, muscle_group, additional_muscles, ex_type, ex_kind, equipment, difficulty_level, url, done_num, view_num) -> None:
        self.id = id
        self.title = title
        self.muscle_group = muscle_group
        self.additional_muscles = additional_muscles
        self.ex_type = ex_type
        self.ex_kind = ex_kind
        self.equipment = equipment
        self.difficulty_level = difficulty_level
        self.url = url
        self.done_num = done_num
        self.view_num = view_num
        self.similarity = 0
        self.popularity = 0

class Workout:
    def __init__(self, id, start_date, end_date, volume, intensity, duration_mins) -> None:
        self.number = None
        self.id = id
        self.start_date = start_date
        self.end_date = end_date
        self.volume = volume
        self.intensity = intensity
        self.duration_mins = duration_mins

class WorkoutExercise:
    def __init__(self, id, workout_id, exercise_id, start_date, end_date) -> None:
        self.id = id
        self.workout_id = workout_id
        self.exercise_id = exercise_id
        self.start_date = start_date
        self.end_date = end_date

class ExerciseSet:
    def __init__(self, id, exercise_table_id, start_date, end_date, rep_count, equipment_weight) -> None:
        self.id = id
        self.exercise_table_id = exercise_table_id
        self.start_date = start_date
        self.end_date = end_date
        self.rep_count = rep_count
        self.equipment_weight = equipment_weight