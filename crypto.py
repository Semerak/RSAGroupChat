# crypto.py
from random import randrange, getrandbits


def is_prime(n, k=128):             # check if it is prime number
    if n == 2 or n == 3:
        return True
    if n <= 1 or n % 2 == 0:
        return False
    s = 0
    r = n - 1
    while r & 1 == 0:
        s += 1
        r //= 2
    for _ in range(k):
        a = randrange(2, n - 1)
        x = pow(a, r, n)
        if x != 1 and x != n - 1:
            j = 1
            while j < s and x != n - 1:
                x = pow(x, 2, n)
                if x == 1:
                    return False
                j += 1
            if x != n - 1:
                return False
    return True


def generate_prime_candidate(length):           # generates random number with given length
    p = getrandbits(length)
    p |= (1 << length - 1) | 1
    return p


def generate_prime_number(length=1024):         # generate prime number
    p = 4
    while not is_prime(p, 5):
        p = generate_prime_candidate(length)
    return p


def euclid(a, q):               # one step of euclid algorithm (simple)
    b = a // q
    r = a % q
    return b, r


def pow_mod(x, y, m):           # calculate pow(x,y) mod m
    binary = bin(y)[2:]
    x0 = x % m
    if binary[-1] == "1":
        c = x
    else:
        c = 1
    for i in range(len(binary) - 1):
        x1 = x0 ** 2 % m
        if binary[-i - 2] == "1":
            c = c * x1 % m
        x0 = x1
    return c


def to_int(m_str):  # function to convert str -> int
    m_int = 0
    for ch in m_str[::-1]:
        m_int = m_int * 128 + ord(ch)
    return m_int


def to_str(m_int):  # function to convert int -> str
    m_str = ""
    copy = m_int
    while copy != 0:
        copy, val = divmod(copy, 128)
        m_str += chr(val)
    return m_str


def ExtendedEuclid(x, y):           # euclid algorithm (extended)
    x0, x1, y0, y1 = 1, 0, 0, 1
    while y > 0:
        q, x, y = int(x // y), y, x % y
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return x0, y0  # two coefficients


def ext_eucl_pos(F, e):  # solve equation (d * e) mod F = 1
    d = ExtendedEuclid(F, e)[1]
    if d < 0:
        return d + F
    return d


def gcd(x, y):
    a, q0 = x, y
    r = 1
    while r != 0:
        b, r = euclid(a, q0)
        a, q0 = q0, r
    return a


class PK:  # class for public key
    def __init__(self, e, n, name=""):
        self.e = e
        self.n = n
        self.name = name

    def encrypt(self, message, coding):
        return pow_mod(coding(message), self.e, self.n)

    def verify(self, message, signature):  # verification of the signature
        int_m = to_int(message)
        int_sig = pow_mod(signature, self.e, self.n)
        return int_m == int_sig


class RSA:
    def __init__(self, *args, **kwargs):
        self.__e = 1
        self.__d = 1
        self.__pk = None
        self.__name = ""
        if len(args) == 2:
            self.__p = generate_prime_number(args[0])
            self.__q = generate_prime_number(args[0])
            self.__name = args[1]
        elif len(args) == 3:
            self.__p = args[0]
            self.__q = args[1]
            self.__name = args[2]
        else:
            raise NameError('Wrong amount of arguments durig initialization of RSA class. len(args)=' + str(len(args)))
        self.__n = self.__p * self.__q
        self.__F = (self.__p - 1) * (self.__q - 1)

    def add_e(self, e):             # if you want to and your own e
        if self.__e == 1:
            self.__e = e

    def get_e(self):                # returns e (if it is not generated, this method generate it)
        if self.__e == 1:
            length = int((self.__F.bit_length() * 0.75))
            while self.__F % self.__e == 0:
                self.__e = generate_prime_number(length)
        return self.__e

    def get_pk(self):               # returns object PK
        if self.__pk is None:
            self.__pk = PK(self.get_e(), self.__n, self.__name)
        return self.__pk

    def __gen_d(self):              # calculate d
        e = self.get_e()
        F = self.__F
        d = ext_eucl_pos(F, e)
        return d

    def __get_d(self):              # returns d (if it is not generated, this method with calculate it)
        if self.__d == 1:
            self.__d = self.__gen_d()
        return self.__d

    def get_name(self):             # returns name of this user
        return self.__name

    def get_pub_key(self):          # returns [e,n]
        return self.get_e(), self.__n

    def decrypt(self, c, coding):
        m = pow_mod(c, self.__get_d(), self.__n)
        return coding(m)

    def sign(self, m, coding):      # sign message
        return pow_mod(coding(m), self.__get_d(), self.__n)


# chinese remainder theorem (make some pre calculation)
def pre_chin(m):
    M = []
    Mult_all = 1
    for mi in m:
        Mult_all = Mult_all * mi

    for mi in m:
        cur_M = int(Mult_all // mi)
        delta = ext_eucl_pos(mi, cur_M)
        M.append(cur_M * delta)
    res = [Mult_all, M]
    return res


# chinese remainder theorem (use pre calculation to get result faster)
def chin_fast(m, b):
    res = 0
    Mult_all = m[0]
    M = m[1]
    for i in range(len(b)):
        res += M[i] * b[i] % Mult_all
    return res % Mult_all


class Group:                        # class for group
    def __init__(self, *argv):
        self.__list = []
        self.__mods = []
        for member in argv:
            self.add(member)
        self.__changed = True
        self.__update_M()

    def add(self, *argv):                   # add user to group by Public Key (class PK)
        for pk in argv:
            for pki in self.__list:
                if pki == pk:
                    return True
                if gcd(pki.n, pk.n) != 1:
                    return False
            self.__list.append(pk)
            self.__mods.append(pk.n)
        self.__changed = True
        return True

    def remove(self, pk):                   # remove user from group by Public Key (class PK)
        if pk in self.__list:
            self.__list.remove(pk)
            self.__mods.remove(pk.n)
            self.__changed = True

    def get(self):                          # return list of PK (who is in the group)
        return self.__list.copy()

    def __update_M(self):                   # makes update to pre calculations for chinese theorem
        if self.__changed:
            self.__pre_M = pre_chin(self.__mods)
            self.__changed = False

    def encrypt(self, message, coding):
        self.__update_M()
        codes = []
        for member in self.get():
            codes.append(member.encrypt(message, coding))
        return chin_fast(self.__pre_M, codes)
