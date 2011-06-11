from midi import *
from midi.MidiOutFile import MidiOutFile
import copy, os, pygame

base_a4 = 440
names = ['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B']

class PianoRoll:

  def __init__(self, midifile=None):
    # Clean representation
    self.startnote = None
    self.length = 0

    # Dirty MIDI administration
    self.key_signature = None
    self.time_signature = None
    self.smtp_offset = None
    self.tempo = None
    self.division = None
    self.sequence_names = []

    # If a file is specified, parse it
    if midifile:
      notebag = MidiToPianoRoll(self)
      stream =  MidiInFile.MidiInFile(notebag, open(midifile))
      stream.read()
      print len(notebag.notes)
      self.built(notebag.notes)


  def __iter__(self):
    return self.generateItems()

  def __len__(self):
    return self.length

  def __contains__(self, note):
    currentnote = startnote
    while not currentnote is None:
      if currentnote is note: return True
      currentnote = currentnote.next
    return False

  def __getitem__(self, i):
    index = 0
    currentnote = self.startnote
    while not currentnote is None:
      if index == i: return currentnote
      currentnote = currentnote.next
      index += 1
    return None

  def generateItems(self):
    currentnote = self.startnote
    while not currentnote is None:
      yield currentnote
      currentnote = currentnote.next

  def insertEvent(self, events, event):
    # Events are primary ordered by time and secundary ordered by pitch
    # No notes yet? Add at beginning
    if len(events) == 0:
      events = [event]
      return events
    # Insert at the right index
    # Loop through events
    for i in range(len(events)):
      # If you find an event that happened at the SAME TIME
      if events[i][0] == event[0]:
        # And its pitch is LOWER
        if events[i][1] < event[1]:
          # Insert BEFORE
          events.insert(i, event)
          return events
      # If you find an event that happened AFTER the current note_on
      elif events[i][0] > event[0]:
        # Insert the note before this event
        events.insert(i, event)
        return events
    # Right place not found? Append
    return events + [event]

  def toEvents(self):
    events = []
    for n in self:
      events = self.insertEvent(events, (n.note_on(), n.note, n.velocity, 'on'))
      events = self.insertEvent(events, (n.note_off(), n.note, n.velocity, 'off'))
    return events


  def exportMidi(self, midifile):
    # Do some preprocessing on the notes, converting them to 
    # ordered note on and note off events:
    print "Preprocessing {0} notes".format(self.length)
    events = self.toEvents()

    print "Creating file"
    out = MidiOutFile(midifile)
    out.header(format=0, nTracks=1, division=self.division)
    out.start_of_track()
    out.sequence_name(', '.join(self.sequence_names))
    out.patch_change(3, 1)
    out.tempo(self.tempo)
    if (self.time_signature):
      out.time_signature(self.time_signature[0],\
          self.time_signature[1],\
          self.time_signature[2],\
          self.time_signature[3])
    if self.key_signature:
      out.key_signature(self.key_signature[0],\
                      self.key_signature[1],\
                      self.key_signature[2],\
                      self.key_signature[3])
    if self.smtp_offset:
      out.smtp_offset(self.smtp_offset[0],\
                      self.smtp_offset[1],\
                      self.smtp_offset[2],\
                      self.smtp_offset[3],\
                      self.smtp_offset[4])
    lastTime = 0
    for e in events:
      if e[3] is 'on':
        out.update_time(e[0]-lastTime)
        lastTime = e[0]
        #out.update_time(96)
        out.note_on(0, e[1], e[2])
      else:
        out.update_time(e[0]-lastTime)
        lastTime = e[0]
        #out.update_time(0)
        out.note_off(0, e[1], e[2])

    out.update_time(0)
    out.end_of_track()
    out.eof()
    out.write()

  # Built a linked list from a list of notes ordered by onset time and pitch
  def built(self, notes):
    currentNote = Note(notes[0][1] - notes[0][0], notes[0][2], notes[0][3])

    self.startnote = currentNote
    self.length = len(notes)

    previous = currentNote
    previousNoteOff = notes[0][1]

    notes.remove(notes[0])

    for (note_on, note_off, note, velocity) in notes:
      currentNote = Note(note_off - note_on, note, velocity)
      currentNote.offset = note_on - previousNoteOff
      currentNote.previous = previous
      previous.next = currentNote
      previous = currentNote
      previousNoteOff = note_off


  def __str__(self):
    string = ''
    for n in self:
      string += str(n) + "\n" 
    return string

  def move(self, note, shift):
    index = self.notes.index(note)
    if self.notes[index].note_on + shift < 0:
      shift = math.abs(self.notes[index].note_on + shift)
    for i in range(index, len(self.notes)):
      self.notes[i].note_on += shift
      self.notes[i].note_off += shift

  def insertAfter(note, beforenote):
    print "Not done yet!"
    
  def insertBefore(note, afternote):
    print "Not done yet!"

  def insertAt(note, time):
    print "Not done yet!"

  def putAfter(note, beforenote):
    print "Not done yet!"
  def putBefore(note, afternote):
    print "Not done yet!"

  def putAt(note, time):
    print "Not done yet!"

  def remove(self, note):
    for n in self:
      if n is note:
        # If first note:
        if not n.previous:
          n.next.previous = None
          self.startnote = n.next
        # if last note:
        elif not n.next:
          n.previous.next = None
        else:
          n.previous.next = n.next
          n.next.previous = n.previous
        break
      n = None
    self.length -= 1

  def setLength(self, note, newlength):
    index = self.notes.index(note)
    shift = self.notes[index].note_on + newlength - self.notes[index].note_off
    self.notes[index].note_off += shift
    for i in range(index+1, len(self.notes)):
      self.notes[i].note_on += shift
      self.notes[i].note_off += shift


  # Also implements one with start and end TIMES
  def cut(self, start, end):
    # This is pretty ugly, isn't it?
    start.previous = None
    end.next = None
    self.startnote = start
    length = 0
    for n in self:
      length += 1
    self.length = length

  def play(self):
    self.exportMidi('.temp.mid')
    os.system("audacious .temp.mid")
    pass


