import re

def encode(string):
    return string.encode('utf8', 'surrogateescape')

def decode(string):
    return string.decode('utf8', 'replace')

def rreplace(s, old, new, occurrence=1):
    li = s.rsplit(old, occurrence)
    return new.join(li)

def inline(string, lower=False):
    s = re.sub('[\n\r\t]', ' ', string)
    s = re.sub(' +', ' ', s)
    return s.strip().lower() if lower else s.strip()
