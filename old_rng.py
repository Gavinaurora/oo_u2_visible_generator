import json
import random

# global variables
file_name = "stdout.txt"
parameter = {}
pas_id = 0
time = 0
floor_name = []
lift_id_pool = []
sche_floor_name = []
predicted_time = {}
speed_pool = []
sche_id_left_pool = []


def __init__():
    global parameter, pas_id, time, lift_id_pool, floor_name
    global sche_floor_name, speed_pool, sche_id_left_pool
    parameter = json.load(open('config.json', 'r', encoding="utf-8"))
    pas_id = parameter['INIT_PAS_ID']
    time = parameter['TIME']
    lift_id_pool = parameter['LIFT_ID']
    floor_name = parameter['FLOOR_NAME']
    sche_floor_name = parameter['SCHE_NAME']
    speed_pool = parameter['SPEED']
    sche_id_left_pool = parameter['LIFT_ID']

    random.shuffle(lift_id_pool)
    random.shuffle(sche_id_left_pool)
    for i in lift_id_pool:
        predicted_time[i] = 0.0


def atomic_mono_gen(pri, from_floor, to_floor):
    with open(file_name, 'a') as f:
        f.write(
            str("[" + str(round(time, 1)) + "]" + str(pas_id) + "-PRI-" + str(pri) + "-FROM-" +
                str(from_floor) + "-TO-" + str(to_floor) + "\n")
        )


def atomic_sche_gen(lift_id, speed, to_floor):
    with open(file_name, 'a') as f:
        f.write(
            str("[" + str(round(time, 1)) + "]SCHE-" + str(lift_id) + "-" +
                str(round(speed, 1)) + "-" + str(to_floor) + "\n")
        )


def chaos_gen():
    global pas_id, time
    s_len = parameter['STD_LEN']
    s_range = parameter['STD_RANGE']
    _len = random.randint(s_len - s_range, s_len + s_range)
    for i in range(_len):
        pri = random.randint(1, 100)
        from_floor = random.choice(floor_name)
        to_floor = random.choice(floor_name)
        while to_floor == from_floor:
            to_floor = random.choice(floor_name)
        atomic_mono_gen(pri, from_floor, to_floor)
        pas_id += 1


def time_little_dif_gen():
    global pas_id, time
    s_len = parameter['STD_LEN']
    s_range = parameter['STD_RANGE']
    time_dif = parameter['TIME_DIF']
    _len = random.randint(s_len - s_range, s_len + s_range)

    for i in range(_len):
        pri = random.randint(1, 100)
        from_floor = random.choice(floor_name)
        to_floor = random.choice(floor_name)
        while to_floor == from_floor:
            to_floor = random.choice(floor_name)
        atomic_mono_gen(pri, from_floor, to_floor)
        pas_id += 1
        time += random.choice(time_dif)


def time_large_dif_gen():
    global pas_id, time
    s_len = parameter['STD_LEN']
    s_range = parameter['STD_RANGE']
    time_dif = parameter['TIME_DIF']
    _len = random.randint(s_len - s_range, s_len + s_range)
    _times = parameter['TIME_TIMES']

    for i in range(_len):
        pri = random.randint(1, 100)
        from_floor = random.choice(floor_name)
        to_floor = random.choice(floor_name)
        while to_floor == from_floor:
            to_floor = random.choice(floor_name)
        atomic_mono_gen(pri, from_floor, to_floor)
        pas_id += 1
        for j in range(_times):
            time += random.choice(time_dif)


def time_large_dif_burst_gen():
    global pas_id, time
    s_len = parameter['BURST_LEN']
    s_range = parameter['BURST_RANGE']
    time_dif = parameter['TIME_DIF']
    _len = random.randint(s_len - s_range, s_len + s_range)
    _times = parameter['TIME_TIMES']
    for i in range(_len):
        pri = random.randint(1, 100)
        from_floor = random.choice(floor_name)
        to_floor = random.choice(floor_name)
        while to_floor == from_floor:
            to_floor = random.choice(floor_name)
        atomic_mono_gen(pri, from_floor, to_floor)
        pas_id += 1
        for j in range(_times):
            time += random.choice(time_dif)


def mono_from_burst_gen():
    global pas_id, time
    s_len = parameter['BURST_LEN']
    s_range = parameter['BURST_RANGE']
    _len = random.randint(s_len - s_range, s_len + s_range)
    from_floor = random.choice(floor_name)
    for i in range(_len):
        pri = random.randint(1, 100)
        to_floor = random.choice(floor_name)
        while to_floor == from_floor:
            to_floor = random.choice(floor_name)
        atomic_mono_gen(pri, from_floor, to_floor)
        pas_id += 1


