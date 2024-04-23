Modeling CPU-NIC communication over PCIe

# Introduction

Traditionally in data centers distributed workloads were run in a single server model,
where the workload is sharded and each shard is run in different servers. This is even
true for modern cloud workloads. This model prohibits efficient sharing of data between
different servers, also the workload is bottlenecked by the least memory available server.

For efficient memory sharing in a data center between servers new technologies are gaining
traction for example RDMA. But this can only directly access another servers memory directly.
When sharing memory between servers an important aspect in maintaining consistency. RDMA
alone doesn't provide answer to this question.

To solve this problem multiple new cache coherent interconnects are being developed.
For example CXL, NVLink etc. These interconnect are either implemented on top of PCIe
or completely new architecture design.

PCIe is widely used for sending and receiving data from host to the peripheral devices.
For example network interface card(NIC), storage device etc. This technology is being used
for a long time now. Now the question is why do we need new interconnects? Can we implement
a coherent interconnect just using PCIe?

To create an interconnection network with PCIe we have all the technology already available.
With PCIe not-transparent bridge (NTB) two server can communicate and exchange data just using
the PCIe protocol. Also, there is NTB switches available which can be used to establish communication
between multiple servers.

To understand if it is possible to create a cache coherent interconnect between severs
using PCIe we need to understand what operations are supported by PCIe? What is the
ordering guarantees between those operations?

The goal of our project is to answer those questions by modeling PCIe communication.
For modeling PCIe communication between CPU and devices we have choose to model
a producer-consumer ring buffer, which is the most prevalent data structure that
used for communication over PCIe. For example NIC uses a producer-consumer ring buffer
to send/receive packets. Ultimately our models will allow us to generate litmus
tests which then we will be able to apply on real hardware to find out what guarantees
each of them provides and create a memory model for a coherent interface implemented
on top of PCIe.

To this end we have following contribution in our project:

1. Understanding different operations over PCIe.
2. Understanding the ordering guarantees between those operations.
3. Understand producer-consumer ring buffer in the context of PCIe communication.
4. Understand how a device such as NIC use such producer-consumer structure using PCIe semantics.
5. Create an operational model using Python.
6. Preliminary model using Forge modeling language to formally test PCIe communication.

In the following text we are giving a brief primer on PCIe and describe
the transmit and receive path for CPU-NIC communication.

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

**PCIe operations:** These DMA and MMIO operations are broken down
to PCIe read and write operations. There are two variant of PCIe read/write
operation. Posted and Non-posted. In non-posted operations a completion event
is generated after completing the operations, which act as acknowledgement.
On the otherhand with posted operation no completion event is generated.

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

# Status

## Operational Model

Currently, the project is in the implementation phase. We have successfully designed and implemented the core functionalities of the ring buffer, including transmit and receive operations. However, there are still several areas that require further refinement and optimization. We have used both Python and Forge to model different scenarios. In Python, we implemented six test cases to verify our model and ran those test cases for 10000 different packets. We found out the scenarios where our test cases fail i.e. the model fails to perform as expected. 

Next steps include:
- Based on the failed test cases, we need to modify the model
- Conducting thorough testing and verification to ensure the correctness and reliability of the implementation
- Optimizing performance and memory utilization to enhance efficiency
- Integrating the ring buffer with real-world systems and applications to evaluate its practical utility

## Forge Model

The forge model is currently in implementation stage. Following functionalities are implemented.
Currently with few minor modifications it is possible to simulate the receive path.
Where NIC is producing and CPU is consuming.

1. Sigs and predicate for ring buffer.
2. Sigs and predicate for DMA write and MMIO write operations.

The next steps include

1. Write predicate for DMA read and MMIO read to simulate transmit path.
2. Break down and write predicate for PCIe read and write ops.
3. Incorporate orderings from PCIe spec.

# Demo

## Operational model with Python

Taking into consideration the following scenario will allow us to illustrate the functionality of our ring buffer implementation:

