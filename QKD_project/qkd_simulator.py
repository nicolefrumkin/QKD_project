import random
import math
from collections import namedtuple

# Define the configuration and statistics structures
Config = namedtuple("Config", [
    "key_size", "key_part_size", "key_part_num", "eavesdropping",
    "calib_error_percentage", "eve_error_percentage", "eve_percent_reproduce",
    "eve_percent_section", "allowed_wrong_bits"
])

class Statistics:
    def __init__(self):
        self.total_run_sections = 0
        self.eves_attack_detected = 0
        self.eves_sections_participated = 0
        self.final_calib_error_bits_count = 0
        self.final_eve_error_bits_count = 0

# Global variables
config = None
statistics = None
key_eve_changed = []

# Initialize configuration and statistics
def initialize():
    global config, statistics
    config = Config(
        key_size=1024,
        key_part_size=64,
        key_part_num=16,
        eavesdropping=False,
        calib_error_percentage=2,
        eve_error_percentage=6,
        eve_percent_reproduce=0,
        eve_percent_section=0,
        allowed_wrong_bits=3
    )

    statistics = Statistics()

# Helper functions
def count_bits(binary_str):
    return sum(1 for char in binary_str if char in ('0', '1'))

def copy_valid_keys(final_key, secret_keys, offset):
    for char in secret_keys:
        if char in ('0', '1'):
            final_key.append(char)
            offset += 1
    return offset

# Key generation functions
def generate_key():
    return ''.join(random.choice(['0', '1']) for _ in range(config.key_part_size))

def generate_calib_key(akey):
    ckey = list(akey)
    num_errors = (config.calib_error_percentage * config.key_part_size) // 100
    error_positions = random.sample(range(config.key_part_size), num_errors)

    for pos in error_positions:
        ckey[pos] = '1' if ckey[pos] == '0' else '0'

    return ''.join(ckey)

def introduce_eve_errors(alice_photons):
    global key_eve_changed
    eve_photons = list(alice_photons)
    if config.eavesdropping and random.randint(0, 100) < config.eve_percent_section:
        replace_count = (config.key_part_size * config.eve_percent_reproduce) // 100
        positions = random.sample(range(config.key_part_size), replace_count)

        for pos in positions:
            eve_photons[pos] = random.choice(['h', 'b', 'v', 'd'])
            key_eve_changed[pos] = '@'

        statistics.eves_sections_participated += 1

    return ''.join(eve_photons)

def create_polar_alice(key):
    return ''.join(
        random.choice(['b', 'h']) if bit == '0' else random.choice(['d', 'v'])
        for bit in key
    )

def create_basis_bob():
    return ''.join(random.choice(['+', 'x']) for _ in range(config.key_part_size))

def compare_polars(single_photons, measurement_bases):
    return ''.join(
        'v' if (photon in ['v', 'h'] and base == '+') or (photon in ['b', 'd'] and base == 'x') else 'x'
        for photon, base in zip(single_photons, measurement_bases)
    )

def create_bobs_key(single_photons, measurement_bases):
    return ''.join(
        '0' if (photon == 'h' and base == '+') or (photon == 'b' and base == 'x') else
        '1' if (photon == 'v' and base == '+') or (photon == 'd' and base == 'x') else ' '
        for photon, base in zip(single_photons, measurement_bases)
    )

def create_sifted_keys(key, single_photons, measurement_results, measurement_bases, bobs_key):
    return ''.join(
        bobs_key[i] if measurement_results[i] == 'v' else ' '
        for i in range(config.key_part_size)
    )

def create_key_distillation(sifted_keys, alice_key, single_photons, single_photons_eve):
    dkey = list(sifted_keys)
    error_key = [' '] * config.key_part_size

    valid_count = math.ceil(sum(1 for bit in sifted_keys if bit != ' ') / 2)

    for _ in range(valid_count):
        while True:
            bit_offset = random.randint(0, config.key_part_size - 1)
            if dkey[bit_offset] != ' ':
                break

        if single_photons[bit_offset] != single_photons_eve[bit_offset] or alice_key[bit_offset] != dkey[bit_offset]:
            error_key[bit_offset] = '*'

        dkey[bit_offset] = ' '

    return ''.join(dkey), ''.join(error_key)

def create_secret_keys(sifted_keys, key_distillation):
    return ''.join(
        sifted_keys[i] if key_distillation[i] != sifted_keys[i] else ' '
        for i in range(config.key_part_size)
    )

# Main simulation logic
def main():
    initialize()

    final_key = []
    offset = 0
    section_num = 1

    while count_bits(final_key) < config.key_size:
        not_valid = True
        while not_valid:
            print(f"\n{'='*100}")
            print(f"                                       Section #{section_num} ({config.key_part_size} bits):")
            print(f"{'='*100}\n")

            statistics.total_run_sections += 1

            key = generate_key()
            key_clib_err = generate_calib_key(key)
            single_photons = create_polar_alice(key_clib_err)
            single_photons_eve = introduce_eve_errors(single_photons)
            measurement_bases = create_basis_bob()
            measurement_results = compare_polars(single_photons_eve, measurement_bases)
            bobs_key = create_bobs_key(single_photons_eve, measurement_bases)
            sifted_keys = create_sifted_keys(key, single_photons_eve, measurement_results, measurement_bases, bobs_key)
            key_distillation, error_key = create_key_distillation(sifted_keys, key, single_photons, single_photons_eve)
            secret_keys = create_secret_keys(sifted_keys, key_distillation)

            def format_key_output(label, key_data):
                print(f" {label}:            ", end="")
                for i, char in enumerate(key_data):
                    print(char, end=" " if (i + 1) % 4 == 0 else "")
                print()

            format_key_output("Alice's Key", key)
            format_key_output("Key with Calib Errors", key_clib_err)
            format_key_output("Single Photons", single_photons)
            format_key_output("Measurement Bases", measurement_bases)
            format_key_output("Measurement Results", measurement_results)
            format_key_output("Bob's Key", bobs_key)
            format_key_output("Sifted Keys", sifted_keys)
            format_key_output("Key Distillation", key_distillation)
            format_key_output("Key Bits Error", error_key)
            format_key_output("Secret Keys", secret_keys)

            if error_key.count('*') <= config.allowed_wrong_bits:
                not_valid = False
                offset = copy_valid_keys(final_key, secret_keys, offset)
                section_num += 1

    print(f"\n{'='*100}")
    print(f"Final Key ({len(final_key)} bits):")
    for i, char in enumerate(final_key):
        print(char, end=" " if (i + 1) % 4 == 0 else "")
    print()

if __name__ == "__main__":
    main()
