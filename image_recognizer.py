import cv2
import numpy as np

# Загрузка конфигурации и весов модели YOLOv3
net = cv2.dnn.readNet('ai_cfg/yolov3.cfg', 'ai_cfg/yolov3.weights')

# Загрузка названий классов, используемых в модели
classes = []
with open('ai_cfg/coco.names', 'r') as f:
    classes = [line.strip() for line in f.readlines()]

# Загрузка изображения
image = cv2.imread('img_to_recognize/5.jpg')
height, width = image.shape[:2]

# Препроцессинг изображения (масштабирование и нормализация)
blob = cv2.dnn.blobFromImage(image, scalefactor=1/255.0, size=(416, 416), swapRB=True, crop=False)

# Установка входного слоя для сети
net.setInput(blob)

# Получение идентификаторов финальных выходных слоев
out_layer_names = net.getUnconnectedOutLayersNames()

# Получение выходов сети
outs = net.forward(out_layer_names)

# Обработка выходов для обнаружения объектов
conf_threshold = 0.5  # Порог для уверенности обнаружения объекта
nms_threshold = 0.4   # Порог для подавления немаксимальных значений

class_ids = []
confidences = []
boxes = []

for out in outs:
    for detection in out:
        scores = detection[5:]
        class_id = np.argmax(scores)
        confidence = scores[class_id]

        if confidence > conf_threshold:
            center_x = int(detection[0] * width)
            center_y = int(detection[1] * height)
            w = int(detection[2] * width)
            h = int(detection[3] * height)

            x = int(center_x - w / 2)
            y = int(center_y - h / 2)

            class_ids.append(class_id)
            confidences.append(float(confidence))
            boxes.append([x, y, w, h])

# Применение немаксимального подавления для устранения дублированных обнаружений
indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

# Проверка содержимого списка indices
print(indices)

# Отображение результатов
for i in indices:
    i = i[0]  # Ошибка может возникнуть здесь, если indices не имеет ожидаемой структуры
    box = boxes[i]
    x, y, w, h = box
    class_id = class_ids[i]
    label = f'{classes[class_id]}: {confidences[i]:.2f}'
    color = (0, 255, 0)  # Зеленый цвет рамки
    cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
    cv2.putText(image, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

# Отображение и сохранение результата
cv2.imshow('Food Detection', image)
cv2.waitKey(0)
cv2.destroyAllWindows()