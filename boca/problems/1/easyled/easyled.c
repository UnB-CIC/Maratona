#include <stdio.h>

int main() {
   char c, lendo = 1;
   int leds = 0;

   while(lendo) {
      c = getchar();
      switch(c) {
         case '1': leds += 2; break;
         case '7': leds += 3; break;
         case '4': leds += 4; break;
         case '2':
         case '3':
         case '5': leds += 5; break;
         case '0':
         case '6':
         case '9': leds += 6; break;
         case '8': leds += 7; break;
         default: lendo = 0;
      }
   }

   printf("%d LEDs\n", leds);

   return 0;
}