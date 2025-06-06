
#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <io.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <time.h>
#include "defs.h"

// akey - Alice's key
// bkey - Bob's key
// skey - shifted keys
// dkey - distillation keys

// 0 - Horizontal (h) (-)
// 1 - Vertical (v) (|)
// 1 - Diagonal () 45° (/)
// 0 - Diagonal () -45° (\)

config_st config;    // defining the variable config that holds the configuration settings
stats_st statistics; // statistics holds the execution statistics
int global_count = 0;
char *key_eve_changed = NULL;

int main(int argc, char **argv)
{
    // initializing parameters
    // double correct_bits_measured;
    // double correct_final_keys;
    clock_t start_time = clock();
    int not_valid = 1;
    int key_bit_errors = 0; // count key-bit errors by comparing Alice's key vs distillation key
    int offset = 0;
    int section_num = 1;
    int prev_section_num = 1;
    char *key = NULL;
    char *key_clib_err = NULL;
    char *key_section = NULL;
    char *bobs_key = NULL;
    char *measurement_bases = NULL;
    char *single_photons = NULL;
    char *single_photons_eve = NULL;
    char *measurement_results = NULL;
    char *sifted_keys = NULL;
    char *key_distillation = NULL;
    char *error_key = NULL;
    char *secret_keys = NULL;
    char *final_key = NULL;
    char *final_alice_key = NULL;
    int eve_attack_detected = 0;

    // read command line parameters
    read_config(argc, argv);

    // randomize
    srand((unsigned int)time(NULL));

    // print symbols
    printf("--------------------------------------------------------------------------------------------------------\n");
    printf("                                   Basis Symbols & Key Generation                                     \n");
    printf("--------------------------------------------------------------------------------------------------------\n");

    printf(" Basis Symbols: \n"
           "   + - Rectilinear Basis \n"
           "   x - Diagonal Basis \n\n"
           " Filter Symbols:\n"
           "   (bit = 1):\n"
           "   d - Diagonal 45 degrees (/) \n"
           "   v - Vertical (|) \n"
           "   (bit = 0):\n"
           "   h - Horizontal (-) \n"
           "   b - Diagonal -45 degrees (\\)\n\n"
           " Measurements Symbols:\n"
           "   v - Correct Measurement \n"
           "   x - Wrong Measurement \n");

    // final bob key
    final_key = (char *)malloc(sizeof(char) * (config.key_size + 1));
    if (final_key == NULL)
        return 1;

    // final alice key
    final_alice_key = (char *)malloc(sizeof(char) * (config.key_size + 1));
    if (final_alice_key == NULL)
        return 1;

    // initilize stats
    memset((void *)&statistics, 0, sizeof(statistics));

    key_eve_changed = (char *)malloc(sizeof(char) * (config.key_part_size + 1));
    if (key_eve_changed == NULL)
        return 1;
    memset(key_eve_changed, ' ', config.key_part_size);
    key_eve_changed[config.key_part_size] = '\0';

    while (count_bits(final_key) < config.key_size)
    {
        while (not_valid)
        {
            if (global_count < 3)
            {
                // generate section
                printf("\n========================================================================================================\n");
                if (prev_section_num != section_num)
                    printf("                                       Section #%d (%d bits):                                           \n", section_num, config.key_part_size);
                else
                    printf("                            Regenerating Section #%d (%d bits) Due to Errors                            \n", section_num, config.key_part_size);

                printf("========================================================================================================\n\n");
            }
            statistics.total_run_sections++;
            key = generate_key(); // alice generated key
            key_clib_err = generate_calib_key(key);
            // single_photons = create_polar_alice(key);
            single_photons = create_polar_alice(key_clib_err);
            // Eve generated polarization (based on Alice's polarization)
            single_photons_eve = introduce_eve_errors(single_photons, key_clib_err);
            measurement_bases = create_basis_bob();
            measurement_results = compare_polars(single_photons_eve, measurement_bases);
            bobs_key = create_bobs_key(single_photons_eve, measurement_bases);
            sifted_keys = create_sifted_keys(key, single_photons_eve, measurement_results, measurement_bases, bobs_key);
            // key_distillation = create_key_distillation(sifted_keys, key, &error_key, &key_bit_errors);
            key_distillation = create_key_distillation(sifted_keys, key, single_photons, single_photons_eve, &error_key, &key_bit_errors);
            secret_keys = create_secret_keys(sifted_keys, key_distillation);
            if (global_count < 3)
            {
                printf(" Alice's Key:            ");
                print_with_spaces(key, config.key_part_size);
                printf(" Key with Calib Errors:  ");
                print_with_spaces(key_clib_err, config.key_part_size);
                printf(" Single Photons:         ");
                print_with_spaces(single_photons, config.key_part_size);

                if (config.eavesdropping)
                {
                    printf(" Single Photons (Eve):   ");
                    print_with_spaces(single_photons_eve, config.key_part_size);
                    printf(" Eve key - bits changed: ");
                    print_with_spaces(key_eve_changed, config.key_part_size);
                    // memset(key_eve_changed, ' ', config.key_part_size);
                }
                printf(" Measurement Bases:      ");
                print_with_spaces(measurement_bases, config.key_part_size);
                printf(" Measurement Results:    ");
                print_with_spaces(measurement_results, config.key_part_size);
                printf(" Bob's Key:              ");
                print_with_spaces(bobs_key, config.key_part_size);
                printf(" Sifted Keys:            ");
                print_with_spaces(sifted_keys, config.key_part_size);
                printf(" Key Distillation:       ");
                print_with_spaces(key_distillation, config.key_part_size);
                printf(" Key Bits Error:         ");
                print_with_spaces(error_key, config.key_part_size);
                printf(" Secret Keys:            ");
                print_with_spaces(secret_keys, config.key_part_size);
                printf(" Final Secret Keys:      ");
                print_final_keys(secret_keys);
            }
            free(error_key);

            if (key_bit_errors <= config.allowed_wrong_bits)
            {
                not_valid = 0;
                // Copy key_section to final_key at the correct position
                int offset_old = offset;
                offset = copy_valid_keys(final_key, final_alice_key, secret_keys, key, offset, config.key_part_size);
                if (global_count < 3)
                {
                    printf(" Final Alice Key Part:   %s\n", final_alice_key + offset_old);
                    printf(" Final Bob Key Part:     %s\n", final_key + offset_old);
                }
                prev_section_num = section_num;
                section_num++;
                // update error-bits-count
                for (int k = 0; k < config.key_part_size; k++)
                    if (secret_keys[k] == '0' || secret_keys[k] == '1')
                        if (secret_keys[k] != key[k])
                        {
                            if (key_eve_changed[k] == '@')
                                statistics.final_eve_error_bits_count++;
                            else
                                statistics.final_calib_error_bits_count++;
                        }
                // 4 dbg
                if (global_count < 3)
                {
                    printf("\n Final Calibration Error Bits: %d\n", statistics.final_calib_error_bits_count);
                    printf(" Final Eve Error Bits:         %d\n", statistics.final_eve_error_bits_count);
                }
            }
            else
            {
                // check eve attack
                if ((float)key_bit_errors * 100 / config.key_part_size > config.eve_error_percentage)
                {
                    eve_attack_detected = 1;
                    statistics.eves_attack_detected++;
                }
                if (global_count < 3)
                {
                    printf("\n************************************************\n");
                    printf("*              Key Bit Errors Report            *\n");
                    printf("*************************************************\n");
                    printf("* Key Bit Errors (calib & eve): %d               *\n", key_bit_errors);
                    printf("* Eve Attack Detected:          %d               *\n", eve_attack_detected);
                    printf("* Calibration Errors config:    %d               *\n", (config.calib_error_percentage * config.key_part_size) / 100);
                    printf("* Allowed Error Bits:           %d               *\n", config.allowed_wrong_bits);
                    printf("* Regenerating key section...                   *\n");
                    printf("**************************************************\n");
                }
            }
            key_bit_errors = 0;
            eve_attack_detected = 0;
            if (config.eavesdropping)
                memset(key_eve_changed, ' ', config.key_part_size);
        }
        not_valid = 1;
        global_count++;
    }

    final_key[config.key_size] = '\0'; // Ensure null-termination
    // write secret key to file
    write_to_file_final_keys(final_key, "bob.key");
    write_to_file_final_keys(final_alice_key, "alice.key");

    printf("\n========================================================================================================\n");
    printf("                                     Final Key (%d bits)\n", count_bits(final_key));
    printf("========================================================================================================\n\n");

    print_with_spaces(final_key, config.key_size);
    printf("\n========================================================================================================\n");
    printf("                               Summary of Key Generation Statistics:\n", count_bits(final_key));
    printf("========================================================================================================\n\n");

    printf("\n  %-32s : %d / %-5d (%d%%)\n", "Final Calibration Error Bits", statistics.final_calib_error_bits_count, config.key_size,
           (statistics.final_calib_error_bits_count * 100) / config.key_size);
    printf("  %-32s : %d / %-5d (%d%%)\n", "Final Eve Error Bits", statistics.final_eve_error_bits_count, config.key_size,
           (statistics.final_eve_error_bits_count * 100) / config.key_size);
    printf("  %-32s : %d / %d\n", "Eve Attacks Detected", statistics.eves_attack_detected, statistics.eves_sections_participated);
    printf("  %-32s : %d bits\n", "Final Key Size", config.key_size);
    printf("  %-32s : %d bits\n", "Key Section Size", config.key_part_size);
    printf("  %-32s : %d bits\n", "Allowed Wrong Bits per Section", config.allowed_wrong_bits);
    printf("  %-32s : %d%%\n", "Calibration Error Percentage", config.calib_error_percentage);
    printf("  %-32s : %d%%\n", "Eavesdropped Sections Percentage", config.eve_percent_section);
    printf("  %-32s : %d%%\n", "Eve Bit Reproduction Percentage", config.eve_percent_reproduce);
    printf("  %-32s : %d erros\n", "Calibration Errors Missed", statistics.final_calib_error_bits_count);
    printf("  %-32s : %d errors\n", "Eve Errors Missed", statistics.final_eve_error_bits_count);
    printf("  %-32s : %d sections\n", "Total Sections Processed", statistics.total_run_sections);
    printf("  %-32s : %d sections\n", "Sections Used for Final Key", section_num);
    clock_t end_time = clock();
    double time_taken = ((double)(end_time - start_time)) / CLOCKS_PER_SEC;
    printf("  %-32s : %.3f seconds\n\n", "Time Taken to Generate the Key", time_taken);
    printf("========================================================================================================\n\n");

    // calculate statistics
    double correct_bits_measured = percent_of_correct_results(key_section, sifted_keys);
    double correct_final_keys = percent_of_correct_final_keys(secret_keys, key_section);
    // print statistics
    printf("Statistics: \n");
    printf("Bob measured %.2f%% correct bits using his basis\n", correct_bits_measured);
    printf("Percent of correct final keys: %.2f%%\n", correct_final_keys);
    printf("Detected %d key bit errors in a section of %d total bits\n\n", key_bit_errors, config.key_part_size);

    // Free allocated memory
    // Note - should be inside the loop
    free(key);
    free(key_clib_err);
    free(bobs_key);
    free(single_photons);
    free(single_photons_eve);
    free(measurement_bases);
    free(measurement_results);
    free(sifted_keys);
    free(key_distillation);
    free(secret_keys);
    free(key_section);

    return 0;
}

