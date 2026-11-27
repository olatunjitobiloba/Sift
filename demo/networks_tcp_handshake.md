# Computer Networks: TCP Three-Way Handshake

The Transmission Control Protocol establishes reliable ordered byte streams across IP networks using a three-way handshake before sending payload data:

1. SYN: The client sends a segment with the SYN flag enabled and an initial sequence number.
2. SYN-ACK: The server replies with both SYN and ACK flags acknowledging the client's sequence number.
3. ACK: The client confirms receipt so both endpoints enter the ESTABLISHED state.

Sliding window flow control limits unacknowledged segments to avoid overflowing the receiver buffer.
