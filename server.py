import tkinter as tk
import socket
import threading
import ssl
from ssl import PROTOCOL_TLS_SERVER


window = tk.Tk()
window.title("Server")



topFrame = tk.Frame(window)
btnStart = tk.Button(topFrame, text="Connect", command=lambda : start_server())
btnStart.pack(side=tk.LEFT)
btnStop = tk.Button(topFrame, text="Stop", command=lambda : stop_server(), state=tk.DISABLED)
btnStop.pack(side=tk.LEFT)
topFrame.pack(side=tk.TOP, pady=(5, 0))


middleFrame = tk.Frame(window)
lblHost = tk.Label(middleFrame, text = "Host: X.X.X.X")
lblHost.pack(side=tk.LEFT)
lblPort = tk.Label(middleFrame, text = "Port:XXXX")
lblPort.pack(side=tk.LEFT)
middleFrame.pack(side=tk.TOP, pady=(5, 0))





server = None
HOST_ADDR = "127.0.0.1"
HOST_PORT = 8082
client_name = " "
clients = []
clients_names = []
server_cert = 'server.crt'
server_key = 'server.key'
client_certs = 'client.crt'



context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.verify_mode = ssl.CERT_REQUIRED
context.load_cert_chain(certfile=server_cert, keyfile=server_key)
context.load_verify_locations(cafile=client_certs) #verify server


# Start server function
def start_server():
    global server, HOST_ADDR, HOST_PORT 
    btnStart.config(state=tk.DISABLED)
    btnStop.config(state=tk.NORMAL)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(socket.AF_INET)
    print(socket.SOCK_STREAM)

    server.bind((HOST_ADDR, HOST_PORT))
    server.listen(5)  # server is listening for client connection

    threading._start_new_thread(accept_clients, (server, " "))

    lblHost["text"] = "Host: " + HOST_ADDR
    lblPort["text"] = "Port: " + str(HOST_PORT)


# Stop server function
def stop_server():  
    global server
    btnStart.config(state=tk.NORMAL)
    btnStop.config(state=tk.DISABLED)


def accept_clients(the_server, y):
    while True:
        client, addr = the_server.accept()
        conn = context.wrap_socket(client, server_side=True) #SSL established, and certificate verified
        print("\nSSL established. Peer: {}".format(conn.getpeercert())) 
        # client can now communicate with server, print out the ca certificate from the client
        clients.append(conn)
        print("\nCipher being used is: {}" .format(conn.cipher()))
        threading._start_new_thread(send_receive_client_message, (conn, addr))


# Function to receive message from current client AND
# Send that message to other clients
def send_receive_client_message(client_connection, client_ip_addr):
    global server, client_name, clients, clients_addr
    client_msg = " "

    # send welcome message to client

    client_name  = client_connection.recv(4096).decode()
    welcome=(f'{client_name} connected')
    for c in clients:
        if c!=client_connection:
            c.send(welcome.encode())
            
    welcome_msg = "Welcome " + client_name + ". Use 'exit' to quit.\n"
    client_connection.send(welcome_msg.encode())
    print(f'name of the client is {client_name}')




    clients_names.append(client_name)
    
    client_msg="These are the available clients that are connected:"
    client_connection.send(client_msg.encode())
    for c in clients_names:
        client_connection.send(c.encode())



    while True:
        data = client_connection.recv(4096).decode()
        if not data: break
        if data == "exit": break
        server_msg=" "

        client_msg = data

        print(client_msg)

        idx = clients.index(client_connection)
        sending_client_name = clients_names[idx]

        for c in clients:
            if c != client_connection:
                server_msg = str(sending_client_name + "->" + client_msg)
                c.send(server_msg.encode())

    # find the client index then remove from both lists(client name list and connection list)
    idx = clients.index(client_connection)
    print(f'{clients_names[idx]} disconnected')
    exit_msg=(f'{clients_names[idx]} disconnected')
    for c in clients:
        if c != client_connection:
            c.send(exit_msg.encode())
    del clients_names[idx]
    del clients[idx]
    client_connection.close()


window.mainloop()