// ******************************************************************************************** //

// printing functions

void print_config(void)
{
    printf("========================================================================================================\n");
    printf("                                        Configuration Details                                         \n");
    printf("========================================================================================================\n");

    printf(" Key Size                     : %d bits\n", config.key_size);
    printf(" Key Part Size                : %d bits\n", config.key_part_size);
    printf(" Number of Key Parts          : %d parts\n", config.key_part_num);
    printf(" Eavesdropping                : %s\n", config.eavesdropping ? "Enabled" : "Disabled");
    printf(" Calibration Error Percentage : %d%%\n", config.calib_error_percentage);
    printf(" Eve Error Percentage         : %d%%\n", config.eve_error_percentage);
    printf(" Eve Reproduction Percentage  : %d%%\n", config.eve_percent_reproduce);
    printf(" Eve section Eavesdropping %%  : %d%%\n", config.eve_percent_section);
    printf(" Allowed Wrong Bits           : %d bit(s)\n", config.allowed_wrong_bits);
}

void print_with_spaces(const char *str, int size)
{
    const int group_size = 4;
    const int groups_per_line = 20; // 8 groups = 32 bits per line

    for (int i = 0; i < size; i++)
    {
        printf("%c", str[i]);

        // Add a space after each group of 4
        if ((i + 1) % group_size == 0)
            printf(" ");

        // Newline after every line (8 groups = 32 bits)
        if ((i + 1) % (group_size * groups_per_line) == 0)
            printf("\n");
    }
    printf("\n");
}

