#import logging

import getpass
import urllib,urllib2
from optparse import OptionParser
from HTMLParser import HTMLParser
import ssl

PATH_TO_LOGIN="/login/"


#LOG_FILE="c:/temp/log1.txt"
class Sender(object):
    def __init__(self,url):
        #para que no verifique el certificado
        self.context=ssl.create_default_context()
        self.context.check_hostname=False
        self.context.verify_mode=ssl.CERT_NONE

        self.cookieHandler = urllib2.HTTPCookieProcessor()
        self.httpsHandler=urllib2.HTTPSHandler(context=self.context)
        #self.opener.add_handler(self.httpsHandler)
        self.opener=urllib2.build_opener(self.cookieHandler,self.httpsHandler)
        self.opener.add_handler(self.cookieHandler)
        
        urllib2.install_opener( self.opener )
        self.csrf_cookie = None
        self.sessionid=None
        self.cookies=[]
        self.options=None
        self.baseUrl=url

    def initForm(self,url):
        #basically to get the coresponding csrftoken for the post
        url=self.baseUrl+"/"+url+"/"
        print url
        page = self.opener.open( url )

        # attempt to get the csrf token from the cookie jar

        for cookie in self.cookieHandler.cookiejar:
            if cookie.name == 'csrftoken':
                self.csrf_cookie = cookie
            if cookie.name == 'sessionid':
                self.sessionid = cookie
        if not cookie:
            raise IOError( "No csrf cookie found" )
    
    def search(self,query,filter):
        url=self.baseUrl+"/search_line/"

        params = {'myquery':query,'myfilter':filter,'csrfmiddlewaretoken': self.csrf_cookie.value,'sessionid':self.sessionid.value}
        #params = {'myquery':query,'myfilter':filter,'csrfmiddlewaretoken': self.csrf_cookie.value}
        data=urllib.urlencode(params)
        request = urllib2.Request(url, data)
        request.add_header( 'Referer', url )
        request.add_header('User-Agent',"Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)")


        salida=urllib2.urlopen(request)
        lineas=""
        h=HTMLParser()
        for l in salida.readlines():
            if l!="\n":lineas+=h.unescape(l)
        return lineas
        #salida=json.load(salida)
        #return salida

    def searchDeleteLine(self,myquery,myfilter):
        url=self.baseUrl+"/search_delete_line/"

        params = {'myquery':myquery,'myfilter':myfilter,'csrfmiddlewaretoken': self.csrf_cookie.value,'sessionid':self.sessionid.value}
        #params = {'myquery':query,'myfilter':filter,'csrfmiddlewaretoken': self.csrf_cookie.value}
        data=urllib.urlencode(params)
        request = urllib2.Request(url, data)
        request.add_header( 'Referer', url )
        request.add_header('User-Agent',"Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)")


        salida=urllib2.urlopen(request)
        lineas=""
        h=HTMLParser()
        for l in salida.readlines():
            if l!="\n":lineas+=h.unescape(l)
        return lineas
        #salida=json.load(salida)
        #return salida

    def addLine(self,texto):
        url=self.baseUrl+"/add_line/"

        params = {'text':texto,'csrfmiddlewaretoken': self.csrf_cookie.value,'sessionid':self.sessionid.value}
        #params = {'myquery':query,'myfilter':filter,'csrfmiddlewaretoken': self.csrf_cookie.value}
        data=urllib.urlencode(params)
        request = urllib2.Request(url, data)
        request.add_header( 'Referer', url )
        request.add_header('User-Agent',"Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)")

        try:
            result=urllib2.urlopen(request)
            if result.code==200:salida="File added successfully."
            else:salida="File not added. error:"+str(result.code)
        except:
            salida="Something went wrong."
            
        
        return salida




    def login( self, username=None, password=None ):
        url=self.baseUrl+"/login/"
        # prompt for the username (if needed), password
        if username == None:
            username = getpass.getpass( 'Username: ' )
        if password == None:
            password = getpass.getpass( 'Password: ' )

        login_page = self.opener.open( url )

        # attempt to get the csrf token from the cookie jar

        for cookie in self.cookieHandler.cookiejar:
            if cookie.name == 'csrftoken':
                self.csrf_cookie = cookie
            if cookie.name == 'sessionid':
                self.sessionid = cookie
        if not cookie:
            raise IOError( "No csrf cookie found" )


        # login using the usr, pwd, and csrf token

        login_data = urllib.urlencode( dict(
                username=username, password=password,
                csrfmiddlewaretoken=self.csrf_cookie.value
                #sessionid=self.sessionid.value

        ) )
        #self.log.debug( "login_data: %s" % login_data )

        req = urllib2.Request( url, login_data )
        req.add_header( 'Referer', url )
        req.add_header('User-Agent',"Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)")
        response = urllib2.urlopen( req )

        #esto puede ser redundante
        for cookie in self.cookieHandler.cookiejar:
            self.cookies.append({cookie.name:cookie.value})
            if cookie.name == 'sessionid':
                self.sessionid = cookie        


        if not self.sessionid:
            raise IOError( 'Authentication refused' )







 
class OptionParserWrapper(OptionParser):
    #needed in order to format the help text. sucks.
    def format_epilog(self, formatter):
        return self.epilog


from optparse import OptionParser
import os

if __name__ == '__main__':

    USAGE = "usage: %prog [options] "
    EPILOGUE = """
    pcfind online
    
    """

    parser = OptionParserWrapper(usage=USAGE, epilog=EPILOGUE)
    parser.add_option("-q", "--query", help="lines to include have this text")
#     parser.add_option("-q", "--askName", action='store_true', default=False,help="option for flags")
    parser.add_option("-f", "--filter", default="",help="text to exclude")
    parser.add_option("-a", "--add", help="add line to database")
    parser.add_option("-d", "--delete", help="add line to database")
    parser.add_option("-u", "--url", help="url")
    parser.add_option("-l", "--login", help="login")

    



    (options, args) = parser.parse_args()
    if not options.url:print "url is needed.";exit(1)
    if not sum([bool(options.query),bool(options.add),bool(options.delete)])==1: print "You have to select only one of -q, -a , -d"; exit(1)
    s=Sender(options.url)
    s.login(options.login)
    if options.query:
        s.initForm("search_line")
        print s.search(options.query,options.filter)
        exit(0)
    if options.add:
        s.initForm("add_line")
        print s.addLine(options.add)
        exit(0)
    if options.delete:
        s.initForm("search_delete_line")
        print s.searchDeleteLine(options.delete,options.filter)
        exit(0)      
        
    


