import scipy as sp
import numpy as np

from wave_helper import *
import math
import os.path

MAX_VOL = 32767
MIN_VOL = -32768
PI = math.pi
INVALID_TEXT_MSG = 'Text is not a valid melody'
INVALID_PATH_MSG = 'The file does not exist'
VALID_TEXT = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'Q'}
seinfeld = load_wave('seinfeld.wav')

batman = load_wave('batman_theme_x.wav')


def reverse_wave(wave):
    reversed_wave = [wave[0], []]
    for index in range((len(wave[1])) - 1, -1, -1):
        reversed_wave[1].append(wave[1][index])
    return reversed_wave


def accelerate_wave(wave):
    acc_wave = [wave[0], []]
    for index in range(0, len(wave[1]), 2):
        acc_wave[1].append(wave[1][index])
    return acc_wave


def slow_wave(wave):
    slow_wave = [wave[0], []]
    for index in range(len(wave[1]) - 1):
        slow_wave[1].append(wave[1][index])
        avg_tup = avg_of_2_tups(wave[1][index], wave[1][index + 1])
        slow_wave[1].append(avg_tup)
    slow_wave[1].append(wave[1][len(wave[1]) - 1])
    return slow_wave


def avg_of_2_tups(tup1, tup2):
    avg_tup = []
    avg_tup.append(int((tup1[0] + tup2[0]) / 2))
    avg_tup.append(int((tup1[1] + tup2[1]) / 2))
    return avg_tup


def inc_vol(wave):
    loud_wave = [wave[0], []]
    for tupple in wave[1]:
        amp_tup = amplify_tup(tupple)
        loud_wave[1].append(amp_tup)
    return loud_wave


def amplify_tup(tup):
    amp_tup = []
    amp_tup1 = int(1.2 * tup[0])
    amp_tup2 = int(1.2 * tup[1])

    if amp_tup1 > MAX_VOL:
        amp_tup1 = MAX_VOL
    elif amp_tup1 < MIN_VOL:
        amp_tup1 = MIN_VOL

    if amp_tup2 > MAX_VOL:
        amp_tup2 = MAX_VOL
    elif amp_tup2 < MIN_VOL:
        amp_tup2 = MIN_VOL

    amp_tup.append(amp_tup1)
    amp_tup.append(amp_tup2)
    return amp_tup


def dec_vol(wave):
    quiet_wave = [wave[0], []]
    for tupple in wave[1]:
        qui_tup = quiet_tup(tupple)
        quiet_wave[1].append(qui_tup)
    return quiet_wave


def quiet_tup(tup):
    qui_tup = []

    qui_tup1 = int(tup[0] / 1.2)
    qui_tup2 = int(tup[1] / 1.2)

    qui_tup.append(qui_tup1)
    qui_tup.append(qui_tup2)

    return qui_tup


def muf_sound(wave):
    muf_wave = [wave[0], []]
    wav_lst = wave[1]
    muf_wave[1].append(avg_of_2_tups(wav_lst[0], wav_lst[1]))
    for index in range(1, len(wav_lst) - 1):
        muf_tup = avg_of_3_tups(wav_lst[index - 1], wav_lst[index],
                                wav_lst[index + 1])
        muf_wave[1].append(muf_tup)
    muf_wave[1].append(
        avg_of_2_tups(wav_lst[len(wav_lst) - 1], wav_lst[len(wav_lst) - 2]))
    return muf_wave


def avg_of_3_tups(tup1, tup2, tup3):
    avg_tup = []
    avg_tup1 = int((tup1[0] + tup2[0] + tup3[0]) / 3)
    avg_tup2 = int((tup1[1] + tup2[1] + tup3[1]) / 3)

    avg_tup.append(avg_tup1)
    avg_tup.append(avg_tup2)
    return avg_tup


def norm_fr_rate(wave1, wave2):
    if wave1[0] > wave2[0]:
        norm_wave1 = build_norm_wave(wave1, wave2)
        norm_wave2 = wave2
    elif wave2[0] > wave1[0]:
        norm_wave2 = build_norm_wave(wave2, wave1)
        norm_wave1 = wave1
    else:
        norm_wave1 = wave1
        norm_wave2 = wave2
    return norm_wave1, norm_wave2


def build_norm_wave(big_wave, small_wave):
    normalized_wave = [small_wave[0], []]
    gcd = math.gcd(big_wave[0], small_wave[0])
    big_gcd_ratio = int(big_wave[0] / gcd)
    small_gcd_ratio = int(small_wave[0] / gcd)
    for index1 in range(0, len(big_wave[1]), big_gcd_ratio):
        for index2 in range(small_gcd_ratio):
            if (index1 + index2) > len(big_wave[1]) - 1:
                break
            else:
                normalized_wave[1].append(big_wave[1][index1 + index2])
    return normalized_wave


def unite_waves(wave1, wave2):
    norm_wav1, norm_wav2 = norm_fr_rate(wave1, wave2)
    if len(norm_wav1[1]) >= len(norm_wav2[1]):
        uni_wave = uni_norm_waves(norm_wav1, norm_wav2)
    else:
        uni_wave = uni_norm_waves(norm_wav2, norm_wav1)
    return uni_wave


def uni_norm_waves(big_wave, small_wave):
    uni_wave = [big_wave[0], []]
    for index1 in range(len(small_wave[1])):
        avg_tup = avg_of_2_tups(big_wave[1][index1], small_wave[1][index1])
        uni_wave[1].append(avg_tup)
    for index2 in range(len(small_wave[1]), len(big_wave[1])):
        uni_wave[1].append(big_wave[1][index2])
    return uni_wave


