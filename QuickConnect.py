import sys, argparse, re
from subprocess import Popen, PIPE

parser = argparse.ArgumentParser(description="Script to quickly connect to a database")
parser.add_argument('--version', action='version', version='%(prog)s 1.0')
parser.add_argument('-s', '--server', dest='server', type=str.lower, help="Server name. Note: only supports .vmpc1.cloud.boeing.com servers")
parser.add_argument('database', type=str.lower, nargs='?', help="Database to connect to", default="")

args = parser.parse_args()
configFileName = 'stored_databases.cfg'

def ContinueOrExit(prompt):    
    answer = input(prompt + " Y/n ") or 'y'
    while True:                
        if answer.lower() == 'n':
            sys.exit()
        elif answer.lower() == 'y':
            break
        else:
            print("Incorrect option.")
            answer = input(prompt + " Y/n ") or 'y'

### MAIN ###

print()

if args.server is not None:
    print(f"Connecting to {args.server}.vmpc1.cloud.boeing.com ...")
    Popen(f"putty.exe {args.server}.vmpc1.cloud.boeing.com")
    sys.exit()

sys.exit()

try:
    with open(configFileName, 'r') as configFile:
        for line in configFile:
            if args.database in line:
                database,hostname=line.split('@')
                print("Connecting to", line)
                Popen(f"putty.exe {hostname}")
                sys.exit()
except FileNotFoundError:
    print("Config file not found. Creating file...")
    with open(configFileName, 'x'):
        print("File created.")
    database = hostname = ""

ContinueOrExit("Database not found. Would you like to register this database?")

database = input(f"Enter the database name [{args.database}]: ").lower() or args.database

proc = Popen(f"tnsping {database}", stdout=PIPE, encoding='utf8')
result,err = proc.communicate()

if 'TNS-03505' in result:
    sys.exit(f"Database {database} not found via TNSPING. Please double check database name.")

rx = re.search("(HOST=.*?.com)", result)
hostname = rx.group().split('=')[1]
hostname = input(f"Enter the host name [{hostname}]: ").lower() or hostname

print(f"You would like to register {database}@{hostname}")
ContinueOrExit("Is this correct?")

with open(configFileName, 'a') as configFile:        
    print(f"Testing connection to {database}@{hostname}...")        
    proc = Popen(f"tnsping {database}", stdout=PIPE, encoding='utf8')
    result,err = proc.communicate()
    
    if hostname in result:    
        configFile.write(f"{database}@{hostname}\n")
        print(f"Connection successful. Registration complete.")

        ContinueOrExit("Would you like to connect now?")
        
        Popen(f"putty.exe {hostname}")
        sys.exit()