
#include <stdio.h>
#include <io.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <stdlib.h>


// #define _CRT_SECURE_NO_WARNINGS
#pragma warning(disable : 4996)

// run arguments bob&bob
// bob1.key bob2.key bob_xor.key
// bob2.key bob_xor.key bob1_restore.key


// run arguments alice&bob
// alice1.key alice2.key alice_xor.key
// bob2.key alice_xor.key bob1_restore.key


void main(int argc, char **argv)
{
    // printf("in main\n");
    if (argc != 4)
    {
        printf("Error: wrong usage, \"main.exe in-key1-file in-key2-file out-key-xor-file\"\n");
        return;
    }


    char *buf1;
    char *buf2;
    char *buf3;

    FILE *fp = NULL;
    struct stat st;
    int file_size;
    int file_size2;

    // get file size
    if (stat(argv[1], &st) == -1)
    {
        printf("Error: failed to get file size\n");
        return;
    }   
    file_size = st.st_size;

    // open file
    fp = fopen(argv[1], "r");
    if( fp == NULL)
    {
        printf("Error: file not exist\n");
        return;
    }

    // read in key 1
    buf1 = (char *)malloc(file_size);
    fread(buf1, 1, file_size, fp);

    fclose(fp);



    // read in key 2

    // get file size
    if (stat(argv[2], &st) == -1)
    {
        printf("Error: failed to get file size2\n");
        return;
    }

    file_size2 = st.st_size;
    
    if (file_size != file_size2)
    {
        printf("Error: files should be the same size (key1 and key2)\n");
        return;
    }

    buf2 = (char *)malloc(file_size2);

    
    // open file
    fp = fopen(argv[2], "r");
    if( fp == NULL)
    {
        printf("Error: file not exist\n");
        return;
    }

    fread(buf2, 1, file_size2, fp);

    fclose(fp);



    buf3 = (char *)malloc(file_size);

    for (int i = 0; i < file_size; i++)
    {
        buf3[i] = ( ( buf1[i] == '1' && buf2[i] == '1' ) || ( buf1[i] == '0' && buf2[i] == '0' ) ) ? '0' : '1';
    }


    fp = fopen(argv[3], "w");
    if ( fp == NULL )
    {
        printf("Error: failed open file for write\n");
        return;
    }

    fwrite(buf3, 1, file_size, fp);

    fclose(fp);

}