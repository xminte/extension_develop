from pymongo import MongoClient
import socket


def scan_port(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.3) # 300ms timeout
    try:
        s.connect((ip, 27017))
        print(f'Port 27017 is open on {ip}')
        s.close()
        scan_mongo(ip)
    except:
        print(f'Port 27017 is not open on {ip}')


def scan_mongo(ip):
    print('Scanning for MongoDB servers...')
    try:
        client = MongoClient(ip, 27017,socketTimeoutMS=3000)
        dbnames = client.list_database_names()
        if dbnames and bool(dbnames) and len(dbnames) > 0:
            print(f'MongoDB Unauthenticated Access on {ip}')
        
    except:
        print(f'No MongoDB Unauthenticated Access on {ip}')


if __name__ == '__main__':
    ip = '47.120.62.179'
    scan_port(ip) 