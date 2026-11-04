import sys
import time

import pygame

from engine.rules import TICK_DT, WIDTH
from game.render import HEIGHT, draw_waiting, draw_world
from metrics.logger import MetricsLogger
from network.impairment import ImpairmentInjector
from network.transport import UDPTransport
from strategies.dead_reckoning import DeadReckoning

CLIENT_PORT = 9998
SERVER_PORT = 9999

# Prediction and rollback will be added in the next stages, once this works first
STRATEGY_MAP = {
    "dead_reckoning": DeadReckoning,
}


def main():
    if len(sys.argv) < 5:
        print("Please use a valid format: python3 -m client.main <strategy_name> <latency_ms> <packet_loss_pct> <trial_id>")
        sys.exit(1)

    strategy_name = sys.argv[1]
    if strategy_name not in STRATEGY_MAP:
        print("Invalid strategy name, choose from:", list(STRATEGY_MAP.keys()))
        sys.exit(1)

    latency_ms = int(sys.argv[2])
    packet_loss_pct = float(sys.argv[3])
    trial_id = sys.argv[4]

    strategy = STRATEGY_MAP[strategy_name]()
    transport = UDPTransport(local_port=CLIENT_PORT)
    injector = ImpairmentInjector(latency_ms=latency_ms, packet_loss_pct=packet_loss_pct)
    logger = MetricsLogger(role="client")

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Hanuman vs Tosakan")
    font = pygame.font.Font(None, 72)

    seq = 0  # Number of the next input to send
    tick = 0
    next_tick_time = time.monotonic()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        inputs = {
            "left": bool(keys[pygame.K_a]),
            "right": bool(keys[pygame.K_d]),
            "jump": bool(keys[pygame.K_SPACE]),
            "punch": bool(keys[pygame.K_e]),
            "kick": bool(keys[pygame.K_q]),
            "block": bool(keys[pygame.K_f]),
        }

        # Send this tick's input to the server through the injector
        strategy.process_input(seq, inputs)
        injector.apply(transport.send, {"seq": seq, "inputs": inputs}, SERVER_PORT)
        seq += 1

        # Apply every server state that has arrived since the last tick
        while True:
            state = transport.receive()
            if state is None:
                break
            if strategy.reconcile(state):
                logger.log_correction(tick)

        strategy.predict(TICK_DT)

        if strategy.world is None:
            draw_waiting(screen, font)
        else:
            draw_world(screen, font, strategy.world)
            if tick % 5 == 0:
                player = strategy.world["player"]
                logger.log_state(tick, (player["x"], player["y"]))
        pygame.display.flip()

        tick += 1
        if tick % 60 == 0:
            logger.flush(trial_id)

        # Wait for the next tick, sending any delayed packets the moment they are due
        next_tick_time += TICK_DT
        if next_tick_time < time.monotonic() - TICK_DT:
            next_tick_time = time.monotonic()  # Fell behind by more than a tick, so do not try to catch up
        while time.monotonic() < next_tick_time:
            injector.release()
            time.sleep(0.001)
        injector.release()

    logger.flush(trial_id)
    pygame.quit()


if __name__ == "__main__":
    main()