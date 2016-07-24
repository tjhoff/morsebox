from morseconverter import convert_text, convert_morse, convert_morse_char
import heapq
import sys
import random

def zero():
    return 0

class MorseStream:
    def __init__(self):
        self.dots_per_second = None # 4.0
        self.tolerance = None
        self.morse_log = ""
        self.words = []
        self.pulses = []
        self.current_word = ""
        self.current_char = ""
        self.last_pulse_analyzed = 0
        self.min_pulses_to_analyze = 50

    def determine_wpm(self):
        # determine minimum consistent pulse time within deviation
        last_set = self.pulses[:-self.min_pulses_to_analyze]

        if len(last_set) == 0:
            return

        def smallest_true_pulse(pulse):
            if pulse[0]:
                return pulse[1]
            else:
                return pulse[1] + 1000

        min_pulse = 0
        def find_dashes(pulse):
            if not pulse[0]:
                return False
            length = pulse[1]
            if length > min_pulse * 2 and length < min_pulse * 4:
                return True
            return False

        def find_dots(pulse):
            if not pulse[0]:
                return False
            length = pulse[1]
            if length < min_pulse * 2:
                return True
            return False

        # Get minimum pulse
        min_pulse = min(last_set, key=smallest_true_pulse)[1]
        # Find dashes that are 2-4x the minimum
        dashes = map(lambda x: x[1], filter(find_dashes, last_set))
        # Find dots that are <2x the minimum
        dots = map(lambda x: x[1], filter(find_dots, last_set))

        if not len(dots):
            return
        avg = sum(dots) / len(dots)

        new_dots_per_second = 1/avg

        wpm_ratio = .01

        if self.dots_per_second:
            self.dots_per_second = (1-wpm_ratio) * self.dots_per_second + wpm_ratio * new_dots_per_second
        else:
            self.dots_per_second = new_dots_per_second
            self.tolerance = .5/self.dots_per_second
            self.analyze_previous_pulses()

        self.tolerance = .5/self.dots_per_second

    def generate_pulses(self, text, dps = 4.0, variance_fn = zero):
        morse = convert_text(text)

        pulses = []

        on_last = False
        for char in morse:
            if char == " ":
                pulses.append((False, (3/dps) + variance_fn()))
                on_last = False
            elif char == "|":
                pulses.append((False, (7/dps) + variance_fn()))
                on_last = False
            elif char == "-":
                if on_last:
                    pulses.append((False, (1/dps) + variance_fn()))
                pulses.append((True, (3/dps) + variance_fn()))
                on_last = True
            elif char == ".":
                if on_last:
                    pulses.append((False, (1/dps) + variance_fn()))
                pulses.append((True, (1/dps) + variance_fn()))
                on_last = True

        pulses.append((False, (7/dps) + variance_fn()))

        return pulses

    def add_pulse(self, state, length):
        self.pulses.append((state, length))

        if self.dots_per_second:

            self.determine_wpm()
            self.analyze_pulse(state, length)
            self.last_pulse_analyzed += 1
        else:
            self.determine_wpm()

    def analyze_previous_pulses(self):
        pulses_analyzed = 0
        for i in range(self.last_pulse_analyzed, len(self.pulses)):
            self.analyze_pulse(self.pulses[i][0], self.pulses[i][1])

    def add_character(self):
        character = self.current_char
        self.current_char = ""
        c = convert_morse_char(character)
        print "Character - {0}={1}".format(character, c)

        if c:
            self.current_word += c

    def analyze_pulse(self, state, length):
        if state == False:
            # deal with tolerance
            if length > 7/self.dots_per_second - self.tolerance * 3:
                # done with current word
                if self.current_char:
                    self.add_character()
                self.words.append(self.current_word)
                self.current_word = ""
                self.morse_log += "|"

            elif length > 3/self.dots_per_second - self.tolerance:
                # done with current character
                self.morse_log += " "
                self.add_character()

            else:
                pass

        else:
            # deal with tolerance
            if length > 3/self.dots_per_second - self.tolerance:
                self.morse_log += "-"
                self.current_char += "-"
            else:
                self.morse_log += "."
                self.current_char += "."

    def get_word(self):
        if len(self.words) == 0:
            return None
        return self.words.pop(0)

if __name__ == "__main__":
    ms = MorseStream()
    def randomizer():
        return (random.random() - .5) * .25

    #pulses = ms.generate_pulses(" if we're going to use that function several times, or if the function is too complex for writing in a single line. However, if we need it only once and it's quite simple (i.e. it contains just one expression, like in the above e", 4.0, randomizer)
    pulses = [(False, 2.1886961460113525), (True, 0.1213231086730957),
     (False, 0.2824079990386963), (True, 0.09081697463989258),
      (False, 0.4741170406341553), (True, 0.14126086235046387),
       (False, 0.8875250816345215), (True, 0.4739968776702881),
        (False, 0.3227880001068115), (True, 0.47413206100463867),
         (False, 0.19171404838562012), (True, 0.5850391387939453),
         (False, 0.6858839988708496), (True, 0.11113500595092773),
         (False, 0.2017810344696045), (True, 0.12132501602172852),
         (False, 0.22200798988342285), (True, 0.12114095687866211),
         (False, 0.595099925994873), (True, 0.44387292861938477),
         (False, 0.24214696884155273), (True, 0.4740409851074219),
         (False, 0.18165302276611328), (True, 0.5951359272003174),
         (False, 0.6454710960388184), (True, 0.15140986442565918),
         (False, 0.12114214897155762), (True, 0.1412961483001709),
         (False, 0.15137410163879395), (True, 0.141279935836792), (False, 0.4136040210723877), (True, 0.4741098880767822), (False, 0.20178914070129395), (True, 0.5345871448516846), (False, 0.18164491653442383), (True, 0.5547101497650146), (False, 0.6758170127868652), (True, 0.1312100887298584), (False, 0.14128804206848145), (True, 0.14128422737121582), (False, 0.16143298149108887), (True, 0.15142011642456055),
          (False, 0.5548059940338135), (True, 0.4741239547729492), (False, 0.20185208320617676), (True, 0.45404815673828125), (False, 0.20178794860839844), (True, 0.5850238800048828), (False, 0.4942440986633301), (True, 0.13120102882385254), (False, 0.14127707481384277), (True, 0.14133286476135254), (False, 0.1312389373779297), (True, 0.23207998275756836), (False, 0.34297990798950195), (True, 0.4639720916748047),
           (False, 0.2321028709411621), (True, 0.5245051383972168), (False, 0.18160390853881836), (True, 0.5043618679046631), (False, 2.1886961460113525)]


    for pulse in pulses:
        ms.add_pulse(pulse[0], pulse[1])

    print len(pulses)
    print len(ms.morse_log)
    print ms.morse_log
    print ms.dots_per_second
    print ms.words