void print_final_keys(char *secret_keys)
{
    int count = 0;
    for (int i = 0; i < config.key_part_size; i++)
    {
        if (secret_keys[i] == '1' || secret_keys[i] == '0')
        {
            printf("%c", secret_keys[i]);
            count++;
            if (count == 4)
            { // Add space every 4 characters
                printf(" ");
                count = 0;
            }
        }
    }
    printf("\n");
}

int write_to_file_final_keys(const char *secret_keys, const char *filename)
{
    FILE *fh;
    int size_written;

    fh = fopen(filename, "w");
    size_written = fwrite(secret_keys, sizeof(char), config.key_size, fh);
    if (config.key_size != size_written)
    {
        printf("Error: failed write secret-key to file\n");
        return -1;
    }

    return 0;
}

// ******************************************************************************************** //

// configuration functions

void usage(void)
{
    printf("======================================\n");
    printf(" Quantum Key Distribution - How to Use\n");
    printf("======================================\n\n");
    printf("Compile the program:   gcc main.c -o qkd.exe\n");
    printf("To run it:             qkd.exe [options]\n\n");

    printf("Available Options:\n");
    printf("  -k<size>        Total number of bits in the final key.\n");
    printf("                  Must be a multiple of 64. (e.g., -k4096)\n\n");

    printf("  -ps<size>       Number of bits in each section (key part).\n");
    printf("                  Must be 32, 64, or 128. (e.g., -ps64)\n\n");

    printf("  -e              Enable Eve (eavesdropper) to interfere\n");
    printf("                  with the communication for simulation.\n\n");

    printf("  -ec<percent>    Percentage of calibration errors (0 to 10).\n");
    printf("                  These are natural noise/errors. (e.g., -ec5)\n\n");

    printf("  -ee<percent>    Error percentage introduced by Eve (0 to 100).\n");
    printf("                  Simulates how noisy Eve's interference is. (e.g., -ee50)\n\n");

    printf("  -ep<percent>    Percent of Eve's bits that match the real ones.\n");
    printf("                  Choose 0, 25, or 50. (e.g., -ep25)\n\n");

    printf("  -es<percent>    Percent of sections Eve tries to listen to.\n");
    printf("                  Choose 0, 10, 25, or 50. (e.g., -es10)\n\n");

    printf("  -a<number>      Number of errors allowed per section.\n");
    printf("                  If exceeded, the section is regenerated.\n\n");

    printf("  -vvv            Enable extra debug printouts during the run.\n\n");

    exit(0);
}

