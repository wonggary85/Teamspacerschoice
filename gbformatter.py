#!/usr/bin/env python3
import sys
import getopt
from groundbreaker import reset_single_use as rsu


def response_formatter(categories):
    inputs = []
    with open('singleuse.txt', 'a+'):
        file.write("\n")
        for category in categories:
            print(f"Writing to file {category}.\nctrl+c to stop current category entry.\n")
            while True:
                try:
                    line = input(f"{category}:")
                except KeyboardInterrupt:
                    break
                else:
                    if line == "":
                        continue
                    else:
                        inputs.append(f"{category}:{line}")
                        file.write(f"{category}:{line}\n")
    print(f"\nWrote {len(inputs)} lines.")
    for item in inputs:
        print(f'\n\t{item}')

        
def print_help():
    print("Helper tool to easily append multiple lines to \'singleuse.txt\' formatted for use with groundbreaker.py.\n")
    print("-l | --love:\tSpecify a single use string")
    print("-d | --dislike:\tSpecify a single use string")
    print("-p | --priority:\tSpecify a single use string")
    print("-n | --need:\tSpecify a single use string")
    print("-r | --reset:\tClears/Resets the singleuse.txt file to default")

    
def main(argv):
    categories = []
    try:
        opts,args = getopt.getopt(sys.argv[1:], 'hrl:d:p:n:',['love=', 'dislike=', 'priority=', 'need='])
    except Exception as err_msg:
        print(err_msg)
        exit()
    for opt,arg in opts:
        if opt in ('-h', '--help'):
            print_help()
            exit()
        elif opt in ('-r', '--reset'):
            rsu()
            print("Cleared singleuse.txt entries.")
            exit()
        elif opt in ('-l', '--love'):
            categories.append('love')
        elif opt in ('-d', '--dislike'):
            categories.append('loathe')
        elif opt in ('-p', '--priority'):
            categories.append('priority')
        elif opt in ('-n', '--need'):
            categories.append('help')
    if len(categories) > 0:
        response_formatter(categories)
    else:
        categories = ['love', 'loathe', 'priority', 'help']
        response_formatter(categories)
    exit()


if __name__=="__main__":
    main(sys.argv[1:])