Let's say that we have a central processing unit (CPU) and a network interface card (NIC) that are connected through a ring buffer. Data packets are created by the central processing unit (CPU), which then writes them to the transmit buffer of the ring buffer. After that, the network interface card (NIC) retrieves these packets from the buffer and processes them effectively.

An illustration of the interaction between the central processing unit (CPU), network interface controller (NIC), and ring buffer can be visualized through the use of code snippets and graphics.

## Axiomatic model with Forge

Currently under implementation.

# Implementation

## Operational model

For the operational model we have used python programming language. The pytest infrastructure is used for implementing the testing of different PCIe operations.

In order to manage the complex dance of data transmission that takes place between the central processing unit (CPU) and the network interface card (NIC), our ring buffer implementation incorporates a wide variety of necessary classes. A range of methods that are customized to the task at hand, including packet transmission, descriptor management, and other techniques, is provided by the CPU class, which stands out as the most prominent component of this architecture. The Network Interface Card (NIC) class, on the other hand, is the one that is responsible for managing buffers and ensuring that the delicate balance between data reception and processing is maintained.

A veritable linchpin that enables seamless communication between the central processing unit (CPU) and the network interface card (NIC) is the ring buffer class, which is at the center of this intricate web. This is made possible by its multidimensional design, which enables it to store and retrieve data in an effective manner. This ensures that the flow of information between these essential components continues to be uninterrupted and smooth.

Our method offers a level of modularity and scalability that is needed for traversing the dynamic landscape of data transfer in current computing settings. This is accomplished by encapsulating complex functionalities within these specialized classes. This modular approach not only makes the development process more efficient, but it also makes the system more flexible and adaptable as a whole.

Furthermore, our implementation places a high priority on speed and resource optimization, making use of cutting-edge approaches to guarantee the highest possible efficiency and the lowest possible latency. We endeavor to unlock the full potential of the CPU-NIC communication pipeline by making thoughtful design choices and meticulously optimizing our efforts. This will allow us to deliver unrivaled performance and reliability in the context of data transfer activities.

In a nutshell, the implementation of our ring buffer is the result of a combination of thorough optimization, meticulous design, and unyielding commitment to quality. We are committed to pushing the boundaries of what is possible in the realm of CPU-NIC communication, fostering innovation and growth in the field of computer systems and software engineering. This commitment will continue as we continue to refine and expand upon this foundation.

## Forge Model

The ring buffer is implemented as sig with partial functions. These represents a one dimensional array which have integer positions.
Each position holds a slot which can be marked with set of Markers sig. This abstract Marker sig tags the buffer. This tag can
be a combination of Head, Tail, Empty or Filled.

Initial predicate: This predicated ensures
- Initially all the positions for the ring buffer slots are valid.
- Initially all the slots are tagged as empty except the first one.
- The first slot is additionally tagged as Head + Tail

DMA Write predicate: Models a DMA write operation for writing packet buffer from NIC to CPU in transmit path
- Checks if the ring buffer is full
- Checks if the i-th position has the tail, in that case move tail to next wrapping slot
- Checks tail is always ahead of head
- Marks the i-th slot as filled

MMIO write predicate: Models NIC register head increment to singal NIC receiving of the packet by consuming the slot
- Checks if the ring buffer is empty
- Check if the i-th position has head, in that case move head to next wrapping slot
- Check head is always behind tail
- Mark the i-th position as Empty.

# Future Work

Future work on this project will focus on:
- Extensive testing and verification to validate the correctness and reliability of the implementation
- Performance optimization to enhance the efficiency of data transfer operations
- Integration with real-world systems and applications to evaluate practical usability

# Discussion

This project helped us to peak at the underlying mechanism for PCIe communication
which is one of the basic building block in today's computer systems. While working
on the project we didn't find lot of work in this space. Huge memory requirement of modern
datacenters which is accelerating the availability of new coherent interconnects
made it even more important to formally study PCIe communication.

While implementing the axiomatic/formal model with Forge we found that Forge documentation is
decent but lack of examples made is hard to understand some of the concepts which was pretty
new for us.
