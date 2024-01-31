import socket
import chatlib
import select
import random

# GLOBALS
users = {}
questions = {}
logged_users = {}  # a dictionary of client hostnames to usernames - will be used later
messages_to_send = []
client_sockets = []

ERROR_MSG = "Error! "
SERVER_PORT = 5000
SERVER_IP = "127.0.0.1"


# HELPER SOCKET METHODS
def add_message_to_queue(conn, packet):#add tuple to "messages_to_send" list
    global messages_to_send
    messages_to_send.append((conn, packet))


def print_client_sockets():
    global client_sockets
    for sock in client_sockets:
        print(sock.getpeername())


def build_and_send_message(conn, code, msg):
    """
    Builds a new message using chatlib, wanted code and message.
    Prints debug info, then sends it to the given socket.
    Paramaters: conn (socket object), code (str), msg (str)
    Returns: Nothing
    """

    packet = chatlib.build_message(code, msg)
    print(packet)
    add_message_to_queue(conn, packet)


def recv_message_and_parse(conn):
    """
    Recieves a new message from given socket.
    Prints debug info, then parses the message using chatlib.
    Paramaters: conn (socket object)
    Returns: cmd (str) and data (str) of the received message.
    If error occured, will return None, None
    """

    data = conn.recv(1024).decode()
    if data == "":
        return "", ""
    cmd, msg = chatlib.parse_message(data)
    return cmd, msg


def print_client_sockets():
    global messages_to_send
    for t in messages_to_send:
        print(t[0].getpeername())


def load_questions():
    """
    Loads questions bank from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: questions dictionary
    """
    questions = {
        1001: {"question": "Who is the main protagonist in Avatar: The Last Airbender?",
               "answers": ["Aang", "Katara", "Sokka", "Zuko"], "correct": 1},
        1002: {"question": "What element does Aang initially bend?", "answers": ["Fire", "Water", "Earth", "Air"],
               "correct": 4},
        1003: {"question": "Who is the leader of the Fire Nation?", "answers": ["Zuko", "Iroh", "Ozai", "Azula"],
               "correct": 3},
        1004: {"question": "What is the name of Sokka and Katara's tribe?",
               "answers": ["Southern Water Tribe", "Northern Water Tribe", "Air Nomads", "Earth Kingdom"],
               "correct": 1},
        1005: {"question": "What is the name of Aang's flying bison?", "answers": ["Appa", "Momo", "Bumi", "Suki"],
               "correct": 1},
        1006: {"question": "Who is known as the 'Blind Bandit'?", "answers": ["Toph Beifong", "Ty Lee", "Mai", "Suki"],
               "correct": 1},
        1007: {"question": "Which of the following is NOT a bending style in the show?",
               "answers": ["Firebending", "Waterbending", "Leafbending", "Earthbending"], "correct": 3},
        1008: {"question": "What is the name of Zuko's sister?", "answers": ["Katara", "Toph", "Azula", "Suki"],
               "correct": 3},
        1009: {"question": "What is the name of the giant library that Aang and his friends visit?",
               "answers": ["Ba Sing Se", "Kyoshi Island", "Omashu", "Wan Shi Tong's Library"], "correct": 4},
        1010: {"question": "Who is the Earth King of Ba Sing Se?", "answers": ["Long Feng", "Bumi", "Ozai", "Kuei"],
               "correct": 4},
        1011: {"question": "Which character is known for their cactus juice-induced hallucinations?",
               "answers": ["Sokka", "Zuko", "Aang", "Momo"], "correct": 1},
        1012: {"question": "What is the name of the spirit that takes the form of a panda in the spirit world?",
               "answers": ["Koh", "Hei Bai", "Wan Shi Tong", "Feng"], "correct": 2},
        1013: {"question": "Who is the leader of the Dai Li, the secret police of Ba Sing Se?",
               "answers": ["Toph", "Long Feng", "Joo Dee", "Iroh"], "correct": 2}
    }

    return questions


def load_user_database():
    """
    Loads users list from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: user dictionary
    """
    users = {
        "test"	:	{"password" :"test" ,"score" :0 ,"questions_asked" :[]},
        "yossi"		:	{"password" :"123" ,"score" :50 ,"questions_asked" :[]},
        "master"	:	{"password" :"master" ,"score" :200 ,"questions_asked" :[]}
    }
    return users


# SOCKET CREATOR