// Check if the user entered valid parameters. If not, display an error and show the available valid parameters
void validate_params(void)
{
    if (config.key_part_size != 32 && config.key_part_size != 64 && config.key_part_size != 128)
    {
        printf("\nError: illegal key part size (key_part_size = %d)\n\n", config.key_part_size);
        usage();
    }

    if (!(config.calib_error_percentage >= 0 && config.calib_error_percentage <= 10))
    {
        printf("\nError: illegal calibration error threshold (calib_error_percentage = %d)\n\n", config.calib_error_percentage);
        usage();
    }

    if (!(config.eve_error_percentage >= 0 && config.eve_error_percentage <= 100))
    {
        printf("\nError: illegal eve error threshold (eve_error_percentage = %d)\n\n", config.eve_error_percentage);
        usage();
    }

    if (!(config.eve_percent_reproduce == 0 || config.eve_percent_reproduce == 25 || config.eve_percent_reproduce == 50))
    {
        printf("\nError: illegal eve reproduce percentage (eve_percent_reproduce = %d)\n\n", config.eve_percent_reproduce);
        usage();
    }

    if (!(config.eve_percent_section == 0 || config.eve_percent_section == 10 || config.eve_percent_section == 25 || config.eve_percent_section == 50))
    {
        printf("\nError: illegal eve section to listen percentage (eve_percent_section = %d)\n\n", config.eve_percent_section);
        usage();
    }
}

