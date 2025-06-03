from time import sleep
from random import random

def exit_random():
    while random()>0.1:
        print("d_two run")
        sleep(2)
    print("d_two exit")

