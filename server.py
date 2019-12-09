import sys
import socket
import random
import json

if len(sys.argv)<3:
    print("Wrong Input")
    raise SystemExit

fileName=sys.argv[1]+".txt"
pktLossProb=float(sys.argv[2])
if pktLossProb >=1 or pktLossProb <=0:
    print("p must be between 0 and 1")
    raise SystemExit

server=('', 7735)
serverSock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    serverSock.bind(server)
    print("Started listening on", server)
except socket.error:
    print("Port already in use")
    raise SystemExit

def checksum(segment, length):
    if (length % 2 != 0):
        segment += "0".encode('utf-8')

    x = segment[0] + ((segment[1]) << 8)
    y = (x & 0xffff) + (x >> 16)

    for i in range(2, len(segment), 2):
        x = segment[i] + ((segment[i + 1]) << 8)
        y = ((x + y) & 0xffff) + ((x + y) >> 16)
    return ~y & 0xffff

sqnNum=0
ackPkt=21845
zeroPkt=0
dataPkts={}
f=open(fileName, 'w')

while True:
    data, addr=serverSock.recvfrom(2048)
    
    if data.decode('utf-8') == "Done":
        print("Data has been successfully written into the file",fileName)
        break

    sqnRcvd=int(data[0:32],2)
    checksumRcvd=int(data[32:48],2)
    payload=data[64:]
    if checksum(payload, len(payload))!=checksumRcvd:
        continue
    elif round(random.random(),2) <= pktLossProb:
        print("Packet loss, sequence number = ",sqnRcvd)
    elif sqnRcvd == sqnNum:
        dataPkt='{:032b}'.format(sqnNum)+'{:016b}'.format(zeroPkt)+'{:016b}'.format(ackPkt)
        serverSock.sendto(dataPkt.encode('utf-8'),addr)
        dataPkts[sqnNum]=payload.decode('utf-8')
        sqnNum+=1
    elif sqnRcvd > sqnNum:
        dataPkt='{:032b}'.format(sqnRcvd)+'{:016b}'.format(zeroPkt)+'{:016b}'.format(ackPkt)
        serverSock.sendto(dataPkt.encode('utf-8'),addr)
        dataPkts[sqnNum]=payload.decode('utf-8')

for key,value in data.items():
    f.write(value)
serverSock.close()
f.close()