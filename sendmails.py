import termcolor
import colorama
import bs4
import urllib.request
import urllib.parse

DEBUG = True
LISTOFLINKS = "listoflinks.txt"

def printDebug(message):
    if DEBUG == True:
        print(termcolor.colored("[D] {0}".format(message), 'yellow'))

def readLine(fname):
    printDebug("Read file '{0}'".format(fname))
    with open(fname) as f:
        lines = f.read().splitlines()
        
    return lines
    
def getDomain(url):
    stripped_url = url.strip()
    if stripped_url:
        parsed_uri = urllib.parse.urlparse(stripped_url)
        return "{uri.netloc}".format(uri=parsed_uri)
        
def getProtocol(url):
    stripped_url = url.strip()
    if stripped_url:
        parsed_uri = urllib.parse.urlparse(stripped_url)
        return "{uri.scheme}".format(uri=parsed_uri)

def getAllLinks(url):
    url_to_parse = url.strip()
    
    printDebug("Try to parse url '{0}'".format(url_to_parse))
    
    if url_to_parse:
        request = urllib.request.Request(url_to_parse,
            headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36' })
        data = urllib.request.urlopen(request)
        content = data.read()
        soup = bs4.BeautifulSoup(content, features="lxml")
        
        links = []
        for s in soup.find_all('a', href=True):
            correctedLink = correctLink(url_to_parse, s['href'])
            
            if correctedLink:
                links.append(correctedLink)
        
        return links

#
# this function corrects links found on a webpage.
# some of these functions shouldn't be send later
# because they are not useful in any way.
#
def correctLink(searchedUrl, foundLink):
    searched_protocol = getProtocol(searchedUrl)
    searched_domain = getDomain(searchedUrl)
    
    stripped_found = foundLink.strip()
    
    if not stripped_found:
        return None
    
    if stripped_found == "#":
        return None
        
    if stripped_found[0:1] == "/":
        return "{0}://{1}{2}".format(searched_protocol, searched_domain, foundLink)
        
    if stripped_found[0:11] == "javascript:":
        return None
    
    return stripped_found

#
# here starts the program
#
colorama.init()

list_of_urls = readLine(LISTOFLINKS)
for l_url in list_of_urls:
    links = getAllLinks(l_url)
    
    for l in links:
        printDebug("Found url: {0}".format(l))