class Note:

  def __init__(self, length, note, velocity):
    self.offset = 0
    self.previous = None
    self.next = None
    self.velocity = velocity
    self.length = length
    self.note = note
  
  # Return absolute pitch
  def pitch(self):
    return base_a4*pow(2,(self.note-57)/12)

  def name(self):
    return '{0}{1}'.format(names[self.note % 12], self.note // 12)

  def setLength(self, length):
    self.length = length

  # Return note_on in absolute time
  def note_on(self):
    if self.previous is None:
      return self.offset
    else:
      return self.offset + self.previous.length + self.previous.note_on() 

  def note_off(self):
    return self.note_on() + self.length

  def __str__(self):
    return "Note: %02x, length: %s, offset: %s, velocity: %02X, absolute onset: %s" % (self.note, self.length, self.offset, self.velocity, self.note_on())


class MidiToPianoRoll(MidiOutStream.MidiOutStream):

  """
  This class listens to a select few midi events relevant for a simple midifile containing a pianomelody
  """


  def __init__(self, roll):
    self.roll = roll
    self.notes_on = []
    self.notes = []
    pass

  def insert(self, (note_on, note_off, pitch, velocity)):
    note = (note_on, note_off, pitch, velocity)
    # Notes are primary ordered by onset time and secundary ordered by pitch
    # No notes yet? Add at beginning
    if len(self.notes) == 0:
      self.notes = [note]
      return
    # Insert at the right index
    # Loop through notes
    for i in range(len(self.notes)):
      # If you find an note that happened at the SAME TIME
      if self.notes[i][0] == note_on:
        # And its pitch is LOWER
        if self.notes[i][1] < pitch:
          # Insert BEFORE
          self.notes.insert(i, note)
      # If you find an note that happened AFTER the current note_on
      elif self.notes[i][0] > note_on:
        # Insert the note before this note
        self.notes.insert(i, note)
        return
    # Right place not found? Append
    self.notes += [note]

  
  # Event Listeners
   
  def channel_message(self, message_type, channel, data):
    pass

  def note_on(self, channel=0, note=0x40, velocity=0x40):
    self.notes_on.append((self.abs_time(), note, velocity))

  def note_off(self, channel=0, note=0x40, velocity=0x40):
    for (note_on, n, velocity) in self.notes_on:
      # Should check if: note_off is later than note_on, note is even in notes_on
      # note appears only once in notes_on
      if note == n:
        self.insert((note_on, self.abs_time(), n, velocity))
        self.notes_on.remove((note_on, n, velocity))
        break

  def header(self, format=0, nTracks=1, division=96):
    self.roll.division = division

  def sequence_name(self, text):
    self.roll.sequence_names += [text]

  def tempo(self, value):
    self.roll.tempo = value

  def smtp_offset(self, hour, minute, second, frame, framePart):
    self.roll.smtp_offset = (hour, minute, second, frame, framePart)

  def time_signature(self, nn, dd, cc, bb):
    self.roll.time_signature = (nn, dd, cc, bb)

  def key_signature(self, sf, mi):
    self.roll.key_signature = (sf, mi)

  def sequencer_specific(self, data):pass
  def aftertouch(self, channel=0, note=0x40, velocity=0x40):pass
  def continuous_controller(self, channel, controller, value):pass
  def patch_change(self, channel, patch):pass
  def channel_pressure(self, channel, pressure):pass
  def pitch_bend(self, channel, value):pass
  def system_exclusive(self, data):pass
  def song_position_pointer(self, value):pass
  def song_select(self, songNumber):pass
  def tuning_request(self):pass
  def midi_time_code(self, msg_type, values):pass
  def eof(self):pass
  def start_of_track(self, n_track=0):pass
  def end_of_track(self):pass
  def sysex_event(self, data):pass
  def meta_event(self, meta_type, data):pass
  def sequence_number(self, value):pass
  def text(self, text):pass
  def copyright(self, text):pass
  def instrument_name(self, text):pass
  def lyric(self, text):pass
  def marker(self, text):pass
  def cuepoint(self, text):pass
  def midi_ch_prefix(self, channel):pass
  def midi_port(self, value):pass

if __name__ == '__main__':
  roll = PianoRoll('0848-01.mid')
  roll.play()
  import simple_rule
  simple_rule.higherIsFaster(roll, 30.0)
  roll.play()
  roll.exportMidi('exp_outp.mid')

