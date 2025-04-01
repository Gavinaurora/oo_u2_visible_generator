import json
import random

# global variables
file_name: str = "stdout.txt"
time: float = 0.0


class Generator:
    def __init__(self):
        global file_name, time
        self.parameter: dict[str:any] = json.load(open('config.json', 'r', encoding="utf-8"))
        self.pas_id: int = self.parameter['INIT_PAS_ID']
        time = self.parameter['TIME']
        self.lift_id_pool: list[int] = self.parameter['LIFT_ID'].copy()
        self.floor_name: list[str] = self.parameter['FLOOR_NAME'].copy()
        self.sche_floor_name: list[str] = self.parameter['SCHE_NAME'].copy()
        self.speed_pool: list[float] = self.parameter['SPEED'].copy()
        self.sche_id_left_pool: list[int] = self.parameter['LIFT_ID'].copy()
        self.predicted_time: dict[int:float] = {}

        random.shuffle(self.lift_id_pool)
        random.shuffle(self.sche_id_left_pool)
        for i in self.lift_id_pool:
            self.predicted_time[i] = 0.0

    def atomic_mono_gen(self, pri, from_floor, to_floor):
        global file_name
        with open(file_name, 'a') as f:
            f.write(
                f"[{round(time, 1):.1f}]{self.pas_id}-PRI-{pri}-FROM-{from_floor}-TO-{to_floor}\n"
            )

    def atomic_sche_gen(self, lift_id, speed, to_floor):
        global file_name
        with open(file_name, 'a') as f:
            f.write(f"[{time:.1f}]SCHE-{lift_id}-{speed:.1f}-{to_floor}\n")

    def chaos_gen(self):
        global time
        s_len = self.parameter['STD_LEN']
        s_range = self.parameter['STD_RANGE']
        _len = random.randint(s_len - s_range, s_len + s_range)
        for i in range(_len):
            pri = random.randint(1, 100)
            from_floor = random.choice(self.floor_name)
            to_floor = random.choice(self.floor_name)
            while to_floor == from_floor:
                to_floor = random.choice(self.floor_name)
            self.atomic_mono_gen(pri, from_floor, to_floor)
            self.pas_id += 1

    def time_little_dif_gen(self):
        global time
        s_len = self.parameter['STD_LEN']
        s_range = self.parameter['STD_RANGE']
        time_dif = self.parameter['TIME_DIF']
        _len = random.randint(s_len - s_range, s_len + s_range)

        for i in range(_len):
            pri = random.randint(1, 100)
            from_floor = random.choice(self.floor_name)
            to_floor = random.choice(self.floor_name)
            while to_floor == from_floor:
                to_floor = random.choice(self.floor_name)
            self.atomic_mono_gen(pri, from_floor, to_floor)
            self.pas_id += 1
            time += random.choice(time_dif)

    def time_large_dif_gen(self):
        global time
        s_len = self.parameter['STD_LEN']
        s_range = self.parameter['STD_RANGE']
        time_dif = self.parameter['TIME_DIF']
        _len = random.randint(s_len - s_range, s_len + s_range)
        _times = self.parameter['TIME_TIMES']

        for i in range(_len):
            pri = random.randint(1, 100)
            from_floor = random.choice(self.floor_name)
            to_floor = random.choice(self.floor_name)
            while to_floor == from_floor:
                to_floor = random.choice(self.floor_name)
            self.atomic_mono_gen(pri, from_floor, to_floor)
            self.pas_id += 1
            for j in range(_times):
                time += random.choice(time_dif)

    def time_large_dif_burst_gen(self):
        global time
        s_len = self.parameter['BURST_LEN']
        s_range = self.parameter['BURST_RANGE']
        time_dif = self.parameter['TIME_DIF']
        _len = random.randint(s_len - s_range, s_len + s_range)
        _times = self.parameter['TIME_TIMES']

        for i in range(_len):
            pri = random.randint(1, 100)
            from_floor = random.choice(self.floor_name)
            to_floor = random.choice(self.floor_name)
            while to_floor == from_floor:
                to_floor = random.choice(self.floor_name)
            self.atomic_mono_gen(pri, from_floor, to_floor)
            self.pas_id += 1
            for j in range(_times):
                time += random.choice(time_dif)

    def mono_from_burst_gen(self):
        global time
        s_len = self.parameter['BURST_LEN']
        s_range = self.parameter['BURST_RANGE']
        _len = random.randint(s_len - s_range, s_len + s_range)
        from_floor = random.choice(self.floor_name)
        for i in range(_len):
            pri = random.randint(1, 100)
            to_floor = random.choice(self.floor_name)
            while to_floor == from_floor:
                to_floor = random.choice(self.floor_name)
            self.atomic_mono_gen(pri, from_floor, to_floor)
            self.pas_id += 1

    def mono_to_burst_gen(self):
        global time
        s_len = self.parameter['BURST_LEN']
        s_range = self.parameter['BURST_RANGE']
        _len = random.randint(s_len - s_range, s_len + s_range)
        to_floor = random.choice(self.floor_name)
        for i in range(_len):
            pri = random.randint(1, 100)
            from_floor = random.choice(self.floor_name)
            while to_floor == from_floor:
                to_floor = random.choice(self.floor_name)
            self.atomic_mono_gen(pri, from_floor, to_floor)
            self.pas_id += 1

    def chaos_burst_gen(self):
        global time
        s_len = self.parameter['BURST_LEN']
        s_range = self.parameter['BURST_RANGE']
        _len = random.randint(s_len - s_range, s_len + s_range)
        for i in range(_len):
            pri = random.randint(1, 100)
            from_floor = random.choice(self.floor_name)
            to_floor = random.choice(self.floor_name)
            while to_floor == from_floor:
                to_floor = random.choice(self.floor_name)
            self.atomic_mono_gen(pri, from_floor, to_floor)
            self.pas_id += 1

    def thorough_burst_gen(self):
        global time
        s_len = self.parameter['BURST_LEN']
        s_range = self.parameter['BURST_RANGE']
        _len = random.randint(s_len - s_range, s_len + s_range)
        for i in range(_len):
            pri = random.randint(1, 100)
            if random.random() < 0.5:
                from_floor = self.floor_name[random.randint(0, 1)]
                to_floor = self.floor_name[-1 - random.randint(0, 1)]
            else:
                from_floor = self.floor_name[-1 - random.randint(0, 1)]
                to_floor = self.floor_name[random.randint(0, 1)]
            self.atomic_mono_gen(pri, from_floor, to_floor)
            self.pas_id += 1

    def std_sche_gen(self):
        global time
        s_len = self.parameter['STD_LEN']
        s_range = self.parameter['STD_RANGE']
        chance_max = self.parameter['SCHE_SUMMON_CHANCE_MAX']

        _len = random.randint(s_len - s_range, s_len + s_range)
        sche_pos = random.randint(1, _len - 2)
        for i in range(_len):
            flag = False
            if i == sche_pos:
                for _ in range(chance_max):
                    to_floor = random.choice(self.sche_floor_name)
                    sche_id = random.choice(self.lift_id_pool)
                    speed = random.choice(self.speed_pool)
                    if self.predicted_time[sche_id] > time:
                        continue
                    else:
                        self.predicted_time[sche_id] = time + speed * len(self.floor_name) + 2.0
                        print(self.predicted_time)
                        self.atomic_sche_gen(sche_id, speed, to_floor)
                        flag = True
                        break
            if flag:
                continue
            pri = random.randint(1, 100)
            from_floor = random.choice(self.floor_name)
            to_floor = random.choice(self.floor_name)
            while to_floor == from_floor:
                to_floor = random.choice(self.floor_name)
            self.atomic_mono_gen(pri, from_floor, to_floor)
            self.pas_id += 1

    def restricted_sche_gen(self):
        global time
        s_len = self.parameter['STD_LEN']
        s_range = self.parameter['STD_RANGE']
        chance_max = self.parameter['SCHE_SUMMON_CHANCE_MAX']

        _len = random.randint(s_len - s_range, s_len + s_range)
        sche_pos = random.randint(1, _len - 2)
        sche_id = self.sche_id_left_pool.pop(1)
        for i in range(_len):
            flag = False
            if i == sche_pos:
                for _ in range(chance_max):
                    speed = random.choice(self.speed_pool)
                    to_floor = random.choice(self.sche_floor_name)
                    if self.predicted_time[sche_id] > time:
                        continue
                    else:
                        self.predicted_time[sche_id] = time + speed * len(self.floor_name) + 2.0
                        self.atomic_sche_gen(sche_id, speed, to_floor)
                        flag = True
                        break
            if flag:
                continue
            else:
                self.sche_id_left_pool.append(sche_id)
            pri = random.randint(1, 100)
            from_floor = random.choice(self.floor_name)
            to_floor = random.choice(self.floor_name)
            while to_floor == from_floor:
                to_floor = random.choice(self.floor_name)
            self.atomic_mono_gen(pri, from_floor, to_floor)
            self.pas_id += 1

    def fin_gen(self, req):
        for i in req:
            if i == 0:
                self.chaos_gen()
            elif i == 1:
                self.time_little_dif_gen()
            elif i == 2:
                self.time_large_dif_gen()
            elif i == 3:
                self.time_large_dif_burst_gen()
            elif i == 4:
                self.mono_from_burst_gen()
            elif i == 5:
                self.mono_to_burst_gen()
            elif i == 6:
                self.chaos_burst_gen()
            elif i == 7:
                self.thorough_burst_gen()
            elif i == 8:
                self.std_sche_gen()
            elif i == 9:
                self.restricted_sche_gen()
