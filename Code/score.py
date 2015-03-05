import music21 as m21
import tools

class Score:

    def __init__(self, score):
        self.score = score
        # Assume each part has the same number of measures and every score has two parts
        parts = []

    def getNoteList():
        return tools.parseScore(self.score)

    def tieless(self):
        # This doesn't actually remove ties, but it does fix the duration of tied notes
        self.score.stripTies(inPlace=True)
        # Now remove every note that is not the start of a tie
        for part in self.score:
            if not isinstance(part, m21.stream.Part):
                continue
            for measure in part:
                if not isinstance(measure, m21.stream.Measure):
                    continue
                for voice in measure:
                    if not isinstance(voice, m21.stream.Voice):
                        continue
                    for note in voice:
                        if isinstance(note, m21.chord.Chord) or isinstance(note, m21.note.Note):
                            if hasattr(note,'tie') and note.tie is not None:
                                if not note.tie.type == 'start':
                                    voice.remove(note)
                                else:
                                    note.tie = None
        return self.score

    #Highest note in part one at any moment
    def melody(self):
        notes = []
        melody = m21.stream.Score()
        partFound = False
        for x in self.score:
            # Only add the first part to the melody
            if partFound:
                break
            if not isinstance(x,m21.stream.Part):
                melody.append(x)
            else:
                part = m21.stream.Part()
                melody.append(part)
                partFound = True
                for y in x:
                    if not isinstance(y, m21.stream.Measure):
                        part.append(y)
                    else:
                        measure = m21.stream.Measure()
                        measure.number = y.number
                        part.append(measure)
                        for z in y:
                            if not isinstance(z, m21.stream.Voice):
                                measure.append(z)
                            else:
                                if not int(z.id) == 1:
                                    continue
                                else:
                                    voice = m21.stream.Voice()
                                    voice.id = 1
                                    measure.append(voice)
                                    for note in z:
                                        if not isinstance(note,m21.chord.Chord):
                                            voice.append(note)
                                        else:
                                            pitches = list(note.sortDiatonicAscending().pitches)
                                            pitches.reverse()
                                            n = m21.note.Note()
                                            n.pitch = pitches[0]
                                            n.duration = note.duration
                                            n.id = note.id
                                            voice.append(n)
        return Score(melody).tieless()
