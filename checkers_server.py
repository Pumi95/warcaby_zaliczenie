import socket
import re
from sys import argv  # IMPORT LIBRARIES
from sys import stdout
from threading import Thread, Timer
import datetime
import os
import os.path
import logging
import Board
import Move
import WinCondition

logging.basicConfig(level=logging.INFO, filename='checkersserver.log',
                    format='[%(levelname)s] %(asctime)s %(threadName)s %(message)s', )

# INICJALIZACJA
buffer_size = 8192
host = '25.31.78.53'
backlog = 10  # Polaczenia w kolejce
block_time = 60  # Czas bana na wypadek trzech niepoprawnych logowan
time_expire = 30 * 60  # Expiry time if user fails to logout

logged_in_users = []  # Przechowuje zalogowanych uzytkownikow
past_connections = {}  # Historia polaczen
blocked_connections = {}  # Przechowuje zablokowanych uzytkownikow
list_of_boards = []  # Przechowuje aktywne plansze do gry


##########################################################################################
##                                  sub-funkcje                                         ##
##########################################################################################


def return_command_size(command):
    counter = 0
    for element in command:
        counter += 1
    #print "Ilosc: " + str(counter)
    return counter


def recv_all(sock, crlf):
    data = ""
    while not data.endswith(crlf):
        data = data + sock.recv(1)
    #print str(data[:-4]) + "\n"

    return data[:-4]


def send_to_client(sock, message, crlf):
    message = message + crlf
    sock.sendall(message)


# Wyszukuje zalogowanego uzytkownika po jego nazwie

def find_user(username):
    for user in logged_in_users:
        if user[0] == username:
            return user
    return None

def is_user_exist(username):
    for user in logged_in_users:
        if user[0] == username:
            return True
    return False


# Wyszukuje grana plansze

def find_board(username):
    for board in list_of_boards:
        if (board[1] == username) or (board[2] == username):
            return board[0]
    return None

# Wyszukuje grana plansze wraz z uzytkownikami do niej przypisanymi

def find_board_full(username):
    for board in list_of_boards:
        if (board[1] == username) or (board[2] == username):
            return board
    return None


# Sprawdza czy dana typu int

def isint(value):
    try:
        int(value)
        return True
    except:
        return False


# Sprawdza poprawnosc podanych koordynatow

def correct_coordinates(command):
    flag = True
    for element in command:
        if isint(element):
            if not (int(element) < 9) and not int(element) > 0:
                flag = False
    return flag


# Zwraca dlugosc komendy

def length_of_command(command):
    amount = 0
    for element in command:
        amount += 1
    return amount


# Sprawdza czy wykonany ruch pionkiem jest poprawny

def check_rules(sender_username, command):
    if length_of_command(command) == 5:
        if correct_coordinates(command):
            start_pos = [int(command[1]), int(command[2])]
            if (find_board_full(sender_username)[1] == sender_username
                and Move.returnCheck(find_board(sender_username), start_pos) == 'x') \
                    or (find_board_full(sender_username)[2] == sender_username
                        and Move.returnCheck(find_board(sender_username), start_pos) == 'o'):
                return True
    return False


##########################################################################################

# Wyswietla uzytkownikow zalogowanych na serwerze

def who_else(client, sender_username):
    other_users = 'Obecnie zalogowani gracze: '

    for user in logged_in_users:
        if user[0] != sender_username:
            if user[2] == True:
                other_users += "[W grze]"
            other_users += user[0] + ' '

    if len(logged_in_users) < 2:
        other_users += 'Brak'

    #client.sendall(other_users)
    send_to_client(client, other_users, "\r\n\r\n")


# Wyswietla menu glowne

def send_old_menu(username, client):

    message ='\nWprowadz komende:\n 1. Nowa Gra\n 2. Gracze online\n 3. Wyloguj\n  '

    receiver_is_logged_in = False
    for user_tuple in logged_in_users:
        if user_tuple[0] == username:
            #user_tuple[1].sendall(message)
            send_to_client(user_tuple[1], message, "\r\n\r\n")
            receiver_is_logged_in = True

    if (not receiver_is_logged_in):
        #client.sendall(username + ' nie jest obecnie zalogowany. ')
        send_to_client(client, str(username) + ' nie jest obecnie zalogowany. ', "\r\n\r\n")


