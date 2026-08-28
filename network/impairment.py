import random # Needed to get random int between 0 and 1
import time # Needed to recreate latency

class ImpairmentInjector:
    def __init__(self, latency_ms: int = 0, packet_loss_pct: float = 0.0):
        self.latency_ms = latency_ms
        self.packet_loss_pct = packet_loss_pct

    def should_drop(self) -> bool:
        return random.random() < (self.packet_loss_pct / 100) # If the pct is 3%, (/100 = 0.03), then if the random integer between 0 and 1 is less than 0.03, return True.

    def apply(self, send_fn, data: bytes, dest_port: int):
    # Check should_drop(), if True, do nothing because the packet is simulated as lost.

    # If not dropped, and latency_ms is greater than 0, delay before actually sending, this simulates network latency.
        if self.should_drop():
            return

        if self.latency_ms > 0:
            time.sleep(self.latency_ms / 1000)

        # Once both checks are complete, we can send the packet
            
        send_fn(data, dest_port)
        # Send the packet by calling the send function with data and dest_port

    
if __name__ == "__main__":

    def fake_send(data, dest_port):
        print(f"Sent: {data} to port {dest_port}")

    print("Testing guaranteed drop (100%)")
    injector_drop = ImpairmentInjector(latency_ms=0, packet_loss_pct=100)
    injector_drop.apply(fake_send, b"test", 9999)
    print("(nothing above this line means dropped correctly)\n")

    print("Testing guaranteed send (0% loss)")
    injector_send = ImpairmentInjector(latency_ms=0, packet_loss_pct=0)
    injector_send.apply(fake_send, b"test", 9999)
        