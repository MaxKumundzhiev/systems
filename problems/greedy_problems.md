# Жадные алгоритмы
Жадный алгоритм прост: на каждом шаге он выбирает оптимальный вариант.
Вся суть жадных алгоритмов сводится к:
    1. определить "что такое эффективно на каждом шаге" - дифиниция локального минимума
    2. использовать дифиниция локального минимума и отсортировать входные данные по этому принциу
    3. пройтись по отсортированным данным и собрать результат


## Задача на составления расписания и рюкзак
Допустим, имеется учебный класс, в котором нужно провести как можно больше уроков. Вы получаете список уроков.
Требуется провести в классе как можно больше уроков. Как отобрать уроки, чтобы полученный набор оказался самым большим из возможных?

```python
schedule = [
    ("drawing", [9:00, 10:00]),
    ("english", [9:30, 10:30]),
    ("math", [10:00, 11:00]),
    ("informatics", [10:30, 11:30]),
    ("music", [11:00, 12:00])
]

def create_optimal_schedule(schedule):
    # Сортируем расписание по концу занятий (это ключевой фактор для жадного алгоритма)
    sorted_schedule = sorted(schedule, key=lambda x: x[1][1])

    optimal_schedule = []   # Итоговое оптимальное расписание
    last_end_time = 0       # Время окончания последнего занятого урока

    for subject, times in sorted_schedule:
        start_time, end_time = times
        
        # Проверяем, начинается ли новый урок позже завершения предыдущего
        if start_time >= last_end_time:
            optimal_schedule.append((subject, list(times)))
            last_end_time = end_time
            
    return optimal_schedule


# find the lesson which ends earliest
# pick next lesson which ends earlist after first
# repeat ...

Жадный алгоритм прост: на каждом шаге он выбирает оптимальный вариант. В нашем примере при выборе
урока выбирается тот урок, который завершается раньше других. В техни-
ческой терминологии: на каждом шаге выбирается локально-оптимальное
решение, а в итоге вы получаете глобально-оптимальное решение. 


Очевидно, жадная стратегия не дает оптимального решения. Впрочем, ре-
зультат не так уж далек от оптимума. В следующей главе я расскажу, как вы-
числить правильное решение. Но вор, забравшийся в магазин, вряд ли станет
стремиться к идеалу. «Достаточно хорошего» решения должно хватить.
Второй пример приводит нас к следующему выводу: иногда идеальное —
враг хорошего. В некоторых случаях достаточно алгоритма, способного
решить задачу достаточно хорошо. И в таких областях жадные алгоритмы
работают просто отлично, потому что они просто реализуются, а получен-
ное решение обычно близко к оптимуму.
```


```python
Вы едете в Европу, и у вас есть семь дней на знакомство с достопри-
мечательностями. Вы присваиваете каждой достопримечательности
стоимость в баллах (насколько вы хотите ее увидеть) и оцениваете
продолжительность поездки. Как обеспечить максимальную стои-
мость (увидеть все самое важное) во время поездки? Предложите
жадную стратегию. Будет ли полученное решение оптимальным?

attractions = [
    {"name": "Эйфелева башня", "cost": 10, "duration": 3},   # Баллов важность / Часы
    {"name": "Колизей", "cost": 9, "duration": 2},
    {"name": "Дворец Версаля", "cost": 8, "duration": 4},
    {"name": "Пантеон", "cost": 7, "duration": 1},
    {"name": "Чеховский театр", "cost": 6, "duration": 2},
    {"name": "Замок Нойшванштайн", "cost": 5, "duration": 3},
    {"name": "Ватиканские музеи", "cost": 4, "duration": 3},
]

# Доступное время в днях (переводим в часы)
total_time_available = 7 * 24  # 7 дней × 24 часа/день

# Расчет отношения ценности ко времени
for attraction in attractions:
    attraction["efficiency"] = attraction["cost"] / attraction["duration"]

# Сортировка достопримечательностей по убыванию эффективности
sorted_attractions = sorted(attractions, key=lambda x: x["efficiency"], reverse=True)

# Планирование маршрута
itinerary = []
current_time_spent = 0

for attraction in sorted_attractions:
    if current_time_spent + attraction["duration"] <= total_time_available:
        itinerary.append(attraction)
        current_time_spent += attraction["duration"]
    else:
        break

print("План поездки:")
for item in itinerary:
    print(f"{item['name']} ({item['cost']} баллов, {item['duration']} часов)")
```



```python
Вы работаете в фирме по производству мебели и поставляете мебель
по всей стране. Коробки с мебелью размещаются в грузовике. Все
коробки имеют разный размер, и вы стараетесь наиболее эффективно
использовать доступное пространство. Как выбрать коробки для того,
чтобы загрузка имела максимальную эффективность? Предложите
жадную стратегию. Будет ли полученное решение оптимальным?


def greedy_loading(capacity_volume, capacity_weight, boxes):
    # Рассчитываем объем каждой коробки
    for box in boxes:
        volume = box["size"][0] * box["size"][1] * box["size"][2]
        box['volume'] = volume
    
    # Сортируем коробки по объему и массе (убывание)
    sorted_boxes = sorted(boxes, key=lambda x: (x['volume'], x['weight']), reverse=True)
    
    loaded_volume = 0
    loaded_weight = 0
    selected_boxes = []
    
    for box in sorted_boxes:
        new_volume = loaded_volume + box['volume']
        new_weight = loaded_weight + box['weight']
        
        # Проверяем ограничения груза
        if new_volume <= capacity_volume and new_weight <= capacity_weight:
            selected_boxes.append(box)
            loaded_volume += box['volume']
            loaded_weight += box['weight']
    
    return selected_boxes


# Тестовые данные
capacity_volume = 10_000  # Объем грузовика
capacity_weight = 5000    # Грузоподъемность грузовика
boxes = [
    {"size": [10, 20, 50], "weight": 10.0},  # маленькая коробка
    {"size": [10, 20, 100], "weight": 30.0}  # большая коробка
]

result = greedy_loading(capacity_volume, capacity_weight, boxes)
print("Загруженные коробки:", result)

```