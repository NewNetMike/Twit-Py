import random
import time

def rand_int(min, max):
    return random.choice(list(range(min, max+1)))

def rand_sleep(min, max, no_message=False):
    r = rand_int(min, max)
    if not no_message: print("Sleeping for: " + str(r) + "s...")
    time.sleep(r)