# Wyswietla menu po rozpoczeciu gry

def send_new_menu(username, client):
    if find_board_full(username)[2] == username:
        tmp = 'Twoj pionek to [x]'
    else:
        tmp = 'Twoj pionek to [o]'
    message = tmp + '\nWybierz komende:\n 1. Wykonaj ruch (startowa x | startowa y | docelowa x | docelowa y\n 2. Opusc Gre\n  '

    receiver = find_user(username)[3]

    receiver_is_logged_in = False
    for user_tuple in logged_in_users:
        if user_tuple[0] == receiver:
            #user_tuple[1].sendall(message)
            send_to_client(user_tuple[1], str(message), "\r\n\r\n")
            receiver_is_logged_in = True

    if (not receiver_is_logged_in):
        #client.sendall(receiver + ' nie jest obecnie zalogowany. ')
        send_to_client(client, str(receiver) + ' nie jest obecnie zalogowany. ' , "\r\n\r\n")


# Wyswietla komunikat nakazujacy oczekiwanie na swoj ruch

def send_wait_communicate(username, client):
    message = '\nZaczekaj na swoj ruch\nJezeli chcesz sie poddac nacisnij 2\n  '

    receiver = find_user(username)[3]

    receiver_is_logged_in = False
    for user_tuple in logged_in_users:
        if user_tuple[0] == receiver:
            #user_tuple[1].sendall(message)
            send_to_client(user_tuple[1], str(message), "\r\n\r\n")
            receiver_is_logged_in = True

    if (not receiver_is_logged_in):
        #client.sendall(receiver + ' nie jest obecnie zalogowany ')
        send_to_client(client, str(receiver) + ' nie jest obecnie zalogowany. ', "\r\n\r\n")


def wait_for_your_move(sender_username, client):
    receiver = find_user(sender_username)[3]

    receiver_is_logged_in = False
    for user_tuple in logged_in_users:
        if user_tuple[0] == receiver:
            receiver_is_logged_in = True

    if not receiver_is_logged_in:
        #client.sendall(receiver + ' gracz skonczyl gre. ')
        send_to_client(client, str(receiver) + ' gracz skonczyl gre ', "\r\n\r\n")


# Wysylanie ruchu
def send_move(sender_username, client, command):
    is_bad = False
    message = ''
    if check_rules(sender_username, command):  # Bardzo dlugi if
        start_pos = [int(command[1]), int(command[2])]
        target_pos = [int(command[3]), int(command[4])]
        msg = Move.move(find_board(sender_username), start_pos, target_pos)
        message = Board.printBoard(find_board(sender_username))
        if WinCondition.isGameEnded(find_board(sender_username)):
            if WinCondition.checkWhoWin(find_board(sender_username)):
                #find_user(find_board_full(sender_username)[2]).sendall('wygrales o')
                send_to_client(find_user(find_board_full(sender_username)[2])[1],'wygrales', "\r\n\r\n")
                send_to_client(find_user(find_board_full(sender_username)[1])[1], 'przegrales', "\r\n\r\n")
                find_user(find_board_full(sender_username)[1])[2] = False
                find_user(find_board_full(sender_username)[2])[2] = False
                send_old_menu(find_board_full(sender_username)[1], find_user(find_board_full(sender_username)[1]))
                send_old_menu(find_board_full(sender_username)[2], find_user(find_board_full(sender_username)[2]))
                list_of_boards.remove(find_board_full(sender_username))
            else:
                #find_user(find_board_full(sender_username)[1]).sendall('wygrales x')
                send_to_client(find_user(find_board_full(sender_username)[1])[1],'wygrales', "\r\n\r\n")
                send_to_client(find_user(find_board_full(sender_username)[2])[1], 'przegrales', "\r\n\r\n")
                find_user(find_board_full(sender_username)[1])[2] = False
                find_user(find_board_full(sender_username)[2])[2] = False
                send_old_menu(find_board_full(sender_username)[1], find_user(find_board_full(sender_username)[1]))
                send_old_menu(find_board_full(sender_username)[2], find_user(find_board_full(sender_username)[2]))
                list_of_boards.remove(find_board_full(sender_username))
    else:
        is_bad = True

    receiver = find_user(sender_username)[3]

    receiver_is_logged_in = False
    for user_tuple in logged_in_users:
        if user_tuple[0] == receiver or user_tuple[0] == sender_username:
            #user_tuple[1].sendall(message)
            send_to_client(user_tuple[1], str(message), "\r\n\r\n")
            #send_to_client(user_tuple[1], str(msg), "\r\n\r\n")
            receiver_is_logged_in = True

    if not receiver_is_logged_in:
        #client.sendall(receiver + ' gracz skonczyl gre. ')
        send_to_client(client, str(receiver) + ' gracz skonczyl gre. ', "\r\n\r\n")

    if not is_bad and msg == 'Ruch wykonany!':
        find_user(sender_username)[4] = False
        find_user(find_user(sender_username)[3])[4] = True
        send_new_menu(sender_username, client)
        send_wait_communicate(find_user(sender_username)[3], find_user(find_user(sender_username)[3])[1])
    else:
        for user in logged_in_users:
            if user[0] == sender_username:
                #user[1].sendall(Board.printBoard(find_board(sender_username)))
                send_to_client(user[1], str(Board.printBoard(find_board(sender_username))), "\r\n\r\n")
                #user[1].sendall('Podano zle dane\n')
                send_to_client(user[1], 'Niepoprawny ruch!!! Sprobuj jeszcze raz.', "\r\n\r\n")
        send_new_menu(find_user(sender_username)[3], client)
    return is_bad


