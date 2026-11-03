import random # Needed to get random int between 0 and 1
import time # Needed to recreate latency

class ImpairmentInjector:
    def __init__(self, latency_ms: int = 0, packet_loss_pct: float = 0.0):
        self.latency_ms = latency_ms
        self.packet_loss_pct = packet_loss_pct
        self.queue = [] # Packets are waiting to be sent

    def should_drop(self) -> bool:
        return random.random() < (self.packet_loss_pct / 100) # If the pct is 3%, (/100 = 0.03), then if the random integer between 0 and 1 is less than 0.03, return True.

    def apply(self, send_fn, data, dest_port):
        # Does not send anything, and never blocks. It only decides the packet's fate and queues it
        if self.should_drop():
            return  # Packet is lost
        due_time = time.monotonic() + self.latency_ms / 1000
        self.queue.append((due_time, send_fn, data, dest_port))
    def release(self):
        # Call once per loop. Sends every queued packet whose delay has passed
        now = time.monotonic()
        waiting = []
        for item in self.queue:
            due_time, send_fn, data, dest_port = item
            if due_time <= now:
                send_fn(data, dest_port)
            else:
                waiting.append(item)
        self.queue = waiting


if __name__ == "__main__":
    sent = []

    def fake_send(data, dest_port):
        sent.append(data)

    # Total loss should send nothing
    drop = ImpairmentInjector(latency_ms=0, packet_loss_pct=100)
    drop.apply(fake_send, "a", 1)
    drop.release()
    print("100% loss, sent:", sent)  # Expect []

    # Zero latency should send on the first release
    fast = ImpairmentInjector(latency_ms=0, packet_loss_pct=0)
    fast.apply(fake_send, "b", 1)
    fast.release()
    print("0ms, sent:", sent)  # Expect ['b']

    # 100ms latency should hold the packet back, then deliver it, without blocking
    slow = ImpairmentInjector(latency_ms=100, packet_loss_pct=0)
    slow.apply(fake_send, "c", 1)
    slow.release()
    print("100ms, straight away:", sent)  # Expect ['b'], 'c' is not due yet
    time.sleep(0.12)
    slow.release()
    print("100ms, after 0.12s:", sent)  # Expect ['b', 'c']