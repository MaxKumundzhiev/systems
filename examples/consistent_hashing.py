import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import unittest

class LoadBalancer:
    def __init__(self):
        self.ring: dict[int, str] = {}
        self.sorted_hashes: list[int] = []
        self._lock = threading.RLock()
    
    def _compile_hash(self, input: str) -> int:
        if not isinstance(input, str):
            raise ValueError("input must be str")
        return int(hashlib.md5(input.encode("utf-8")).hexdigest(), 16)
    
    def _find_closest_node_on_ring(self, target: int) -> str:
        left, right = 0, len(self.sorted_hashes)
        while right - left > 1:
            middle = (left + right) // 2
            if self.sorted_hashes[middle] < target:
                left = middle
            else:
                right = middle
        idx = left % len(self.sorted_hashes)
        node_hash = self.sorted_hashes[idx]
        return self.ring[node_hash]
    
    def add(self, node: str):
        if not isinstance(node, str):
            raise ValueError("node must be str")
        key: int = self._compile_hash(input=node)
        value: str = node
        if not isinstance(key, int):
            raise SystemError("hash must be int")
        with self._lock:
            if key in self.ring:
                raise KeyError("node hash collision")
            self.ring[key] = value
            self.sorted_hashes.append(key)
            self.sorted_hashes.sort()
    
    def remove(self, node: str):
        if not isinstance(node, str):
            raise ValueError("node must be str")
        key: int = self._compile_hash(input=node)
        if not isinstance(key, int):
            raise SystemError("hash must be int")
        with self._lock:
            if key not in self.ring:
                raise KeyError("node not found")
            del self.ring[key]
            self.sorted_hashes.remove(key)

    def get(self, user_id: str):
        if not isinstance(user_id, str):
            raise ValueError("user_id must be str")
        key: int = self._compile_hash(input=user_id)
        if not isinstance(key, int):
            raise SystemError("hash must be int")
        with self._lock:
            if not self.sorted_hashes:
                return None
            return self._find_closest_node_on_ring(target=key)

# ---------------- unittest for LoadBalancer ----------------

class TestLoadBalancer(unittest.TestCase):
    def test_add_remove_and_get(self):
        """Тестирование базовых операций добавления, удаления и получения узлов."""
        lb = LoadBalancer()
        
        # Добавление узлов
        lb.add("serverA")
        lb.add("serverB")
        lb.add("serverC")
        self.assertEqual(len(lb.ring), 3)
        self.assertEqual(len(lb.sorted_hashes), 3)
        
        # Проверка получения узла для определенного ID
        node = lb.get("test_user_id")
        self.assertIn(node, ["serverA", "serverB", "serverC"])
        
        # Удаление узла
        lb.remove("serverB")
        self.assertEqual(len(lb.ring), 2)
        self.assertEqual(len(lb.sorted_hashes), 2)
        self.assertNotIn("serverB", lb.ring.values())

        # Повторная проверка получения узла после удаления
        node = lb.get("test_user_id")
        self.assertIn(node, ["serverA", "serverC"])
        
        # Тестирование пустой коллекции
        lb.remove("serverA")
        lb.remove("serverC")
        self.assertIsNone(lb.get("test_user_id"))
        self.assertEqual(len(lb.ring), 0)

    def test_concurrency_safety(self):
        """Тестирование потокобезопасности класса при одновременном доступе."""
        lb = LoadBalancer()
        for i in range(10):
            lb.add(f"server_{i}")
        
        num_requests = 1000
        user_ids = [f"user_{i}" for i in range(num_requests)]
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(lb.get, uid) for uid in user_ids]
            
            # Ждем завершения всех задач
            results = [f.result() for f in futures]
            
        # Проверяем, что все запросы были обработаны и возвращены корректные узлы
        self.assertEqual(len(results), num_requests)
        for result in results:
            self.assertIn(result, lb.ring.values())

    def test_edge_cases(self):
        """Тестирование граничных случаев, таких как пустой балансировщик и коллизии."""
        lb = LoadBalancer()
        
        # Тест на пустой балансировщик
        self.assertIsNone(lb.get("some_user"))
        
        # Тест на коллизию хешей (сгенерируем искусственно)
        # Добавим узел, хеш которого совпадает с уже существующим
        with self.assertRaises(KeyError):
            lb.add("node1")
            lb.add("node1")
        
        # Тест на попытку удаления несуществующего узла
        with self.assertRaises(KeyError):
            lb.remove("nonexistent_node")

    def test_thread_safe_modification(self):
        """Тестирование безопасного добавления/удаления узлов из разных потоков."""
        lb = LoadBalancer()
        
        def add_node(name):
            lb.add(name)

        def remove_node(name):
            try:
                lb.remove(name)
            except KeyError:
                pass # Ожидаем, что узел может быть уже удален
                
        def get_node(user):
            lb.get(user)

        with ThreadPoolExecutor(max_workers=20) as executor:
            add_futures = [executor.submit(add_node, f"node_{i}") for i in range(10)]
            get_futures = [executor.submit(get_node, f"user_{i}") for i in range(200)]
            remove_futures = [executor.submit(remove_node, f"node_{i}") for i in range(5)]
            
            # Ждем завершения всех задач
            for fut in add_futures + get_futures + remove_futures:
                fut.result()
        
        # Убедимся, что после всех операций, состояние балансировщика корректно
        self.assertGreater(len(lb.ring), 0)
        self.assertGreater(len(lb.sorted_hashes), 0)

# ---------------- Demo with ThreadPoolExecutor ----------------
# (оставлен без изменений, чтобы показать, как можно запускать тесты)

if __name__ == "__main__":
    print("--- Running tests ---")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    print("\n--- Demo with ThreadPoolExecutor ---")
    
    lb = LoadBalancer()
    lb.add(node="serverA")
    lb.add(node="serverB")
    lb.add(node="serverC")

    print("=== 3 servers (concurrent) ===")
    requests = ["max", "arseniy", "nino", "vika", "vasya", "mashs", "bill"]

    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = {pool.submit(lb.get, uid): uid for uid in requests}
        for fut in as_completed(futs):
            uid = futs[fut]
            node = fut.result()
            print(f"for userID {uid} request forwarded to {node}")

    print("\n=== 2 servers (concurrent) ===")
    lb.remove(node="serverB")
    with ThreadPoolExecutor(max_workers=8) as pool:
        for uid, node in zip(requests, pool.map(lb.get, requests)):
            print(f"for userID {uid} request forwarded to {node}")

    print("\n=== scale test: 1000 requests ===")
    big = [f"user{i}" for i in range(1000)]
    with ThreadPoolExecutor(max_workers=200) as pool:
        assigned = list(pool.map(lb.get, big, chunksize=32))
    from collections import Counter
    print(Counter(assigned))