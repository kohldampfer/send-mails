import termcolor
import colorama
import bs4
import urllib.request
import urllib.parse
import re
import email.mime.multipart
import email.mime.text
import smtplib
import os.path
import configparser

DEBUG = True
LISTOFLINKS = "listoflinks.txt"
ALL_LINKS = []
LINKSALREADYSENT_FILE = "linksalreadysent.txt"
LINKSALREADYSENT = []

config = configparser.ConfigParser()
config.read("emailsettings.ini")

_host = config['EmailSettings']['Host']
_port = config['EmailSettings']['Port']
_sender = config['EmailSettings']['Sender']
_receiver = config['EmailSettings']['Receiver']
_password = config['EmailSettings']['Password']
smtp_obj = None

def printDebug(message):
    if DEBUG == True:
        print(termcolor.colored("[D] {0}".format(message), 'yellow'))

def readFile(fname):
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
        
def isLinkInGlobalLinkList(link):
    stripped_link = link.strip()
    
    if link:
        if link in ALL_LINKS:
            return True
    
    return False

def getAllLinks(url):
    url_to_parse = url.strip()
    
    printDebug("Try to parse url '{0}'".format(url_to_parse))
    
    if url_to_parse:
    
        domain = getDomain(url_to_parse)
    
        request = urllib.request.Request(url_to_parse,
            headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36' })
        data = urllib.request.urlopen(request)
        content = data.read()
        
        if domain == "www.youtube.com" or domain == "youtube.com":
            yt_links = re.findall("\/watch\?v=[^\"]+", str(content))
            for yl in yt_links:
                ALL_LINKS.append("https://youtube.com{0}".format(yl))
        else:
            soup = bs4.BeautifulSoup(content, features="lxml")
            
            links = []
            for s in soup.find_all('a', href=True):
                correctedLink = correctLink(url_to_parse, s['href'])
                
                if correctedLink and not isLinkInGlobalLinkList(correctedLink):
                    ALL_LINKS.append(correctedLink)

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
        
    if stripped_found[0:11] == "javascript:":
        return None
        
    if stripped_found[0:1] == "/":
        stripped_found = "{0}://{1}{2}".format(searched_protocol, searched_domain, foundLink)
    
    if not (stripped_found[0-7] == "http://" or not stripped_found[0-8] == "https://"):
        stripped_found = "{0}://{1}/{2}".format(searched_protocol, searched_domain, foundLink)
        
    pattern = ""
    if searched_domain == "stackoverflow.com":
        pattern = "questions/[0-9]+"
    elif searched_domain == "superuser.com":
        pattern = "questions/[0-9]+"
    elif searched_domain == "security.stackexchange.com":
        pattern = "questions/[0-9]+"
    elif searched_domain == "wordpress.stackexchange.com":
        pattern = "questions/[0-9]+"
    elif searched_domain == "unix.stackexchange.com":
        pattern = "questions/[0-9]+"
    elif searched_domain == "askubuntu.com":
        pattern = "questions/[0-9]+"
    elif searched_domain == "www.bloggerei.de":
        pattern = "c.php\?lid=[0-9]+"
    elif searched_domain == "www.rss-verzeichnis.de":
        pattern = "[0-9]+[-a-z]+"
    elif searched_domain == "www.bloggeramt.de":
        pattern = "/blogverzeichnis/"
    elif searched_domain == "www.blogwolke.de":
        pattern = "www.blogwolke.de/[-0-9a-z]+/$"
    elif searched_domain == "jamesmckay.net":
        pattern = "[0-9]+/[0-9]+"
    elif searched_domain == "blog.silentsignal.eu":
        pattern = "[0-9]+/[0-9]+/[0-9]+/[a-z0-9]"
    
    if re.search(pattern, stripped_found):
        return stripped_found
    
    return None

def getTitleFromUrl(url):
    stripped_url = url.strip()
    
    if stripped_url:
        domain = getDomain(stripped_url)
        
        request = urllib.request.Request(stripped_url,
        headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36' })
        data = urllib.request.urlopen(request)
        content = data.read()
        
        if domain == "www.youtube.com" or domain == "youtube.com":
            title_search = re.search(r'"title":"[^"]+"', str(content))
            title = title_search.group(0)
            title = title.replace("\"title\":\"", "")
            title = title.replace("\"", "")
        else:
            soup = bs4.BeautifulSoup(content, features="lxml")
            title = soup.find_all('title')[0].text
        
        return title
    
    return None

def sendMail(url):
    stripped_url = url.strip()
    
    if stripped_url:
        domain = getDomain(stripped_url)
        title = getTitleFromUrl(stripped_url)
        
        msg = email.mime.multipart.MIMEMultipart()
        msg['From'] = _sender
        msg['To'] = _receiver
        msg['Subject'] = "[{0}] {1}".format(domain, title)
        body = email.mime.text.MIMEText('''
There is new content on site {0}:
Title: {1}
Url: {2}
'''.format(domain, title, stripped_url))

        msg.attach(body)
        
        text = msg.as_string()
        smtp_obj.sendmail(_sender, _receiver, text)
        
        appendToSentLinks(stripped_url)

def appendToSentLinks(url):
    with open(LINKSALREADYSENT_FILE, "a") as file:
        file.write("{0}\n".format(url))

#
# here starts the program
#
colorama.init()

#
# login to smtp
#
print("Try to get access to SMTP ...")
printDebug("Host is {0}".format(_host))
printDebug("Port is {0}".format(_port))
smtp_obj = smtplib.SMTP(_host, _port)
smtp_obj.ehlo()
smtp_obj.starttls()
smtp_obj.ehlo()
smtp_obj.login(_sender, _password)

#
# read file with urls which should be parsed
#
list_of_urls = readFile(LISTOFLINKS)
for l_url in list_of_urls:
    getAllLinks(l_url)

#
# read file with links, which already were sent
#
if os.path.isfile(LINKSALREADYSENT_FILE):
    LINKSALREADYSENT = readFile(LINKSALREADYSENT_FILE)
    
if DEBUG == True:
    printDebug("Show all found links ...")
    for l in ALL_LINKS:
        printDebug("Found link {0}".format(l))

email_counter = 0
for l in ALL_LINKS:
    try:
        if email_counter < 3:
            if not l in LINKSALREADYSENT:
                print("Processing link {0} ...".format(l))
                # send mail and save it into a file
                sendMail(l)
                email_counter = email_counter + 1
    except Exception as e_inner:
        print("An error occurred.")
        print(e_inner)


print("Close SMTP connection ...")
smtp_obj.quit()

print("End")