void read_config(int argc, char **argv)
{
    // initilize config
    memset((void *)&config, 0, sizeof(config));

    // set default parameters values
    config.key_size = 4096;
    config.key_part_size = 64;
    config.key_part_num = config.key_size / config.key_part_size;
    config.eavesdropping = 1;
    config.calib_error_percentage = 10;
    config.eve_error_percentage = 50;
    config.eve_percent_reproduce = 50;
    config.eve_percent_section = 50;
    config.allowed_wrong_bits = 0;

    // save arguments as config parameters
    for (int i = 1; i < argc; i++)
    {
        if (strncmp(argv[i], "-h", 2) == 0)
            usage();
        if (strncmp(argv[i], "-k", 2) == 0)
            config.key_size = atoi(argv[i] + 2);
        else if (strncmp(argv[i], "-ps", 3) == 0)
            config.key_part_size = atoi(argv[i] + 3);
        else if (strncmp(argv[i], "-pn", 3) == 0)
            config.key_part_num = atoi(argv[i] + 3);
        else if (strncmp(argv[i], "-ec", 3) == 0)
            config.calib_error_percentage = atoi(argv[i] + 3);
        else if (strncmp(argv[i], "-ee", 3) == 0)
            config.eve_error_percentage = atoi(argv[i] + 3);
        else if (strncmp(argv[i], "-ep", 3) == 0)
            config.eve_percent_reproduce = atoi(argv[i] + 3);
        else if (strncmp(argv[i], "-es", 3) == 0)
            config.eve_percent_section = atoi(argv[i] + 3);
        else if (strncmp(argv[i], "-e", 2) == 0)
            config.eavesdropping = 1;
        else if (strncmp(argv[i], "-a", 2) == 0)
            config.allowed_wrong_bits = atoi(argv[i] + 2);
    }

    // check if the parameter entered are valid
    validate_params();

    // print the configuration parameters
    if (global_count < 3)
        print_config();
}

// ******************************************************************************************** //

// keys generation functions

char *generate_key(void)
{
    char *key = (char *)malloc(sizeof(char) * (config.key_part_size + 1)); // +1 for null terminator
    if (key == NULL)
        return NULL;
    key[config.key_part_size] = '\0'; // Null-terminate the string

    for (int i = 0; i < config.key_part_size; i++)
    {
        int rand_num = rand() % 100; // Generate a random number between 0 and 99
        if (rand_num < 50)
        {
            key[i] = '1'; // First half (0-49) -> generate '1'
        }
        else
        {
            key[i] = '0'; // Second half (50-99) -> generate '0'
        }
    }

    return key;
}

