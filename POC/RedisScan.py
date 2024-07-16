import socket
import redis

ip = '192.168.65.173'
port = 6379

def scan_port(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.3) # 300ms timeout
    try:
        s.connect((ip, 6379))
        print(f'Port 6379 is open on {ip}')
        s.close()
        check_redis_auth(ip)
    except:
        print(f'Port 6379 is not open on {ip}')
    

def check_redis_auth(ip):
    try:
        r = redis.StrictRedis(host=ip, port=6379, socket_timeout=0.3)
        r.ping()
        print(f'Redis Unauthenticated Access on {ip}')
    except:
        print(f'No Redis Unauthenticated Access on {ip}')


scan_port(ip)