# Rozpoczecie nowej gry

def new_game(sender_username, client, command):
    message = 'Gre zainicjowal ' + sender_username + ': \n'
    receiver = command[1]
    message += Board.printBoard(find_board(sender_username))

    receiver_is_logged_in = False
    for user_tuple in logged_in_users:
        if user_tuple[0] == receiver or user_tuple[0] == sender_username:
            #user_tuple[1].sendall(message)
            send_to_client(user_tuple[1], str(message), "\r\n\r\n")
            receiver_is_logged_in = True

    if not receiver_is_logged_in:
        #client.sendall(receiver + ' nie jest obecnie zalogowany ')
        send_to_client(client, str(receiver) + ' nie jest obecnie zalogowany ', "\r\n\r\n")


# Powrot do menu

def exit_game(client):
    for user in logged_in_users:
        if user[1] == client:
            tmp = find_user(user[0])
            if tmp[3] != None:
                tmp_send = find_user(tmp[3])
                user[2] = False
                user[3] = None
                user[4] = False
                tmp_send[2] = False
                tmp_send[3] = None
                tmp_send[4] = False
                #tmp_send[1].sendall('Gracz przeciwny sie wylogowal - wygrales walkowerem!')
                send_to_client(tmp_send[1], 'Gracz przeciwny sie wylogowal - wygrales walkowerem!', "\r\n\r\n")
                send_old_menu(tmp_send[0], tmp_send[1])
                #send_old_menu(user[0], user[1])

# Wylogowywanie

def logout(client):
    for user in logged_in_users:
        if user[1] == client:
            tmp = find_user(user[0])
            if tmp[3] != None:
                tmp_send = find_user(tmp[3])
                user[2] = False
                user[3] = None
                user[4] = False
                tmp_send[2] = False
                tmp_send[3] = None
                tmp_send[4] = False
                #tmp_send[1].sendall('Gracz przeciwny sie wylogowal - wygrales walkowerem!')
                send_to_client(tmp_send[1], 'Gracz przeciwny sie wylogowal - wygrales walkowerem!', "\r\n\r\n")
                send_old_menu(tmp_send[0], tmp_send[1])
    #client.sendall('Good bye!')
    send_to_client(client, 'Good bye!', "\r\n\r\n")
    client.close()


# Obsluzenie wyjscia gracza w trakcie gry

