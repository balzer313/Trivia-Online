# Imports:
import random
import socket
import pygame
import sys
import tkinter as tk
from tkinter import ttk
import time
from PIL import Image, ImageTk
import os
import chatlib  # To use chatlib functions or consts, use chatlib.****

SERVER_IP = "127.0.0.1"  # Our server will run on same computer as client
SERVER_PORT = 5000


# HELPER SOCKET METHODS

def build_and_send_message(conn, code, msg):
    """
    Builds a new message using chatlib, wanted code and message.
    Prints debug info, then sends it to the given socket.
    Paramaters: conn (socket object), code (str), msg (str)
    Returns: Nothing
    """
    packet = chatlib.build_message(code, msg)
    print(packet)
    conn.send(packet.encode())


def recv_message_and_parse(conn):
    """
    Recieves a new message from given socket.
    Prints debug info, then parses the message using chatlib.
    Paramaters: conn (socket object)
    Returns: cmd (str) and data (str) of the received message.
    If error occured, will return None, None
    """

    data = conn.recv(1024).decode()
    cmd, msg = chatlib.parse_message(data)
    print(cmd, msg)
    return cmd, msg


def connect():
    # Implement Code
    user_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    user_socket.connect((SERVER_IP, SERVER_PORT))
    return user_socket


def error_and_exit(msg):
    sys.exit(msg)
    pass

def clear_window(root):
    # Remove widgets from the window
    for widget in root.winfo_children():
        widget.destroy()



def login(conn):
    ######################create login page########################
    root = tk.Tk()
    root.title("Login")
    root.configure(bg='white')
    root.geometry("450x550")  # Set the window size

    # Load the Instagram logo image
    logo_image = Image.open("photos/aang_logo.jpg")
    logo_image = logo_image.resize((100, 100))  # Resize the image
    logo_photo = ImageTk.PhotoImage(logo_image)

    # Add a label for the logo
    logo_label = tk.Label(root, image=logo_photo, bg='white')
    logo_label.pack(pady=10)

    # Add a label for the logo
    title_label = tk.Label(root, text="Avatar Trivia", font=("Helvetica", 24), bg='white')
    title_label.pack(pady=20)

    # Add entry fields for username and password
    username_label = tk.Label(root, text="Username:", bg='white')
    username_label.pack()
    username_entry = tk.Entry(root, bg='light gray')
    username_entry.pack(pady=5)

    password_label = tk.Label(root, text="Password:", bg='white')
    password_label.pack()
    password_entry = tk.Entry(root, show="*", bg='light gray')  # Show * for password input
    password_entry.pack(pady=10)

    status_label = tk.Label(root, text="", fg="red", bg="white")
    status_label.pack()

    ########################################################

    login_successful = False  # Flag to track login success
    def login_button_command():
        nonlocal login_successful  # Access the flag from the outer scope
        data = chatlib.join_msg([username_entry.get(), password_entry.get()])
        build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["login_msg"], data)
        cmd, msg = recv_message_and_parse(conn)
        print(cmd,msg)
        if cmd == chatlib.PROTOCOL_SERVER["login_ok_msg"]:
            status_label.config(text="Successfully logged in.", fg="green")
            root.update()
            print("Successfully logged in.")
            login_successful = True  # Set the flag to True for successful login
            time.sleep(0.7)
            root.destroy()
        else:
            status_label.config(text="Failed to log in.", fg="red")
            print("Failed to log in.")
            username_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)
    # Create login button
    login_button = tk.Button(root, text="Login", bg="light blue", fg="white", bd=2, relief=tk.GROOVE,font=("Helvetica", 16), width=15, height=2, command=login_button_command)
    login_button.pack(padx=10, pady=10)
    root.mainloop()
    if login_successful:
        return login_successful




def logout(conn):
    build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["logout_msg"], "")
    pass


def build_send_recv_parse(conn, cmd, data):
    build_and_send_message(conn, cmd, data)
    return recv_message_and_parse(conn)


def get_score(conn):
    msg_code, msg = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["score_msg"], "")
    if msg_code != chatlib.PROTOCOL_SERVER["your_score_msg"]:
        msg = "Error. Impaired information was received from the server."
    print(msg)
    return msg


