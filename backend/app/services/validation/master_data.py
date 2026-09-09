from typing import Dict, List, Any

# Indian Administrative Master Hierarchy for Hackathon Prototype
# Covers major states with districts, mandals/tehsils, and villages

INDIAN_ADMIN_HIERARCHY: Dict[str, Dict[str, Dict[str, List[str]]]] = {
    "Telangana": {
        "Ranga Reddy": {
            "Shamshabad": ["Mamidipally", "Gollapally", "Kothwalguda", "Satamrai", "Chinnagolkonda"],
            "Rajendranagar": ["Budvel", "Attapur", "Bandlaguda", "Hyderguda"],
            "Gandipet": ["Kokapet", "Narsingi", "Manikonda", "Gandipet", "Puppalguda"]
        },
        "Medchal-Malkajgiri": {
            "Ghatkesar": ["Ankushapur", "Edulabad", "Kondapur", "Pocharam"],
            "Keesara": ["Bogaram", "Cheeryal", "Nagaram", "Yadgarpally"]
        }
    },
    "Maharashtra": {
        "Pune": {
            "Haveli": ["Wagholi", "Hadapsar", "Manjari", "Khadakwasla", "Uruli Kanchan"],
            "Mulshi": ["Hinjawadi", "Maan", "Marunji", "Pirangut", "Kasarsai"]
        },
        "Nagpur": {
            "Nagpur Rural": ["Besa", "Beltarodi", "Wadi", "Hingna"]
        }
    },
    "Uttar Pradesh": {
        "Lucknow": {
            "Mohanlalganj": ["Bakas", "Khujauli", "Dhanuwa", "Kankaha"],
            "Bakshi Ka Talab": ["Kathwara", "Rampur", "Bhargawan", "Asthir"]
        }
    },
    "Karnataka": {
        "Bengaluru Rural": {
            "Devanahalli": ["Vijayapura", "Budigere", "Channarayapatna", "Bidalur"],
            "Nelamangala": ["T.Begur", "Doddabele", "Sompura", "Solur"]
        }
    }
}

VALID_AREA_UNITS = [
    "Acres", "Hectares", "Guntas", "Guntha", "Bigha", "Biswa", 
    "Sq. Yards", "Sq. Meters", "Cent", "Acre"
]

VILLAGE_CENTROIDS: Dict[str, Dict[str, float]] = {
    "Mamidipally": {"lat": 17.2530, "lng": 78.4410},
    "Gollapally": {"lat": 17.2610, "lng": 78.4280},
    "Kothwalguda": {"lat": 17.2750, "lng": 78.3950},
    "Kokapet": {"lat": 17.3910, "lng": 78.3240},
    "Narsingi": {"lat": 17.3780, "lng": 78.3580},
    "Puppalguda": {"lat": 17.4020, "lng": 78.3490},
    "Wagholi": {"lat": 18.5790, "lng": 73.9820},
    "Hinjawadi": {"lat": 18.5910, "lng": 73.7380},
    "Pirangut": {"lat": 18.5130, "lng": 73.6790},
    "Bakas": {"lat": 26.7450, "lng": 81.0120},
    "Budigere": {"lat": 13.1180, "lng": 77.7420},
    "Default": {"lat": 17.3850, "lng": 78.4867}  # Hyderabad regional fallback
}

def validate_hierarchy(state: str, district: str, mandal: str, village: str) -> bool:
    """Verifies that the administrative chain State -> District -> Mandal -> Village is valid."""
    state_clean = state.strip()
    dist_clean = district.strip()
    mandal_clean = mandal.strip()
    village_clean = village.strip()
    
    # Case-insensitive lookup
    for s_name, districts in INDIAN_ADMIN_HIERARCHY.items():
        if s_name.lower() == state_clean.lower():
            for d_name, mandals in districts.items():
                if d_name.lower() == dist_clean.lower():
                    for m_name, villages in mandals.items():
                        if m_name.lower() == mandal_clean.lower():
                            for v_name in villages:
                                if v_name.lower() == village_clean.lower():
                                    return True
    return False

def get_village_centroid(village: str) -> Dict[str, float]:
    for name, coords in VILLAGE_CENTROIDS.items():
        if name.lower() == village.lower():
            return coords
    return VILLAGE_CENTROIDS["Default"]
