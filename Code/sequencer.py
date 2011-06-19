from pygame import midi
import util, time

class Sequencer:

  def __init__(self):
    midi.init()



  def play(self, notes):
    notes.printinfo()
    # Choose an output device
    devices = []
    for i in range(midi.get_count()):
      info = midi.get_device_info(i)
      devices.append("{0}, {1}, Input:{2}, Output:{3}".format(info[0], info[1], info[2], info[3]))

    device = util.menu("Choose an output device", devices)
    out = midi.Output(device)

    # Translate notes into midi events
    print "Preprocessing"
    events = notes.toEvents()

    print "Playing"
    lastTime = 0
    on = 0
    off = 0
    for e in events:
      # Calculate relative time and convert to seconds
      ticks = e[0] - lastTime
      # This is not right yet
      seconds = notes.ticks_to_seconds(ticks)
      if e[3] is 'on':
        #out.update_time(e[0]-lastTime)
        time.sleep(seconds)
        lastTime = e[0]
        out.note_on(e[1], e[2], 0)
      elif e[3] is 'off':
        #out.update_time(e[0]-lastTime)
        time.sleep(seconds)
        lastTime = e[0]
        # Sometimes note_offs are lost? 
        # Unbelievably sending twice reduces this.
        out.note_off(e[1], e[2], 0)
        out.note_off(e[1], e[2], 0)
    #out.close()
    

if __name__ == '__main__':
  import representation as mr
  notes = mr.NoteList('../MidiFiles/0848-01.mid')
  seq = Sequencer()
  seq.play(notes)
#out.write([[[0x9, 50, 80], 0],[[0x9, 53, 80], 500],[[0x8, 53, 0], 1500],[[0x, 50, 0], 2000]])
