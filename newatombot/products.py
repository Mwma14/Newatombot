# products.py
import config

# Helper function to calculate credit cost based on the central ratio
def calculate_credit_cost(price_mmk: int) -> float:
    """Calculates credit cost from MMK, rounding to 2 decimal places."""
    return round(price_mmk * config.CREDIT_PER_MMK, 2)

INITIAL_PRODUCTS = {
    "ATOM": {
        "Points": [
            {"id": "atom_pts_500", "name": "500 Points", "price_mmk": 1500},
            {"id": "atom_pts_1000", "name": "1000 Points", "price_mmk": 3000},
            {"id": "atom_pts_2000", "name": "2000 Points", "price_mmk": 5500},
        ],
        "Mins": [
            {"id": "atom_min_50", "name": "Any-net 50 Mins", "price_mmk": 800},
            {"id": "atom_min_100", "name": "Any-net 100 Mins", "price_mmk": 1550},
            {"id": "atom_min_150", "name": "Any-net 150 Mins", "price_mmk": 2300},
        ],
        "Internet Packages": [
            {"id": "atom_pkg_15k", "name": "15k Plan", "price_mmk": 10900},
            {"id": "atom_pkg_25k", "name": "25k Plan", "price_mmk": 19200},
        ],
        "Data": [
            {"id": "atom_data_1gb", "name": "1GB Data", "price_mmk": 1000},
        ],
        "Beautiful Numbers": [],
    },
    "MYTEL": {
        "Data": [
            {"id": "mytel_data_1k", "name": "1000MB", "price_mmk": 950, "extra": "(တစ်လ)"},
            {"id": "mytel_data_3333", "name": "3333MB", "price_mmk": 3200, "extra": "(7ရက်)"},
            {"id": "mytel_data_5k", "name": "5000MB", "price_mmk": 4500, "extra": "(15ရက်)"},
        ],
        "Mins": [
            {"id": "mytel_min_90", "name": "90 Mins", "price_mmk": 870, "extra": "(တစ်လ)"},
            {"id": "mytel_min_180", "name": "180 Mins", "price_mmk": 1700, "extra": "(တစ်လ)"},
            {"id": "mytel_min_any58", "name": "Any-net 58", "price_mmk": 1000, "extra": "(15day)"},
        ],
        "Plan Packages": [
            {"id": "mytel_plan_10k", "name": "10000MB Plan", "price_mmk": 9000, "extra": "👉 သက်တမ်း ၁လ\n👉 ƁƖԼԼချေး မရ / Ɓ2Ɓ မရ"},
            {"id": "mytel_plan_14g", "name": "14GB + 1050min", "price_mmk": 13300, "extra": "👉 သက်တမ်း ၁လ\n👉 ƁƖԼԼချေး မရ / Ɓ2Ɓ မရ"},
            {"id": "mytel_plan_20k", "name": "20000MB Plan", "price_mmk": 17800, "extra": "👉 သက်တမ်း ၁လ\n👉 ƁƖԼԼချေး မရ / Ɓ2Ɓ မရ"},
        ],
        "Beautiful Numbers": [],
    },
    "OOREDOO": {
        "Data": [
            {"id": "ooredoo_data_1g", "name": "1GB", "price_mmk": 950, "extra": "(10day)"},
            {"id": "ooredoo_data_2.9g", "name": "2.9GB", "price_mmk": 2700},
            {"id": "ooredoo_data_5.8g", "name": "5.8GB", "price_mmk": 5400},
            {"id": "ooredoo_data_8.7g", "name": "8.7GB", "price_mmk": 8100},
        ],
        "Plan Packages": [
            {"id": "ooredoo_plan_11.6g", "name": "11.6GB Plan", "price_mmk": 10800, "extra": "👉 သက်တမ်း ၁လ\n👉 ƁƖԼԼချေး မရ / Ɓ2Ɓ မရ"},
            {"id": "ooredoo_plan_4.9g", "name": "4.9GB + ONNET100", "price_mmk": 5150, "extra": "👉 သက်တမ်း ၁လ\n👉 ƁƖԼԼချေး မရ / Ɓ2Ɓ မရ"},
            {"id": "ooredoo_plan_9.8g", "name": "9.8GB + ONNET300", "price_mmk": 10200, "extra": "👉 သက်တမ်း ၁လ\n👉 ƁƖԼԼချေး မရ / Ɓ2Ɓ မရ"},
        ],
         "Beautiful Numbers": [],
    },
    "MPT": {
        "Data": [
            {"id": "mpt_data_1.1g", "name": "1.1GB", "price_mmk": 950},
            {"id": "mpt_data_2.2g", "name": "2.2GB", "price_mmk": 1950},
        ],
        "Minutes": [
            {"id": "mpt_min_any55", "name": "Any-net 55 MIN", "price_mmk": 950},
            {"id": "mpt_min_any115", "name": "Any-net 115 MIN", "price_mmk": 1850},
            {"id": "mpt_min_on170", "name": "On-net 170 MIN", "price_mmk": 1800},
        ],
        "Plan Packages": [
            {"id": "mpt_plan_15k", "name": "15K Plan", "price_mmk": 14400},
            {"id": "mpt_plan_25k", "name": "25K Plan", "price_mmk": 24400},
        ],
         "Beautiful Numbers": [],
    }
}