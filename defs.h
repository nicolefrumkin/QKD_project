#ifndef DEFS_H // Check if DEFS_H has not been defined yet
#define DEFS_H // Define DEFS_H to prevent multiple inclusion of this file

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <math.h>
#include <assert.h>

// Configuration structure for holding command-line parameters
typedef struct {
    int key_size;
    int key_part_size;
    int key_part_num;
    int eavesdropping;
    int calib_error_percentage; // number of error originating from uncalibrated equipment
    int eve_error_percentage;  // threshold above which Eve is eavesdropping
    int eve_percent_reproduce; // percentage of photons Eve captures and regenerates for Bob
    int eve_percent_section; // percentage of number of sections eve listens to
    int allowed_wrong_bits;
} config_st;

extern config_st config;  // This allows this variable to be accessed from other source files

// statistics info
typedef struct {
    int eves_attack_detected;           // eve's attack detected on a key section eve eavesdropping
    int eves_sections_participated;     // number of sections eve was involved in
    int total_run_sections;             // number of sections to generate the final key
    int final_calib_error_bits_count;
    int final_eve_error_bits_count;
} stats_st;

extern stats_st statistics;


// Function declarations
char* generate_key(void);
char* generate_calib_key(const char* akey);
void use_key(char* msg, const char* key);
void print_with_spaces(const char* str, int size);
char* create_polar_alice(char* key);
char* create_basis_bob(void);
char* compare_polars(char* single_photons, char* measurement_bases);
char* create_bobs_key(char* single_photons, char* measurement_bases);
char* create_sifted_keys(char* key, char* single_photons, char* measurement_results, char* measurement_bases, char* bobs_key);
// char* create_key_distillation(char* sifted_keys, char* key, int* key_bit_errors);
char* create_key_distillation(char* sifted_keys, char* alice_key, char* single_photons, char* single_photons_eve, char** error_key, int* key_bit_errors);
char* create_secret_keys(char* sifted_keys, char* key_distillation);
void print_final_keys(char* secret_keys);
double percent_of_correct_results(char* key, char* sifted_keys);
double percent_of_correct_final_keys(char* secret_keys, char* key);
char* introduce_eve_errors(char* single_photons, char* key_clib_err);
void read_config(int argc, char** argv);
int count_bits(const char* str);
int copy_valid_keys(char* final_key, char* final_alice_key, const char* secret_keys, const char* key, int offset, int key_part_size);
int write_to_file_final_keys(const char *secret_keys, const char *filename);

// this line marks the end of the block
#endif // DEFS_H
