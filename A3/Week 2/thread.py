import socket
import sys
import time
import hashlib
import threading
import matplotlib.pyplot as plt

ip=sys.argv[1]
port=int(sys.argv[2])
message="SendSize\nReset\n\n"
message=message.encode()
sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

total_bytes=0
time_cutoff=0.002
rate = 1/time_cutoff
sock.settimeout(0.01)
max_byte_limit=1448
num_threads = 5
start_time=time.time()

ai=1
md=2

while(True):
    sock.sendto(message,(ip,port))
    try:
        server_reply,server_address=sock.recvfrom(2048)
    except socket.timeout:
        continue
    print(server_reply)
    total_bytes=int(server_reply[6:len(server_reply)-2].decode())
    break

print("Total bytes: ",total_bytes)

final_data = ["" for i in range(num_threads)]
# end_offset_list=[[] for i in range(num_threads)]
# end_time_list=[[] for i in range(num_threads)]
# start_time_list=[[] for i in range(num_threads)]
# start_offset_list=[[] for i in range(num_threads)]
# rate_list=[[] for i in range(num_threads)]
# time_list=[[] for i in range(num_threads)]

def get_lines (i, offset, limit, rate):
    total_received=offset
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.settimeout(0.01)

    current_thread_time=time.time()
    # start_offset_list[i].append(offset)
    # start_time_list[i].append(current_thread_time-start_time)

    while (total_received<limit):
        number_of_bytes=min(max_byte_limit, limit-offset)
        data_request="Offset: "+str(offset)+"\nNumBytes: "+str(number_of_bytes)+"\n\n"
        data_request=data_request.encode()
        # print(i, offset, rate)
        time.sleep(1/rate)
        try:
            sock.sendto(data_request,(ip,port))
        except socket.timeout:
            continue

        try:
            server_reply,server_address=sock.recvfrom(2048)
        except socket.timeout:
            rate/=md
            continue

        # print(server_reply.decode())
        server_reply=server_reply.decode()
        received_offset=int(server_reply.split('\n')[0].split(': ')[1])

        # print(received_offset," ",offset)

        if(received_offset != offset):
            continue

        server_reply=server_reply.split('\n')[3:]

        actual_data='\n'.join(server_reply)

        if(len(actual_data.encode()) != number_of_bytes):
            continue
    
        # rate_list[i].append(rate)
        rate += ai

        current_thread_time=time.time()
        # end_offset_list[i].append(offset)
        # end_time_list[i].append(current_thread_time-start_time)
        # time_list[i].append(current_thread_time-start_time)

        #actual data is just the actual lines
        final_data[i]+=actual_data
        total_received+=number_of_bytes
        offset+=number_of_bytes

        # if(total_received<limit):
        #     current_thread_time=time.time()
        #     start_offset_list[i].append(offset)
        #     start_time_list[i].append(current_thread_time-start_time)

    sock.close()

threads = []

size = [(total_bytes + num_threads - 1) // num_threads for i in range (num_threads)]
if (total_bytes % num_threads > 0):
    size[-1] -= num_threads - total_bytes % num_threads

print(size)

pref = [0 for i in range (num_threads + 1)]
for i in range (1, num_threads + 1):
    pref[i] = pref[i - 1] + size[i - 1]

for i in range(num_threads):
    print(i, pref[i], pref[i + 1])
    thread = threading.Thread(target=get_lines, args=(i, pref[i], pref[i + 1], rate))
    threads.append(thread)
    thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()

final_data = "".join(final_data)

# print(final_data)
final_data_bytes=final_data.encode()
print(len(final_data_bytes))
md5_hash=hashlib.md5(final_data_bytes).hexdigest()
print("MD5 hash: ",md5_hash)

submit_text="Submit: "+"2021CS10551_2021CS50948@COL334\n"+"MD5: "+md5_hash+"\n\n"

while(True):
    try:
        sock.sendto(submit_text.encode(),(ip,port))
    except socket.timeout:
        continue
    break

while(True):
    try:
        server_reply,server_address=sock.recvfrom(2048)
    except socket.timeout:
        continue
    # print(server_reply.decode())
    f=server_reply.decode().split(':')
    if(f[0]!="Result"):
        continue
    print(server_reply.decode())
    break

sock.close()

# for i in range(num_threads-2,-1,-1):
#     print("For thread "+str(i)+" : "+str(len(end_offset_list[i+1])))
#     end_offset_list[i]=end_offset_list[i]+end_offset_list[i+1]
#     end_time_list[i]=end_time_list[i]+end_time_list[i+1]
#     start_offset_list[i]=start_offset_list[i]+start_offset_list[i+1]
#     start_time_list[i]=start_time_list[i]+start_time_list[i+1]

# print("Approx total offsets: ",total_bytes/max_byte_limit)
# print("This is length of offset list: ",len(end_offset_list[0]))
# print("This is length of time list: ",len(end_time_list[0]))

# fig=plt.figure(figsize=(10,10),dpi=200)
# plt.scatter(start_time_list[0],start_offset_list[0],marker='o',color='blue')
# plt.scatter(end_time_list[0],end_offset_list[0],marker='o',color='orange')
# plt.xlabel("Response time of offset")
# plt.ylabel("Offset")
# plt.savefig("md2_offset_vs_time_with_aimd.png")

# time_lower_bound=0
# time_upper_bound=0.5

# magnified_start_time_list=[]
# magnified_start_offset_list=[]
# for i in range(len(start_time_list[0])):
#     if(start_time_list[0][i]<time_lower_bound or start_time_list[0][i]>time_upper_bound):
#         continue
#     magnified_start_time_list.append(start_time_list[0][i])
#     magnified_start_offset_list.append(start_offset_list[0][i])

# magnified_end_time_list=[]
# magnified_end_offset_list=[]
# for i in range(len(end_time_list[0])):
#     if(end_time_list[0][i]<time_lower_bound or end_time_list[0][i]>time_upper_bound):
#         continue
#     magnified_end_time_list.append(end_time_list[0][i])
#     magnified_end_offset_list.append(end_offset_list[0][i])

# print(len(magnified_start_time_list))
# print(len(magnified_end_time_list))

# fig=plt.figure(figsize=(10,10),dpi=200)
# plt.scatter(magnified_start_time_list,magnified_start_offset_list,marker='o',color='blue')
# plt.scatter(magnified_end_time_list,magnified_end_offset_list,marker='o',color='orange')
# plt.xlabel("Response time of offset")
# plt.ylabel("Offset")
# plt.savefig("magnified_offset_vs_time.png")

# colors=["red","magenta","blue","green","brown"]
# fig=plt.figure()
# for i in range(num_threads):
#     plt.plot(time_list[i],rate_list[i],color=colors[i],label="Thread "+str(i))
#     plt.xlabel("Time elapsed")
#     plt.ylabel("Rate at which requests are sent")
# plt.legend()
# plt.savefig("md2_rate_vs_time_graph.png")