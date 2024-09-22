import tkinter as tk
from tkinter import messagebox

from data_manager import DataManager


class GUIManager:

    def __init__(self):
        self.data_manager = DataManager()
        self.root = tk.Tk()
        self.root.title("JSON Editor")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.ui_table = {"item_btn_list": [], "edit_page": {}}

        self.current_item_id = None
        self.font_size = 12
        self.data_font_size = 12

        self.init_frame()
        self.load_data()
        self.list_items()
        self.main_page()

    def init_frame(self):
        self.build_top_frame()
        self.build_left_frame()
        self.build_main_frame()

    def load_data(self):
        if not self.data_manager.load_data('data.json'):
            messagebox.showerror("파일 오류", "데이터 파일을 로드할 수 없습니다.")

    def build_top_frame(self, rebuild=False):
        if rebuild:
            self.ui_table["top_frame"].destroy()
        self.ui_table["top_frame"] = tk.Frame(self.root)
        self.ui_table["top_frame"].pack(side=tk.TOP, fill=tk.X, pady=(2, 20))
        new_button = tk.Button(
            self.ui_table["top_frame"], text="New",
            font=("Arial", self.font_size), padx=10, pady=5,
            command=self.new_item
        )
        new_button.pack(side=tk.LEFT, fill=tk.Y)
        save_button = tk.Button(
            self.ui_table["top_frame"], text="Save",
            font=("Arial", self.font_size), padx=10, pady=5,
            command=self.save
        )
        save_button.pack(side=tk.LEFT, fill=tk.Y)
        main_button = tk.Button(
            self.ui_table["top_frame"], text="Dashboard",
            font=("Arial", self.font_size), padx=10, pady=5,
            command=self.main_page
        )
        main_button.pack(side=tk.LEFT, fill=tk.Y)

    def build_left_frame(self, rebuild=False):
        if rebuild:
            self.ui_table["left_frame"].destroy()
        self.ui_table["left_frame"] = tk.Frame(self.root)
        self.ui_table["left_frame"].pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

    def build_main_frame(self, rebuild=False):
        if rebuild:
            self.ui_table["main_frame"].destroy()
        self.ui_table["main_frame"] = tk.Frame(self.root, width=1024, height=512)
        self.ui_table["main_frame"].pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.ui_table["main_frame"].pack_propagate(False)

    def list_items(self):
        for item_btn in self.ui_table["item_btn_list"]:
            item_btn.destroy()
        self.ui_table["item_btn_list"].clear()

        for idx, (item_id, status) in enumerate(self.data_manager.get_item_id_list(include_status=True)):
            if status == "normal":
                status_emoji = '✅'
            elif status == "deleted":
                status_emoji = '❌'
            elif status == "added":
                status_emoji = '🆕'
            else:
                status_emoji = '⚠️'
            item_text = f"{'⚫' if item_id == self.current_item_id else '︎'}Item {idx + 1} {status_emoji}"
            btn = tk.Button(
                self.ui_table["left_frame"],
                text=item_text,
                font=("Arial", self.font_size),
                padx=10, pady=5,
                command=lambda x=item_id: self.load_item(x)
            )
            btn.pack(fill=tk.X)
            self.ui_table["item_btn_list"].append(btn)

    def main_page(self):
        if self.current_item_id:
            self.apply_item()

        self.build_main_frame(rebuild=True)
        self.current_item_id = None
        self.list_items()
        main_label = tk.Label(
            self.ui_table["main_frame"], text="Welcome to json editor", font=("Arial", self.font_size)
        )
        main_label.pack()

    def load_item(self, item_id: int):
        if self.current_item_id:
            self.apply_item()

        item = self.data_manager.get_item(item_id)
        self.current_item_id = item_id
        self.list_items()
        self.build_main_frame(rebuild=True)

        input_label = tk.Label(self.ui_table["main_frame"], text="Input", font=("Arial", self.font_size))
        input_label.pack()
        self.ui_table["edit_page"]["input_text"] = tk.Text(
            self.ui_table["main_frame"], font=("Arial", self.data_font_size), height=10
        )
        self.ui_table["edit_page"]["input_text"].pack(fill=tk.X, expand=True)
        self.ui_table["edit_page"]["input_text"].insert(tk.END, item['input'])

        output_label = tk.Label(self.ui_table["main_frame"], text="Output", font=("Arial", self.font_size))
        output_label.pack()
        self.ui_table["edit_page"]["output_text"] = tk.Text(
            self.ui_table["main_frame"], font=("Arial", self.data_font_size), height=10
        )
        self.ui_table["edit_page"]["output_text"].pack(fill=tk.X, expand=True)
        self.ui_table["edit_page"]["output_text"].insert(tk.END, item['output'])

        button_frame = tk.Frame(self.ui_table["main_frame"])
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        rollback_button = tk.Button(
            button_frame, text="Rollback",
            font=("Arial", self.font_size), padx=10, pady=5,
            command=self.apply_item
        )
        rollback_button.pack(side=tk.LEFT, padx=(0, 5), pady=5)
        delete_button = tk.Button(
            button_frame, text="Delete",
            font=("Arial", self.font_size), padx=10, pady=5,
            command=self.delete_item
        )
        delete_button.pack(side=tk.LEFT, pady=5)

    def apply_item(self):
        current_input = self.ui_table["edit_page"]["input_text"].get('1.0', tk.END).rstrip('\n')
        current_output = self.ui_table["edit_page"]["output_text"].get('1.0', tk.END).rstrip('\n')

        result = self.data_manager.update_item(self.current_item_id, current_input, current_output)
        self.list_items()
        if not result:
            messagebox.showinfo("데이터 연동 실패", "알 수 없는 오류가 발생했습니다.")

    def delete_item(self):
        if self.current_item_id is None:
            return

        result = self.data_manager.delete_item(self.current_item_id)
        if result:
            self.list_items()
            self.main_page()
        else:
            messagebox.showinfo("삭제 실패", "알 수 없는 오류가 발생했습니다.")

    def new_item(self):
        new_item_id = self.data_manager.add_item()
        self.list_items()
        self.load_item(new_item_id)

    def save(self):
        self.data_manager.save_data()
        self.list_items()

    def on_closing(self):
        if self.current_item_id:
            self.apply_item()

        if not self.data_manager.saved:
            result = messagebox.askyesno("종료", "종료하기 전에 변경사항을 저장하시겠습니까?")
            if result:
                self.data_manager.save_data()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
