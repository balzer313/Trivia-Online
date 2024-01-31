# Protocol Constants

CMD_FIELD_LENGTH = 16  # Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4  # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10 ** LENGTH_FIELD_LENGTH - 1  # Max size of data field according to protocol
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1  # Exact size of header (CMD+LENGTH fields)
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH  # Max size of total message
DELIMITER = "|"  # Delimiter character in protocol

# Protocol Messages
# In this dictionary we will have all the client and server command names

PROTOCOL_CLIENT = {
    "login_msg": "LOGIN",
    "logout_msg": "LOGOUT",
    "logged_users": "LOGGED",
    "question_msg": "GET_QUESTION",
    "answer_msg": "SEND_ANSWER",
    "score_msg": "MY_SCORE",
    "highscore_msg": "HIGHSCORE",
    "join_tournament_msg": "JOIN_TOURNAMENT",
    "leave_tournament_msg": "LEAVE_TOURNAMENT"
}  # .. Add more commands if needed

PROTOCOL_SERVER = {
    "login_ok_msg": "LOGIN_OK",
    "login_failed_msg": "ERROR",
    "logged_ans_msg": "LOGGED_ANSWER",
    "your_question_msg": "YOUR_QUESTION",
    "correct_ans_msg": "CORRECT_ANSWER",
    "wrong_ans_msg": "WRONG_ANSWER",
    "your_score_msg": "YOUR_SCORE",
    "all_score_msg": "ALL_SCORE",
    "error_msg": "ERROR",
    "no_question_msg": "NO_QUESTION",
    "tournament_ok_msg": "TOURNAMENT_OK"

}  # ..  Add more commands if needed

# Other constants

ERROR_RETURN = None  # What is returned in case of an error


def valid_cmd(cmd):
    return cmd in PROTOCOL_SERVER.values() or cmd in PROTOCOL_CLIENT.values()


def build_cmd(cmd):
    # Set command to proper length, according to the protocol (16 chars)
    return cmd + " "*(16 - len(cmd))


def parse_cmd(cmd):
    # Parse command field to command
    slicing_index_start = -1
    slicing_index_end = 16
    for i in range(0, len(cmd)):
        if cmd[i] != " " and slicing_index_start == -1:
            slicing_index_start = i
        if slicing_index_start != -1 and cmd[i] == " ":
            slicing_index_end = i
            break

    return cmd[slicing_index_start:slicing_index_end]


def build_length(data):
    # Set data length field to proper length, according to the protocol (4 chars)
    length_of_len_data = len(str(len(data)))  # The length of the numerical value representing the length of the data field
    return "0"*(4 - length_of_len_data) + str(len(data))


def parse_length(data):
    # Parse length field to numerical value
    slicing_index_start = -1
    slicing_index_end = len(data)
    for i in range(0, 4):
        if slicing_index_start == -1 and data[i].isnumeric() or data[i] == "-":
            slicing_index_start = i
        if slicing_index_start != -1 and not data[i].isnumeric():
            slicing_index_end = i
            break

    return data[slicing_index_start:slicing_index_end]


def build_message(cmd, data):
    if valid_cmd(cmd):
        command = build_cmd(cmd)
        length = build_length(str(data))
        full_msg = join_msg([command, length, str(data)])
        return full_msg
    return ERROR_RETURN


def parse_message(data):
    """
    Parss protocol message and returns command name and data field
    Returns: cmd (str), data (str). If some error occured, returns None, None
    """
    lst_of_components = split_msg(data, 3)
    if lst_of_components is not ERROR_RETURN:
        if len(lst_of_components[0]) == 16:
            length = parse_length(lst_of_components[1])
            cmd = parse_cmd(lst_of_components[0])
            msg = lst_of_components[-1]
            if length.isnumeric():
                if int(length) == len(msg):
                    return cmd, msg
    return ERROR_RETURN, ERROR_RETURN


def split_msg(msg, expected_fields):
    """
    Helper method. gets a string and number of expected fields in it. Splits the string
    using protocol's delimiter (|) and validates that there are correct number of fields.
    Returns: list of fields if all ok. If some error occured, returns None
    """
    lst_of_components = msg.split("|")
    if len(lst_of_components) > expected_fields:
        lst_of_components[expected_fields-1] = "|".join(lst_of_components[expected_fields-1:])
        lst_of_components = lst_of_components[:expected_fields]
    if len(lst_of_components) == expected_fields:
        return lst_of_components
    return ERROR_RETURN


def join_msg(msg_fields):
    return "|".join(msg_fields)

# Implement code ...