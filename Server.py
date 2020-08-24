import socket
import random
from cryptography.fernet import Fernet


def crypt_send(pl, data):
    if len(data) > 15:
        print('SENDING DATA LONGER THAN 15 BYTES')  # Data must be <15 bytes to be 100b long when encrypted
    token = f.encrypt(data)
    pl.sendall(token)


def crypt_recv(pl):
    token = pl.recv(100)
    return f.decrypt(token)


host = socket.gethostname()
port = 12345
player_count = int(input('Enter number of players: '))
while player_count not in (5, 6, 7, 8, 9, 10):
    player_count = int(input('Enter number of players (5-10): '))

key = Fernet.generate_key()
print('Key: ', key.decode())
f = Fernet(key)  # AES-256 in CBC mode

player = []

draw_pile = ['F', 'L', 'F', 'F', 'L', 'F', 'F', 'L', 'F', 'F', 'L', 'F', 'F', 'L', 'F', 'F', 'L']
discard_pile = []

roles = ['Liberal', 'Fascist', 'Liberal', 'Hitler', 'Liberal']
add_roles = ['Liberal', 'Fascist', 'Liberal', 'Fascist', 'Liberal']

if player_count != 5:
    for i in range(player_count-5):
        roles.append(add_roles[i])

random.shuffle(draw_pile)
random.shuffle(roles)
pres_x = random.randint(0, player_count-1)
president = pres_x

b_draw_pile = str(draw_pile)
str_pres = str(president)
str_player_count = str(player_count)
player_names = []
roles_taken = ''
fascists = ''
liberal_pol = 0
fascist_pol = 0
election_tracker_pos = 0
special_election = False
killed_players = ''
not_hitler = [0] * player_count
agree_veto = None

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

    sock.bind((host, port))
    sock.setblocking(False)

    sock.listen(0)
    count1 = 0
    count2 = 0
    count3 = 0
    while count3 != player_count:
        if count1 != player_count:
            try:
                client, addr = sock.accept()
                print(addr, 'has connected\n')
                player.append(client)
                crypt_send(player[count1], (str(count1)+str_pres+str_player_count).encode())
                player[count1].setblocking(False)
                count1 += 1
            except BlockingIOError:
                pass
        if count2 == count3:
            try:
                crypt_send(player[count2], roles_taken.encode())
                count2 += 1
            except IndexError:
                continue
        try:
            choice_name = crypt_recv(player[count3]).decode()
            choice = choice_name[0]
            player_names.append(choice_name[1:])
            roles_taken += choice
            print(roles_taken)
            role = roles[int(choice)]
            if role == 'Fascist':
                fascists += str(count3)
            elif role == 'Hitler':
                fascists = str(count3) + fascists
            crypt_send(player[count3], role.encode())
            player[count3].setblocking(True)
            count3 += 1
        except BlockingIOError:
            continue

# Fascists acknowledge each other
for fascist in fascists[1:]:
    crypt_send(player[int(fascist)], fascists.encode())
if player_count < 7:
    crypt_send(player[int(fascists[0])], fascists.encode())

for i in range(player_count):
    for j in range(player_count):
        crypt_send(player[i], player_names[j].encode())

