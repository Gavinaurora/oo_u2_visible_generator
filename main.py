import json
import tkinter as tk
import os
from typing import Dict, List, Any
import generator
import random

rng = generator.Generator()


# pyinstaller -F G:\OO_U2_RNG\main.py -i G:\OO_U2_RNG\the_d6.ico -n oo_gen_v0.2.2


class GUIApplication:
    def __init__(self, config_path: str = "config.json"):
        # 初始化配置和运行时数据
        self.config: Dict[str, Any] = self._load_config(config_path)
        self.running_time: float = 1.0
        self.ui_components: Dict[str, Any] = {}
        self.current_functions: List[str] = []
        self.function_queue: List[int] = []

        # GUI初始化
        self.root = self._create_root_window()
        self._create_menu()
        self._create_side_panel()
        self._create_function_list()
        self._create_output_elements()
        self._create_status_bar()
        with open("stdout.txt", "w"):
            pass

        # 初始化RNG模块
        rng.__init__()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _create_root_window(self) -> tk.Tk:
        """创建主窗口"""
        root = tk.Tk()
        root.title("OO U2 数据生成器 hw6版本 by Gavinaurora")
        root.iconbitmap("the_d6.ico")
        root.geometry("1000x750")
        root.resizable(False, False)
        return root

    def _create_side_panel(self):
        """创建左侧控制面板"""
        control_buttons = [
            ("加入选定策略", self._add_selected_function),
            ("移除最后的策略", self._remove_last_function),
            ("移除所有的策略", self._clear_all_functions),
            ("显示所选策略介绍", self._show_selected_info),
            ("重置数据生成器", self._reset_system),
            ("获取某些特别信息", self._get_dialogue)
        ]

        for idx, (text, command) in enumerate(control_buttons):
            btn = tk.Button(
                self.root,
                text=text,
                width=15,
                height=2,
                command=command
            )
            btn.place(x=0, y=idx * 30, height=30, width=130)

    def _create_function_list(self):
        """创建功能列表区域"""
        self.ui_components["function_list"] = tk.Listbox(self.root)
        for idx, func in enumerate(self.config["FUNC_LIST"]):
            self.ui_components["function_list"].insert(idx, func)
        self.ui_components["function_list"].place(x=200, y=0, width=200, height=300)
        # 显示已选功能的区域
        self.ui_components["selected_func_var"] = tk.StringVar()
        label = tk.Label(
            self.root,
            bg="white",
            fg="black",
            font=("Arial", 12),
            width=30,
            textvariable=self.ui_components["selected_func_var"],
            justify="left"
        )
        label.place(x=700, y=0)

    def _create_output_elements(self):
        """创建输出相关的界面元素"""
        # 日志输出区域
        self.ui_components["output_text"] = tk.Text(
            self.root,
            wrap=tk.WORD,
            font=("Arial", 12)
        )
        self.ui_components["output_text"].place(x=0, y=310, height=260, width=400)
        # 生成时间控制区域
        time_control_frame = tk.Frame(self.root)
        time_control_frame.place(x=0, y=580)
        # 时间调节滑块
        self.ui_components["time_scale"] = tk.Scale(
            time_control_frame,
            label="下一条指令的时间",
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            length=400,
            showvalue=False,
            tickinterval=5,
            resolution=0.1,
            command=self._update_time
        )
        self.ui_components["time_scale"].grid(row=0, column=0)
        # 时间显示标签
        self.ui_components["time_display"] = tk.Label(
            time_control_frame,
            bg="white",
            fg="black",
            width=10,
            text=f"{self.running_time}s"
        )
        self.ui_components["time_display"].grid(row=0, column=1)
        # 生成按钮
        generate_single_btn = tk.Button(
            self.root,
            text="生成单条数据",
            width=15,
            height=2,
            command=self._generate_data
        )
        generate_single_btn.place(x=870, y=670, height=30, width=130)
        generate_multi_btn = tk.Button(
            self.root,
            text="生成多条数据",
            width=15,
            height=2,
            command=self._generate_multi_data
        )
        generate_multi_btn.place(x=870, y=700, height=30, width=130)

    def _create_menu(self):
        """创建菜单系统"""
        menu_bar = tk.Menu(self.root)
        # 文件菜单
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="退出", command=self.root.quit)
        menu_bar.add_cascade(label="文件", menu=file_menu)
        # 设置菜单
        setting_menu = tk.Menu(menu_bar, tearoff=0)
        setting_menu.add_command(label="参数设置", command=self._show_settings)
        menu_bar.add_cascade(label="设置", menu=setting_menu)
        self.root.config(menu=menu_bar)

    def _create_status_bar(self):
        """创建状态栏"""
        self.ui_components["status_var"] = tk.StringVar()
        self.ui_components["status_var"].set("你好，欢迎使用我的可视化数据生成器！")

        status_label = tk.Label(
            self.root,
            textvariable=self.ui_components["status_var"],
            width=85,
            height=2,
            bg="white",
            fg="black",
            font=("Arial", 12),
            anchor="w"
        )
        status_label.place(x=0, y=690)

    def _update_selected_display(self):
        """更新已选功能显示"""
        display_text = "\n".join(self.current_functions)
        self.ui_components["selected_func_var"].set(display_text)

    def _add_selected_function(self):
        """添加选中的功能到队列"""
        try:
            selection = self.ui_components["function_list"].get(
                self.ui_components["function_list"].curselection())
        except tk.TclError:
            self.ui_components["status_var"].set("ERROR! 未选择任何策略")
            return
        # 获取配置信息
        func_index = self.config["FUNC_LIST"].index(selection)
        max_queue_length = 20
        # 更新状态信息
        if len(self.function_queue) >= max_queue_length:
            self.ui_components["status_var"].set("WARNING! 队列已达安全容，但是可以正常生成")
        else:
            self.ui_components["status_var"].set(
                self.config["FUNC_DESCRIPTION"][func_index])
        # 添加到队列
        self.current_functions.append(selection)
        self.function_queue.append(func_index)
        self._update_selected_display()

    def _remove_last_function(self):
        """移除最后添加的功能"""
        if not self.function_queue:
            self.ui_components["status_var"].set("ERROR! 队列已空")
            return
        self.function_queue.pop()
        self.current_functions.pop()
        self._update_selected_display()
        self.ui_components["status_var"].set("已移除最后添加的策略")

    def _clear_all_functions(self):
        """清空所有选中功能"""
        self.function_queue.clear()
        self.current_functions.clear()
        self._update_selected_display()
        self.ui_components["status_var"].set("已清空全部策略队列")

    def _show_selected_info(self):
        """显示当前选中功能的详细信息"""
        try:
            selection = self.ui_components["function_list"].get(
                self.ui_components["function_list"].curselection())
        except tk.TclError:
            self.ui_components["status_var"].set("WARNING! 未选择有效策略队列")
            return
        func_index = self.config["FUNC_LIST"].index(selection)
        self.ui_components["status_var"].set(
            self.config["FUNC_DESCRIPTION"][func_index])

    def _get_dialogue(self):
        """显示对话"""
        if random.random() < 0.95:
            string: str = random.choice(self.config['DIALOGUE'])
        else:
            string: str = random.choice(self.config['BONUS'])
        self.ui_components["status_var"].set(string)

    def _generate_data(self, output_file="stdout.txt", out=True):
        """执行数据生成操作"""
        if not self.function_queue:
            self.ui_components["status_var"].set("WARNING! 空队列无法生成数据")
            return
        # 调用RNG模块生成数据
        rng.fin_gen(self.function_queue)
        if out:
            # 更新界面状态
            self.ui_components["status_var"].set("数据生成成功！")
            self.ui_components["time_display"].config(
                text=f"{round(generator.time, 1)}s")
            self.ui_components["time_scale"].set(generator.time)
            # 加载生成结果到文本框
            self.ui_components["output_text"].delete("1.0", tk.END)
            with open(output_file, "r", encoding="utf-8") as f:
                self.ui_components["output_text"].insert(tk.END, f.read())

    def _generate_multi_data(self):
        if not self.function_queue:
            self.ui_components["status_var"].set("WARNING! 空队列无法生成数据")
            return
        prefix: str = self.config["MULTI_OUTPUT_PREFIX"]
        times: int = self.config["MULTI_OUTPUT_TIMES"]
        saved_time: float = generator.time
        for i in range(times):
            rng.__init__()
            with open(generator.file_name, "w", encoding="utf-8") as f:
                f.write("")
            generator.time = saved_time
            name: str = 'out_files/' + prefix + str(i) + '.txt'
            self._generate_data(out=False)
            with open(generator.file_name, 'r', encoding='utf-8') as source:
                with open(name, "w", encoding='utf-8') as target:
                    for line in source:
                        target.write(line)
        self.ui_components["status_var"].set("多条数据生成完成。输出的文件在./outfiles文件中。")

    def _reset_system(self):
        """执行系统重置操作"""
        # 清空文件内容
        with open(generator.file_name, "w", encoding="utf-8") as f:
            f.write("")
        folder_path = "./out_files"  # 替换为你的文件夹路径
        # 遍历文件夹内文件并删除
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"删除失败 {file_path}: {str(e)}")
        # 重置界面状态
        self.ui_components["output_text"].delete("1.0", tk.END)
        self.function_queue.clear()
        self.current_functions.clear()
        self._update_selected_display()
        self.ui_components["time_display"].config(text="1.0s")
        self.ui_components["time_scale"].set(1.0)

        # 重新初始化RNG模块
        rng.__init__()
        self.ui_components["status_var"].set("生成器已经重置完成。")

    def _update_time(self, value: str):
        """更新时间参数"""
        self.running_time = float(value)
        self.ui_components["time_display"].config(
            text=f"{self.running_time}s")
        generator.time = self.running_time

    def _show_settings(self):
        """显示参数设置窗口"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("参数设置")
        settings_window.geometry("800x620")
        settings_window.grab_set()


if __name__ == "__main__":
    app = GUIApplication()
    tk.mainloop()
