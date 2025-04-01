import json
import random

# 保持全局变量不动
file_name: str = "stdout.txt"
time: float = 0.0


class Generator:
    def __init__(self):
        # 提前从配置中提取高频参数
        self.parameter = json.load(open('config.json', 'r', encoding="utf-8"))
        # 初始化类属性（直接从 parameter 提取）
        self.pas_id = self.parameter['INIT_PAS_ID']
        self.lift_id_pool = self.parameter['LIFT_ID'].copy()
        self.floor_name = self.parameter['FLOOR_NAME'].copy()
        self.sche_floor_name = self.parameter['SCHE_NAME'].copy()
        self.speed_pool = self.parameter['SPEED'].copy()
        self.sche_id_left_pool = self.parameter['LIFT_ID'].copy()
        self.predicted_time = {}

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
        # 打乱初始池
        random.shuffle(self.lift_id_pool)
        random.shuffle(self.sche_id_left_pool)
        for lift_id in self.lift_id_pool:
            self.predicted_time[lift_id] = 0.0

    def _write_to_file(self, content: str) -> None:
        """统一文件写入操作"""
        with open(file_name, 'a') as f:
            f.write(content)

    def _random_unique_floors(self) -> tuple[str, str]:
        """生成不重复的起始/目标楼层"""
        from_floor = random.choice(self.floor_name)
        to_floor = random.choice(self.floor_name)
        while to_floor == from_floor:
            to_floor = random.choice(self.floor_name)
        return from_floor, to_floor

    def _atomic_mono_gen(self, pri: int, from_floor: str, to_floor: str) -> None:
        global time  # 保留 global 声明以满足时间格式要求
        content = f"[{round(time, 1):.1f}]{self.pas_id}-PRI-{pri}-FROM-{from_floor}-TO-{to_floor}\n"
        self._write_to_file(content)

    def _atomic_sche_gen(self, lift_id: int, speed: float, to_floor: str) -> None:
        global time  # 准确记录全局时间
        content = f"[{time:.1f}]SCHE-{lift_id}-{speed:.1f}-{to_floor}\n"
        self._write_to_file(content)

    def _base_mono_gen(
            self, add_time: bool = False, times: int = 1, burst_target: str = None
    ) -> None:
        """
        通用生成乘客请求的基函数
        - add_time: 是否增加时间
        - times: 时间增加的次数
        - burst_target: 指定爆发的楼层类型 ('from' 或 'to')
        """
        global time  # 需要修改全局时间时保留 global
        _len = random.randint(self.std_len - self.std_range, self.std_len + self.std_range)
        # 处理特定爆发场景
        fixed_floor = None
        if burst_target == 'from':
            fixed_floor = random.choice(self.floor_name)
        elif burst_target == 'to':
            fixed_floor = random.choice(self.floor_name)
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
                for _ in range(times):
                    time += random.choice(self.time_dif)

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
        _len = random.randint(self.burst_len - self.burst_range, self.burst_len + self.burst_range)
        for _ in range(_len):
            self._base_mono_gen(add_time=True, times=self.time_times)

    def _mono_from_burst_gen(self) -> None:
        """固定起始楼层爆发生成"""
        self._base_mono_gen(burst_target='from')

    def _mono_to_burst_gen(self) -> None:
        """固定目标楼层爆发生成"""
        self._base_mono_gen(burst_target='to')

    def _chaos_burst_gen(self) -> None:
        """随机爆发生成"""
        self._base_mono_gen()

    def _schedule_base(self, restricted: bool = False) -> None:
        """调度生成的基函数"""
        global time
        _len = random.randint(self.std_len - self.std_range, self.std_len + self.std_range)
        sche_pos = random.randint(1, _len - 2)
        chance_max = self.parameter['SCHE_SUMMON_CHANCE_MAX']
        # 处理是否使用受限调度
        sche_id = None
        if restricted:
            sche_id = self.sche_id_left_pool.pop(0) if len(self.sche_id_left_pool) > 1 else None
        for i in range(_len):
            if i == sche_pos:
                success = False
                for _ in range(chance_max):
                    to_floor = random.choice(self.sche_floor_name)
                    speed = random.choice(self.speed_pool)
                    selected_id = sche_id if restricted else random.choice(self.lift_id_pool)

                    if selected_id is None:
                        continue
                    if self.predicted_time[selected_id] > time:
                        continue
                    else:
                        self.predicted_time[selected_id] = time + speed * len(self.floor_name) + 2.0
                        self._atomic_sche_gen(selected_id, speed, to_floor)
                        success = True
                        break
                if success:
                    continue
                elif restricted:
                    self.sche_id_left_pool.append(sche_id)
            # 生成普通乘客请求
            pri = random.randint(1, 100)
            from_floor, to_floor = self._random_unique_floors()
            self._atomic_mono_gen(pri, from_floor, to_floor)
            self.pas_id += 1

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
                if self.predicted_time[selected_id] > time:
                    continue
                else:
                    self.predicted_time[selected_id] = time + speed * len(self.floor_name) + 2.0
                    self._atomic_sche_gen(selected_id, speed, to_floor)
                    break

    def _fin_gen(self, req: list) -> None:
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
                10: self._all_restricted_sche_gen
            }[req_type]
            _method()
