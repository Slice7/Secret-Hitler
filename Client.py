from tkinter import *
from tkinter import ttk
import socket
from cryptography.fernet import Fernet
from time import sleep


def crypt_send(packet):
    if len(packet) > 15:
        print('SENDING DATA LONGER THAN 15 BYTES')
    token = f.encrypt(packet)
    sock.sendall(token)


def return_send(packet):
    if len(packet) > 15:
        print('SENDING DATA LONGER THAN 15 BTYES')
    token = f.encrypt(packet)
    sock.sendall(token)
    global return_query_val
    return_query_val = packet.decode()


def crypt_recv():
    sock.setblocking(False)
    while True:
        try:
            token = sock.recv(100)
            packet = f.decrypt(token).decode()
            break
        except BlockingIOError:
            root.update()
            sleep(0.02)
    sock.setblocking(True)
    return packet


def envelope_x():
    if my_role == 'Fascist' or (my_role == 'Hitler' and player_count < 7):
        sock.setblocking(False)
        fascists_packet = crypt_recv()
        if len(fascists_packet) != (player_count-1)//2:  # in case chancellor is received in fascist packet; shouldn't be necessary
            global chancellor
            chancellor = int(fascists_packet[-1])
            fascists_packet = fascists_packet[:-1]
        fascists = []
        for pos, fascist in enumerate(fascists_packet[1:]):
            fascists.append(ttk.Label(board, image=fascist_img, padding='-2 -2 -2 -2'))
            fascists[pos].place(x=icon_pos[int(fascist)][0], y=icon_pos[int(fascist)][1])
        hitler = ttk.Label(board, image=hitler_img, padding='-2 -2 -2 -2')
        hitler.place(x=icon_pos[int(fascists_packet[0])][0], y=icon_pos[int(fascists_packet[0])][1])
    if my_role == 'Hitler' and player_count > 6:
        hitler = ttk.Label(board, image=hitler_img, padding='-2 -2 -2 -2')
        hitler.place(x=icon_pos[ID][0], y=icon_pos[ID][1])
    global resume
    resume = True