char *generate_calib_key(const char *akey)
{
    int pos;

    char *ckey = (char *)malloc(sizeof(char) * (config.key_part_size + 1)); // +1 for null terminator
    if (ckey == NULL)
        return NULL;

    // copy alice key to ckey
    memcpy(ckey, akey, config.key_part_size);
    ckey[config.key_part_size] = '\0'; // Null-terminate the string

    // tmp arr for marking the already switched bits
    int *pint_arr = (int *)malloc(sizeof(int) * (config.key_part_size));
    memset(pint_arr, 0, sizeof(int) * (config.key_part_size));

    // introduce errors based on calib_error_percentage
    int num_errors = (config.calib_error_percentage * config.key_part_size) / 100; // Calculate number of errors to introduce
    // printf("Calibration errors: number of bits to change=%d %d %d\n", num_errors, config.calib_error_percentage, config.key_part_size);

    for (int i = 0; i < num_errors; i++)
    {
        while (1)
        {
            pos = rand() % config.key_part_size; // Random position to flip
            if (pint_arr[pos] == 0)
                break;
        }
        ckey[pos] = (ckey[pos] == '0') ? '1' : '0'; // Flip the bit
        pint_arr[pos] = 1;
    }

    free(pint_arr);

    return ckey;
}

char *introduce_eve_errors(char *alice_photons, char *key_clib_err)
{
    int replace_count;
    int rand_num;
    int pos;
    char measur_base;
    char measur_bit;

    // Generate Eve's photons based on Alice's (single_photons)
    char *eve_photons = (char *)malloc(sizeof(char) * (config.key_part_size + 1));
    if (eve_photons == NULL)
        return NULL;
    memcpy(eve_photons, alice_photons, config.key_part_size);
    eve_photons[config.key_part_size] = '\0';

    // tmp arr for marking the already switched bits
    int *pint_arr = (int *)malloc(sizeof(int) * (config.key_part_size));
    memset(pint_arr, 0, sizeof(int) * (config.key_part_size));

    if (config.eavesdropping == 1 && (rand() % 100) < config.eve_percent_section)
    {
        // increment the number of eve's sections attack
        statistics.eves_sections_participated++;

        // Calculate how many continuous photons to replace based on eve_percent_reproduce
        replace_count = (config.key_part_size * config.eve_percent_reproduce) / 100;

        // Replace a continuous block of photons
        for (int i = 0; i < replace_count; i++)
        {
            while (1)
            {
                pos = rand() % config.key_part_size; // Random position to change
                if (pint_arr[pos] == 0)
                    break;
            }

            measur_base = (rand() % 100) < 50 ? '+' : 'x';

            if ((alice_photons[pos] == 'h' && measur_base == '+') ||
                (alice_photons[pos] == 'b' && measur_base == 'x'))
            {
                measur_bit = '0';                                     // Set '0' for horizontal or -45°
                eve_photons[pos] = ((rand() % 100) < 50) ? 'h' : 'b'; // generates bit = 0
            }
            else if ((alice_photons[pos] == 'v' && measur_base == '+') ||
                     (alice_photons[pos] == 'd' && measur_base == 'x'))
            {
                measur_bit = '1';                                     // Set '1' for vertical or 45°
                eve_photons[pos] = ((rand() % 100) < 50) ? 'v' : 'd'; // generates bit = 1
            }
            else
            {
                // generate bit
                measur_bit = (rand() % 100) < 50 ? '0' : '1';
                key_clib_err[pos] = measur_bit;
                if (measur_bit == '0')
                    eve_photons[pos] = ((rand() % 100) < 50) ? 'h' : 'b'; // generates bit = 0
                else
                    eve_photons[pos] = ((rand() % 100) < 50) ? 'v' : 'd'; // generates bit = 1
            }

            pint_arr[pos] = 1;
        }

        // copy bits changed to key_eve_changed
        for (int i = 0; i < config.key_part_size; i++)
            if (pint_arr[i] == 1)
                key_eve_changed[i] = '@';
    }

    free(pint_arr);

    return eve_photons;
}

// create the polarizations for Alice
char *create_polar_alice(char *key)
{
    char *single_photons = (char *)malloc(sizeof(char) * (config.key_part_size + 1)); // +1 for null terminator
    if (single_photons == NULL)
        return NULL;

    for (int i = 0; i < config.key_part_size; i++)
    {
        int rand_num = rand() % 100; // Generate a random number between 0 and 99
        if (key[i] == '0')
        {
            // Bit is 0, choose between 'b' and 'h'
            single_photons[i] = (rand_num < 50) ? 'b' : 'h';
        }
        else if (key[i] == '1')
        {
            // Bit is 1, choose between 'd' and 'v'
            single_photons[i] = (rand_num < 50) ? 'd' : 'v';
        }
    }

    single_photons[config.key_part_size] = '\0'; // Null-terminate the string
    return single_photons;
}

