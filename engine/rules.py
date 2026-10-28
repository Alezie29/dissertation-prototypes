# Game rules with no pygame in them, so a headless server can run the exact same code

WIDTH = 800
SPEED = 200  # Pixels per second
GRAVITY = 1800  # Pixels per second, per second
JUMP_SPEED = 700  # Pixels per second, upwards
GROUND_Y = 230.0  # Top edge of the rect when standing on the floor
FIGHTER_W, FIGHTER_H = 60, 120
MAX_HEALTH = 100
BLOCK_DIVISOR = 5  # A blocked attack will only deal a fifth of the damage
BLOCK_HOLD = 0.3  # Seconds a block stays up after the key is released

# The rules always advance in steps of exactly this size, so every run behaves the same
TICK_RATE = 60
TICK_DT = 1 / TICK_RATE

# Bot tuning
BOT_RANGE = 45  # Gap in pixels at which the bot stops walking and starts attacking
BOT_WARN = 0.35  # Seconds of yellow warning before each Tosakan attack
BOT_PRESS = 0.1  # How long the bot holds an attack button at the start of each cycle

# The bot repeats this script forever, one step after another (step name, seconds)
BOT_SCRIPT = [
    ("approach", 1.5),  # Walk toward Hanuman until in range
    ("punch", 0.9),  # Warn, then punch
    ("retreat", 0.8),  # Walk away to create space
    ("approach", 1.2),
    ("kick", 1.05),  # Warn, then kick
    ("guard", 1.0),  # Hold block
    ("retreat", 0.6),
    ("approach", 1.2),
]
BOT_CYCLE = sum(length for _, length in BOT_SCRIPT)

# One table describes every attack, cleaner code instead of a new variable each different attack added
ATTACKS = {
    "punch": {"duration": 0.3,  "start": 0.1, "end": 0.2, "damage": 10, "w": 50, "h": 30, "y_off": 30},
    "kick":  {"duration": 0.45, "start": 0.2, "end": 0.3, "damage": 15, "w": 70, "h": 25, "y_off": 70},
}


def new_fighter(x):
    return {
        "x": x, "y": GROUND_Y, "vx": 0.0, "vy": 0.0,
        "health": MAX_HEALTH,
        "facing": 1, # 1 = facing right, -1 = facing left
        "blocking": False, # Recalculated every fame
        "block_t": 0.0, # Seconds of guard left, refreshes when block key is held
        "attack_kind": None, # This will be punch, kick, or None
        "attack_t": -1.0, # -1 represents the fighter not attacking
        "hit_done": False, # Stops one punch damaging every frame of active window
        "bot_t": 0.0, # Bot timer, only used by the bot, rollback can restore from here
        "warning": False, # True while the bot is winding up, drawn as a yellow outline
    }


def new_world():
    # Same keys as GameState.entities, so the two can be joined up later
    return {"player": new_fighter(150.0), "npc": new_fighter(600.0)}


def is_ko(world):
    return world["player"]["health"] <= 0 or world["npc"]["health"] <= 0


def step_fighter(fighter, inputs, dt):
    # This will work on any fighter dict, never reads the keyboard
    on_floor = fighter["y"] >= GROUND_Y
    attacking = fighter["attack_t"] >= 0

    # Holding block refreshes the guard timer, and the guard lingers briefly after release
    if inputs["block"] and on_floor and not attacking:
        fighter["block_t"] = BLOCK_HOLD
    else:
        fighter["block_t"] = max(0.0, fighter["block_t"] - dt)
    blocking = fighter["block_t"] > 0 and on_floor and not attacking
    fighter["blocking"] = blocking

    # A grounded fighter is rooted while attacking, every attack becomes a commitment, reduces spamming of attacks
    if not (attacking and on_floor) and not blocking:
        if inputs["left"]:
            fighter["x"] -= SPEED * dt
        if inputs["right"]:
            fighter["x"] += SPEED * dt

    # No jumping out of an attack (animation cancel) or a block
    if inputs["jump"] and on_floor and not attacking and not blocking:  # Fighter on the floor
        fighter["vy"] = -JUMP_SPEED  # Y grows downwards, so up is negative

    fighter["vy"] += GRAVITY * dt
    fighter["y"] += fighter["vy"] * dt

    if fighter["y"] >= GROUND_Y:  # Fighter has landed
        fighter["y"] = GROUND_Y
        fighter["vy"] = 0

    fighter["x"] = max(0, min(fighter["x"], WIDTH - FIGHTER_W))

    # Start an attack only if one isn't already running and if fighter is not blocking. If both keys are held, punch wins.
    if fighter["attack_t"] < 0 and not blocking:
        kind = None
        if inputs["punch"]:
            kind = "punch"
        elif inputs["kick"]:
            kind = "kick"  # Punch wins if both keys are held
        if kind is not None:
            fighter["attack_kind"] = kind
            fighter["attack_t"] = 0.0
            fighter["hit_done"] = False

    # Attack timer counts with dt, not real time. 
    if fighter["attack_t"] >= 0:
        fighter["attack_t"] += dt
        if fighter["attack_t"] >= ATTACKS[fighter["attack_kind"]]["duration"]:
            fighter["attack_t"] = -1.0
            fighter["attack_kind"] = None

