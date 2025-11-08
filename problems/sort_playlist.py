"""
we do have a playlist counter

artist A: times played
artist B: times played
        ...

we have to sort in in ascending order (from the smallest to biggest)
"""


class Playlist:
    def __init__(self) -> None:
        self.frequencies = [
            ["Neytral Milk Hotel", 94], ["Kishore Kumar", 141],
            ["Wilco", 111], ["Radiohead", 156],
            ["Beck", 88], ["The Black Keys", 35]
        ]
    
    def like(self, artist: str) -> None:
        for idx in range(len(self.frequencies)):
            name, _ = self.frequencies[idx]
            if name == artist:
                self.frequencies[idx][1] += 1

    def refresh(self):
        return self.__sort_asc()
    
    def __find_smallest(self, arr):
        smallest_val, smallest_idx = arr[0][1], 0
        for idx in range(len(arr)):
            if arr[idx][1] < smallest_val:
                smallest_val, smallest_idx = arr[idx][1], idx
        return smallest_idx

    def __sort_asc(self):
        sorted = []
        for _ in range(len(self.frequencies)):
            smallest = self.__find_smallest(self.frequencies)
            sorted.append(self.frequencies.pop(smallest))
        self.frequencies = sorted
        return self.frequencies



playlist = Playlist()
print(playlist.refresh())
[playlist.like(artist="Beck") for _ in range(10)]
[playlist.like(artist="Radiohead") for _ in range(100)]

print(playlist.refresh())
[playlist.like(artist="Neytral Milk Hotel") for _ in range(45)]

print(playlist.refresh())
[playlist.like(artist="The Black Keys") for _ in range(100821)]
print(playlist.refresh())