def play_question(conn):
    msg_code, msg = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["question_msg"], "")
    list=[]#will help us get the wuestions info for the gui
    if msg_code == chatlib.PROTOCOL_SERVER["no_question_msg"]:
        print("Server ran out of questions.")
        list.append("Server ran out of questions.")

    elif msg_code == chatlib.PROTOCOL_SERVER["your_question_msg"]:
        components = msg.split("|")
        for component in components:
            list.append(component)
        print(components[1])
        for i in range(1,5):
            print(i , ":", components[1+i])

        # ans = input("Enter number of correct answer: (1,2,3,4):")
        # packet = chatlib.join_msg([components[0], ans])
        # msg_code, msg = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["answer_msg"], packet)
        #
        # if msg_code == chatlib.PROTOCOL_SERVER["wrong_ans_msg"]:
        #     print(f"Incorrect. The correct answer is:{msg}")
        # elif msg_code == chatlib.PROTOCOL_SERVER["correct_ans_msg"]:
        #     print("Correct! Well done.")
        # else:
        #     print("Error. Server sent impaired information.")
    else:
        list.append("Error. Server sent impaired information.")
        print("Error. Server sent impaired information.")
    return list, conn


def get_highscore(conn):
    msg_code, msg = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["highscore_msg"], "")

    if msg_code != chatlib.PROTOCOL_SERVER["all_score_msg"]:
        msg = "Error. Server sent impaired information."
    print(msg)
    return msg


def get_logged_users(conn):
    msg_code, msg = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["logged_users"], "")
    if msg_code != chatlib.PROTOCOL_SERVER["logged_ans_msg"]:
        msg = "Error. Server sent impaired information."
    return msg


