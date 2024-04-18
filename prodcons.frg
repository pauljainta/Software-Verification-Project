#lang forge

abstract sig Operation {}

one sig DMA, MMIO extends Operation {}

abstract sig Marker {}

one sig Filled, Empty, Head, Tail extends Marker {}

one sig RingBuffer {
    buffer: pfunc Int -> Marker
}

pred InitValidRing {
    all i: Int | (i < 0 or i > 7) implies RingBuffer.buffer[i] = Empty
}

pred InitRing {
    RingBuffer.buffer[0] = Empty => RingBuffer.buffer[0] = Head + Tail + Empty
}

pred IsRingEmpty {
    #{i: Int | RingBuffer.buffer[i] = Filled} = 0
}

pred IsRingFull {
    #{i: Int | RingBuffer.buffer[i] = Filled} = 7
}

fun AddOneWrap(m: Int): Int {
    let ret = add[m, 1] {
        ret < 8 => ret else 0
    }

}

pred DMAWrite {
    all i: Int | RingBuffer.buffer[i] = Tail => {
        RingBuffer.buffer[i] = Filled
        RingBuffer.buffer[AddOneWrap[i]] = Tail
    }
}

pred MMIOWrite {
    all i: Int | RingBuffer.buffer[i] = Head => {
        RingBuffer.buffer[i] = Empty
        RingBuffer.buffer[AddOneWrap[i]] = Head
    }
}

pred PCIEOperation[op: Operation] {
    IsRingEmpty
    not IsRingFull
    op = DMA => DMAWrite else MMIOWrite
}

run {
    InitRing
    some op: Operation | PCIEOperation[op]
} for exactly 5 Int