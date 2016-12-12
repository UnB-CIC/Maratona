/* https://www.urionlinejudge.com.br/judge/en/problems/view/1168
 * gnramos@unb.br
 * Strings, */

#include <stdio.h>

using namespace std;

int main() {
   int N, c;
   unsigned long long leds;

   scanf("%d\n", &N);

   while(N--) {
      leds = 0;
      do {
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
            default: break;
         }
      } while(c != '\n');

      printf("%llu leds\n", leds);
  }
   return 0;
}