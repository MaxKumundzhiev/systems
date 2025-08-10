import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed


class LoadBalancer:
    def __init__(self):
        self.ring: dict[int, str] = {}          # {hashOfNode: address}
        self.sorted_hashes: list[int] = []      # [nodeAHash, nodeBHash, ...]
        self._lock = threading.RLock()          # protect shared state
    
    def _compile_hash(self, input: str) -> int:
        """Method, which compiles hash of input;"""
        if not isinstance(input, str):
            raise ValueError("input must be str")
        return int(hashlib.md5(input.encode("utf-8")).hexdigest(), 16)
    
    def _find_closest_node_on_ring(self, target: int) -> str:
        """Method, which looks up closest node for input; (predecessor)"""
        # Caller holds the lock and ensures ring is non-empty
        left, right = 0, len(self.sorted_hashes)
        while right - left > 1:
            middle = (left + right) // 2
            good = (self.sorted_hashes[middle] < target)
            if good:
                left = middle
            else:
                right = middle
        idx = left % len(self.sorted_hashes)   # wrap-around safe
        node_hash = self.sorted_hashes[idx]
        return self.ring[node_hash]
    
    def add(self, node: str):
        """Method, which adds new node to ring;"""
        if not isinstance(node, str):
            raise ValueError("node must be str")
        key: int = self._compile_hash(input=node)
        value: str = node
        if not isinstance(key, int):
            raise SystemError("hash must be int")
        with self._lock:
            if key in self.ring:               # collision guard
                raise KeyError("node hash collision")
            self.ring[key] = value
            self.sorted_hashes.append(key)
            self.sorted_hashes.sort()
    
    def remove(self, node: str):
        """Method, which removes node from ring;"""
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
        """Method, which gets node from ring;"""
        if not isinstance(user_id, str):
            raise ValueError("user_id must be str")
        key: int = self._compile_hash(input=user_id)
        if not isinstance(key, int):
            raise SystemError("hash must be int")
        with self._lock:
            if not self.sorted_hashes:
                return None
            return self._find_closest_node_on_ring(target=key)


# ---------------- Demo with ThreadPoolExecutor ----------------

if __name__ == "__main__":
    lb = LoadBalancer()
    lb.add(node="serverA")
    lb.add(node="serverB")
    lb.add(node="serverC")

    print("=== 3 servers (concurrent) ===")
    requests = ["max", "arseniy", "nino", "vika", "vasya", "mashs", "bill"]

    # Use a fixed-size pool to process requests concurrently
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

    # Scale test: 1000 requests
    print("\n=== scale test: 1000 requests ===")
    big = [f"user{i}" for i in range(1000)]
    with ThreadPoolExecutor(max_workers=200) as pool:
        assigned = list(pool.map(lb.get, big, chunksize=32))
    # Simple distribution check (optional)
    from collections import Counter
    print(Counter(assigned))
