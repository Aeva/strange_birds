
import time
import subprocess
from random import shuffle, randint
from alsa_midi import SequencerClient, WRITE_PORT, READ_PORT, NoteOnEvent, NoteOffEvent, ProgramChangeEvent
from ascii import *


if False:
    import alsa_midi
    for event in dir(alsa_midi):
        if event.endswith("Event"):
            print(event)
    exit()


client = SequencerClient("strange birds")
port = client.create_port(
    "output",
    caps=READ_PORT)


timidity_proc = None
connection = None
device_priority = ["Arturia MicroFreak", "TiMidity"]

for target in device_priority:
    for device in client.list_ports(output=True):
        if device.client_name == target:
            connection = device.client_name
            port.connect_to(device)
            break

if connection != None:
    print(f"Connected to {connection}")

else:
    import subprocess
    try:
        timidity_proc = subprocess.Popen(["timidity", "-iA", "-Os", "--volume=200"])
        time.sleep(1)
    except OSError:
        print("Unable to start timidity :(")
        timidity_proc = None

    target = "TiMidity"
    for device in client.list_ports(output=True):
        if device.client_name == target:
            connection = device.client_name
            port.connect_to(device)

send_note_off = False
note_offset = 0
if connection == "TiMidity":
    # programs 21, 53, 91, 93, 94, 95, and 97 all work pretty well here
    event = ProgramChangeEvent(channel=0, value=95)
    client.event_output(event, port=port)
    note_offset = -12
    send_note_off = True

time.sleep(1)
if not connection:
    print(f"Unable to connect midi output :(")


voices = 4
primes = [19, 41, 83, 167]
status = [p - primes[0] for p in primes]
active = [-1, -1, -1, -1]

root = 60 - 24

deck = [root + 5, root + 9, root + 8, root + 12, root + 11, root + 16, root + 15, root + 17]
shuffle(deck)
deck.insert(0, root)
for i in range(len(deck)):
    deck[i] += note_offset

discard = []

def colorize(notes, pallet):
    return [f"{fg(color)}{note}" for note, color in zip(notes, pallet)]

def colorize_l(notes, pallet):
    pallet = ([pallet[0]] * max(len(notes) - len(pallet), 0)) + pallet
    return colorize(notes, pallet[-len(notes):])

def colorize_r(notes, pallet):
    return colorize(notes, pallet + ([pallet[-1]] * max(len(notes) - len(pallet), 0)))

def underline_new(notes, cursor):
    hand = []
    for i, note in enumerate(notes):
        if note > -1:
            if i == cursor:
                hand.append(f"{UNDER}{BOLD}{fg(15)}{note}{RESET}")
            else:
                hand.append(f"{BOLD}{fg(231)}{note}{RESET}")
    return hand

def spread(pile):
    if pile:
        return f" {'·'.join(map(str, pile))} "
    else:
        return " "

try:
    elapsed_time = 0
    while True:
        pending = []
        for voice in range(voices):
            status[voice] -= elapsed_time
            if status[voice] <= 0:
                status[voice] = primes[voice]
                pending.append(voice)
                if active[voice] > -1:
                    note = active[voice]
                    active[voice] = -1
                    discard.append(note)
                    if send_note_off:
                        event = NoteOffEvent(note=note, velocity=0)
                        client.event_output(event, port=port)

        for voice in pending:
            draw = deck.pop(0)
            active[voice] = draw

            discard_part = spread(colorize_l(discard, [238, 240, 242, 244]))
            #hand_part = spread([n for n in active if n > -1])
            hand_part = spread(underline_new(active, voice))
            deck_part = spread(colorize_r(deck, [118, 76, 34, 28, 22]))
            print(" " + f"{discard_part}{RESET}⌜{hand_part}⌟{deck_part}".strip() + RESET)
            #print(" " + f"{discard_part}{RESET}⌜{BOLD}{fg(15)}{hand_part}{RESET}⌟{deck_part}".strip() + RESET)

            event = NoteOnEvent(note=draw, velocity=randint(96, 127))
            client.event_output(event, port=port)

            if len(deck) == 0:
                print(f"{ITALIC}reshuffling{RESET}")
                deck = discard
                discard = []
                shuffle(deck)

        client.drain_output()

        elapsed_time = min(status)
        print(f"{fg(4)}{ITALIC}Zzz{RESET}{fg(4)} ({elapsed_time} seconds){RESET}")
        time.sleep(elapsed_time)


except KeyboardInterrupt:
    pass

if timidity_proc:
    timidity_proc.kill()
    time.sleep(1)

#while True:
#    client.event_output(
#    NoteOnEvent(note=60),
