import datetime
import math

def milsToDateTime(ms):
    time_in_millis = ms
    dt = datetime.datetime.fromtimestamp(time_in_millis / 1000.0)
    return dt.isoformat(' ', 'seconds')

def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier



class FOBASE():
    def __init__(self):
        self.foob =[]

    

def fooLogger(name,mode,data):
            if mode == "w":
                FILE = open(f'{name}.txt',"w")
                FILE.close()
                return self
            if mode == "a":
                FILE = open(f'{name}.txt',"a")
                DATA = data
                FILE.writelines(DATA)
                FILE.close()
                return self

def write_list_to_file(name,list):
    # places = ['Berlin', 'Cape Town', 'Sydney', 'Moscow']

    FILE = open(f'{name}',"a")
    for listitem in list:
        FILE.write('%s\n' % listitem)
    FILE.close()

def read_list_from_file(name,list_to_write_to):
    

# open file and read the content in a list
    FILE = open(name, 'r')
    for line in FILE:
        # remove linebreak which is the last character of the string
        item = line[:-1]

        # add item to the list
        list_to_write_to.append(item)
    FILE.close()

class Arr():
    def __init__(self):
        self.arr = []
    def append(self,value):
        self.arr.append(value)
        return self
    def get_arr(self):
        return self.arr





