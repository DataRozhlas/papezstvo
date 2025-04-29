import os
import time
import requests
import json

def get_all_popes():
    """
    Query Wikidata for all entities who have held the position of Pope (Q19546)
    Returns data with human-readable labels
    """
    # Wikidata SPARQL endpoint
    url = "https://query.wikidata.org/sparql"
    
    # SPARQL query to get all popes with their labels
    # This query gets all entities that held position "pope" (Q19546)
    query = """
    SELECT ?pope ?popeLabel ?birth ?death ?birthPlaceLabel ?startDate ?endDate WHERE {
      ?pope wdt:P39 wd:Q172748.  # position held: pope
      OPTIONAL { ?pope wdt:P569 ?birth. }  # birth date
      OPTIONAL { ?pope wdt:P570 ?death. }  # death date
      OPTIONAL { ?pope wdt:P19 ?birthPlace. }  # place of birth
      OPTIONAL { 
        ?pope p:P39 ?statement.
        ?statement ps:P39 wd:Q172748.
        OPTIONAL { ?statement pq:P580 ?startDate. }  # start date of being pope
        OPTIONAL { ?statement pq:P582 ?endDate. }  # end date of being pope
      }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    ORDER BY ?startDate
    """
    
    # Make request with format specified as JSON
    headers = {"Accept": "application/json"}
    params = {"query": query, "format": "json"}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def get_detailed_pope_data(pope_id):
    """
    Get detailed data for a specific pope entity including labels
    """
    entity_id = pope_id.split('/')[-1]
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.json"
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting data for {pope_id}: {response.status_code}")
        return None

def save_pope_data():
    """
    Save all pope data to JSON files in the downloads/popes directory
    """
    # Create directory if it doesn't exist
    os.makedirs("downloads/antipopes", exist_ok=True)
    
    # Get list of all popes
    popes_data = get_all_popes()
    if not popes_data:
        print("Failed to retrieve popes data")
        return
    
    # Extract pope entities
    popes = popes_data["results"]["bindings"]
    print(f"Found {len(popes)} antipopes")
    
    # For each pope, get detailed data and save to file
    for i, pope in enumerate(popes):
        pope_id = pope["pope"]["value"]
        pope_label = pope["popeLabel"]["value"]
        entity_id = pope_id.split('/')[-1]
        
        print(f"Downloading data for {pope_label} ({entity_id}) - {i+1}/{len(popes)}")
        
        # Get detailed data
        detailed_data = get_detailed_pope_data(pope_id)
        
        if detailed_data:
            # Save to file
            filename = f"downloads/antipopes/{entity_id}_{pope_label.replace(' ', '_')}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(detailed_data, f, ensure_ascii=False, indent=2)
            
            # Be nice to the Wikidata servers by waiting between requests
            time.sleep(1)
        else:
            print(f"Skipping {pope_label} due to error")
    
    # Save the overview data as well
    with open("downloads/antipopes/all_popes_summary.json", "w", encoding="utf-8") as f:
        json.dump(popes_data, f, ensure_ascii=False, indent=2)
    
    print("Download complete!")

if __name__ == "__main__":
    save_pope_data()