def build_melody(note_list):
    list_of_melody = [2000, []]
    for i in range(0, len(note_list)-1, 2):
        if note_list[i] == 'Q':
            current_note = build_empty(int(note_list[i + 1]))
        else:
            current_note = build_note(note_list[i], int(note_list[i + 1]))
        list_of_melody[1] += current_note
    return list_of_melody


def build_note(note, length):
    freq_of_note = note_to_freq(note)
    spc = (2000 / freq_of_note)

    note_list = []
    for i in range(int(length * (2000 / 16))):
        note_list.append([sample_i(i, spc), sample_i(i, spc)])
    return note_list


def build_empty(length):
    empty_note = []
    for i in range(int(length * (2000 / 16))):
        empty_note.append([0, 0])
    return empty_note


def sample_i(i, spc):
    return int(MAX_VOL * math.sin((2 * PI) * (i / spc)))


def note_to_freq(note):
    if note == 'A':
        return 440
    elif note == 'B':
        return 494
    elif note == 'C':
        return 523
    elif note == 'D':
        return 587
    elif note == 'E':
        return 659
    elif note == 'F':
        return 698
    elif note == 'G':
        return 784


def read_melody(filepath):
    if os.path.isfile(filepath):
        melody_file = open(filepath, 'r')
        text_in_file = list(melody_file.read())
        clean_melody_list = []
        for i in range(len(text_in_file)):
            if text_in_file[i] != ' ' and text_in_file[i] != '\n':
                clean_melody_list.append(text_in_file[i])
        return clean_melody_list
    else:
        return False


def check_invalid_text(melody_text):
    for i in range(len(melody_text), 2):
        if melody_text(i) not in VALID_TEXT:
            return False
        elif type(melody_text(i + 1)) != 'int':
            return False
        elif len(melody_text) %2 != 0:
            return False


def main_menu():
    print("Welcome to the best song editor in the aquarium!")
    print("insert 1 to edit an existing file")
    print("insert 2 to combine two files")
    print("insert 3 to compose your own song")
    print("insert 4 to exit the editor")
    # user_input = 0
    user_input = input()
    # while user_input != '4':

        # print("insert 1 to edit an existing file")
        # print("insert 2 to combine two files")
        # print("insert 3 to compose your own song")
        # print("insert 4 to exit the editor")

        # user_input = input()
    if user_input == '1':
        main_edit()
        return True
    elif user_input == '2':
        main_combine()
        return True
    elif user_input == '3':
        main_compose()
        return True
    elif user_input == '4':
        print('goodbye!')
        return False
    else:
        print('not a valid input! restart the editor')
        return True


def main_edit():
    file_path = ''
    while os.path.isfile(file_path) is False:
        print('Enter the file path:')
        file_path = input()
        if os.path.isfile(file_path):
            break
    user_file = load_wave(file_path)
    new_wave = change_existing_file(user_file)
    save_menu(new_wave)
    return


def change_existing_file(user_file):
    user_input = 0
    while int(user_input) not in range(1, 7):
        print('What would you like to do with your file?')
        print('1 - Reverse my song')
        print('2 - Accelerate my song')
        print('3 - Slow down my song')
        print('4 - increase the volume')
        print('5 - decrease the volume')
        print('6 - Run a low pass filter on my song')
        user_input = input()
        if int(user_input) not in range(1, 7):
            print('Please enter a valid input')
    new_wave = []
    if user_input == '1':
        new_wave = reverse_wave(user_file)
    elif user_input == '2':
        new_wave = accelerate_wave(user_file)
    elif user_input == '3':
        new_wave = slow_wave(user_file)
    elif user_input == '4':
        new_wave = inc_vol(user_file)
    elif user_input == '5':
        new_wave = dec_vol(user_file)
    elif user_input == '6':
        new_wave = muf_sound(user_input)
    return new_wave


def save_menu(wave):
    user_input = 0
    while int(user_input) not in range(1, 3):
        print('1 - Save the file')
        print('2 - Change the new file')
        user_input = input()
        if int(user_input) not in range(1, 3):
            print('Please enter a valid input')

    if user_input == '1':
        file_name = input('Save as: ')
        save_wave(wave[0], wave[1], file_name)
        print('Your file has been saved as: ' + file_name)
        print(save_wave(wave[0], wave[1], file_name))  # DELETE
    elif user_input == '2':
        change_existing_file(wave)
    main_menu()
    return


def main_combine():
    is_file1 = False
    is_file2 = False
    file1_path = ''
    file2_path = ''
    while is_file1 is False or is_file2 is False:
        user_input = input('Enter your files path is the following format: \n '
                           '<file1_path><file2_path> \n')
        if '><' not in user_input:
            print('The input is not in the correct format')
            is_file1 = False
            is_file2 = False
        else:
            user_input = user_input.strip('<')
            user_input = user_input.strip('>')
            user_input_lst = user_input.split('><')
            file1_path = user_input_lst[0]
            file2_path = user_input_lst[1]
            is_file1 = os.path.isfile(file1_path)
            is_file2 = os.path.isfile(file2_path)
            if is_file1 is False:
                print('File 1 does not exist')
            elif is_file2 is False:
                print('File 2 does not exist')
    file1 = load_wave(file1_path)
    file2 = load_wave(file2_path)
    new_wave = unite_waves(file1, file2)
    save_menu(new_wave)
    return


def main_compose():
    is_melody = True
    while is_melody:
        user_input = input('Enter your melody file path: \n')
        is_melody = read_melody(user_input)
        melody_list = build_melody(is_melody)
        save_menu(melody_list)


def main():
    run_menu = True
    while run_menu is True:
        run_menu = main_menu()


if __name__ == "__main__":
    main()
