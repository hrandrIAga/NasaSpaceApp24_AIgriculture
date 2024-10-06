import requests
from math import radians, sin, cos, sqrt, atan2

# Constantes
BASE_URL = "https://eonet.gsfc.nasa.gov/api/v3"
API_KEY = "qaOKyHuKUG7IekFbEmYIhskQkn0hggNLK6uZVDgR"
RAYON_TERRE = 6371  # en kilomètres

def get_all_events():
    """Récupère tous les événements de l'API EONET."""
    url = f"{BASE_URL}/events"
    params = {
        "api_key": API_KEY,
        "status": "all"  # Pour obtenir à la fois les événements ouverts et fermés
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erreur lors de la requête : {e}")
        return None

def extract_events_with_locations(events_data):
    """Extrait les événements avec leurs localisations."""
    events_with_locations = []
    if events_data and 'events' in events_data:
        for event in events_data['events']:
            event_info = {
                'id': event['id'],
                'title': event['title'],
                'description': event.get('description', 'Pas de description'),
                'categories': [cat['title'] for cat in event['categories']],
                'sources': [source['url'] for source in event.get('sources', [])],
                'geometries': []
            }
            
            for geometry in event['geometries']:
                if 'coordinates' in geometry:
                    event_info['geometries'].append({
                        'date': geometry['date'],
                        'type': geometry['type'],
                        'coordinates': geometry['coordinates']
                    })
            
            if event_info['geometries']:
                events_with_locations.append(event_info)
    
    return events_with_locations

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calcule la distance entre deux points en utilisant la formule de Haversine."""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = RAYON_TERRE * c
    return distance

def find_nearby_events(lat, lon, events, rayon=20):
    """Trouve les événements proches dans un rayon donné."""
    nearby_events = []
    for event in events:
        for geometry in event['geometries']:
            if geometry['type'] == 'Point':
                event_lon, event_lat = geometry['coordinates']
                distance = calculate_distance(lat, lon, event_lat, event_lon)
                if distance <= rayon:
                    nearby_events.append({
                        'id': event['id'],
                        'title': event['title'],
                        'distance': round(distance, 2),
                        'date': geometry['date']
                    })
                    break  # On ne prend que la première géométrie qui correspond
    return nearby_events

def main():
    # Récupération de tous les événements
    all_events_data = get_all_events()
    
    if all_events_data:
        # Extraction des événements avec leurs localisations
        events_with_locations = extract_events_with_locations(all_events_data)
        
        print(f"Nombre total d'événements récupérés : {len(events_with_locations)}")
        
        # Test de la fonction find_nearby_events
        lat_test, lon_test = 40.7128, -74.0060  # Coordonnées de New York City
        nearby = find_nearby_events(lat_test, lon_test, events_with_locations)
        
        print(f"\nÉvénements proches de la latitude {lat_test} et longitude {lon_test}:")
        for event in nearby:
            print(f"- {event['title']} (ID: {event['id']}) à {event['distance']} km, Date: {event['date']}")
    else:
        print("Impossible de récupérer les données des événements.")

if __name__ == "__main__":
    main()