def client_exit(client, client_ip, client_port):
    for user in logged_in_users:
        if user[1] == client:
            tmp = find_user(user[0])
            if tmp[3] != None:
                tmp_send = find_user(tmp[3])
                user[2] = False
                user[3] = None
                user[4] = False
                tmp_send[2] = False
                tmp_send[3] = None
                tmp_send[4] = False
                #tmp_send[1].sendall('Gracz przeciwny sie wylogowal - wygrales walkowerem!')
                send_to_client(tmp_send[1], 'Gracz przeciwny sie wylogowal - wygrales walkowerem!', "\r\n\r\n")
                send_old_menu(tmp_send[0], tmp_send[1])
            logged_in_users.remove(user)

    print 'Client on %s : %s disconnected' % (client_ip, client_port)
    logging.info("Client on IP {} & Port {} Disconnected".format(client_ip, client_port))
    open("user_pass.txt", 'w').close()
    stdout.flush()
    client.close()


# Funkcja wywolywana przy zbyt dlugiej nieaktywnosci uzytkownika

def client_timeout(client, client_identifier):
    #client.sendall('Twoja sesja zostala zakonczona przez zbyt dluga bezczynnosc ')
    send_to_client(client, 'Twoja sesja zostala zakonczona przez zbyt dluga bezczynnosc ', "\r\n\r\n")
    client.close()


# Wiersz polecen

def prompt_commands(client, client_ip_and_port, username):
    while 1:
        try:
            if not find_user(username)[2]:  #menu glowne
                #client.sendall('\nWprowadz komende:\n 1. Nowa Gra\n 2. Gracze online\n 3. Wyloguj\n  ')
                send_to_client(client, '\nWprowadz komende:\n 1. Nowa Gra\n 2. Gracze online\n 3. Wyloguj\n  ', "\r\n\r\n")

            timeout_countdown = Timer(time_expire, client_timeout, (client, client_ip_and_port))
            timeout_countdown.start()

            #command = client.recv(buffer_size).split()
            command = recv_all(client,"\r\n\r\n").split()

            timeout_countdown.cancel()
            past_connections[username] = datetime.datetime.now()

        except:
            logout(client)
            client.close()
        #print find_user(username)
        if return_command_size(command) != 0:
            if find_user(username)[2] == False:  #rozpoczecie nowej gry
                if command[0] == "1":
                    if return_command_size(command) == 2:
                        if is_user_exist(command[1]):
                            if find_user(command[1])[2] == False:
                                if command[1] != username:
                                    list_of_boards.append([Board.createBoard(), username, command[1]])
                                    find_user(username)[2] = True
                                    find_user(username)[3] = command[1]
                                    find_user(command[1])[2] = True
                                    find_user(command[1])[3] = username
                                    find_user(command[1])[4] = True
                                    new_game(username, client, command)
                                    send_new_menu(username, client)
                                    send_wait_communicate(find_user(username)[3], find_user(find_user(username)[3])[1])
                                else:
                                    send_to_client(client, 'Nie mozesz wybrac samego siebie', "\r\n\r\n")
                            else:
                                send_to_client(client, 'Wybrany gracz jest w trakcie gry .. ', "\r\n\r\n")
                        else:
                            send_to_client(client, 'Gracz o podanej nazwie nie istnieje ', "\r\n\r\n")
                    else:
                        send_to_client(client, 'Zla ilosc argumentow. Sprobuj jeszcze raz... ', "\r\n\r\n")
                elif command[0] == "2" and return_command_size(command) == 1:
                    who_else(client, username)
                elif command[0] == "3" and return_command_size(command) == 1:
                    logout(client)
                elif command[0] == "1" and find_user(command[1])[2] == True  and return_command_size(command) == 2:
                    #client.sendall('Wybrany gracz jest w trakcie gry .. ')
                    send_to_client(client, 'Wybrany gracz jest w trakcie gry .. ', "\r\n\r\n")
                else:
                    #client.sendall('Nie znaleziono podanej komendy. ')
                    send_to_client(client, 'Nie znaleziono podanej komendy lub zostala zle wprowadzona. ', "\r\n\r\n")

            elif find_user(username)[4]:  # komendy po rozpoczeciu gry, gdy jest twoj ruch
                if command[0] == "1" and return_command_size(command) == 5:
                    send_move(username, client, command)

                elif command[0] == "2" and return_command_size(command) == 1:
                    exit_game(client)
                else:
                    #client.sendall('Nie znaleziono podanej komendy. ')
                    send_to_client(client, 'Nie znaleziono podanej komendy lub zostala zle wprowadzona. ', "\r\n\r\n")

            else:  # komendy po rozpoczeciu gry, gdy jest ruch przeciwnika
                if command[0] == "1":
                    wait_for_your_move(username, client)
                elif command[0] == "2" and return_command_size(command) == 1:
                    exit_game(client)
                else:
                    #client.sendall('Nie znaleziono podanej komendy. ')
                    send_to_client(client, 'Nie znaleziono podanej komendy lub zostala zle wprowadzona. ', "\r\n\r\n")
        else:
            send_to_client(client, 'Nie wprowadzono polecenia. ', "\r\n\r\n")

