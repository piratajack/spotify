# linked_lists.py
class Node:
    def __init__(self, song):
        self.song = song
        self.next = None
        self.prev = None

class SimpleLinkedList:
    def __init__(self):
        self.head = None
        self.current = None
        self.size = 0

    def add_item(self, song):
        new_node = Node(song)
        if not self.head:
            self.head = new_node
            self.current = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self.size += 1

    def remove_item(self):
        if not self.current:
            return None
        removed_song = self.current.song
        if self.current == self.head:
            self.head = self.current.next
            self.current = self.head
        else:
            temp = self.head
            while temp.next != self.current:
                temp = temp.next
            temp.next = self.current.next
            self.current = temp.next or temp
        self.size -= 1
        return removed_song

    def next_item(self):
        if self.current and self.current.next:
            self.current = self.current.next
            return self.current.song
        return None

    def previous_item(self):
        if not self.current:
            return None
        temp = self.head
        while temp and temp.next != self.current:
            temp = temp.next
        if temp and temp != self.current:
            self.current = temp
            return self.current.song
        return None

    def get_current_item(self):
        return self.current.song if self.current else None

    def get_all_songs(self):
        songs = []
        current = self.head
        while current:
            songs.append(current.song.to_dict())
            current = current.next
        return songs

class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.current = None
        self.size = 0

    def add_item(self, song):
        new_node = Node(song)
        if not self.head:
            self.head = new_node
            self.current = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
            new_node.prev = current
        self.size += 1

    def remove_item(self):
        if not self.current:
            return None
        removed_song = self.current.song
        if self.current == self.head:
            self.head = self.current.next
            if self.head:
                self.head.prev = None
            self.current = self.head
        else:
            self.current.prev.next = self.current.next
            if self.current.next:
                self.current.next.prev = self.current.prev
            self.current = self.current.next or self.current.prev
        self.size -= 1
        return removed_song

    def next_item(self):
        if self.current and self.current.next:
            self.current = self.current.next
            return self.current.song
        return None

    def previous_item(self):
        if self.current and self.current.prev:
            self.current = self.current.prev
            return self.current.song
        return None

    def get_current_item(self):
        return self.current.song if self.current else None

    def get_all_songs(self):
        songs = []
        current = self.head
        while current:
            songs.append(current.song.to_dict())
            current = current.next
        return songs

class CircularLinkedList:
    def __init__(self):
        self.head = None
        self.current = None
        self.size = 0

    def add_item(self, song):
        new_node = Node(song)
        if not self.head:
            self.head = new_node
            new_node.next = new_node
            self.current = new_node
        else:
            current = self.head
            while current.next != self.head:
                current = current.next
            current.next = new_node
            new_node.next = self.head
        self.size += 1

    def remove_item(self):
        if not self.current:
            return None
        removed_song = self.current.song
        if self.size == 1:
            self.head = None
            self.current = None
        else:
            temp = self.head
            while temp.next != self.current:
                temp = temp.next
            temp.next = self.current.next
            if self.current == self.head:
                self.head = self.current.next
            self.current = self.current.next
        self.size -= 1
        return removed_song

    def next_item(self):
        if self.current:
            self.current = self.current.next
            return self.current.song
        return None

    def previous_item(self):
        if self.current:
            temp = self.head
            while temp.next != self.current:
                temp = temp.next
            self.current = temp
            return self.current.song
        return None

    def get_current_item(self):
        return self.current.song if self.current else None

    def get_all_songs(self):
        songs = []
        if not self.head:
            return songs
        current = self.head
        while True:
            songs.append(current.song.to_dict())
            current = current.next
            if current == self.head:
                break
        return songs

class CircularDoublyLinkedList:
    def __init__(self):
        self.head = None
        self.current = None
        self.size = 0

    def add_item(self, song):
        new_node = Node(song)
        if not self.head:
            self.head = new_node
            new_node.next = new_node
            new_node.prev = new_node
            self.current = new_node
        else:
            last = self.head.prev
            new_node.next = self.head
            new_node.prev = last
            last.next = new_node
            self.head.prev = new_node
        self.size += 1

    def remove_item(self):
        if not self.current:
            return None
        removed_song = self.current.song
        if self.size == 1:
            self.head = None
            self.current = None
        else:
            self.current.prev.next = self.current.next
            self.current.next.prev = self.current.prev
            if self.current == self.head:
                self.head = self.current.next
            self.current = self.current.next
        self.size -= 1
        return removed_song

    def next_item(self):
        if self.current:
            self.current = self.current.next
            return self.current.song
        return None

    def previous_item(self):
        if self.current:
            self.current = self.current.prev
            return self.current.song
        return None

    def get_current_item(self):
        return self.current.song if self.current else None

    def get_all_songs(self):
        songs = []
        if not self.head:
            return songs
        current = self.head
        while True:
            songs.append(current.song.to_dict())
            current = current.next
            if current == self.head:
                break
        return songs