char *create_basis_bob(void)
{
    int rand_base;
    char *measurement_bases = (char *)malloc(sizeof(char) * config.key_part_size);
    if (measurement_bases == NULL)
        return NULL;

    // Generate random polarizations for each bit
    for (int i = 0; i < config.key_part_size; i++)
    {
        rand_base = rand() % 100; // Generate a random number between 0 and 99
        if (rand_base < 50)
        {
            rand_base = 1; // First half (0-49) -> generate '1'
        }
        else
        {
            rand_base = 0; // Second half (50-99) -> generate '0'
        }
        measurement_bases[i] = rand_base ? 'x' : '+'; // Assign 'd' if 1, else 'r'
    }

    return measurement_bases;
}

char *compare_polars(char *single_photons, char *measurement_bases)
{
    char *measurement_results = (char *)malloc(sizeof(char) * config.key_part_size);
    if (measurement_results == NULL)
        return NULL;

    for (int i = 0; i < config.key_part_size; i++)
    {
        // rectillinear case (+)
        if ((single_photons[i] == 'v' || single_photons[i] == 'h') && (measurement_bases[i] == '+'))
        {
            measurement_results[i] = 'v';
        }
        // diagonal case (x)
        else if ((single_photons[i] == 'b' || single_photons[i] == 'd') && (measurement_bases[i] == 'x'))
        {
            measurement_results[i] = 'v';
        }
        // no match found
        else
        {
            measurement_results[i] = 'x';
        }
    }

    return measurement_results;
}

char *create_bobs_key(char *single_photons, char *measurement_bases)
{
    // int rand_bit;
    char *bobs_key = (char *)malloc(sizeof(char) * (config.key_part_size + 1));
    if (bobs_key == NULL)
        return NULL;

    // Iterate over the single_photons and measurement_bases to create Bob's key
    for (int i = 0; i < config.key_part_size; i++)
    {
        if ((single_photons[i] == 'h' && measurement_bases[i] == '+') ||
            (single_photons[i] == 'b' && measurement_bases[i] == 'x'))
        {
            bobs_key[i] = '0'; // Set '0' for horizontal or -45°
        }
        else if ((single_photons[i] == 'v' && measurement_bases[i] == '+') ||
                 (single_photons[i] == 'd' && measurement_bases[i] == 'x'))
        {
            bobs_key[i] = '1'; // Set '1' for vertical or 45°
        }
        else
        {
            //// guess bit
            // rand_bit = rand() % 100;
            // if (rand_bit < 50) {
            //     bobs_key[i] = '1';  // First half (0-49) -> generate '1'
            // }
            // else {
            //     bobs_key[i] = '0';  // Second half (50-99) -> generate '0'
            // }
            bobs_key[i] = ' ';
        }
    }

    bobs_key[config.key_part_size] = '\0'; // Null-terminate the string
    return bobs_key;
}

// validate polarization between Alice & Bob (on public channel)
char *create_sifted_keys(char *key, char *single_photons, char *measurement_results, char *measurement_bases, char *bobs_key)
{
    char *skey = (char *)malloc(sizeof(char) * (config.key_part_size + 1)); // +1 for null terminator
    if (skey == NULL)
        return NULL;

    memset(skey, ' ', sizeof(char) * (config.key_part_size + 1));

    for (int i = 0; i < config.key_part_size; i++)
    {
        if (measurement_results[i] == 'v')
        {
            skey[i] = bobs_key[i];
        }
    }
    skey[config.key_part_size] = '\0';
    return skey;
}