def current_segment(t):
    # Finds which step of the bot script the timer is in, and how far into that step
    t = t % BOT_CYCLE
    for name, length in BOT_SCRIPT:
        if t < length:
            return name, t
        t -= length
    return "approach", 0.0  # Only reached by floating point rounding at the very end


def bot_inputs(bot, target, dt):
    # Scripted bot: Uses only the two fighter dicts and its own timer, never random or the real clock
    bot["bot_t"] += dt
    inputs = {"left": False, "right": False, "jump": False, "punch": False, "kick": False, "block": False}
    bot["warning"] = False

    name, seg_t = current_segment(bot["bot_t"])
    gap = abs(bot["x"] - target["x"]) - FIGHTER_W # Empty space between the two fighters
    toward = "left" if target["x"] < bot["x"] else "right"
    away = "right" if toward == "left" else "left"

    if name == "approach":
        if gap > BOT_RANGE:
            inputs[toward] = True
    elif name == "retreat":
        inputs[away] = True
    elif name == "guard":
        inputs["block"] = True
    elif name in ("punch", "kick"):
        if seg_t < BOT_WARN:
            bot["warning"] = True  # Stand still and telegraph so the player has time to react
        elif seg_t < BOT_WARN + BOT_PRESS and gap <= BOT_RANGE and bot["attack_t"] < 0:
            inputs[name] = True  # The step name is also the attack name
    return inputs

def attack_rect(fighter):
    # Returns the hitbox as (x, y, w, h), or None if the fighter is not in an attack's active window
    if fighter["attack_kind"] is None:
        return None
    atk = ATTACKS[fighter["attack_kind"]]
    t = fighter["attack_t"]
    if t < atk["start"] or t > atk["end"]:
        return None
    if fighter["facing"] == 1:
        x = fighter["x"] + FIGHTER_W  # Starts at the right edge
    else:
        x = fighter["x"] - atk["w"]  # Starts at the left edge
    y = fighter["y"] + atk["y_off"]
    return (x, y, atk["w"], atk["h"])


def boxes_overlap(a, b):
    # Each box is (x, y, w, h), and boxes that only touch at an edge do not count
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


def resolve_hit(attacker, defender):
    # Needs both fighters, so it cannot live inside step_fighter
    hitbox = attack_rect(attacker)
    if hitbox is None or attacker["hit_done"]:
        return
    defender_box = (defender["x"], defender["y"], FIGHTER_W, FIGHTER_H)
    if boxes_overlap(hitbox, defender_box):
        damage = ATTACKS[attacker["attack_kind"]]["damage"]
        if defender["blocking"]:
            damage = damage // BLOCK_DIVISOR  # Fighters always face each other, so a block covers the front
        defender["health"] = max(0, defender["health"] - damage)
        attacker["hit_done"] = True


def separate(mover, blocker):
    # Pushes the mover out of the blocker, so the blocker is never shoved
    overlap_x = FIGHTER_W - abs(mover["x"] - blocker["x"])
    overlap_y = FIGHTER_H - abs(mover["y"] - blocker["y"])
    if overlap_x > 0 and overlap_y > 0:
        if mover["x"] < blocker["x"]:
            mover["x"] -= overlap_x  # Mover is on the left, so push left
        else:
            mover["x"] += overlap_x  # Mover is on the right, so push right
        # Keep the mover inside the window
        mover["x"] = max(0, min(mover["x"], WIDTH - FIGHTER_W))


def step_world(world, player_inputs, dt):
    # Runs one whole tick of the game, and does nothing once someone is knocked out
    if is_ko(world):
        return
    player = world["player"]
    npc = world["npc"]

    # Each fighter always faces the other one
    player["facing"] = 1 if npc["x"] > player["x"] else -1
    npc["facing"] = -player["facing"]

    # The bot decides from the current state, then both fighters step
    npc_inputs = bot_inputs(npc, player, dt)
    step_fighter(player, player_inputs, dt)
    step_fighter(npc, npc_inputs, dt)

    separate(player, npc)

    resolve_hit(player, npc)
    resolve_hit(npc, player)