

def encode(string):
    return string.encode('utf8', 'surrogateescape')

def decode(string):
    return string.decode('utf8', 'replace')

def rreplace(s, old, new, occurrence=1):
    li = s.rsplit(old, occurrence)
    return new.join(li)