def mono_to_burst_gen():
    global pas_id, time
    s_len = parameter['BURST_LEN']
    s_range = parameter['BURST_RANGE']
    _len = random.randint(s_len - s_range, s_len + s_range)
    to_floor = random.choice(floor_name)
    for i in range(_len):
        pri = random.randint(1, 100)
        from_floor = random.choice(floor_name)
        while to_floor == from_floor:
            to_floor = random.choice(floor_name)
        atomic_mono_gen(pri, from_floor, to_floor)
        pas_id += 1


def chaos_burst_gen():
    global pas_id, time
    s_len = parameter['BURST_LEN']
    s_range = parameter['BURST_RANGE']
    _len = random.randint(s_len - s_range, s_len + s_range)
    for i in range(_len):
        pri = random.randint(1, 100)
        from_floor = random.choice(floor_name)
        to_floor = random.choice(floor_name)
        while to_floor == from_floor:
            to_floor = random.choice(floor_name)
        atomic_mono_gen(pri, from_floor, to_floor)
        pas_id += 1


def thorough_burst_gen():
    global pas_id, time
    s_len = parameter['BURST_LEN']
    s_range = parameter['BURST_RANGE']
    _len = random.randint(s_len - s_range, s_len + s_range)
    for i in range(_len):
        pri = random.randint(1, 100)
        if random.random() < 0.5:
            from_floor = floor_name[random.randint(0, 1)]
            to_floor = floor_name[-1 - random.randint(0, 1)]
        else:
            from_floor = floor_name[-1 - random.randint(0, 1)]
            to_floor = floor_name[random.randint(0, 1)]
        atomic_mono_gen(pri, from_floor, to_floor)
        pas_id += 1


def std_sche_gen():
    global pas_id, time, lift_id_pool, floor_name, predicted_time, sche_floor_name, speed_pool
    s_len = parameter['STD_LEN']
    s_range = parameter['STD_RANGE']
    chance_max = parameter['SCHE_SUMMON_CHANCE_MAX']

    _len = random.randint(s_len - s_range, s_len + s_range)
    sche_pos = random.randint(1, _len - 2)
    for i in range(_len):
        flag = False
        if i == sche_pos:
            for _ in range(chance_max):
                to_floor = random.choice(sche_floor_name)
                sche_id = random.choice(lift_id_pool)
                speed = random.choice(speed_pool)
                if predicted_time[sche_id] > time:
                    continue
                else:
                    predicted_time[sche_id] = time + speed * len(floor_name) + 2.0
                    print(predicted_time)
                    atomic_sche_gen(sche_id, speed, to_floor)
                    flag = True
                    break
        if flag:
            continue
        pri = random.randint(1, 100)
        from_floor = random.choice(floor_name)
        to_floor = random.choice(floor_name)
        while to_floor == from_floor:
            to_floor = random.choice(floor_name)
        atomic_mono_gen(pri, from_floor, to_floor)
        pas_id += 1


def restricted_sche_gen():
    global pas_id, time, lift_id_pool, floor_name, predicted_time, sche_floor_name, speed_pool
    s_len = parameter['STD_LEN']
    s_range = parameter['STD_RANGE']
    chance_max = parameter['SCHE_SUMMON_CHANCE_MAX']

    _len = random.randint(s_len - s_range, s_len + s_range)
    sche_pos = random.randint(1, _len - 2)
    sche_id = sche_id_left_pool.pop(1)
    for i in range(_len):
        flag = False
        if i == sche_pos:
            for _ in range(chance_max):
                speed = random.choice(speed_pool)
                to_floor = random.choice(sche_floor_name)
                if predicted_time[sche_id] > time:
                    continue
                else:
                    predicted_time[sche_id] = time + speed * len(floor_name) + 2.0
                    atomic_sche_gen(sche_id, speed, to_floor)
                    flag = True
                    break
        if flag:
            continue
        else:
            sche_id_left_pool.append(sche_id)
        pri = random.randint(1, 100)
        from_floor = random.choice(floor_name)
        to_floor = random.choice(floor_name)
        while to_floor == from_floor:
            to_floor = random.choice(floor_name)
        atomic_mono_gen(pri, from_floor, to_floor)
        pas_id += 1


def fin_gen(req):
    for i in req:
        if i == 0:
            chaos_gen()
        elif i == 1:
            time_little_dif_gen()
        elif i == 2:
            time_large_dif_gen()
        elif i == 3:
            time_large_dif_burst_gen()
        elif i == 4:
            mono_from_burst_gen()
        elif i == 5:
            mono_to_burst_gen()
        elif i == 6:
            chaos_burst_gen()
        elif i == 7:
            thorough_burst_gen()
        elif i == 8:
            std_sche_gen()
        elif i == 9:
            restricted_sche_gen()
