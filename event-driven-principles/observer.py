"""
Паттерн Observer
--> В event-driven архитектуре этот паттерн используется для регистрации и обработки событий. <--

Паттерн Observer используется для оповещения об изменениях в объекте других объектов, которые на него подписаны.

В данном примере у нас есть класс Sensor, который может генерировать данные (например, температуру).
У этого класса есть список observers – объектов, которые должны быть оповещены об изменениях данных. 
Когда вызывается метод notify_observers, все объекты из списка observers получают уведомление об изменениях. 
Классы AlertSystem и DataRecorder являются примерами таких объектов.
"""


class Sensor:
    def __init__(self) -> None:
        self.observers = []
    
    def register(self, observer):
        self.observers.append(observer)
    
    def notify(self, data):
        for observer in self.observers:
            observer.update(data)


class AlertSystem:
    def update(self, data):
        if data > 100:
            print(f"Alert! tempreture > {data}")


class RecordingSystem:
    def __init__(self) -> None:
        self.storage = []

    def update(self, data):
        self.storage.append(data)
        print("New record occurred")


sensor = Sensor()
alert_sys = AlertSystem()
recording_sys = RecordingSystem()

sensor.register(alert_sys)
sensor.register(recording_sys)

sensor.notify(data=100)
sensor.notify(data=150)
sensor.notify(data=80)



"""
Паттерн Command
--> В event-driven архитектуре этот паттерн используется для обработки событий. <--

Паттерн Command используется для инкапсуляции запроса как объект и передачи его другим объектам, которые могут его обработать.
"""