import urllib2
import json
import re

def getAnimeList(username):
    apiUrl = "http://mal-api.com/animelist/" + username
    f = urllib2.urlopen(apiUrl)
    j = json.loads(f.read())
    return j["anime"]
    
def getUserId(username):
    profileUrl = "http://myanimelist.net/profile/" + username
    f = urllib2.urlopen(profileUrl)
    
    profileHtml = f.read()
    
    userIdRegEx = r'<a href="http://myanimelist.net/myfriends.php\?go=add&id=([0-9]+)" title=".*">Send Friend Request</a>'
    
    m = re.search(userIdRegEx, profileHtml)
    
    if m is None:
        raise Exception("No RegEx match in getUserId for %s" % username)
        
    return m.group(1)
    
def getRandomUsername():
    # Use the url for getting a random list
    url = "http://myanimelist.net/users.php?lucky=1"
    f = urllib2.urlopen(url)

    # Extract the username from the title
    usernameRegex = r"<title>([\S]+)'s Anime List - MyAnimeList.net</title>"
    match = re.search(usernameRegex, f.read())

    if match is None:
        raise Exception("No regular expression match")
        
    return match.group(1)
    
def getRecentOnlineUsernames():
    url = "http://myanimelist.net/users.php"
    f = urllib2.urlopen(url)
    
    # Extract all matches of a profile url
    usernameRegex = r'<a href="http://myanimelist.net/profile/([\S]+)">[\S]+</a>'
    
    match = re.findall(usernameRegex, f.read())
    
    if match is None:
        return []
        
    return match
        
    
       