valid_playlists = ['1v1','2v2','3v3','Hoops','Rumble','Dropshot','Snowday','Tournaments','Un-Ranked']
valid_options = ["mmr","div"]

def getArgs(params):
    hiddenPlaylists = []
    hiddenOptions = []
    args = params._list
    for key,value in args:
        value = value.lower().capitalize()
        if value == "False":
            if key in valid_playlists:
                hiddenPlaylists.append(key)
            if key in valid_options:
                hiddenOptions.append(key)
    return hiddenPlaylists,hiddenOptions

def filterRank(rank_data, hiddenPlaylists, hiddenOptions):
    print()