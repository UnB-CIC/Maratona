
leds = 0

number = str(input())
num_leds = {'0': 6, '1': 2, '2': 5, '3': 5, '4': 4, '5': 5, '6': 6, '7': 3,
            '8': 7, '9': 6}
leds = sum([num_leds[c] for c in number])
print('{} LEDs'.format(leds))
