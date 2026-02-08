BIOMES = [
    {
        "name": "FARM",
        "sky": (210, 235, 255),
        "hill1": (180, 230, 190),
        "hill2": (165, 220, 180),
        "ground": (200, 235, 200),
        "line": (70, 120, 70),
        "obstacle_color": (80, 50, 25),
        "enemy_rate_mult": 1.0,
        "lob_chance": 0.35,
        "pickup_weights": {"corn": 0.62, "shield": 0.14, "rapid": 0.14, "magnet": 0.10},
    },
    {
        "name": "CITY",
        "sky": (225, 225, 235),
        "hill1": (170, 170, 180),
        "hill2": (145, 145, 160),
        "ground": (210, 210, 220),
        "line": (90, 90, 100),
        "obstacle_color": (60, 60, 70),
        "enemy_rate_mult": 1.15,
        "lob_chance": 0.22,
        "pickup_weights": {"corn": 0.55, "shield": 0.16, "rapid": 0.19, "magnet": 0.10},
    },
    {
        "name": "VOLCANO",
        "sky": (250, 220, 200),
        "hill1": (210, 150, 120),
        "hill2": (185, 120, 95),
        "ground": (235, 200, 180),
        "line": (150, 70, 40),
        "obstacle_color": (120, 60, 40),
        "enemy_rate_mult": 1.35,
        "lob_chance": 0.50,
        "pickup_weights": {"corn": 0.52, "shield": 0.18, "rapid": 0.18, "magnet": 0.12},
    },
    {
        "name": "NIGHT",
        "sky": (55, 60, 80),
        "hill1": (70, 90, 110),
        "hill2": (50, 70, 95),
        "ground": (90, 110, 120),
        "line": (20, 30, 40),
        "obstacle_color": (30, 30, 40),
        "enemy_rate_mult": 1.10,
        "lob_chance": 0.30,
        "pickup_weights": {"corn": 0.58, "shield": 0.18, "rapid": 0.14, "magnet": 0.10},
    },
]

BIOME_DURATION = 90.0

def pick_weighted(weights, r):
    c = 0.0
    for k in ["corn", "shield", "rapid", "magnet"]:
        c += weights[k]
        if r <= c:
            return k
    return "corn"
