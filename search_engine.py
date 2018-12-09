import requests
import bs4
import re


class Node:
    def __init__(self, label=None, data={}):
        self.label = label
        self.data = data
        self.child = {}

    def add_child(self, key, data={}):
        if not isinstance(key, Node):
            self.child[key] = Node(key, data)
        else:
            self.child[key.label] = key

    def __getitem__(self, key):
        return self.child[key]


class Trie:
    def __init__(self):
        self.head = Node()

    def __getitem__(self, key):
        return self.head.child[key]

    def add(self, word, where=''):
        current_node = self.head
        word_finished = True

        for i in range(len(word)):
            if word[i] in current_node.child:
                current_node = current_node.child[word[i]]
            else:
                word_finished = False
                break

        if not word_finished:
            while i < len(word):
                current_node.add_child(word[i])
                current_node = current_node.child[word[i]]
                i += 1

        if not word_finished:
            current_node.data = {where: 1}
        else:
            try:
                count = current_node.data.get(where)
            except:
                current_node.data[where] = 0
                count = current_node.data.get(where)
            if count:
                count += 1
                current_node.data[where] = count

    def has_word(self, word):
        if not word:
            raise ValueError('Trie.has_word requires a not-Null string')
        elif word == '':
            return False

        current_node = self.head
        exists = True
        for letter in word:
            if letter in current_node.child:
                current_node = current_node.child[letter]
            else:
                exists = False
                break

        if exists:
            if len(current_node.data) == 0:
                exists = False

        return exists

    def start_with_prefix(self, prefix):
        """ Returns a list of all words in tree that start with prefix """
        words = list()
        if not prefix:
            raise ValueError('Requires not-Null prefix')

        top_node = self.head
        for letter in prefix:
            if letter in top_node.child:
                top_node = top_node.child[letter]
            else:
                return words

        if top_node == self.head:
            queue = [node for key, node in top_node.child.iteritems()]
        else:
            queue = [top_node]

        while queue:
            current_node = queue.pop()
            if current_node.data:
                words.append(current_node.data)

            queue = [node for key, node in current_node.child.iteritems()] + queue

        return words

    def getData(self, word):
        if not self.has_word(word):
            raise ValueError('{} not found in trie'.format(word))

        current_node = self.head
        for letter in word:
            current_node = current_node[letter]

        return current_node.data


if __name__ == '__main__':

    stopwords_trie = Trie()
    stopwords_file = open('stopwords.txt', 'r')

    if stopwords_file:
        for line in stopwords_file:
            for word in line.split():
                word = word.replace("\n", "")
                stopwords_trie.add(word)

    links_scan = open('links.txt', 'r')
    links_trie = Trie()

    if links_scan:
        for link in links_scan:
            page = requests.get(link[:-1])
            soup = bs4.BeautifulSoup(page.content, 'html.parser')

            for ptag in soup.findAll('p'):
                for word in ptag.get_text().split():
                    word = re.sub('[^0-9a-zA-Z]+', '', word.lower())

                    if word:
                        if word.strip() != "":
                            if stopwords_trie.has_word(word):
                                pass
                            else:
                                links_trie.add(word, link[:-1])

    while True:
        print "***********\nEnter string to be found:\n"
        read_line = raw_input()
        read_line = read_line.replace("\n", "")

        if "exit()" in read_line:
            break

        if read_line.strip() is "":
            continue

        results = {}
        for word in read_line.split():
            word = re.sub('[^0-9a-zA-Z]+', '', word.lower())
            if stopwords_trie.has_word(word):
                continue

            if links_trie.has_word(word):
                data = links_trie.getData(word)

                try:
                    word_results = results[word]
                except:
                    results[word] = []
                    word_results = results[word]

                word_results.append(data)

        ranked_results = []
        for key, value in results.iteritems():
            for key1, value1 in value[0].iteritems():
                found = True
                for rr in ranked_results:
                    if rr[0] == key1:
                        rr[1] += value1
                        found = False
                        break
                if found:
                    ranked_results.append([key1, value1])

        sorted(ranked_results, key = lambda s: s[1])
        print "#######\nFollowing results have been found : "
        for rr in ranked_results:
            print rr[0]

        print "\n"
