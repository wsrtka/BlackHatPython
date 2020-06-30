import urllib.parse
import urllib.error
import urllib.request
import threading
import queue


threads = 5
target_url = 'http://testphp.vulnweb.com'
wordlist_file = '/home/wsrtk/Downloads/all.txt'
resume = None
user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0'


def build_wordlist(wordlist_file):

    fd = open(wordlist_file, 'rb')
    raw_words = fd.readlines()
    fd.close()

    found_resume = False
    words = queue.Queue()

    for word in raw_words:

        word = word.strip()

        if resume is not None:
            if found_resume:
                words.put(word)
            
            else:
                if word == resume:
                    found_resume = True
                    print('Resuming process from %s' % resume)

        else:
            words.put(word)

    return words


def dir_bruter(word_queue, extensions=None):

    while not word_queue.empty():

        attempt = word_queue.get()

        attempt_list = []

        if '.' not in attempt.decode():
            attempt_list.append('/%s/' % attempt)

        else:
            attempt_list.append('/%s' % attempt)

        if extensions:
            for extension in extensions:
                attempt_list.append('/%s%s' % (attempt, extensions))

        for brute in attempt_list:

            url = '%s%s' % (target_url, urllib.parse.quote(brute))

            try:
                headers = {}
                headers['User-Agent'] = user_agent

                r = urllib.request.Request(url, headers=headers)

                response = urllib.request.urlopen(r)

                if len(response.read()) and response.code != 500:
                    print('[%d] => %s' % (response.code, url))
            except urllib.error.HTTPError as e:
                if hasattr(e, 'code') and e.code != 404 and e.code != 500:
                    print('[!] %d => %s' % (e.code, url))

                pass


word_queue = build_wordlist(wordlist_file)
extensions = ['.php', '.bak', '.orig', '.inc']

for i in range(threads):
    t = threading.Thread(target=dir_bruter, args=(word_queue, extensions,))
    t.start()
