import json
import random

file_name: str = "stdout.txt"
time: float = 0.0


# created by Gavinaurora


class Generator:
    def __init__(self):
        # 提前从配置中提取高频参数
        self.parameter = json.load(open('config.json', 'r', encoding="utf-8"))
        # 初始化类属性（直接从 parameter 提取）
        self.pas_id = self.parameter['INIT_PAS_ID']
        self.lift_id_pool = self.parameter['LIFT_ID'].copy()
        self.available_sche_id_pool = self.lift_id_pool.copy()
        self.floor_name = self.parameter['FLOOR_NAME'].copy()
        self.sche_floor_name = self.parameter['SCHE_NAME'].copy()
        self.speed_pool = self.parameter['SPEED'].copy()
        self.sche_id_left_pool = self.parameter['LIFT_ID'].copy()
        self.earliest_sche_time: {int: float} = {}
        self.exchange_floors = []
        self.earliest_update_time = {}

        # 设置全局初始时间
        global time
        time = self.parameter['TIME']  # 初始化全局 time

        # 参数快捷访问（减少后续字典访问）
        self.std_len = self.parameter['STD_LEN']
        self.std_range = self.parameter['STD_RANGE']
        self.time_dif = self.parameter['TIME_DIF']
        self.burst_len = self.parameter['BURST_LEN']
        self.burst_range = self.parameter['BURST_RANGE']
        self.time_times = self.parameter['TIME_TIMES']
        self.contents: list[str] = []
        # 打乱初始池
        random.shuffle(self.lift_id_pool)
        random.shuffle(self.sche_id_left_pool)
        random.shuffle(self.available_sche_id_pool)
        # sche 时间限制
        for lift_id in self.lift_id_pool:
            self.earliest_sche_time[lift_id] = 0.0
            self.earliest_update_time[lift_id] = 0.0

    def _write_to_contents(self, content: str) -> None:
        """统一文件写入操作"""
        self.contents.append(content)

    def _random_unique_floors(self) -> tuple[str, str]:
        """生成不重复的起始/目标楼层"""
        from_floor = random.choice(self.floor_name)
        to_floor = random.choice(self.floor_name)
        while to_floor == from_floor:
            to_floor = random.choice(self.floor_name)
        return from_floor, to_floor

    def _atomic_mono_gen(self, pri: int, from_floor: str, to_floor: str) -> None:
        global time
        content = f"[{round(time, 1):.1f}]{self.pas_id}-PRI-{pri}-FROM-{from_floor}-TO-{to_floor}\n"
        self._write_to_contents(content)

    def _base_mono_gen(
            self, add_time: bool = False, times: int = 1, burst_target: str = None, vol: str = 'std',
            minimum_time_add: float = 0.0, chosen_floor: str = None
    ) -> None:
        """
        通用生成乘客请求的基函数
        - add_time: 是否增加时间
        - times: 时间增加的次数
        - burst_target: 指定爆发的楼层类型 ('from' 或 'to')
        """
        global time
        fixed_time = time + minimum_time_add + 0.001
        if vol == 'std':
            _len = random.randint(self.std_len - self.std_range, self.std_len + self.std_range)
        elif vol == 'burst':
            _len = random.randint(self.burst_len - self.burst_range, self.burst_len + self.burst_range)
        else:
            _len = 5
        # 处理特定爆发场景
        fixed_floor = None
        if burst_target == 'from':
            if chosen_floor is None:
                fixed_floor = random.choice(self.floor_name)
            else:
                fixed_floor = chosen_floor
        elif burst_target == 'to':
            if chosen_floor is None:
                fixed_floor = random.choice(self.floor_name)
            else:
                fixed_floor = chosen_floor
        for _ in range(_len):
            pri = random.randint(1, 100)
            if burst_target:
                # 根据爆发类型生成楼层
                if burst_target == 'from':
                    from_floor = fixed_floor
                    to_floor = random.choice(self.floor_name)
                    while to_floor == from_floor:
                        to_floor = random.choice(self.floor_name)
                else:
                    to_floor = fixed_floor
                    from_floor = random.choice(self.floor_name)
                    while from_floor == to_floor:
                        from_floor = random.choice(self.floor_name)
            else:
                from_floor, to_floor = self._random_unique_floors()  # 使用统一方法生成楼层
            self._atomic_mono_gen(pri, from_floor, to_floor)
            self.pas_id += 1
            # 时间处理逻辑
            if add_time:
                for j in range(times):
                    time += random.choice(self.time_dif)
        if add_time and time < fixed_time:
            time = fixed_time

    def _chaos_gen(self) -> None:
        """基础随机生成"""
        self._base_mono_gen()

    def _time_little_dif_gen(self) -> None:
        """小时间差生成"""
        self._base_mono_gen(add_time=True)

    def _time_large_dif_gen(self) -> None:
        """大时间差生成"""
        self._base_mono_gen(add_time=True, times=self.time_times)

    def _time_large_dif_burst_gen(self) -> None:
        """爆发性大时间差生成"""
        self._base_mono_gen(add_time=True, times=self.time_times, vol='burst')

    def _mono_from_burst_gen(self) -> None:
        """固定起始楼层爆发生成"""
        self._base_mono_gen(burst_target='from', vol='burst')

    def _mono_to_burst_gen(self) -> None:
        """固定目标楼层爆发生成"""
        self._base_mono_gen(burst_target='to', vol='burst')

    def _chaos_burst_gen(self) -> None:
        """随机爆发生成"""
        self._base_mono_gen(vol='burst')

    def _schedule_base(self, restricted: bool = False) -> None:
        """调度生成的基函数"""
        global time
        if len(self.available_sche_id_pool) == 0:
            return
        chance_max = self.parameter['SCHE_SUMMON_CHANCE_MAX']
        # 处理是否使用受限调度
        sche_id = None
        if restricted:
            sche_id = self.sche_id_left_pool.pop(0) if len(self.sche_id_left_pool) > 0 else None
        selected_id = 0
        success = False
        for _ in range(chance_max):
            to_floor = random.choice(self.sche_floor_name)
            speed = random.choice(self.speed_pool)
            selected_id = sche_id if restricted else random.choice(self.available_sche_id_pool)

            if selected_id is None:
                continue
            if self.earliest_sche_time[selected_id] > time:
                continue
            else:
                self.earliest_sche_time[selected_id] = time + speed * len(self.floor_name) + 2.0
                self._atomic_sche_gen(selected_id, speed, to_floor)
                success = True
                break
        if success:
            self.earliest_update_time[selected_id] = time + 8.0
            return
        elif restricted:
            self.sche_id_left_pool.append(sche_id)
        print("不存在合法的sche请求！")

    def _atomic_sche_gen(self, lift_id: int, speed: float, to_floor: str) -> None:
        global time
        content = f"[{time:.1f}]SCHE-{lift_id}-{speed:.1f}-{to_floor}\n"
        self._write_to_contents(content)

    def _std_sche_gen(self) -> None:
        """标准调度生成"""
        self._schedule_base()

    def _restricted_sche_gen(self) -> None:
        """受限制调度生成"""
        self._schedule_base(restricted=True)

    def _thorough_burst_gen(self) -> None:
        """全方向爆发生成（极端场景）"""
        _len = random.randint(self.burst_len - self.burst_range, self.burst_len + self.burst_range)
        for _ in range(_len):
            pri = random.randint(1, 100)
            if random.random() < 0.5:
                from_floor = self.floor_name[random.randint(0, 1)]
                to_floor = self.floor_name[-1 - random.randint(0, 1)]
            else:
                from_floor = self.floor_name[-1 - random.randint(0, 1)]
                to_floor = self.floor_name[random.randint(0, 1)]
            self._atomic_mono_gen(pri, from_floor, to_floor)
            self.pas_id += 1

    def _all_restricted_sche_gen(self) -> None:
        """将所有可能的调度请求生成（极端场景）"""
        global time
        chance_max = self.parameter['SCHE_SUMMON_CHANCE_MAX']
        for selected_id in self.lift_id_pool:
            for _ in range(chance_max):
                to_floor = random.choice(self.sche_floor_name)
                speed = random.choice(self.speed_pool)
                if selected_id is None:
                    continue
                if self.earliest_sche_time[selected_id] > time:
                    continue
                else:
                    self.earliest_sche_time[selected_id] = time + speed * len(self.floor_name) + 2.0
                    self.earliest_update_time[selected_id] = time + 8.0
                    self._atomic_sche_gen(selected_id, speed, to_floor)
                    break

    def _void_time_diff(self):
        """+8.0s"""
        global time
        time = time + 8.0

    def _remove_updated_sche(self, remove: int) -> None:
        """清除掉被更新的电梯的调度请求的合法性"""
        self.sche_id_left_pool = list(filter(lambda i: i != remove, self.sche_id_left_pool))
        self.available_sche_id_pool = list(filter(lambda i: i != remove, self.available_sche_id_pool))

    def _time_guaranteed_dif_gen(self) -> None:
        """至少时间差8s的大时间差生成"""
        self._base_mono_gen(add_time=True, times=self.time_times, minimum_time_add=4.0)
        self._base_mono_gen(add_time=True, times=self.time_times, minimum_time_add=4.0)

    def _atomic_update_gen(self, upper_lift: int, lower_lift: int, to_floor: str) -> None:
        """生成一条更新指令"""
        global time
        content = f"[{time:.1f}]UPDATE-{upper_lift}-{lower_lift}-{to_floor}\n"
        self._write_to_contents(content)

    def _upper_lower(self) -> (int, int):
        global time
        chance_max = self.parameter['SCHE_SUMMON_CHANCE_MAX']
        j: int = 0
        upper_lift: int = 0
        lower_lift: int = 0
        flag: bool = False
        for i in range(chance_max):
            j = random.randint(0, len(self.available_sche_id_pool) - 1)
            upper_lift = self.available_sche_id_pool[j]
            print(self.earliest_sche_time[upper_lift])
            if self.earliest_sche_time[upper_lift] <= time:
                flag = False
                break
            else:
                flag = True
        for i in range(chance_max):
            k = random.randint(0, len(self.available_sche_id_pool) - 1)
            lower_lift = self.available_sche_id_pool[k]
            if j != k and self.earliest_sche_time[lower_lift] <= time:
                flag = False
                break
            else:
                flag = True
        if flag:
            print("无可用数据")
            return None, None
        else:
            return upper_lift, lower_lift

    def _update_base(self, exchange_floor: str, complete: bool = False) -> None:
        """更新生成的基函数"""
        global time
        if len(self.available_sche_id_pool) < 2:
            print("没有可用的update电梯！")
            return
        if complete:
            while len(self.available_sche_id_pool) > 1:
                upper_lift, lower_lift = self._upper_lower()
                if upper_lift is None:
                    return
                self._remove_updated_sche(upper_lift)
                self._remove_updated_sche(lower_lift)
                self._atomic_update_gen(upper_lift, lower_lift, exchange_floor)
        else:
            upper_lift, lower_lift = self._upper_lower()
            if upper_lift is None:
                return
            self._remove_updated_sche(upper_lift)
            self._remove_updated_sche(lower_lift)
            self._atomic_update_gen(upper_lift, lower_lift, exchange_floor)

    def _std_update_gen(self) -> None:
        """标准生成1条更新"""
        exchange_floor = random.choice(self.sche_floor_name)
        self.exchange_floors.append(exchange_floor)
        self._update_base(exchange_floor)

    def _all_update_gen(self) -> None:
        """生成所有可用更新"""
        exchange_floor = random.choice(self.sche_floor_name)
        self.exchange_floors.append(exchange_floor)
        self._update_base(exchange_floor, True)

    def _update_from_gen(self) -> None:
        """固定有交换的起始楼层爆发生成"""
        if len(self.exchange_floors) == 0:
            return
        chosen_floor = random.choice(self.exchange_floors)
        self._base_mono_gen(burst_target='from', vol='burst', chosen_floor=chosen_floor)

    def _update_to_gen(self) -> None:
        """固定有交换的终点楼层爆发生成"""
        if len(self.exchange_floors) == 0:
            return
        chosen_floor = random.choice(self.exchange_floors)
        self._base_mono_gen(burst_target='to', vol='burst', chosen_floor=chosen_floor)

    def fin_gen(self, req: list) -> None:
        """总控生成函数（保持原分派逻辑）"""
        for req_type in req:
            _method = {
                0: self._chaos_gen,
                1: self._time_little_dif_gen,
                2: self._time_large_dif_gen,
                3: self._time_large_dif_burst_gen,
                4: self._mono_from_burst_gen,
                5: self._mono_to_burst_gen,
                6: self._chaos_burst_gen,
                7: self._thorough_burst_gen,
                8: self._std_sche_gen,
                9: self._restricted_sche_gen,
                10: self._all_restricted_sche_gen,
                11: self._time_guaranteed_dif_gen,
                12: self._void_time_diff,
                13: self._std_update_gen,
                14: self._all_update_gen,
                15: self._update_from_gen,
                16: self._update_to_gen
            }[req_type]
            _method()
        for content in self.contents:
            with open(file_name, mode='a', encoding='utf-8') as f:
                f.write(content)
        self.contents.clear()
