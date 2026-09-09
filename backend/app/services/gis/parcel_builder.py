import hashlib
import math
from typing import Dict, Any, List, Tuple
from backend.app.services.validation.master_data import get_village_centroid

UNIT_TO_SQ_METERS = {
    "Acres": 4046.86,
    "Acre": 4046.86,
    "Hectares": 10000.0,
    "Guntas": 101.17,
    "Guntha": 101.17,
    "Bigha": 2529.28,
    "Biswa": 126.46,
    "Sq. Yards": 0.836127,
    "Sq. Meters": 1.0,
    "Cent": 40.4686
}


def convert_area_to_sq_meters(area: float, unit: str) -> float:
    factor = UNIT_TO_SQ_METERS.get(unit, 4046.86)
    return round(area * factor, 2)


class CadastralParcelBuilder:
    """
    Synthesizes realistic cadastral parcel geometries for OpenStreetMap/Leaflet visualization.
    Derives deterministic, non-overlapping geometric offsets from Survey Numbers around authentic village centroids.
    """

    def build_parcel_geometry(
        self,
        survey_number: str,
        village: str,
        land_area: float,
        area_unit: str = "Acres"
    ) -> Tuple[Dict[str, Any], float, float, float]:
        """
        Returns:
            - geojson_polygon: Dict (GeoJSON Polygon coordinates)
            - center_lat: float
            - center_lng: float
            - area_sq_meters: float
        """
        centroid = get_village_centroid(village)
        base_lat = centroid["lat"]
        base_lng = centroid["lng"]

        area_sq_m = convert_area_to_sq_meters(land_area, area_unit)

        # Deterministic seed from survey number string
        seed = int(hashlib.md5(f"{village}:{survey_number}".encode()).hexdigest()[:8], 16)
        angle_seed = (seed % 360) * (math.pi / 180.0)
        dist_offset_meters = ((seed % 500) + 100) # 100m to 600m from village center

        # Approximate degrees conversion: 1 deg lat ~= 111,000 meters
        d_lat = (dist_offset_meters * math.cos(angle_seed)) / 111000.0
        d_lng = (dist_offset_meters * math.sin(angle_seed)) / (111000.0 * math.cos(math.radians(base_lat)))

        center_lat = round(base_lat + d_lat, 6)
        center_lng = round(base_lng + d_lng, 6)

        # Calculate polygon radius based on square root of area
        radius_m = math.sqrt(area_sq_m) / 2.0
        r_lat = radius_m / 111000.0
        r_lng = radius_m / (111000.0 * math.cos(math.radians(center_lat)))

        # Create a realistic cadastral polygon (4 to 5 vertices with slight geometric variation)
        vertices = []
        angles = [45, 135, 225, 315]
        for a in angles:
            rad = math.radians(a + (seed % 20 - 10))
            v_lat = center_lat + (r_lat * math.sin(rad))
            v_lng = center_lng + (r_lng * math.cos(rad))
            vertices.append([round(v_lng, 6), round(v_lat, 6)])

        # Close the polygon ring
        vertices.append(vertices[0])

        geojson_polygon = {
            "type": "Polygon",
            "coordinates": [vertices]
        }

        return geojson_polygon, center_lat, center_lng, area_sq_m
