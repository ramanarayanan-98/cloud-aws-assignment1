import requests
import json


def scrape_func(term,offset,limit):
    api_url = f"https://api.yelp.com/v3/businesses/search?term={term}&location=manhattan&limit={limit}&offset={offset}"
    payload={}
    headers = {
    'Authorization': '<api-key>'
    }

    response = requests.request("GET", api_url, headers=headers, data=payload)
    restaurant_list = json.loads(response.text)["businesses"]
    return restaurant_list

def append_to_file(term,new_data):
    filename = f"{'_'.join(term.lower().split())}.json"
    try:
        file = open(filename,'x+')
        file_data = {}
        file_data["restaurants"] = []
    except:
        file = open(filename,'r+')
        file_data = json.load(file)
    
    for row in new_data:
        file_data["restaurants"].append(row)
    file.seek(0)
    json.dump(file_data, file, indent = 4)

def search_for(term):
    totalLimit = 1000
    limit = 50
    offset = 0
    while limit+offset <= totalLimit:
        output = scrape_func(term,offset,limit)
        append_to_file(term,output)
        offset += limit


if __name__ == "__main__":
    terms = ["Italian restaurants","Chinese Restaurants","Indian restaurants","Mexican restaurants", "Japanese restaurants"]
    for term in terms:
        search_for(term)