# Logowanie

def login(client, username):
    #client.sendall('\nZalogowano pomyslnie !!! Witaj w grze Warcaby OnLine')
    send_to_client(client, '\nZalogowano pomyslnie !!! Witaj w grze Warcaby OnLine', "\r\n\r\n")
    logged_in_users.append([username, client, False, None, False])  # [nazwa uzytkownika, socket, czy w grze, z kim sparowany, czy twoj ruch]
    past_connections[username] = datetime.datetime.now()


# Blokowanie

def block(ip_addr, client_sock, username):
    list_of_blocked_usernames = blocked_connections[ip_addr]
    list_of_blocked_usernames.append(username)
    blocked_connections[ip_addr] = list_of_blocked_usernames
    client_sock.close()


# Odblokowywanie zablokowanych uzytkownikow

def unblock(ip_addr, username):
    list_of_blocked_usernames = blocked_connections[ip_addr]
    list_of_blocked_usernames.remove(username)
    blocked_connections[ip_addr] = list_of_blocked_usernames


# Sprawdza czy uzytkownik zablokowany

def is_blocked(ip_addr, username):
    list_of_blocked_usernames = blocked_connections[ip_addr]
    if (username in list_of_blocked_usernames):
        return True
    return False


# Sprawdza czy uzytkownik zalogowany

def is_already_logged_in(username):
    for user in logged_in_users:
        if user[0] == username:
            return True
    return False


# Funkcja logowania

def prompt_login(client_sock, client_ip, client_port):
    username = 'default'

    while (not username in logins):
        #client_sock.sendall('\nWprowadz poprawna nazwe uzytkownika ')
        send_to_client(client_sock, '\nWprowadz poprawna nazwe uzytkownika ', "\r\n\r\n")
        #username = client_sock.recv(buffer_size)
        username = recv_all(client_sock,"\r\n\r\n").split()
        username = username[0]

        if (is_blocked(client_ip, username)):
            #client_sock.('Dostep do danego konta jest czasowo zablokowany')
            send_to_client(client_sock, 'Dostep do danego konta jest czasowo zablokowany', "\r\n\r\n")
            username = 'default'

        if (is_already_logged_in(username)):
            #client_sock.sendall('Uzytkownik o tym loginie jest obecnie zalogowany')
            send_to_client(client_sock, 'Uzytkownik o tym loginie jest obecnie zalogowany', "\r\n\r\n")
            username = 'default'

    login_attempt_count = 0

    while login_attempt_count < 3:
        #client_sock.sendall('Wprowadz swoje haslo ')
        send_to_client(client_sock, 'Wprowadz swoje haslo ', "\r\n\r\n")
        #password = client_sock.recv(buffer_size)
        password = recv_all(client_sock,"\r\n\r\n").split()
        password = password[0]

        if (logins[username] != password):
            login_attempt_count += 1
            #client_sock.sendall('Podano niewlasciwy login badz haslo. Sprobuj ponownie. ')
            send_to_client(client_sock, 'Podano niewlasciwy login badz haslo. Sprobuj ponownie. ', "\r\n\r\n")

        elif (logins[username]) and (logins[username] == password):
            login(client_sock, username)
            return (True, username, False)

    return (False, username, False)


# Funcja tworzenia nowego uzytkownika

