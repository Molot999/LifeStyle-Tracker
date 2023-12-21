import matplotlib.pyplot as plt
from enum import Enum

class Graph_Type(Enum):
    volume = 'volume',
    intensity = 'intensity',
    duration = 'duration'

def get_graph(user_id, workout_count, graph_type:Graph_Type, vol_list=None) -> str:
    # Создание данных для графика
    x = list(range(1 ,workout_count+1))
    y = vol_list

    # Построение графика
    plt.plot(x, y)
    plt.xticks(x)

    plt.xlabel('Тренировки')

    if graph_type is Graph_Type.volume or graph_type is Graph_Type.intensity:
        y_label = 'Вес, кг'
    elif graph_type is Graph_Type.duration:
        y_label = 'Время, мин'
    plt.ylabel(y_label)

    if graph_type is Graph_Type.volume:
        title = 'Объем (тоннаж)'
    elif graph_type is Graph_Type.intensity:
        title = 'Интенсивность (средний вес)'
    elif graph_type is Graph_Type.duration:
        title = 'Длительность'
    plt.title(title)

    if graph_type is Graph_Type.volume:
        val = 'volume'
    elif graph_type is Graph_Type.intensity:
        val = 'intensity'
    elif graph_type is Graph_Type.duration:
        val = 'duration'

    file_name = f'{user_id}_{val}.jpg'
    plt.savefig(f'workout_stats/{file_name}')
    plt.close()

if __name__ == '__main__':
    x = [41040.0, 84921.25]
    y = [52.25, 75.15]     
    z =[72, 68]
    get_graph(1, 2, Graph_Type.volume, x)
    # import dbconnection as db
    # username = 'Molot369'
    # user_workouts:list = db.get_user_workouts(username)
    # user_id = db.get_user_id(username)
    # volume_list = [workout.volume for workout in user_workouts]
    # intensity_list = [workout.intensity for workout in user_workouts]
    # time_list = [workout.duration_mins for workout in user_workouts]
    # get_graph(user_id, len(user_workouts), Graph_Type.volume, weight_list=volume_list)
    # get_graph(user_id, len(user_workouts), Graph_Type.intensity, weight_list=intensity_list)
    # get_graph(user_id, len(user_workouts), Graph_Type.duration, time_list=time_list)