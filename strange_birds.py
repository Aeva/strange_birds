
import time
from random import shuffle, randint
from alsa_midi import SequencerClient, WRITE_PORT, READ_PORT, NoteOnEvent, NoteOffEvent

client = SequencerClient("strange birds")
port = client.create_port(
    "output",
    caps=READ_PORT)

for device in client.list_ports(input=True):
    if device.client_name == "Arturia MicroFreak":
        port.connect_to(device)
        print("connected")
        break

root = 60 - 24

deck = [root + 5, root + 9, root + 8, root + 12, root + 11, root + 16, root + 15, root + 17]
shuffle(deck)
deck.insert(0, root)

discard = []

def spread(pile):
    if pile:
        return f" {'·'.join(map(str, pile))} "
    else:
        return " "

try:
    while True:
        if len(discard) > 4:
            event = NoteOffEvent(note=discard[0], velocity=0)
            client.event_output(event, port=port)
            client.drain_output()

        draw = deck.pop(0)
        print(" " + f"{spread(discard)}⌜{draw}⌟{spread(deck)}".strip())
        discard.append(draw)

        event = NoteOnEvent(note=draw, velocity=randint(96, 127))
        client.event_output(event, port=port)

        client.drain_output()
        if draw == root:
            time.sleep(10)
        else:
            time.sleep(randint(8,20))

        if len(deck) == 0:
            print("reshuffling")
            deck = discard[:-4]
            discard = discard[-4:]
            shuffle(deck)
            time.sleep(1)

        time.sleep(1)

except KeyboardInterrupt:
    pass



#while True:
#    client.event_output(
#    NoteOnEvent(note=60),
