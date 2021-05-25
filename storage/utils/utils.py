

def addquotes(string):
    if not type(string) == str:
        string = str(string)

    return "\"{}\"".format(string.strip('"'))