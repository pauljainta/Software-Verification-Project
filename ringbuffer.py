TX_PACKET_BUFFER_SIZE = 1024
RX_PACKET_BUFFER_SIZE = 1024
TX_DESC_RING_SIZE = 16
RX_DESC_RING_SIZE = 16

tx_packet_buffer = bytearray(TX_PACKET_BUFFER_SIZE)
tx_desc_ring_buffer = [0] * TX_DESC_RING_SIZE
tx_head = 0
tx_tail = 0

rx_packet_buffer = bytearray(RX_PACKET_BUFFER_SIZE)
rx_desc_ring_buffer = [0] * RX_DESC_RING_SIZE
rx_head = 0
rx_tail = 0

class CPU:
    def __init__(self):
        pass

    def write_packet_to_buffer(self, packet_data):
        global tx_packet_buffer
        tx_packet_buffer = bytearray(packet_data)

    def create_descriptor(self, packet_address):
        return packet_address  # For simplicity, descriptor is just the address of the packet in the buffer

    def write_descriptor_to_ring_buffer(self, descriptor):
        global tx_tail
        global tx_desc_ring_buffer
        tx_desc_ring_buffer[tx_tail] = descriptor

    def read_head_pointer(self):
        global tx_head
        return tx_head

    def increment_tx_tail_pointer(self):
        global tx_tail
        # MMIO Write: Increment tx_tail pointer
        tx_tail = (tx_tail + 1) % len(tx_desc_ring_buffer)

    def fetch_packet(self):
        global rx_head
        global rx_desc_ring_buffer
        descriptor = rx_desc_ring_buffer[rx_head]
        packet_address = descriptor
        # MMIO Read: Fetch the packet from rx_packet buffer using packet_address
        packet_data = rx_packet_buffer
        # Increment rx_head pointer
        rx_head = (rx_head + 1) % len(rx_desc_ring_buffer)
        return packet_data

    def increment_rx_head_pointer(self):
        global rx_head
        # MMIO Write: Increment rx_head pointer
        rx_head = (rx_head + 1) % len(rx_desc_ring_buffer)


class NIC:
    def __init__(self):
        pass

    def write_packet_to_buffer(self, packet_data):
        global rx_packet_buffer
        rx_packet_buffer = bytearray(packet_data)

    def create_descriptor(self, packet_address):
        return packet_address  # For simplicity, descriptor is just the address of the packet in the buffer    

    def receive_packet(self, packet_data):
        global rx_packet_buffer
        rx_packet_buffer = bytearray(packet_data)

    def write_descriptor_to_ring_buffer(self, descriptor):
        global rx_tail
        global rx_desc_ring_buffer
        rx_desc_ring_buffer[rx_tail] = descriptor

    def read_tail_pointer(self):
        global rx_tail
        return rx_tail

    def increment_rx_tail_pointer(self):
        global rx_tail
        # MMIO Write: Increment rx_tail pointer
        rx_tail = (rx_tail + 1) % len(rx_desc_ring_buffer)

    def fetch_packet(self):
        global tx_head
        global tx_desc_ring_buffer
        # descriptor = tx_desc_ring_buffer[tx_head]
        # packet_address = descriptor
        # DMA read: Fetch the packet from tx_packet buffer using packet_address
        packet_data = tx_packet_buffer
        # Increment tx_head pointer
        tx_head = (tx_head + 1) % len(tx_desc_ring_buffer)
        return packet_data

    def increment_rx_head_pointer(self):
        global rx_head
        # MMIO Write: Increment rx_head pointer
        rx_head = (rx_head + 1) % len(rx_desc_ring_buffer)


import random
import string
import unittest
import argparse


