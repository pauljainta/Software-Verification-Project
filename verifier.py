import random
import string
import unittest
import argparse
from ringbuffer import *


class TestRingBufferOperations(unittest.TestCase):
    def setUp(self):
        # Initialize CPU and NIC objects
        self.cpu = CPU()
        self.nic = NIC()

    def test_transmit_path(self):
        # Generate random packet data
        packet_data = bytearray(random.choices(string.ascii_lowercase.encode(), k=10))  # Example packet data
        self.cpu.write_packet_to_buffer(packet_data)
        descriptor = self.cpu.create_descriptor(id(self.cpu.tx_packet_buffer))
        self.cpu.write_descriptor_to_ring_buffer(descriptor)
        self.cpu.increment_head_pointer()

        # Verify TX ring buffer content
        expected_content = [id(self.cpu.tx_packet_buffer)]
        actual_content = [desc for desc in self.cpu.tx_desc_ring_buffer if desc != 0]
        self.assertEqual(actual_content, expected_content, f"Test case 'test_transmit_path' failed for packet data: {packet_data}")

    def test_receive_path(self):
        # Generate random packet data
        packet_data = bytearray(random.choices(string.ascii_lowercase.encode(), k=10))  # Example packet data
        self.nic.receive_packet(packet_data)
        descriptor = id(self.nic.rx_packet_buffer)
        self.nic.write_descriptor_to_ring_buffer(descriptor)
        self.nic.increment_tail_pointer()

        # Verify RX ring buffer content
        expected_content = [id(self.nic.rx_packet_buffer)]
        actual_content = [desc for desc in self.nic.rx_desc_ring_buffer if desc != 0]
        self.assertEqual(actual_content, expected_content, f"Test case 'test_receive_path' failed for packet data: {packet_data}")

    def test_empty_tx_buffer(self):
        # Generate random packet data
        packet_data = bytearray(random.choices(string.ascii_lowercase.encode(), k=10))  # Example packet data
        self.cpu.write_packet_to_buffer(packet_data)
        descriptor = self.cpu.create_descriptor(id(self.cpu.tx_packet_buffer))
        self.cpu.tx_desc_ring_buffer = [0] * len(self.cpu.tx_desc_ring_buffer)  # Empty the TX descriptor ring buffer
        self.cpu.write_descriptor_to_ring_buffer(descriptor)
        self.cpu.increment_head_pointer()
        self.assertEqual(self.cpu.tx_desc_ring_buffer[self.cpu.tx_head], descriptor, f"Test case 'test_empty_tx_buffer' failed for packet data: {packet_data}")  # Ensure descriptor is written

    def test_full_rx_buffer(self):
        # Generate random packet data
        packet_data = bytearray(random.choices(string.ascii_lowercase.encode(), k=10))  # Example packet data
        self.nic.receive_packet(packet_data)
        descriptor = id(self.nic.rx_packet_buffer)
        self.nic.write_descriptor_to_ring_buffer(descriptor)
        self.nic.increment_tail_pointer()
        # Fill the RX descriptor ring buffer to full capacity
        self.nic.rx_desc_ring_buffer = [id(bytearray())] * len(self.nic.rx_desc_ring_buffer)
        # Attempt to write a new descriptor
        new_descriptor = id(bytearray())
        self.nic.write_descriptor_to_ring_buffer(new_descriptor)
        self.assertNotEqual(self.nic.rx_desc_ring_buffer[self.nic.rx_tail], new_descriptor, f"Test case 'test_full_rx_buffer' failed for packet data: {packet_data}")  # Ensure new descriptor is not written


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
            print(f"TEST NO {i}")
            random.seed()  # Reset the random seed for each iteration to get different random inputs
            runner.run(unittest.TestLoader().loadTestsFromTestCase(TestRingBufferOperations))
