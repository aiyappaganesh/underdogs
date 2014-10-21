from music21 import *

s = stream.Stream()
n1 = note.Note()
n1.pitch = pitch.Pitch(name='E')
n1.duration.type = 'half'
n1.duration.quarterLength
s.append(n1)
s.show()