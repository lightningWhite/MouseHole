import argparse
import os
import socket
import sys
import re

# In one terminal on the machine you have a mouse, run this command:
python3 mouseHole.py -p <IPAddress of Recieving Machine> -d /bogus

# On the same machine, run this:
sudo evtest --grab /dev/input/<mouseEvent> | nc -u 127.0.0.1 44144

# On the other computer, run this:
python3 mouseHole.py -s -d /dev/input/<mouseEvent>

# Then you should be able to command the mouse on the other computer
# Note that you have to have a mouse plugged into the other computer
# for a device to be present. I need to create a device to be controlled.

# It would be nice to run the netcat command from within the python script


def get_args():
    """
    Parse the args passed to the script by the user
    and return them.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--publish",
        action="store",
        required=False,
        dest="ip_address",
        help="Whether to publish the mouse movements and to what IP address to publish to",
    )
    parser.add_argument(
        "-s",
        "--subscribe",
        action="store_true",
        required=False,
        dest="subscribe",
        help="Whether to subscribe to the mouse movements",
    )
    parser.add_argument(
        "-d",
        "--device",
        action="store",
        required=True,
        dest="device",
        help="The device that should be published or controlled (e.g. /dev/input/by-id/usb-Logitech_USB_Optical_Mouse-event-mouse)",
    )
    return parser.parse_args()


def main():

    args = get_args()

    pub_port = 44044

    if args.subscribe:

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        server_address = ("127.0.0.1", pub_port)
        sock.bind(server_address)
        
        while True:
            msg, sender = sock.recvfrom(4096)
            command = msg.decode("utf-8")
            command = command.replace("DEVICE", args.device)
            
            print(f"Executing: {command}")
            os.system(command)


    if args.ip_address:
      
        intermediate_port = 44144
        snd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        rcv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = ("127.0.0.1", intermediate_port)
        rcv_sock.bind(server_address)
     
        # Receive messages from this machine, and resend them to the subscribing machine
        while True:
            msg, sender = rcv_sock.recvfrom(4096)
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
        
        
            if event_type and event_code and event_value:
                print(f"type: {event_type}, code: {event_code}, value: {event_value}")
                command = f"evemu-event DEVICE --type {event_type} --code {event_code} --value {event_value} --sync"
                print(f"The command: {command}")
                snd_sock.sendto(command.encode(), (args.ip_address, pub_port))






if __name__=="__main__":
    main()

