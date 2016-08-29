import csv
import logging

log = logging.getLogger(__name__)


def load(file, splits=1):
    content = []
    with open(file, 'r', encoding='utf8') as tsvin:
        reader = csv.DictReader(tsvin, delimiter='\t')
        for row in reader:
            dictionary = {}
            for k in row:
                dictionary[k] = row[k]
            content.append(dictionary)
    res = []
    for _ in range(splits):
        res.append([])
    for i, dictionary in enumerate(content):
        rr = i % splits
        res[rr].append(dictionary)
    return res