// validate bits between Alice & Bob (on public channel)
char *create_key_distillation(char *sifted_keys, char *alice_key, char *single_photons, char *single_photons_eve, char **error_key, int *key_bit_errors)
{
    double valid_count = 0;
    int bit_offset;

    char *dkey = (char *)malloc(sizeof(char) * (config.key_part_size + 1)); // +1 for null terminator
    if (dkey == NULL)
        return NULL;

    *error_key = (char *)malloc(sizeof(char) * (config.key_part_size + 1)); // +1 for null terminator
    if (*error_key == NULL)
        return NULL;
    memset(*error_key, ' ', config.key_part_size);
    (*error_key)[config.key_part_size] = '\0';

    // copy sifted keys to dkey
    memcpy(dkey, sifted_keys, config.key_part_size);

    // count how many valid bits in sifted keys
    for (int i = 0; i < config.key_part_size; i++)
    {
        if (sifted_keys[i] != ' ')
        {
            valid_count++;
        }
    }
    valid_count = ceil(valid_count / 2);

    for (int i = 0; i < valid_count; i++)
    {
        // find next valid bit to compare
        while (1)
        {
            bit_offset = rand() % config.key_part_size;
            if (dkey[bit_offset] == ' ' || dkey[bit_offset] == '@')
                continue;
            else
                break;
        }
        // compare Alice & Bob bits
        // if (alice_key[bit_offset] != dkey[bit_offset])
        if ((single_photons[bit_offset] != single_photons_eve[bit_offset]) ||
            (alice_key[bit_offset] != dkey[bit_offset]))
        {
            (*key_bit_errors)++;

            // makr error bit
            (*error_key)[bit_offset] = '*';
        }

        // drop this bit
        dkey[bit_offset] = '@';
    }

    for (int i = 0; i < config.key_part_size; i++)
        if (dkey[i] == '@')
            dkey[i] = sifted_keys[i];
        else
            dkey[i] = ' ';

    return dkey;
}

char *create_secret_keys(char *sifted_keys, char *key_distillation)
{
    char *secret_keys = (char *)malloc(sizeof(char) * (config.key_part_size + 1)); // +1 for null terminator
    if (secret_keys == NULL)
        return NULL;

    // Initialize the array with spaces
    memset(secret_keys, ' ', sizeof(char) * config.key_part_size);

    secret_keys[config.key_part_size] = '\0'; // Null-terminate the string

    for (int i = 0; i < config.key_part_size; i++)
    {
        if (key_distillation[i] != sifted_keys[i])
        {
            secret_keys[i] = sifted_keys[i];
        }
    }

    return secret_keys;
}

// ******************************************************************************************** //

// statistics functions

double percent_of_correct_results(char *key, char *sifted_keys)
{
    int count = 0;
    for (int i = 0; i < config.key_part_size; i++)
    {
        if (sifted_keys[i] == key[i])
        {
            count++;
        }
    }
    return (double)count / config.key_part_size * 100;
}

double percent_of_correct_final_keys(char *secret_keys, char *key)
{
    double correct_count = 0;
    for (int i = 0; i < config.key_part_size; i++)
    {
        // compare Alice & Bob bits
        if (key[i] == secret_keys[i])
            correct_count++;
    }

    return (double)correct_count / config.key_part_size * 100;
}

int count_bits(const char *str)
{
    int count = 0;

    // Iterate through the string and count '0's and '1's
    for (int i = 0; str[i] != '\0'; i++)
    {
        if (str[i] == '0' || str[i] == '1')
        {
            count++;
        }
    }

    return count;
}

int copy_valid_keys(char *final_key, char *final_alice_key, const char *secret_keys, const char *key, int offset, int key_part_size)
{
    // Iterate through secret_keys and copy valid characters
    for (int i = 0; i < key_part_size; i++)
    {
        if (secret_keys[i] == '0' || secret_keys[i] == '1')
        {
            final_key[offset] = secret_keys[i];
            final_alice_key[offset] = key[i];
            offset++;
        }
    }

    // Null-terminate the final_key at the correct position
    final_key[offset] = '\0';
    final_alice_key[offset] = '\0';
    return offset;
}
