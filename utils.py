

def getlastblock(storage):
    hollowchain = storage.getchain(buildcascade=False)
    if not hollowchain:
        return False
    
    return hollowchain[-1]