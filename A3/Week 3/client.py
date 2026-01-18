import socket
import hashlib
import time
from time import perf_counter
from collections import OrderedDict
import queue

ENTRY_ID = "1234"   # My entry ID
TEAM_NAME = "team"  # My team name
# start_time = perf_counter()
CHUNK_SIZE = 1448

# Open a file in write mode ('w')
    # Write some text to the file

# The file is automatically closed when the 'with' block is exited


SERVER_IP = '127.0.0.1'
SERVER_PORT = 9802

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(0.005)

def send_request(req):
    client_socket.sendto(req.encode(), (SERVER_IP, SERVER_PORT))

def receive_response():
    data, server_address = client_socket.recvfrom(2048)
    return data.decode()

def send_n_requests(offset_list,data_size):
    for i in offset_list:
        num_bytes = min(CHUNK_SIZE, data_size - i)
        req = f"Offset: {i}\nNumBytes: {num_bytes}\n\n"
        send_request(req)
        time.sleep(0.003)

    return

def receive_n_response(offset_list, ans,start_time):
    accepted_list = []
    remaining_list = []
    for i in offset_list:
        try:
            response = receive_response()
            if response.startswith("Offset:"):
                lines = response.split('\n')
                offset_no = int(lines[0].split(':')[1])
                accepted_list.append(offset_no)
                result_text = ""
                if (lines[2] == "Squished"):
                    result_text = '\n'.join(lines[4:])
                else:
                    result_text = '\n'.join(lines[3:])
                ans[offset_no] = result_text
                s = offset_no 
                with open('data.txt', 'a') as file:
                    file.write(f"{offset_no} {perf_counter()-start_time}\n")
                time.sleep(0.003)
                print(offset_no)
        except socket.timeout:
            continue
    for i in offset_list:
        if i not in accepted_list:
            remaining_list.append(i)
    return remaining_list


def main():
    start_time = perf_counter()
    total_offset_list = queue.Queue()
    client_socket.connect((SERVER_IP, SERVER_PORT))
    ans = OrderedDict()
    i = 0
    send_request("SendSize\nReset\n\n")
    response=""
    while(i<100):
        try:
            response = receive_response()
            break
        except socket.timeout:
            i+=1
    print(response)
    if not response.startswith("Size:"):
        print("Invalid response for SendSize request.")
        return

    data_size = int(response.split(":")[1])
    print(f"max size: {data_size}")
    burst_size = 5

    x = 0
    while(x < data_size):
        ans[x] = ""
        total_offset_list.put(x)
        x += CHUNK_SIZE


    
    while not total_offset_list.empty():
        offset_list = []
        for i in range(min(total_offset_list.qsize(), burst_size)):
            myoffset = total_offset_list.get()
            offset_list.append(myoffset)

        send_n_requests(offset_list,data_size)
        l = receive_n_response(offset_list, ans,start_time)
        # print(offset_list, l)
        # print(l)

        if(len(l) == 0):
            burst_size+=1
        else:
            burst_size = max(burst_size//2, 1)

        for i in l:
            total_offset_list.put(i)
        # print(len(total_offset_list))

  
    ans2=""
    for i in ans:
        ans2 += ans[i]
    print(len(ans2))
    
    md5_hash = hashlib.md5(ans2.encode("utf-8")).hexdigest()


    send_request(f"Submit: [{ENTRY_ID}@{TEAM_NAME}]\nMD5: {md5_hash}\n\n")
    response = receive_response()
    while (not (response.__contains__("Result: ") and response.__contains__("Time: ") and response.__contains__("Penalty: "))):
        response = receive_response()
    print(response)

    client_socket.close()

if __name__ == '__main__':
    main()