def prompt_create_username(client_sock):
    #client_sock.sendall('Witaj w grze Warcaby OnLine. Czy chcesz stowrzyc nowego Gracza? [tak/nie]')
    send_to_client(client_sock, 'Witaj w grze Warcaby OnLine. Czy chcesz stowrzyc nowego Gracza? [tak/nie]', "\r\n\r\n")
    #response = client_sock.recv(buffer_size)
    response = recv_all(client_sock,"\r\n\r\n").split()

    if (response[0] == "tak"):
        created_username = False
        new_user = ""
        while (not created_username):
            #client_sock.sendall('Wprowadz Login ')
            send_to_client(client_sock, 'Wprowadz Login ', "\r\n\r\n")
            #new_user = client_sock.recv(buffer_size)
            new_user = recv_all(client_sock,"\r\n\r\n").split()

            if (len(new_user[0]) < 3 or len(new_user[0]) > 8):
                #client_sock.sendall('Login musi zawierac od 3 do 8 znakow ')
                send_to_client(client_sock, 'Login musi zawierac od 3 do 8 znakow ', "\r\n\r\n")

            elif (new_user[0] in logins):
                #client_sock.sendall('Gracz o podanym loginie istnieje. Sprobuj jeszcze raz')
                send_to_client(client_sock, 'Gracz o podanym loginie istnieje. Sprobuj jeszcze raz', "\r\n\r\n")
            else:
                created_username = True

        new_pass = ""
        created_password = False
        while (not created_password):
            #client_sock.sendall('Wprowadz haslo')
            send_to_client(client_sock, 'Wprowadz haslo', "\r\n\r\n")
            #new_pass = client_sock.recv(buffer_size)
            new_pass = recv_all(client_sock,"\r\n\r\n").split()

            if (len(new_pass[0]) < 4 or len(new_pass[0]) > 8):
                #client_sock.sendall('Haslo musi zawierac od 4 do 8 znakow')
                send_to_client(client_sock, 'Haslo musi zawierac od 4 do 8 znakow', "\r\n\r\n")
            else:
                created_password = True

        new_user = new_user[0]
        new_pass = new_pass[0]
        with open('user_pass.txt', 'a') as aFile:
            aFile.write('\n' + new_user + ' ' + new_pass)

        logins[new_user] = new_pass

        #client_sock.sendall('Stworzono nowego Gracza!! Teraz mozesz sie zalogowac\n')
        send_to_client(client_sock, 'Stworzono nowego Gracza!! Teraz mozesz sie zalogowac\n', "\r\n\r\n")


# Obsluga uzytkownika

def handle_client(client_sock, client_ip_and_port):
    client_ip = client_ip_and_port[0]
    client_port = client_ip_and_port[1]

    if (not blocked_connections.has_key(client_ip)):
        blocked_connections[client_ip] = []

    prompt_create_username(client_sock)

    try:
        while 1:
            user_login = prompt_login(client_sock, client_ip, client_port)
            logging.info("User Login Info = {}".format(user_login))

            if (user_login[0]):
                prompt_commands(client_sock, client_ip_and_port, user_login[1])
            else:
                #client_sock.sendall('Nieudana proba zalogowana zbyt duza ilosc razy. Sprobuj ponownie za 60 sekund')
                send_to_client(client_sock, 'Nieudana proba zalogowana zbyt duza ilosc razy. Sprobuj ponownie za 60 sekund', "\r\n\r\n")
                block(client_ip, client_sock, user_login[1])
                Timer(block_time, unblock, (client_ip, user_login[1])).start()
    except:
        client_exit(client_sock, client_ip, client_port)


# Zwraca zalogowanych w historii uzytkownikow

def populate_logins_dictionaries():
    user_logins = {}

    with open('user_pass.txt') as aFile:
        for line in aFile:
            (key, val) = line.split()
            user_logins[key] = val

    return user_logins


def main(argv):
    server_port = 9537
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, server_port))
    sock.listen(backlog)
    print 'Server on port ' + str(server_port)
    logging.info("The game server is running on IP address 127.0.0.1 & on PORT number {}".format(server_port))
    stdout.flush()

    try:
        while 1:
            client_connection, addr = sock.accept()
            print 'Client connected on ' + str(addr[0]) + ':' + str(addr[1])
            logging.info("game Client Connected on IP {} & Port {}".format(host, server_port))
            stdout.flush()
            thread = Thread(target=handle_client, args=(client_connection, addr))
            thread.start()
    except (KeyboardInterrupt, SystemExit):
        stdout.flush()
        open("user_pass.txt", 'w').close()
        print '\nServer shut down.'


logins = populate_logins_dictionaries()
main(argv)
