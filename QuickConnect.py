import argparse, re
from subprocess import Popen, PIPE

parser = argparse.ArgumentParser(description="Script to quickly connect to a database")
parser.add_argument('--version', action='version', version='%(prog)s 1.0')
parser.add_argument('database', type=str, nargs='?', help="Database to connect to", default="")
parser.add_argument('-r', '--register', nargs=2, help="Name of database to register")

args = parser.parse_args()
configFileName = 'stored_databases.cfg'
print()

with open(configFileName, 'a+') as configFile:
    database=""
    hostname=""
    # If database not found, ask to add it along with the host name
    for line in configFile:
        if args.database in line:
            database,hostname=line.split('@')
            Popen(f"putty.exe {hostname}")
            break

if database == "" and hostname == "":
    answer = input("Database not found. Would you like to register this database? y/N ") or 'n'

    if answer.lower() == 'n':
        exit()
    
    database = input(f"Enter the database name [{args.database}]: ") or args.database

    proc = Popen(f"tnsping {database}", stdout=PIPE, encoding='utf8')
    out,err = proc.communicate()

    if out.find('TNS-03505'):
        print("Database not found via TNSPING. Please double check database name.")
        exit()

    rx = re.search("(HOST=.*?.com)", out)
    hostname = rx.group().split('=')[1]
    hostname = input(f"Enter the host name [{hostname}]: ") or hostname

    print(f"You would like to register {database}@{hostname}")
    answer = input("Is this correct? Y/n ")  or 'y'

    if answer.lower() == 'n':
        exit()

    with open(configFileName, 'a') as configFile:        
        print(f"Testing connection to {database}@{hostname}...")        
        proc = Popen(f"tnsping {database}", stdout=PIPE, encoding='utf8')
        out,err = proc.communicate()
        
        if out.find(hostname):
            configFile.write(f"{database}@{hostname}\n")
            print(f"Connection successful. Registration complete.")
            answer = input("Would you like to connect now? Y/n") or 'y'

            if answer.lower() == 'n':
                exit()
            
            Popen(f"putty.exe {hostname}")
            exit

# Show help