while True:
    if agree_veto == b'j':
        ja, nein = 0, 0
        agree_veto = None
    else:
        print('President:', president)

        chancellor = int(crypt_recv(player[president]))
        print('President nominates:', chancellor)

        # Send choice to remaining players
        for i in [x for x in range(player_count) if x != president]:
            crypt_send(player[i], str(chancellor).encode())

        # Collect votes
        votes = ''
        for i in [x for x in range(player_count) if str(x) not in killed_players]:
            votes += crypt_recv(player[i]).decode()
            print(votes)

        # Send votes to all players
        for i in range(player_count):
            crypt_send(player[i], votes.encode())

        # Count the votes
        ja, nein = 0, 0
        for vote in votes:
            if vote == 'j':
                ja += 1
            else:
                nein += 1

    # If vote Ja
    if ja > nein:

        if fascist_pol > 2 and not_hitler[chancellor] != 1:
            is_hitler = crypt_recv(player[chancellor])
            print('Is chancellor Hitler? ', is_hitler)
            for i in [x for x in range(player_count) if x != chancellor]:
                crypt_send(player[i], is_hitler)
            if is_hitler == b'j':
                print('Fascists win!')
                break
            else:
                not_hitler[chancellor] = 1

        policies = ''
        for i in range(3):
            policies += draw_pile.pop(0)
        print(policies)

        if len(draw_pile) < 3:
            discard_pile += draw_pile
            random.shuffle(discard_pile)
            draw_pile = discard_pile
            discard_pile = []

        # Send president top three policies
        crypt_send(player[president], policies.encode())
        discard = crypt_recv(player[president]).decode()
        print('President discarded:', discard)
        policies = policies.replace(discard, '', 1)
        print('Chancellor policies:', policies)
        discard_pile.append(discard)

        # Send chancellor remaining two policies
        crypt_send(player[chancellor], policies.encode())
        if fascist_pol == 5:
            veto = crypt_recv(player[chancellor])
            print('Chancellor\'s veto?', veto)

            if veto == b'j':
                for i in [x for x in range(player_count) if x != chancellor]:
                    crypt_send(player[i], veto)

                agree_veto = crypt_recv(player[president])
                print('President agrees?', agree_veto)
                for i in [x for x in range(player_count) if x != president]:
                    crypt_send(player[i], agree_veto)
                if agree_veto == b'j':
                    discard_pile += [policies[0], policies[1]]
                    continue
                else:
                    discard = crypt_recv(player[chancellor]).decode()
            else:
                discard = veto.decode()
        else:
            discard = crypt_recv(player[chancellor]).decode()

        print('Chancellor discarded:', discard)
        print('chancellor policies', policies)
        policy = policies.replace(discard, '', 1)
        discard_pile.append(discard)

        # Send remaining players the policy
        for i in [x for x in range(player_count) if x != chancellor]:
            crypt_send(player[i], policy.encode())

        # Add policy to board
        if policy == 'F':
            fascist_pol += 1
            if fascist_pol == 6:
                print('Fascists win!')
                break

            # Executive powers
            if (player_count > 8 and fascist_pol == 1) or (player_count > 6 and fascist_pol == 2):
                investigate = crypt_recv(player[president]).decode()
                print('President investigates: ', investigate)
                if investigate in fascists:
                    crypt_send(player[president], b'Fascist')
                else:
                    crypt_send(player[president], b'Liberal')
                for i in [x for x in range(player_count) if x != president]:
                    crypt_send(player[i], investigate.encode())

            elif fascist_pol == 3:
                if player_count < 7:
                    crypt_send(player[president], (draw_pile[0]+draw_pile[1]+draw_pile[2]).encode())
                else:
                    # special election
                    special_election = True
                    temp_pres = crypt_recv(player[president])
                    print('President nominated: ', temp_pres)
                    for i in [x for x in range(player_count) if x != president]:
                        crypt_send(player[i], temp_pres)

            elif 3 < fascist_pol < 6:
                kill = crypt_recv(player[president]).decode()
                print('President formally executed: ', kill)
                killed_players += kill
                for i in [x for x in range(player_count) if x != president]:
                    crypt_send(player[i], kill.encode())

                if not_hitler[int(kill)] != 1:
                    is_hitler = crypt_recv(player[int(kill)])
                    print('Is', kill, 'Hitler? ', is_hitler)

                    for i in [x for x in range(player_count) if x != int(kill)]:
                        crypt_send(player[i], is_hitler)

                    if is_hitler == b'j':
                        print('Liberals win!')
                        break
                    else:
                        not_hitler[int(kill)] = 1
        else:
            liberal_pol += 1

        election_tracker_pos = 0

    # If vote Nein
    else:
        election_tracker_pos += 1
        print('Election tracker:', election_tracker_pos)

        if election_tracker_pos == 3:
            policy = draw_pile.pop(0)
            for p in player:
                crypt_send(p, policy.encode())
            if policy == 'F':
                fascist_pol += 1
                if fascist_pol == 6:
                    print('Fascists win!')
                    break
            else:
                liberal_pol += 1

            election_tracker_pos = 0

            if len(draw_pile) < 3:
                discard_pile += draw_pile
                random.shuffle(discard_pile)
                draw_pile = discard_pile
                discard_pile = []

    if liberal_pol == 5:
        print('Liberals win!')
        break

    if not special_election:
        pres_x += 1
        while str(pres_x % player_count) in killed_players:
            pres_x += 1
        president = pres_x
    else:
        president = int(temp_pres.decode())
        special_election = False

    president = president % player_count
    print(len(draw_pile))
    print(len(discard_pile))