def env_selection(choice):
    choice_name = choice+my_name
    crypt_send(choice_name.encode())
    global my_role
    token = sock.recv(100)
    my_role = f.decrypt(token).decode()
    env_title.destroy()
    for e in envelopes:
        e.destroy()
    envelopes_menu.place(x=(board_x-(env_x*2 + 32))//2, y=env_menu_y)
    if my_role == 'Fascist':
        fas_party.grid(column=0, row=1, padx=(10, 5), pady=10)
        sec_fas1.grid(column=1, row=1, padx=(5, 10))
    elif my_role == 'Hitler':
        fas_party.grid(column=0, row=1, padx=(10, 5), pady=10)
        secret_hitler.grid(column=1, row=1, padx=(5, 10))
    else:
        lib_party.grid(column=0, row=1, padx=(10, 5), pady=10)
        sec_lib1.grid(column=1, row=1, padx=(5, 10))

    cross1 = Button(envelopes_menu, image=cross_img, borderwidth=0, highlightthickness=0,
                    command=lambda: (envelopes_menu.destroy(), pres.place(x=label_pos[president][0], y=label_pos[president][1]), envelope_x()))
    cross1.grid(column=1, row=0, sticky='E')


def pol_selection(choice):
    crypt_send(choice.encode())
    policy_menu.destroy()
    global discard
    discard = choice


def player_button(player):
    crypt_send(str(player).encode())
    global player_selection
    player_selection = player


def query(message):
    vote_menu = ttk.Label(board, style='TFrame')
    vote_menu.place(x=(board_x-(2*jn_x - 20))//2, y=jn_menu_y)
    vote_title = ttk.Label(vote_menu, text=message, style='TLabel')
    ja_ = Button(vote_menu, image=ja_img, borderwidth=0, highlightthickness=0,
                 command=lambda: (crypt_send(b'j'), vote_menu.destroy(), notification.place(x=notif_x, y=0)))
    nein_ = Button(vote_menu, image=nein_img, borderwidth=0, highlightthickness=0,
                   command=lambda: (crypt_send(b'n'), vote_menu.destroy(), notification.place(x=notif_x, y=0)))
    vote_title.grid(column=0, row=0, columnspan=2)
    ja_.grid(column=0, row=1, padx=5, pady=5)
    nein_.grid(column=1, row=1, padx=5, pady=5)


def return_query(message):
    jn_menu = ttk.Label(board, style='TFrame')
    jn_menu.place(x=(board_x-(2*jn_x - 20))//2, y=jn_menu_y)
    jn_title = ttk.Label(jn_menu, text=message, style='TLabel')
    ja_ = Button(jn_menu, image=ja_img, borderwidth=0, highlightthickness=0, command=lambda: (return_send(b'j'), jn_menu.destroy()))
    nein_ = Button(jn_menu, image=nein_img, borderwidth=0, highlightthickness=0, command=lambda: (return_send(b'n'), jn_menu.destroy()))
    jn_title.grid(column=0, row=0, columnspan=2)
    ja_.grid(column=0, row=1, padx=5, pady=5)
    nein_.grid(column=1, row=1, padx=5, pady=5)


def hitler_func(is_hitler_, menu, title):
    global hitler_val
    if my_role != 'Hitler' or is_hitler_ == 'n':
        if (my_role == 'Hitler') != (is_hitler_ == 'j'):
            title['text'] = 'Nice try.\nAre you Hitler?'
        elif my_role != 'Hitler':
            hitler_val = 'n'
            menu.destroy()
    else:
        hitler_val = 'j'
        menu.destroy()


def hitler_query(message):
    jn_menu = ttk.Label(board, style='TFrame')
    jn_menu.place(x=(board_x-(2*jn_x - 20))//2, y=jn_menu_y)
    jn_title = ttk.Label(jn_menu, text=message, style='TLabel')
    ja_ = Button(jn_menu, image=ja_img, borderwidth=0, highlightthickness=0, command=lambda: hitler_func('j', jn_menu, jn_title))
    nein_ = Button(jn_menu, image=nein_img, borderwidth=0, highlightthickness=0, command=lambda: hitler_func('n', jn_menu, jn_title))
    jn_title.grid(column=0, row=0, columnspan=2)
    ja_.grid(column=0, row=1, padx=5, pady=5)
    nein_.grid(column=1, row=1, padx=5, pady=5)


def window_resize(*args):
    wid = root.winfo_width()
    hei = root.winfo_height()
    wid1 = (wid-board_x) // 2
    hei1 = (hei-board_y) // 2
    mainframe['padding'] = '{} {} 0 0'.format(str(wid1), str(hei1))


key = input('Key: ')
key = key.strip().encode()
f = Fernet(key)  # AES-256 in CBC mode

host = socket.gethostname()
port = 12345
my_name = input('Enter your name (max 12 chars): ')
while len(my_name) > 12:
    my_name = input('Enter your name (max 12 chars): ')

player_names = []
fascist_pol = 0
liberal_pol = 0
election_tracker_count = 0
ineligible_chancellor = []
special_election = False
killed_players = []
agree_veto = None
resume = False

root = Tk()
root.title('Secret Hitler')
root.bind('<Configure>', window_resize)

fascist_img = PhotoImage(file='Assets\\icons\\fascist.png')
hitler_img = PhotoImage(file='Assets\\icons\\hitler.png')
ja_icon_img = PhotoImage(file='Assets\\icons\\ja_icon.png')
nein_icon_img = PhotoImage(file='Assets\\icons\\nein_icon.png')

ttk.Style().configure('TFrame', background='#302E2E')
ttk.Style().configure('TLabel', background='#302E2E', foreground='white', font=('MV Boli', 12))

mainframe = ttk.Frame(root)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

mainframe.grid(column=0, row=0, sticky='NSEW')
screen_resolution = (root.winfo_screenwidth(), root.winfo_screenheight())
if screen_resolution[0] < 1897 or screen_resolution[1] < 1080:
    res = '720'
    board_x = 1349
    board_y = 700
    env_x = 157
    sec_id_x = 190
    jn_x = 199
    pol_x = 89

    player_pos_dict = {5: ((633, 639), (101, 520), (280, 39), (1003, 39), (1172, 520)),
                       6: ((633, 639), (133, 582), (64, 134), (640, 39), (1209, 134), (1141, 582)),
                       7: ((633, 639), (155, 574), (50, 257), (408, 39), (865, 39), (1223, 257), (1118, 574)),
                       8: ((633, 639), (208, 618), (44, 329), (204, 49), (640, 39), (1069, 49), (1229, 329), (1065, 618)),
                       9: ((633, 639), (255, 626), (59, 417), (59, 100), (435, 39), (838, 39), (1214, 100), (1214, 417), (1018, 626)),
                       10: ((633, 639), (274, 626), (30, 458), (30, 174), (284, 39), (640, 39), (989, 39), (1243, 174), (1243, 458), (998, 626))}

    liberal_pos = [429, 529, 629, 730, 831]  # liberal policy on board
    lib_y = 158
    fascist_pos = [380, 480, 581, 681, 782, 883]  # fascist policy on board
    fas_y = 412
    election_tracker_pos = [553, 621, 689, 757]  # do i need to explain this one lol
    election_tracker_y = 296

    env_menu_y, mem_menu_y = 116, 116
    jn_menu_y, pol_menu_y = 38, 38
    peek_menu_y = 238
    notif_x = 450

else:
    res = '1080'
    board_x = 1895
    board_y = 985
    env_x = 201
    sec_id_x = 138
    jn_x = 324
    pol_x = 122

    player_pos_dict = {5: ((915, 905), (157, 737), (395, 60), (1424, 60), (1662, 737)),
                       6: ((915, 905), (202, 825), (105, 194), (915, 60), (1714, 194), (1617, 825)),
                       7: ((915, 905), (233, 813), (85, 367), (588, 60), (1231, 60), (1734, 367), (1586, 813)),
                       8: ((915, 905), (308, 875), (77, 469), (302, 75), (915, 60), (1517, 75), (1742, 469), (1511, 875)),
                       9: ((915, 905), (373, 886), (98, 593), (98, 147), (626, 60), (1193, 60), (1721, 147), (1721, 593), (1446, 886)),
                       10: ((915, 905), (401, 887), (51, 650), (51, 250), (414, 61), (915, 60), (1405, 61), (1768, 250), (1768, 650), (1418, 887))}

    liberal_pos = [610, 747, 886, 1023, 1163]  # liberal policy on board
    lib_y = 229
    fascist_pos = [541, 679, 817, 956, 1095, 1234]  # fascist policy on board
    fas_y = 580
    election_tracker_pos = [780, 874, 968, 1062]  # do i need to explain this one lol
    election_tracker_y = 419

    env_menu_y, mem_menu_y = 171, 171
    jn_menu_y, pol_menu_y = 40, 40
    peek_menu_y = 325
    notif_x = 800

board_56_img = PhotoImage(file='Assets\\{}\\boards\\board_5-6.gif'.format(res))
board_78_img = PhotoImage(file='Assets\\{}\\boards\\board_7-8.gif'.format(res))
board_910_img = PhotoImage(file='Assets\\{}\\boards\\board_9-10.gif'.format(res))

envelope_img = PhotoImage(file='Assets\\{}\\misc\\envelope.png'.format(res))
chancellor_img = PhotoImage(file='Assets\\{}\\misc\\chancellor.png'.format(res))
president_img = PhotoImage(file='Assets\\{}\\misc\\president.png'.format(res))
ja_img = PhotoImage(file='Assets\\{}\\misc\\ja.png'.format(res))
nein_img = PhotoImage(file='Assets\\{}\\misc\\nein.png'.format(res))
tracker_img = PhotoImage(file='Assets\\{}\\misc\\tracker.png'.format(res))
cross_img = PhotoImage(file='Assets\\{}\\misc\\cross.png'.format(res))

lib_party_img = PhotoImage(file='Assets\\{}\\parties\\lib_party.png'.format(res))
fas_party_img = PhotoImage(file='Assets\\{}\\parties\\fas_party.png'.format(res))

lib_pol1_img = PhotoImage(file='Assets\\{}\\policies\\lib_pol1.png'.format(res))
lib_pol2_img = PhotoImage(file='Assets\\{}\\policies\\lib_pol2.png'.format(res))
lib_pol3_img = PhotoImage(file='Assets\\{}\\policies\\lib_pol3.png'.format(res))
fas_pol1_img = PhotoImage(file='Assets\\{}\\policies\\fas_pol1.png'.format(res))
fas_pol2_img = PhotoImage(file='Assets\\{}\\policies\\fas_pol2.png'.format(res))
fas_pol3_img = PhotoImage(file='Assets\\{}\\policies\\fas_pol3.png'.format(res))

sec_lib1_img = PhotoImage(file='Assets\\{}\\roles\\sec_lib1.png'.format(res))
sec_fas1_img = PhotoImage(file='Assets\\{}\\roles\\sec_fas1.png'.format(res))
secret_hitler_img = PhotoImage(file='Assets\\{}\\roles\\secret_hitler.png'.format(res))

root.minsize(board_x, board_y)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

    print('Connecting...')
    try:
        sock.connect((host, port))
        print('Connection successful')
    except ConnectionRefusedError:
        print('Connection failed')

    ID_Pr_PC_token = sock.recv(100)
    ID_Pres_PC = f.decrypt(ID_Pr_PC_token).decode()
    ID, president, player_count = int(ID_Pres_PC[0]), int(ID_Pres_PC[1]), int(ID_Pres_PC[2:])
    players_remaining = player_count
    pres_x = president
    not_hitler = [0] * player_count
    player_pos = player_pos_dict[player_count]
    liberal_policies = []
    fascist_policies = []

    if player_count < 7:
        board = ttk.Label(mainframe, image=board_56_img, padding='-2 -2 -2 -2')
    elif player_count < 9:
        board = ttk.Label(mainframe, image=board_78_img, padding='-2 -2 -2 -2')
    else:
        board = ttk.Label(mainframe, image=board_910_img, padding='-2 -2 -2 -2')
    board.grid(column=0, row=0)

    election_tracker = ttk.Label(board, image=tracker_img, padding='-2 -2 -2 -2')
    election_tracker.place(x=election_tracker_pos[0], y=election_tracker_y)

    envelopes_menu = ttk.Label(board, style='TFrame')
    fas_party = ttk.Label(envelopes_menu, image=fas_party_img, padding='-2 -2 -2 -2')
    lib_party = ttk.Label(envelopes_menu, image=lib_party_img, padding='-2 -2 -2 -2')
    sec_fas1 = ttk.Label(envelopes_menu, image=sec_fas1_img, padding='-2 -2 -2 -2')
    secret_hitler = ttk.Label(envelopes_menu, image=secret_hitler_img, padding='-2 -2 -2 -2')
    sec_lib1 = ttk.Label(envelopes_menu, image=sec_lib1_img, padding='-2 -2 -2 -2')
    sheev = ttk.Label(board, image=chancellor_img, padding='-2 -2 -2 -2')
    pres = ttk.Label(board, image=president_img, padding='-2 -2 -2 -2')

    icon_pos = []  # fascist/hitler icons
    label_pos = []  # president/chancellor
    vote_icon_pos = []  # ja/nein icons
    players = []
    for i in range(player_count):
        j = (i-ID) % player_count
        icon_pos.append([player_pos[j][0]-35, player_pos[j][1]-2])
        label_pos.append([player_pos[j][0], player_pos[j][1]+30])
        vote_icon_pos.append([player_pos[j][0]+85, player_pos[j][1]-3])
        players.append(ttk.Button(board, text='', state='disabled', command=lambda i=i: player_button(i)))
        players[i].place(x=player_pos[j][0], y=player_pos[j][1])

    if ID != 0:
        envelopes_menu.place(x=notif_x, y=0)
        env_title = ttk.Label(envelopes_menu, text='Waiting for envelopes', style='TLabel')
        env_title.grid(row=0, column=0, padx=5, pady=5, columnspan=(player_count+1) & (-2))  # round up to even

        roles_taken = crypt_recv()
        envelopes_menu.place(x=board_x//2-(((player_count+1)//2)*env_x+((player_count-1)//2)*10+40)//2, y=env_menu_y)
        env_title['text'] = 'Choose an envelope'
    else:
        envelopes_menu.place(x=board_x//2-(((player_count+1)//2)*env_x+((player_count-1)//2)*10+40)//2, y=env_menu_y)
        roles_taken = crypt_recv()
        env_title = ttk.Label(envelopes_menu, text='Choose an envelope', style='TLabel')
        env_title.grid(row=0, column=0, pady=5, columnspan=(player_count+1) & (-2))  # round up to even

    envelopes = []
    for i in range(player_count):
        j = str(i)
        envelopes.append(Button(envelopes_menu, image=envelope_img, borderwidth=0, highlightthickness=0, command=lambda j=j: env_selection(j)))
        if j in roles_taken:
            pass
        else:
            envelopes[i].grid(column=(2*i % player_count), row=2*i//player_count + 1, padx=10, pady=(5, 10), columnspan=2)

    while not resume:
        root.update()
        sleep(0.02)
    resume = True

    for i in range(player_count):
        player_names.append(crypt_recv())
        players[i]['text'] = player_names[i]

    notification = ttk.Label(board, text='', padding='5 5 5 5', style='TLabel')

    while True:

        if agree_veto == 'j':
            ja, nein = 0, 0

        else:
            if ID == president:
                notification['text'] += 'Nominate a chancellor'
                notification.place(x=notif_x, y=0)
                for i in [x for x in range(player_count) if x not in ineligible_chancellor+killed_players+[ID]]:
                    players[i].state(['!disabled'])

                while True:
                    try:
                        chancellor = player_selection
                        del player_selection
                        break
                    except NameError:
                        root.update()
                        sleep(0.02)

                notification.destroy()
                for i in [x for x in range(player_count) if x not in ineligible_chancellor + killed_players + [ID]]:
                    players[i].state(['disabled'])
            else:
                notification['text'] += 'Waiting for {} to nominate a chancellor'.format(player_names[president])
                notification.place(x=notif_x, y=0)
                chancellor = int(crypt_recv())
                notification.destroy()

            try:
                for vote in vote_icons:
                    vote.destroy()
            except NameError:
                pass

            if ID not in killed_players:
                if ID == chancellor:
                    query('{} nominates you.\nElect government?'.format(player_names[president]))
                else:
                    query('{} nominates {}.\nElect government?'.format(player_names[president], player_names[chancellor]))
                notification = ttk.Label(board, text='Waiting for votes', padding='5 5 5 5', style='TLabel')
            else:
                notification = ttk.Label(board, text='{} nominates {}.\nWaiting for votes'.format(player_names[president], player_names[chancellor]),
                                         padding='5 5 5 5', style='TLabel')
                notification.place(x=notif_x, y=0)

            votes = crypt_recv()
            vote_icons = []
            ja, nein = 0, 0

            for i, j in enumerate([x for x in range(player_count) if x not in killed_players]):
                if votes[i] == 'j':
                    vote_icons.append(ttk.Label(board, image=ja_icon_img, padding='-2 -2 -2 -2'))
                    vote_icons[i].place(x=vote_icon_pos[j][0], y=vote_icon_pos[j][1])
                    ja += 1
                else:
                    vote_icons.append(ttk.Label(board, image=nein_icon_img, padding='-2 -2 -2 -2'))
                    vote_icons[i].place(x=vote_icon_pos[j][0], y=vote_icon_pos[j][1])
                    nein += 1

        if ja > nein:
            notification['text'] = 'Government elected!'
            sheev.place(x=label_pos[chancellor][0], y=label_pos[chancellor][1])
            if players_remaining < 6:
                ineligible_chancellor = [chancellor]
            else:
                ineligible_chancellor = [chancellor, president]

            if fascist_pol > 2 and not_hitler[chancellor] != 1:
                if ID == chancellor:
                    hitler_query('Are you Hitler?')
                    while True:
                        try:
                            is_hitler = hitler_val
                            del hitler_val
                            break
                        except NameError:
                            root.update()
                            sleep(0.02)
                    if is_hitler == 'n':
                        not_hitler[chancellor] = 1
                        crypt_send(b'n')
                    else:
                        notification['text'] = 'Well done, mein Führer. Fascists win!'
                        crypt_send(b'j')
                        break

                elif ID != chancellor:
                    notification['text'] += '\nIs {} Hitler?'.format(player_names[chancellor])
                    game_over = crypt_recv()
                    if game_over == 'j':
                        notification['text'] = '{} is Hitler! Fascists win!'.format(player_names[chancellor])
                        break
                    else:
                        notification['text'] = '{} is not Hitler!'.format(player_names[chancellor])
                        not_hitler[chancellor] = 1

            #### PRESIDENT DISCARDS POLICY ####
            if ID == president:
                policies = crypt_recv()

                # Create policy menu
                policy_menu = ttk.Label(board, style='TFrame')
                policy_menu.place(x=(board_x - (3*pol_x+60))//2, y=pol_menu_y)
                policy_title = ttk.Label(policy_menu, text='DISCARD one', style='TLabel')
                policy_title.grid(row=0, column=0, pady=(5, 0), columnspan=3)

                policy_list = []
                for i in range(3):
                    if policies[i] == 'L':
                        policy_list.append(
                            Button(policy_menu, image=lib_pol3_img, borderwidth=0, highlightthickness=0, command=lambda: pol_selection('L')))
                    else:
                        policy_list.append(
                            Button(policy_menu, image=fas_pol3_img, borderwidth=0, highlightthickness=0, command=lambda: pol_selection('F')))
                policy_list[0].grid(column=0, row=1, padx=(10, 5), pady=10)
                policy_list[1].grid(column=1, row=1, padx=(5, 5), pady=10)
                policy_list[2].grid(column=2, row=1, padx=(5, 10), pady=10)

                while True:
                    try:
                        del discard
                        break
                    except NameError:
                        root.update()
                        sleep(0.02)

                notification['text'] = 'Waiting for policy'

                if fascist_pol == 5:
                    veto = crypt_recv()
                    if veto == 'j':
                        notification.destroy()
                        return_query('Chancellor wishes to veto this agenda.\nDo you agree to the veto?')
                        while True:
                            try:
                                agree_veto = return_query_val
                                del return_query_val
                                break
                            except NameError:
                                root.update()
                                sleep(0.02)
                        if agree_veto == 'j':
                            notification = ttk.Label(board, text='', padding='5 5 5 5', style='TLabel')
                            notification.place(x=notif_x, y=0)  # shall I put this here or at the top
                            continue
                        else:
                            notification = ttk.Label(board, text='Veto overruled!\nWaiting for policy', padding='5 5 5 5', style='TLabel')
                            notification.place(x=notif_x, y=0)
                            policy = crypt_recv()
                    else:
                        policy = veto
                else:
                    policy = crypt_recv()

            #### CHANCELLOR DISCARDS POLICY ####
            elif ID == chancellor:
                notification['text'] += '\nWaiting for president'
                policies = crypt_recv()
                notification.destroy()

                # Create policy menu
                policy_menu = ttk.Label(board, style='TFrame')
                policy_menu.place(x=(board_x - (2*pol_x + 40))//2, y=pol_menu_y)
                policy_title = ttk.Label(policy_menu, text='DISCARD one', style='TLabel')
                policy_title.grid(row=0, column=0, pady=(5, 0), columnspan=2)

                policy_list = []
                for i in range(2):
                    if policies[i] == 'L':
                        policy_list.append(
                            Button(policy_menu, image=lib_pol3_img, borderwidth=0, highlightthickness=0, command=lambda: pol_selection('L')))
                    else:
                        policy_list.append(
                            Button(policy_menu, image=fas_pol3_img, borderwidth=0, highlightthickness=0, command=lambda: pol_selection('F')))
                policy_list[0].grid(column=0, row=1, padx=(10, 5), pady=10)
                policy_list[1].grid(column=1, row=1, padx=(5, 10), pady=10)

                ## VETO ##
                if fascist_pol == 5:
                    policy_veto_title = ttk.Label(policy_menu, text='Do you wish to veto this agenda?', style='TLabel')
                    policy_veto_title.grid(row=2, column=0, pady=(5, 0), columnspan=2)
                    veto_ja = Button(policy_menu, image=ja_img, borderwidth=0, highlightthickness=0,
                                     command=lambda: (return_send(b'j'), policy_menu.destroy()))
                    veto_ja.grid(column=0, row=3, padx=5, pady=5, columnspan=2)
                    while True:
                        try:
                            veto = return_query_val
                            del return_query_val
                            break
                        except NameError:
                            try:
                                veto = discard  # No [del discard] because needed later
                                break
                            except NameError:
                                root.update()
                                sleep(0.02)
                    if veto == 'j':
                        notification = ttk.Label(board, text='Waiting for {} to respond'.format(player_names[president]), padding='5 5 5 5',
                                                 style='TLabel')
                        notification.place(x=notif_x, y=0)
                        agree_veto = crypt_recv()
                        if agree_veto == 'j':
                            notification['text'] = '{} agreed to the veto!\n'.format(player_names[president])
                            continue
                        else:
                            # Create second policy menu
                            notification.destroy()
                            policy_menu = ttk.Label(board, style='TFrame')
                            policy_menu.place(x=(board_x - (2*pol_x + 40))//2, y=pol_menu_y)
                            policy_title = ttk.Label(
                                policy_menu, text='{} is disinclined to acquiesce to your request\nDISCARD one'.format(player_names[president]),
                                style='TLabel')
                            policy_title.grid(row=0, column=0, columnspan=2)

                            policy_list = []
                            for i in range(2):
                                if policies[i] == 'L':
                                    policy_list.append(
                                        Button(policy_menu, image=lib_pol3_img, borderwidth=0, highlightthickness=0,
                                               command=lambda: pol_selection('L')))
                                else:
                                    policy_list.append(
                                        Button(policy_menu, image=fas_pol3_img, borderwidth=0, highlightthickness=0,
                                               command=lambda: pol_selection('F')))
                            policy_list[0].grid(column=0, row=1, padx=(10, 5), pady=10)
                            policy_list[1].grid(column=1, row=1, padx=(5, 10), pady=10)

                # above if statement won't run if chancellor selects policy
                while True:  # waits for policy if president rejects veto, discards policy if veto was never requested
                    try:
                        policy = policies.replace(discard, '', 1)
                        del discard
                        break
                    except NameError:
                        root.update()
                        sleep(0.02)
                notification = ttk.Label(board, text='', padding='5 5 5 5', style='TLabel')

            #### EVERYONE ELSE WAITS FOR POLICY ####
            else:
                notification['text'] += '\nWaiting for policy'
                if fascist_pol == 5:
                    veto = crypt_recv()
                    if veto == 'j':
                        notification['text'] = 'Chancellor wishes to veto this agenda'
                        agree_veto = crypt_recv()
                        if agree_veto == 'j':
                            notification['text'] = '{} agreed to the veto!\n'.format(player_names[president])
                            continue
                        else:
                            notification['text'] = '{} overruled the veto!\nWaiting for policy'.format(player_names[president])
                            policy = crypt_recv()
                    else:
                        policy = veto
                else:
                    policy = crypt_recv()
                notification.destroy()
                notification = ttk.Label(board, text='', padding='5 5 5 5', style='TLabel')

            #### PLACE POLICY ON BOARD ####
            if policy == 'F':
                fascist_pol += 1
                if fascist_pol < 4:
                    fascist_policies.append(ttk.Label(board, image=fas_pol1_img, padding='-2 -2 -2 -2'))
                    fascist_policies[fascist_pol-1].place(x=fascist_pos[fascist_pol-1], y=fas_y)
                elif fascist_pol < 6:
                    fascist_policies.append(ttk.Label(board, image=fas_pol2_img, padding='-2 -2 -2 -2'))
                    fascist_policies[fascist_pol-1].place(x=fascist_pos[fascist_pol-1], y=fas_y)
                else:
                    fascist_policies.append(ttk.Label(board, image=fas_pol2_img, padding='-2 -2 -2 -2'))
                    fascist_policies[fascist_pol-1].place(x=fascist_pos[5], y=fas_y)
                    notification['text'] = 'Fascists win!'
                    break

                #### PRESIDENTIAL POWERS ####
                if ID == president:
                    notification['text'] = ''
                    ## investigate loyalty ##
                    if (player_count > 8 and fascist_pol == 1) or (player_count > 6 and fascist_pol == 2):
                        notification['text'] = 'Which player would you like to investigate?'
                        for i in [x for x in range(player_count) if x not in ineligible_chancellor+killed_players+[ID]]:
                            players[i].state(['!disabled'])
                        while True:
                            try:
                                investigate = player_selection
                                for i in [x for x in range(player_count) if x not in ineligible_chancellor+killed_players+[ID]]:
                                    players[i].state(['disabled'])
                                del player_selection
                                break
                            except NameError:
                                root.update()
                                sleep(0.02)
                        notification.destroy()
                        membership = crypt_recv()
                        revealed_membership_menu = ttk.Label(board, style='TFrame')
                        revealed_membership_menu.place(x=(board_x-env_x)//2, y=mem_menu_y)
                        revealed_membership_title = ttk.Label(revealed_membership_menu, text=str(investigate)+' is a '+membership+'!', style='TLabel')
                        revealed_membership_title.grid(row=0, column=0)
                        if membership == 'Fascist':
                            party = ttk.Label(revealed_membership_menu, image=fas_party_img)
                        else:
                            party = ttk.Label(revealed_membership_menu, image=lib_party_img)
                        party.grid(column=0, row=1, columnspan=2, padx=5, pady=5)
                        cross = Button(revealed_membership_menu, image=cross_img, borderwidth=0, highlightthickness=0,
                                       command=lambda: revealed_membership_menu.destroy())
                        cross.grid(column=1, row=0, sticky='NE')
                        notification = ttk.Label(board, text='', padding='5 5 5 5', style='TLabel')

                    elif fascist_pol == 3:
                        ## policy peek ##
                        if player_count < 7:
                            top_three = crypt_recv()

                            peek_menu = ttk.Label(board, style='TFrame')
                            peek_menu.place(x=(board_x-(3*pol_x+60))//2, y=peek_menu_y)
                            peek_title = ttk.Label(peek_menu, text='Policy peek', style='TLabel')
                            peek_title.grid(row=0, column=1, pady=5)

                            policy_peek = []
                            for i in range(3):
                                if top_three[i] == 'L':
                                    policy_peek.append(Label(peek_menu, image=lib_pol3_img, borderwidth=0, highlightthickness=0))
                                else:
                                    policy_peek.append(Label(peek_menu, image=fas_pol3_img, borderwidth=0, highlightthickness=0))
                            policy_peek[0].grid(column=0, row=1, padx=(10, 5), pady=10)
                            policy_peek[1].grid(column=1, row=1, padx=(5, 5), pady=10)
                            policy_peek[2].grid(column=2, row=1, padx=(5, 10), pady=10)
                            cross = Button(peek_menu, image=cross_img, borderwidth=0, highlightthickness=0, command=lambda: (peek_menu.destroy()))
                            cross.grid(column=2, row=0, sticky='NE')

                        ## special election ##
                        else:
                            special_election = True
                            notification['text'] = 'Choose the next presidential candidate'
                            for i in [x for x in range(player_count) if x not in killed_players+[ID]]:
                                players[i].state(['!disabled'])
                            while True:
                                try:
                                    temp_pres = player_selection
                                    for i in [x for x in range(player_count) if x not in killed_players + [ID]]:
                                        players[i].state(['disabled'])
                                    del player_selection
                                    break
                                except NameError:
                                    root.update()
                                    sleep(0.02)
                            notification['text'] = ''

                    ## execution ##
                    elif 3 < fascist_pol < 6:
                        notification['text'] = 'I formally execute:'
                        for i in [x for x in range(player_count) if x not in killed_players + [ID]]:
                            players[i].state(['!disabled'])
                        while True:
                            try:
                                kill = player_selection
                                for i in [x for x in range(player_count) if x not in killed_players + [ID]]:
                                    players[i].state(['disabled'])
                                del player_selection
                                break
                            except NameError:
                                root.update()
                                sleep(0.02)
                        if kill == chancellor:
                            del ineligible_chancellor[0]
                        if not_hitler[kill] != 1:
                            notification['text'] = 'Is {} Hitler?'.format(player_names[kill])
                            game_over = crypt_recv()
                            if game_over == 'j':
                                notification['text'] = '{} is Hitler! Liberals win!'.format(player_names[kill])
                                break
                            else:
                                notification['text'] = '{} is not Hitler!\n'.format(player_names[kill])
                                not_hitler[kill] = 1
                        else:
                            notification['text'] = ''

                        killed_players.append(kill)
                        players_remaining -= 1

                # Everyone else receives president's actions
                elif (player_count > 8 and fascist_pol == 1) or (player_count > 6 and fascist_pol == 2):
                    notification['text'] = 'Waiting for {} to investigate loyalty'.format(player_names[president])
                    notification.place(x=notif_x, y=0)
                    investigate = int(crypt_recv())
                    if ID == investigate:
                        notification['text'] = '{} has investigated your loyalty\n'.format(player_names[president])
                    else:
                        notification['text'] = '{} has investigated {}\'s loyalty\n'.format(player_names[president], player_names[investigate])

                elif fascist_pol == 3 and player_count > 6:
                    special_election = True
                    notification['text'] = 'Waiting for {} to choose the next presidential candidate'.format(player_names[president])
                    notification.place(x=notif_x, y=0)
                    temp_pres = int(crypt_recv())
                    if ID == temp_pres:
                        notification['text'] = '{} has chosen you to be the next presidential candidate.\n'.format(player_names[president])
                    else:
                        notification['text'] = '{} has chosen {} to be the next presidential candidate.\n'.format(player_names[president],
                                                                                                                  player_names[temp_pres])

                elif 3 < fascist_pol < 6:
                    notification['text'] = '{} formally executes:'.format(player_names[president])
                    notification.place(x=notif_x, y=0)
                    kill = int(crypt_recv())
                    if kill == chancellor:
                        del ineligible_chancellor[0]
                    if ID == kill:
                        notification['text'] = '{} formally executes: you'.format(player_names[president])
                        if not_hitler[ID] != 1:
                            hitler_query('Are you Hitler?')
                            while True:
                                try:
                                    is_hitler = hitler_val
                                    del hitler_val
                                    break
                                except NameError:
                                    root.update()
                                    sleep(0.02)
                            if is_hitler == 'n':
                                notification['text'] = ''
                                not_hitler[ID] = 1
                                crypt_send(b'n')
                            else:
                                notification['text'] = 'Liberals win!'
                                crypt_send(b'j')
                                break
                        else:
                            notification['text'] += '\n'

                    elif not_hitler[kill] != 1:
                        notification['text'] = '{} formally executes: {}\nIs {} Hitler?'.format(player_names[president], player_names[kill],
                                                                                                player_names[kill])
                        game_over = crypt_recv()
                        if game_over == 'j':
                            notification['text'] = '{} is Hitler! Liberals win!'.format(player_names[kill])
                            break
                        else:
                            not_hitler[kill] = 1
                            notification['text'] = '{} is not Hitler!\n'.format(player_names[kill])
                    else:
                        notification['text'] = '{} formally executes: {}\n'.format(player_names[president], player_names[kill])

                    killed_players.append(kill)
                    players_remaining -= 1

            elif policy == 'L':
                liberal_pol += 1
                if liberal_pol < 5:
                    liberal_policies.append(ttk.Label(board, image=lib_pol1_img, padding='-2 -2 -2 -2'))
                    liberal_policies[liberal_pol-1].place(x=liberal_pos[liberal_pol-1], y=lib_y)
                    notification['text'] = ''
                    notification.place(x=notif_x, y=0)  # president's notif already placed, everyone else's isn't
                else:
                    liberal_policies.append(ttk.Label(board, image=lib_pol2_img, padding='-2 -2 -2 -2'))
                    liberal_policies[4].place(x=liberal_pos[4], y=lib_y)
                    notification = ttk.Label(board, text='Liberals win!', padding='5 5 5 5', style='TLabel')
                    notification.place(x=notif_x, y=0)  # president's notif already placed, everyone else's isn't
                    break

            election_tracker_count = 0
            election_tracker.place(x=election_tracker_pos[0], y=election_tracker_y)

        else:
            if agree_veto == 'j':
                agree_veto = None
            else:
                notification['text'] = 'Government rejected!\n'
            election_tracker_count += 1
            election_tracker.place(x=election_tracker_pos[election_tracker_count], y=election_tracker_y)
            if election_tracker_count == 3:
                policy = crypt_recv()
                if policy == 'F':
                    fascist_pol += 1
                    if fascist_pol < 4:
                        fascist_policies.append(ttk.Label(board, image=fas_pol1_img, padding='-2 -2 -2 -2'))
                        fascist_policies[fascist_pol-1].place(x=fascist_pos[fascist_pol-1], y=fas_y)
                    elif fascist_pol < 6:
                        fascist_policies.append(ttk.Label(board, image=fas_pol2_img, padding='-2 -2 -2 -2'))
                        fascist_policies[fascist_pol-1].place(x=fascist_pos[fascist_pol-1], y=fas_y)
                    else:
                        fascist_policies.append(ttk.Label(board, image=fas_pol2_img, padding='-2 -2 -2 -2'))
                        fascist_policies[fascist_pol-1].place(x=fascist_pos[5], y=fas_y)
                        notification['text'] += 'Fascists win!'
                        break
                elif policy == 'L':
                    liberal_pol += 1
                    if liberal_pol < 5:
                        liberal_policies.append(ttk.Label(board, image=lib_pol1_img, padding='-2 -2 -2 -2'))
                        liberal_policies[liberal_pol-1].place(x=liberal_pos[liberal_pol-1], y=lib_y)
                    else:
                        liberal_policies.append(ttk.Label(board, image=lib_pol2_img, padding='-2 -2 -2 -2'))
                        liberal_policies[4].place(x=liberal_pos[4], y=lib_y)
                        notification['text'] += 'Liberals win!'
                        break

                election_tracker_count = 0
                election_tracker.place(x=election_tracker_pos[0], y=election_tracker_y)
                ineligible_chancellor = []

        if not special_election:
            pres_x += 1
            while pres_x % player_count in killed_players:
                pres_x += 1
            president = pres_x
        else:
            president = int(temp_pres)
            special_election = False

        president = president % player_count
        pres.place(x=label_pos[president][0], y=label_pos[president][1])

    root.mainloop()
