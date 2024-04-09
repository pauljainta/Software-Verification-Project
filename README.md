## How CPU and NIC communicate to Receive/Transimt Packets ##


### Primer ###

There is two kinds of operations that happens over PCIe. DMA and MMIO.

**MMIO:** A portion of the NIC memory is mapped in the Host memory.
Host can read and write to that memory. When host write to that
memory it generates a MMIO write transaction and data is reached
to NIC memory. when host reads from it a MMIO read transaction
is generated and host gets the data from the NIC. MMIO is used
to read/write small data from/to the NIC. Typically it is 32bit
or 64bit value.

**DMA:** Host gives access a portion of the memory to the NIC. Then
NIC can do DMA read to read from that memory and DMA write to
write into that memory. DMA is used to read/write larger values,
for example 1KB, 4KB etc.

**Packet buffers:** A packet buffer is a piece of memory where transmitting
and received packets are kept. There is two packet buffers. Transmit buffer(TX buffer),
where host keeps the packets that will be transmitted. And receive buffer(RX buffer),
where NIC pushes packet that are received.

**Descriptor ring buffer:** It's a ring buffer that points to the packet buffers.
There is two descriptor ring buffer. RX ring buffer. Each entry in the buffer,
points to packet in the RX buffer. And TX ring buffer. Each entry points to
a packet in TX buffer. As these are ring buffers there is head and tail pointer
for each of the rings. These pointers are kept in NIC memory.

### How a Packet is sent (Transmit path) ###

1. CPU write the packet in the TX packet buffer.
2. Create a descriptor with the address to the packet in the TX packet buffer.
3. Writes the descriptor in the TX descriptor ring buffer.
4. Increments the tail pointer with MMIO write.
5. NIC agents see that the tail pointer increased that means CPU wants to transmit a new packet.
6. NIC does a DMA read to read the descripotr in current head.
7. NIC does a DMA read in the packet buffer address found in the descriptor to read the packet.
8. Transmit the packet.
9. Increments the head pointer to singnal the CPU that the packet is sent.
10. CPU reads the head pointer through MMIO read and sees that it is incremented meaning the packet is sent.

### How a packet is received (Receive Path) ###

1. NIC receives a packet.
2. NIC does a DMA write to write the packet in the RX packet buffer.
3. NIC does a DMA write to write the descriptor to the packet in the RX descriptor ring.
4. Increments the RX ring buffer tail pointer to signal host that a new packet is received.
5. Host does MMIO read to read the RX ring buffer tail pointer and sees that it is incremented
   meaning a new packet if received.
6. Host then increments the head pointer through MMIO write.
7. NIC sees the new head pointer, meaning host received the packet.

## Glossary ##

1. **DMA (Direct Memory Access):**

   - DMA is a mechanism that allows hardware devices, like the NIC, to access system memory (kernel memory) directly without involving the CPU.
   - In the context of networking, DMA enables the NIC to transfer data to and from the kernel memory without CPU intervention, which improves system performance.
   - When data arrives at the NIC, instead of involving the CPU to transfer it to kernel memory, the NIC's DMA controller handles the transfer directly.
   - This process offloads the data transfer task from the CPU, allowing it to focus on other tasks while data is being transferred between the NIC and kernel memory.

2. **MMIO (Memory-Mapped I/O):**

   - MMIO is a method for accessing hardware devices, such as the NIC, as if they were memory-mapped locations.
   - In MMIO, certain addresses in the system's address space are reserved for communicating with hardware devices.
   - When the CPU wants to communicate with a hardware device, it reads from or writes to these memory-mapped addresses, triggering operations on the device.
   - MMIO is commonly used for configuring and controlling hardware devices, such as programming the NIC with network settings or initiating data transfers.

**Process with DMA and MMIO:**

**Data Reception (NIC to Kernel Memory):**

- Data arrives at the NIC from the network.
- The NIC's DMA controller, using MMIO, accesses the receive ring buffer in kernel memory directly.
- The NIC writes the incoming data directly to the receive ring buffer using DMA.
- Once the data transfer is complete, the NIC may raise an interrupt to notify the CPU of the newly received data.

**Consumption by Kernel:**

- Upon receiving the interrupt or polling the receive ring buffer, the CPU's kernel processes the received data.
- The kernel parses and analyzes the data, performing necessary networking operations (e.g., protocol handling, packet filtering).
- If further processing is required, the kernel may copy the data from the receive ring buffer to other kernel data structures.

**Data Transmission (Kernel Memory to NIC):**

- When the CPU needs to transmit data, it places the data into the transmit ring buffer in kernel memory.
- The NIC's DMA controller, using MMIO, accesses the transmit ring buffer directly.
- The NIC reads the data from the transmit ring buffer using DMA and sends it out over the network.
- Once the transmission is complete, the NIC may raise an interrupt to notify the CPU.

In this process, DMA and MMIO work together to facilitate efficient data transfer between the NIC, CPU, and kernel memory, while the producer-consumer model ensures synchronized and efficient communication.
