from datetime import datetime, timezone
import pandas as pd
import os
import time
import requests as req
API_KEY='aeGsf6pRiFNcKlupDMxVGPH2g4iZ6api'
TOPIC = 'politics'
file_path = '../etl/data/articles.csv'

# Check if the file already exists
if os.path.exists(file_path):
    df = pd.read_csv(file_path)
else:
    df = pd.DataFrame()

for i in range(150):
    url = 'https://api.nytimes.com/svc/search/v2/articlesearch.json?q=' + TOPIC + '&api-key=' + API_KEY + '&page=' + str(i)
    response = req.get(url).json()
    time.sleep(12)  # Adjust based on the API's rate limit guidelines
    
    articles = []
    
    if 'response' in response and 'docs' in response['response']:
        docs = response['response']['docs']
        for doc in docs:
            filteredDoc = {}
            filteredDoc['title'] = doc['headline']['main']
            filteredDoc['abstract'] = doc['abstract']
            filteredDoc['paragraph'] = doc['lead_paragraph']
            filteredDoc['pub_date'] = doc['pub_date']
            articles.append(filteredDoc)
    else:
        print("No response or docs found in response:", response)
    
    df_new = pd.DataFrame(data=articles)
    
    # Append new data to existing DataFrame
    df = pd.concat([df, df_new], ignore_index=True)

# After all iterations, save the combined DataFrame to the CSV file
df.to_csv(file_path, index=False)

#df.to_csv('../etl/data/articles.csv', index=True)