def setup_socket():
    """
    Creates new listening socket and returns it
    Recieves: -
    Returns: the socket object
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((SERVER_IP, SERVER_PORT))
    sock.listen(5)
    return sock


def send_error(conn, error_msg):
    """
    Send error message with given message
    Recieves: socket, message error string from called function
    Returns: None
    """
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["error_msg"], error_msg)


def handle_getscore_message(conn, username):
    global users
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["your_score_msg"], users[username]["score"])


def handle_logout_message(conn):
    """
    Closes the given socket (in laster chapters, also remove user from logged_users dictioary)
    Recieves: socket
    Returns: None
    """
    global logged_users

    del logged_users[conn.getpeername()]


def handle_login_message(conn, data):
    """
    Gets socket and message data of login message. Checks  user and pass exists and match.
    If not - sends error and finished. If all ok, sends OK message and adds user and address to logged_users
    Recieves: socket, message code and data
    Returns: None (sends answer to client)
    """
    global users  # This is needed to access the same users dictionary from all functions
    global logged_users	 # To be used later

    user_info = chatlib.split_msg(data, 2)
    if user_info is not None and len(user_info) == 2:
        username = user_info[0]
        password = user_info[1]
        if username in users.keys():
            if username in logged_users.values():
                send_error(conn, "Error. User already logged in.")
                return
            if users[username]["password"] == password:
                build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_ok_msg"], "")
                logged_users[conn.getpeername()] = username
            else:
                send_error(conn, "Password does not match the given username.")
        else:
            send_error(conn, "Username does not exist in the current context.")
    else:
        send_error(conn, "Error. Client sent impaired information.")


def handle_gethighscore_message(conn):
    global users
    st = ""
    user_list = []
    for user in users.keys():
        user_list.append([user, str(users[user]["score"])])
    # Sort the list by the score
    user_list.sort(key=lambda x: int(x[1]), reverse=True)
    for user in user_list[:5]:
        st += str(user[0]+": "+user[1]+"\n")
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["all_score_msg"], st)


def handle_getloggedusers_message(conn):
    global logged_users
    st = ""
    for user in logged_users.values():
        st += user + ", "
    data = st[:-2]
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["logged_ans_msg"], data)


def handle_client_message(conn, cmd, data):
    """
    Gets message code and data and calls the right function to handle command
    Recieves: socket, message code and data
    Returns: None
    """
    global logged_users	 # To be used later
    print(cmd)
    if cmd == "LOGIN":
        handle_login_message(conn, data)
    elif cmd == "MY_SCORE":
        handle_getscore_message(conn, logged_users[conn.getpeername()])
    elif cmd == "GET_QUESTION":
        handle_question_message(conn)
    elif cmd == "SEND_ANSWER":
        handle_answer_message(conn, logged_users[conn.getpeername()], data)
    elif cmd == "HIGHSCORE":
        handle_gethighscore_message(conn)
    elif cmd == "LOGGED":
        handle_getloggedusers_message(conn)
    elif cmd == "" or cmd == "LOGOUT":
        handle_logout_message(conn)
    else:
        send_error(conn, "Error. The requested command does not exist in the current context.")

def get_rand_item(items):
    if items == None:
        return None
    elif len(items) == 0:
        return None
    else:
        return random.choice(items)

def create_random_question(username):
    global users
    global questions

    questions_asked = users[username]["questions_asked"]
    questions_not_asked = [q for q in questions if q not in questions_asked]
    question_index = get_rand_item(questions_not_asked)
    if question_index is None:
        return None, None
    question_info = list(questions[question_index].values())
    question_info.insert(0, str(question_index))
    question_info[-2] = chatlib.join_msg(question_info[-2])
    question_info[-1] = str(question_info[-1])
    return chatlib.join_msg(question_info), int(question_info[0])


def handle_question_message(conn):
    global logged_users
    global users

    username = logged_users[conn.getpeername()]
    data, index = create_random_question(username)
    if data is None:
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["no_question_msg"], "")
    else:
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["your_question_msg"], data)
        users[username]["questions_asked"].append(index)


def handle_answer_message(conn, username, ans_data):
    global users
    global questions

    msg_components = ans_data.split("|")
    question_id = int(msg_components[0])
    choice = int(msg_components[1])
    if choice == questions[question_id]["correct"]:
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["correct_ans_msg"], "")
        users[username]["score"] += 5
    else:
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["wrong_ans_msg"], questions[question_id]["correct"])


def main():
    # Initializes global users and questions dicionaries using load functions, will be used later
    global users
    global questions
    global logged_users
    global messages_to_send
    global client_sockets

    xlist = []

    print("Welcome to Trivia Server!")
    users = load_user_database()
    questions = load_questions()
    server_socket = setup_socket()
    while True:
        print('new loop')
        send_list = [t[0] for t in messages_to_send]
        rlist, wlist, xlist = select.select([server_socket] + client_sockets, send_list, xlist)
        print(rlist)
        #Handle recv list
        for s in rlist:
            if s is server_socket:
                conn, addr = s.accept()
                client_sockets.append(conn)
            else:
                cmd, data = recv_message_and_parse(s)
                print(f"Data from existing client:\n{cmd,data}")
                can_handle = (s.getpeername() in logged_users) or (cmd == "LOGIN")
                if can_handle:
                    handle_client_message(s, cmd, data)
                    print(f"Handled {cmd} command successfully.")
                    if cmd == 'LOGOUT' or cmd == "":
                        print(f"connection ended with {s.getpeername()}.")
                        client_sockets.remove(s)
                elif cmd == "":
                    print(f"connection ended with {s.getpeername()}.")
                    client_sockets.remove(s)
                else:
                    xlist.append(s)

        #Handle write list:
        for s in wlist:
            packet = [item for item in messages_to_send if item[0] is s]
            if packet is not None:
                packet = packet[0][1]
                s.send(packet.encode())
                messages_to_send.remove((s, packet))

        #Handle error list:
        for s in xlist:
            build_and_send_message(s, "ERROR", "Error. Login is required in order to perform requested action.")
        # conn, addr = server_socket.accept()
        # is_occupied = True
        # while is_occupied:
        #     try:
        #         cmd, data = recv_message_and_parse(conn)
        #         can_handle = (conn.getpeername() in logged_users) or (cmd == "LOGIN")
        #         if can_handle:
        #             handle_client_message(conn, cmd, data)
        #             print(f"Handled {cmd} command successfully.")
        #             if cmd == "LOGOUT":
        #                 print("connection ended.")
        #                 is_occupied = False
        #     except ConnectionAbortedError:
        #         print("Connection aborted.")
        #         is_occupied = False
        # conn.close()


if __name__ == '__main__':
    main()