class TestRingBufferOperations(unittest.TestCase):
    def setUp(self):
        # Initialize buffers before each test case
        global tx_packet_buffer, tx_desc_ring_buffer, rx_packet_buffer, rx_desc_ring_buffer, tx_head, tx_tail, rx_head, rx_tail
        tx_packet_buffer = bytearray(TX_PACKET_BUFFER_SIZE)
        tx_desc_ring_buffer = [0] * TX_DESC_RING_SIZE
        rx_packet_buffer = bytearray(RX_PACKET_BUFFER_SIZE)
        rx_desc_ring_buffer = [0] * RX_DESC_RING_SIZE
        tx_head = 0
        tx_tail = 0
        rx_head = 0
        rx_tail = 0

    def test_transmit_path_CPU_to_NIC(self):
        # Generate random packet data
        packet_data = bytearray(random.choices(string.ascii_lowercase.encode(), k=10))  # Example packet data
        cpu = CPU()
        nic = NIC()
        
        global tx_tail, tx_head
        global tx_desc_ring_buffer

        # Simulate CPU behavior
        cpu.write_packet_to_buffer(packet_data)
        self.assertEqual(tx_packet_buffer, packet_data, f"Test case 'test_transmit_path_CPU_to_NIC' failed for packet {packet_data}: Packet data not written to TX packet buffer correctly")

        descriptor = cpu.create_descriptor(id(tx_packet_buffer))
        cpu.write_descriptor_to_ring_buffer(descriptor)
        self.assertEqual(tx_desc_ring_buffer[tx_tail], descriptor, f"Test case f'test_transmit_path_CPU_to_NIC' failed for packet {packet_data}: Descriptor not written to TX descriptor ring buffer correctly")
    
        # Increment tx_tail pointer
        cpu.increment_tx_tail_pointer()

        # Simulate NIC behavior
        packet_received = nic.fetch_packet()
        self.assertEqual(packet_received, packet_data, f"Test case 'test_transmit_path_CPU_to_NIC' failed for packet {packet_data}: Packet data mismatch")
        
        self.assertEqual(tx_head, tx_tail, f"Test case 'test_transmit_path_CPU_to_NIC' failed for packet {packet_data}: Head and Tail Mismatch after Transmission")


    def test_transmit_path_NIC_to_CPU(self):
        # Generate random packet data
        packet_data = bytearray(random.choices(string.ascii_lowercase.encode(), k=10))  # Example packet data
        cpu = CPU()
        nic = NIC()
        
        global rx_tail, rx_head
        global rx_desc_ring_buffer

        # Simulate CPU behavior
        nic.write_packet_to_buffer(packet_data)
        self.assertEqual(rx_packet_buffer, packet_data, f"Test case 'test_transmit_path_NIC_to_CPU' failed for packet {packet_data}: Packet data not written to TX packet buffer correctly")

        descriptor = nic.create_descriptor(id(rx_packet_buffer))
        nic.write_descriptor_to_ring_buffer(descriptor)
        self.assertEqual(rx_desc_ring_buffer[rx_tail], descriptor, f"Test case f'test_transmit_path_NIC_to_CPU' failed for packet {packet_data}: Descriptor not written to TX descriptor ring buffer correctly")
    
        # Increment tx_tail pointer
        nic.increment_rx_tail_pointer()

        # Simulate NIC behavior
        packet_received = cpu.fetch_packet()
        self.assertEqual(packet_received, packet_data, f"Test case 'test_transmit_path_NIC_to_CPU' failed for packet {packet_data}: Packet data mismatch")
        
        self.assertEqual(rx_head, rx_tail, f"Test case 'test_transmit_path_NIC_to_CPU' failed for packet {packet_data}: Head and Tail Mismatch after Transmission")
    
    def test_transmit_path_CPU_to_NIC_Empty_Buffer(self):
        # Generate random packet data
        packet_data = bytearray(random.choices(string.ascii_lowercase.encode(), k=10))  # Example packet data
        nic = NIC()
        
        global tx_tail, tx_head
        global tx_desc_ring_buffer
        # Simulate NIC behavior
        packet_received = nic.fetch_packet()
        self.assertEqual(packet_received, packet_data, f"Test case 'test_transmit_path_CPU_to_NIC_Empty_Buffer' failed for packet {packet_data}: Packet data mismatch")
        
        self.assertEqual(tx_head, tx_tail, f"Test case 'test_transmit_path_CPU_to_NIC_Empty_Buffer' failed for packet {packet_data}: Head and Tail Mismatch after Transmission")
    

    def test_transmit_path_NIC_to_CPU_Empty_Buffer(self):
        # Generate random packet data
        packet_data = bytearray(random.choices(string.ascii_lowercase.encode(), k=10))  # Example packet data
        cpu = CPU()
        global rx_tail, rx_head
        global rx_desc_ring_buffer
        # Simulate NIC behavior
        packet_received = cpu.fetch_packet()
        self.assertEqual(packet_received, packet_data, f"Test case 'test_transmit_path_NIC_to_CPU_Empty_Buffer' failed for packet {packet_data}: Packet data mismatch")
        
        self.assertEqual(rx_head, rx_tail, f"Test case 'test_transmit_path_NIC_to_CPU_Empty_Buffer' failed for packet {packet_data}: Head and Tail Mismatch after Transmission")


    def test_rx_buffer_full_CPU_write_fail(self):
        # Fill up the RX buffer
        for i in range(RX_DESC_RING_SIZE):
            descriptor = id(bytearray())  # Simulate different packet addresses
            rx_desc_ring_buffer[i] = descriptor

        cpu = CPU()
        packet_data = bytearray(random.choices(string.ascii_lowercase.encode(), k=10))  # Example packet data

        # Attempt to write a packet to the full RX buffer
        cpu.write_packet_to_buffer(packet_data)

        # Ensure the buffer state remains unchanged
        self.assertEqual(rx_packet_buffer, bytearray(RX_PACKET_BUFFER_SIZE), "Test case 'test_rx_buffer_full_CPU_write_fail' failed: RX buffer modified when full")
        self.assertEqual(rx_desc_ring_buffer.count(0), 0, "Test case 'test_rx_buffer_full_CPU_write_fail' failed: RX descriptor ring buffer modified when full")


    def test_tx_buffer_full_NIC_write_fail(self):
        # Fill up the RX buffer
        for i in range(RX_DESC_RING_SIZE):
            descriptor = id(bytearray())  # Simulate different packet addresses
            tx_desc_ring_buffer[i] = descriptor

        nic = NIC()
        packet_data = bytearray(random.choices(string.ascii_lowercase.encode(), k=10))  # Example packet data

        # Attempt to write a packet to the full RX buffer
        nic.write_packet_to_buffer(packet_data)

        # Ensure the buffer state remains unchanged
        self.assertEqual(tx_packet_buffer, bytearray(RX_PACKET_BUFFER_SIZE), "Test case 'test_tx_buffer_full_NIC_write_fail' failed: TX buffer modified when full")
        self.assertEqual(tx_desc_ring_buffer.count(0), 0, "Test case 'test_tx_buffer_full_CPU_write_fail' failed: TX descriptor ring buffer modified when full")


if __name__ == '__main__':
    # Create argument parser
    parser = argparse.ArgumentParser(description="Run test cases with customizable count")
    parser.add_argument("--test-count", type=int, default=10000, help="Number of times to run the test suite")

    # Parse arguments
    args = parser.parse_args()

    # Open a file to write the test results
    with open("result.txt", "w") as file:
        # Redirect the output to the file
        runner = unittest.TextTestRunner(stream=file)
        
        # Run the test suite
        for i in range(args.test_count):
            file.write(f"\n\nTEST NO {i}\n")
            random.seed()  # Reset the random seed for each iteration to get different random inputs
            runner.run(unittest.TestLoader().loadTestsFromTestCase(TestRingBufferOperations))
