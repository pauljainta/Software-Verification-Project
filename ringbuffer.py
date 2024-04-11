class CPU:
    def __init__(self):
        self.tx_packet_buffer = bytearray(1024)  # Example TX packet buffer
        self.tx_desc_ring_buffer = [0] * 16  # Example TX descriptor ring buffer
        self.rx_desc_ring_buffer = [0] * 16  # Example RX descriptor ring buffer
        self.tx_head = 0
        self.tx_tail = 0

    def write_packet_to_buffer(self, packet_data):
        self.tx_packet_buffer = bytearray(packet_data)

    def create_descriptor(self, packet_address):
        return packet_address  # For simplicity, descriptor is just the address of the packet in the buffer

    def write_descriptor_to_ring_buffer(self, descriptor):
        self.tx_desc_ring_buffer[self.tx_tail] = descriptor
        self.tx_tail = (self.tx_tail + 1) % len(self.tx_desc_ring_buffer)

    def read_head_pointer(self):
        return self.tx_head

    def increment_head_pointer(self):
        self.tx_head = (self.tx_head + 1) % len(self.tx_desc_ring_buffer)


class NIC:
    def __init__(self):
        self.rx_packet_buffer = bytearray(1024)  # Example RX packet buffer
        self.rx_desc_ring_buffer = [0] * 16  # Example RX descriptor ring buffer
        self.rx_head = 0
        self.rx_tail = 0

    def receive_packet(self, packet_data):
        self.rx_packet_buffer = bytearray(packet_data)

    def write_descriptor_to_ring_buffer(self, descriptor):
        self.rx_desc_ring_buffer[self.rx_tail] = descriptor
        self.rx_tail = (self.rx_tail + 1) % len(self.rx_desc_ring_buffer)

    def read_tail_pointer(self):
        return self.rx_tail

    def increment_tail_pointer(self):
        self.rx_tail = (self.rx_tail + 1) % len(self.rx_desc_ring_buffer)


class RingBuffer:
    def __init__(self, size):
        self.buffer = [None] * size
        self.head = 0
        self.tail = 0

    def enqueue(self, item):
        self.buffer[self.tail] = item
        self.tail = (self.tail + 1) % len(self.buffer)

    def dequeue(self):
        item = self.buffer[self.head]
        self.head = (self.head + 1) % len(self.buffer)
        return item