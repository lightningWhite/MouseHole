import socket
import sys
import re

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ("127.0.0.1", 44044)
sock.bind(server_address)

while True:
    msg, sender = sock.recvfrom(4096)
    new_msg = msg.decode("utf-8")
    print(new_msg)

    event_list = new_msg.split()
    event_type = ""
    event_code = ""
    event_value = ""

    idx = 0
    for item in event_list:
        if item == "type":
            if (idx + 2 < len(event_list)):
                event_type = event_list[idx + 2]
                event_type = re.sub('[()]', '', event_type)
                event_type = re.sub('[,]', '', event_type)
        elif item == "code":
            if (idx + 2 < len(event_list)):
                event_code = event_list[idx + 2]
                event_code = re.sub('[()]', '', event_code)
                event_code = re.sub('[,]', '', event_code)
        elif item == "value":
            if (idx + 1 < len(event_list)):
                event_value = event_list[idx + 1]
        idx = idx + 1


    device = "/dev/input/event12"
    if event_type and event_code and event_value:
        print("Got all three!")
        print(f"type: {event_type}, code: {event_code}, value: {event_value}")
        command = f"evemu-event {device} --type {event_type} --code {event_code} --value {event_value} --sync"
        print(f"The command: {command}")

