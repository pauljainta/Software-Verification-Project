module NIC

import module UTIL

// Define the NIC signature
sig NIC {}


// Facts about NIC
fact {
    // The NIC has a receive buffer
    one ReceiveBuffer
}

// Predicates for NIC interactions
pred DataArrivalToNIC(packet: Packet) {
    // Predicate to simulate data arrival at NIC
    some ReceiveBuffer
    // Simulated action of adding data to the receive buffer
    AddDataToRingBuffer[packet, ReceiveBuffer]
}

pred TransmitDataFromNIC {
    // Predicate to simulate data transmission from NIC
    // Simulated action of retrieving data from the transmit buffer
    RetrieveDataFromRingBuffer[_, TransmitBuffer]
}