def main():
    try:
        client_sock = connect()
        print(client_sock)
        is_logged = login(client_sock)
        if is_logged:
            pygame.init()
            pygame.mixer.init()
            pygame.mixer.music.load("music/avatar_menu_music.mp3")
            pygame.mixer.music.play(-1)  # Loop the music indefinitely





            trivia = tk.Tk()
            trivia.title("Trivia")
            frame = ttk.Frame(trivia)
            frame.pack(fill=tk.BOTH, expand=tk.YES)  # Use pack geometry manager with fill and expand options

            # Load and set the background image
            original_background_image = Image.open("photos/menu_background2.jpg")
            background_image = ImageTk.PhotoImage(original_background_image)
            background_label = ttk.Label(frame, image=background_image)
            background_label.image = background_image  # Keep a reference to the image object
            background_label.place(x=0, y=0, relwidth=1, relheight=1)

            style = ttk.Style()
            style.configure("TButton",
                            padding=10,
                            font=("Helvetica", 14, "bold"),
                            foreground="black",
                            background="#336699",
                            relief="flat",
                            width=15,
                            height=2
                            )


            def logout_command():
                logout(client_sock)
                trivia.destroy()

            def score_command():
                # Remove all widgets from the frame
                for widget in frame.winfo_children():
                    widget.destroy()

                # Define a function to show the score
                def show_score():
                    score = get_score(client_sock)
                    score_label = tk.Label(frame, text=f"Score: {score}", font=("Helvetica", 14, "bold"))
                    score_label.place(relx=0.5, rely=0.5,
                                      anchor="center")  # Place the score_label widget in the center of the frame

                    def recreate_widgets():
                        # Remove score_label from the frame
                        score_label.destroy()
                        # Recreate the widgets in the frame using grid geometry manager
                        recreate_menu_widgets()

                    # Create a "Back" button with increased spacing using rely=0.7
                    back_button = ttk.Button(frame, text="Back", command=recreate_widgets)
                    back_button.place(relx=0.5, rely=0.7,
                                      anchor="center")  # Place the back_button widget below the score_label with increased spacing in the center of the frame

                # Call the show_score function after a delay of 100 milliseconds
                trivia.after(100, show_score)

            def question_command():
                for widget in frame.winfo_children():
                    widget.destroy()

                def show_question():
                    def recreate_widgets():
                        # Remove score_label from the frame
                        for widget in frame.winfo_children():
                            widget.destroy()
                        # Recreate the widgets in the frame using pack geometry manager
                        recreate_menu_widgets()

                    def check_answer(que_id, option_number, options):
                        print([str(que_id), str(option_number)])
                        packet = chatlib.join_msg([str(que_id), str(option_number)])
                        msg_code, msg = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["answer_msg"], packet)

                        if msg_code == chatlib.PROTOCOL_SERVER["wrong_ans_msg"]:
                            print(f"Incorrect. The correct answer is: {options[int(msg)-1]}")
                            for widget in frame.winfo_children():
                                widget.destroy()
                                # Load and set the background image
                                happy_images = os.listdir("photos/aang_sad")
                                pic = random.choice(happy_images)
                                background_image = Image.open(f"photos/aang_sad\\{pic}")
                                background_image = background_image.resize((728, 410))
                                background_image2 = ImageTk.PhotoImage(background_image)
                                background_label = ttk.Label(frame, image=background_image2)
                                background_label.image = background_image2  # Keep a reference to the image object
                                background_label.place(x=0, y=0, relwidth=1, relheight=1)
                            lab = tk.Label(frame, text=f"Incorrect. The correct answer is: {options[int(msg)-1]}",
                                           font=("Helvetica", 22), fg="red")
                            lab.pack(pady=150)
                            back_button = ttk.Button(frame, text="Back", command=recreate_widgets)
                            back_button.pack(pady=10)
                        elif msg_code == chatlib.PROTOCOL_SERVER["correct_ans_msg"]:
                            print("Correct! Well done.")
                            for widget in frame.winfo_children():
                                widget.destroy()
                            # Load and set the background image
                            happy_images = os.listdir("photos/aang_happy")
                            pic = random.choice(happy_images)
                            background_image = Image.open(f"photos/aang_happy\\{pic}")
                            background_image = background_image.resize((728, 410))
                            background_image2 = ImageTk.PhotoImage(background_image)
                            background_label = ttk.Label(frame, image=background_image2)
                            background_label.image = background_image2  # Keep a reference to the image object
                            background_label.place(x=0, y=0, relwidth=1, relheight=1)
                            lab = tk.Label(frame, text="Correct! Well done.", font=("Helvetica", 22), fg="green")
                            lab.pack(pady=150)
                            back_button = ttk.Button(frame, text="Back", command=recreate_widgets)
                            back_button.pack(pady=10)
                        else:
                            print("Error. Server sent impaired information.")
                            lab = tk.Label(frame, text="Error. Server sent impaired information.",
                                           font=("Helvetica", 14))
                            lab.pack(pady=150)

                    question_list, conn = play_question(client_sock)
                    print(question_list[0])
                    if question_list[0] == "Error. Server sent impaired information." or question_list[
                        0] == "Server ran out of questions.":
                        for widget in frame.winfo_children():
                            widget.destroy()
                        error_label = tk.Label(frame, text="No More Questions Left", font=("Helvetica", 14))
                        error_label.pack(pady=150)
                        back_button = ttk.Button(frame, text="Back", command=recreate_widgets)
                        back_button.pack(pady=10)
                    else:
                        question_label = tk.Label(frame, text=question_list[1],
                                                  font=("Helvetica", 14))  # the actual question
                        question_label.pack(pady=10)
                        option_buttons = []
                        option_number = 1
                        que_id = question_list[0]
                        for option in question_list[2:6]:
                            button = tk.Button(frame, text=option, width=20, font=('Comic Sans MS', 12),
                                               fg='dark blue', bg='white', activeforeground='light blue',
                                               activebackground='light gray',
                                               bd=2, relief='solid', highlightthickness=1, highlightcolor='dark blue',
                                               command=lambda option=option, option_number=option_number: check_answer(
                                                   que_id, option_number, question_list[2:6]))
                            button.pack(pady=5)
                            option_buttons.append(button)
                            option_number += 1

                        # Create a "Back" button
                        back_button = ttk.Button(frame, text="Back", command=recreate_widgets)
                        back_button.pack(pady=10)



                # Call the show_score function after a delay of 100 milliseconds
                trivia.after(100, show_question)

            def highscore_command():
                for widget in frame.winfo_children():
                    widget.destroy()

                def show_high_score():
                    high_score = get_highscore(client_sock)

                    # Create a frame for high score display
                    high_score_frame = tk.Frame(frame, width=728, height=410)
                    high_score_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

                    # Create a label to display the high score
                    high_score_label = tk.Label(high_score_frame, text="High Score:", font=("Helvetica", 20, "bold"))
                    high_score_label.pack(pady=10)

                    # Create a label to display the actual high score value
                    high_score_value_label = tk.Label(high_score_frame, text=high_score, font=("Helvetica", 18))
                    high_score_value_label.pack(pady=10)

                    def recreate_widgets():
                        # Remove score_label from the frame
                        high_score_label.destroy()
                        # Recreate the widgets in the frame using grid geometry manager
                        recreate_menu_widgets()

                    # Create a "Back" button
                    back_button = ttk.Button(high_score_frame, text="Back", command=recreate_widgets, style="TButton")
                    back_button.pack(pady=10)

                # Call the show_score function after a delay of 100 milliseconds
                trivia.after(100, show_high_score)

            def logged_command():
                for widget in frame.winfo_children():
                    widget.destroy()

                def show_logged():
                    logged = get_logged_users(client_sock)
                    logged_label = tk.Label(frame, text=logged, font=("Helvetica", 14))
                    logged_label.place(relx=0.5, rely=0.5, anchor="center")

                    def recreate_widgets():
                        # Remove score_label from the frame
                        logged_label.destroy()
                        # Recreate the widgets in the frame using grid geometry manager
                        recreate_menu_widgets()

                    # Create a "Back" button
                    back_button = ttk.Button(frame, text="Back", command=recreate_widgets)
                    back_button.place(relx=0.5, rely=0.7,anchor="center")

                # Call the show_score function after a delay of 100 milliseconds
                trivia.after(100, show_logged)

            def recreate_menu_widgets():
                # Remove all widgets from the frame
                for widget in frame.winfo_children():
                    widget.destroy()
                background_label = ttk.Label(frame, image=background_image)
                background_label.image = background_image  # Keep a reference to the image object
                background_label.place(x=0, y=0, relwidth=1, relheight=1)
                # Recreate the widgets in the frame using grid geometry manager

                score_button = ttk.Button(frame, text="Score", command=score_command)
                score_button.grid(row=1, column=0, padx=10, pady=10)

                question_button = ttk.Button(frame, text="Question", command=question_command)
                question_button.grid(row=2, column=0, padx=10, pady=10)

                highscore_button = ttk.Button(frame, text="Highscore", command=highscore_command)
                highscore_button.grid(row=3, column=0, padx=10, pady=10)

                logged_button = ttk.Button(frame, text="Logged", command=logged_command)
                logged_button.grid(row=0, column=0, padx=10, pady=10)

                logout_button = ttk.Button(frame, text="Logout", command=logout_command)
                logout_button.grid(row=4, column=0, padx=10, pady=10)
                # Load and set the icon image
                icon_image = Image.open("photos/sound_icons/sound_on.png")
                icon_image = icon_image.resize((60, 60))
                icon_photo = ImageTk.PhotoImage(icon_image)
                icon_image2 = Image.open("photos/sound_icons/Sound_off.png")
                icon_image2 = icon_image2.resize((60, 60))
                icon_photo2 = ImageTk.PhotoImage(icon_image2)

                def switch_music():
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.pause()
                        switch_button.config(image=icon_photo2)
                    else:
                        pygame.mixer.music.unpause()
                        switch_button.config(image=icon_photo)

                # Create switch button as an icon button
                style = ttk.Style()
                style.configure('Small.TButton', padding=0)  # Set padding to 0 to remove extra space around the button


                if pygame.mixer.music.get_busy():
                    switch_button = ttk.Button(frame, image=icon_photo, command=switch_music, compound='left',
                                               style='Small.TButton')
                    switch_button.image = icon_photo
                    switch_button.place(x=660, y=342, width=icon_photo.width(), height=icon_photo.height())
                else:
                    switch_button = ttk.Button(frame, image=icon_photo2, command=switch_music, compound='left',
                                               style='Small.TButton')
                    switch_button.image = icon_photo2
                    switch_button.place(x=660, y=342, width=icon_photo.width(), height=icon_photo.height())




            score_button = ttk.Button(frame, text="Score", command=score_command)
            score_button.grid(row=1, column=0, padx=10, pady=10)

            question_button = ttk.Button(frame, text="Question", command=question_command)
            question_button.grid(row=2, column=0, padx=10, pady=10)

            highscore_button = ttk.Button(frame, text="Highscore", command=highscore_command)
            highscore_button.grid(row=3, column=0, padx=10, pady=10)

            logged_button = ttk.Button(frame, text="Logged", command=logged_command)
            logged_button.grid(row=0, column=0, padx=10, pady=10)

            logout_button = ttk.Button(frame, text="Logout", command=logout_command)
            logout_button.grid(row=4, column=0, padx=10, pady=10)


            # Load and set the icon image
            icon_image = Image.open("photos/sound_icons/sound_on.png")
            icon_image = icon_image.resize((60, 60))
            icon_photo = ImageTk.PhotoImage(icon_image)
            icon_image2 = Image.open("photos/sound_icons/Sound_off.png")
            icon_image2 = icon_image2.resize((60, 60))
            icon_photo2 = ImageTk.PhotoImage(icon_image2)
            def switch_music():
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.pause()
                    switch_button.config(image=icon_photo2)
                else:
                    pygame.mixer.music.unpause()
                    switch_button.config(image=icon_photo)
            # Create switch button as an icon button
            style = ttk.Style()
            style.configure('Small.TButton', padding=0)  # Set padding to 0 to remove extra space around the button
            switch_button = ttk.Button(frame, image=icon_photo, command=switch_music, compound='left',style='Small.TButton')

            # Set button size to match the size of the icon
            switch_button.image = icon_photo  # Store a reference to the image object to prevent garbage collection
            switch_button.place(x=660, y=342, width=icon_photo.width(), height=icon_photo.height())

            trivia.geometry("728x410")
            trivia.mainloop()


    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    main()
