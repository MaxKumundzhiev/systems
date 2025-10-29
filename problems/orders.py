class Order:
    def __init__(self, item: str, quantity: int) -> None:
        self.item = item
        self.quantity = quantity
        self.next = None
        self.prev = None


class OrdersQueue:
    def __init__(self) -> None:
        self.head = None
        self.tail = None
        self.size = 0
    
    # Добавление заказа в конец очереди
    def enqueue(self, order: Order) -> None:
        if not self.head:
            self.head = order
            self.tail = order
        else:
            # Связываем новый заказ с последним элементом списка
            old_tail = self.tail
            old_tail.next = order
            order.prev = old_tail
            self.tail = order
            
        self.size += 1
        return
    
    # Извлечение первого элемента очереди
    def dequeue(self):
        if not self.head:
            raise Exception("Очередь пуста")
        
        removed_order = self.head
        next_head = removed_order.next
        
        if next_head is not None:
            next_head.prev = None
        else:
            # Если очередь становится пустой, сбрасываем хвост тоже
            self.tail = None
        
        self.head = next_head
        self.size -= 1
        
        return removed_order
    
    def status(self) -> None:
        current = self.head
        while current:
            print(current.item)
            current = current.next
        return
    


queue = OrdersQueue()
queue.enqueue(order=Order(item="meat", quantity=1))
queue.enqueue(order=Order(item="fish", quantity=2))
queue.enqueue(order=Order(item="coffee", quantity=5))
queue.status()
queue.dequeue()
queue.status()