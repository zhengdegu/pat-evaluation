#!/usr/bin/env python3
import csv
import requests
with open("/tmp/result.csv", 'w') as result:
    writer = csv.writer(result)
    with open("test.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            patid = row['patid']
            value = float(row['value'])
            url = 'http://gitlab.intelipev.com:9090/api/evaluation/start?patid={}&reload=1'.format(
                patid)
            # url = 'http://localhost:5000/api/evaluation/start?patid={}&reload=1'.format(
            #     patid)
            # print(url)
            r = requests.get(url)
            r = r.json()
            low_price = r['price'][0]
            high_price = r['price'][1]
            print(patid)
            writer.writerow(
                [patid, "{:.2f}-{:.2f}".format(low_price, high_price)])
