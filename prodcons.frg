#lang forge/bsl

sig Buffer {}

sig RingBuffer {
    buffer: set Bufffer,
    head: one Int,
    tail: one Int
}

pred InitState[r: RingBuffer] {
    r.buffer = empty
}