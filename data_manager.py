from typing import List, Dict
import json
import os
import shutil

from models import DataItem

'''
Need to implement validation Check algorithm
'''


class DataManager:

    def __init__(self):
        self.item_id_list: List[int] = []
        self.items: Dict[int, DataItem] = {}
        self.saved = True

    def get_item_id_list(self, include_status=False):
        if not include_status:
            return self.item_id_list
        ret_list = []
        for item_id in self.item_id_list:
            ret_list.append([item_id, self.items[item_id].status])
        return ret_list

    def get_item(self, item_id: int) -> Dict:
        if item_id not in self.items:
            raise LookupError(f"item_id {item_id} does not existed.")
        return self.items[item_id].get()

    def add_item(self) -> int:
        self.item_id_list.sort()
        new_item_id = self.item_id_list[-1] + 1 if self.item_id_list else 0
        self.item_id_list.append(new_item_id)
        self.items[new_item_id] = DataItem(new_item_id, status="added")
        self.saved = False
        return new_item_id

    def update_item(self, item_id: int, input_text: str, output_text: str) -> bool:
        if item_id not in self.items:
            raise LookupError(f"item_id {item_id} does not existed.")

        if self.items[item_id].update(input_text, output_text):
            self.saved = False
        return True

    def delete_item(self, item_id: int):
        if item_id not in self.items:
            raise LookupError(f"item_id {item_id} does not existed.")
        self.items[item_id].delete()
        self.saved = False
        return True

    def load_data(self, data_path: str) -> bool:
        if not os.path.isfile(data_path):
            return False

        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item_id, item in enumerate(data):
            self.item_id_list.append(item_id)
            self.items[item_id] = DataItem(item_id, item["input"], item["output"])
        return True

    def get_status_diff(self):
        status_diff_list = []
        for item_id in self.item_id_list:
            if self.items[item_id].status != "normal":
                status_diff_list.append([item_id, self.items[item_id].status])
        return status_diff_list

    def save_data(self) -> bool:
        status_diff = self.get_status_diff()

        tmp_buffer = {}
        for item_id, status in status_diff:
            if status == "deleted":
                tmp_buffer[item_id] = self.items[item_id]
                self.item_id_list.remove(item_id)
                del self.items[item_id]
            elif status == "changed":
                tmp_buffer[item_id] = "changed"
                self.items[item_id].apply()
            else:
                tmp_buffer[item_id] = "<add>"
                self.items[item_id].apply()

        try:
            with open('tmp.json', 'w', encoding='utf-8') as f:
                f.write("[\n")
                for idx, (_, item) in enumerate(sorted(self.items.items(), key=lambda x: x[0])):
                    json_lines = json.dumps(item.export(), ensure_ascii=False, indent=2).split("\n")
                    for line_idx, line in enumerate(json_lines):
                        if line_idx < len(json_lines)-1:
                            f.write(f"  {line}\n")
                        else:
                            f.write(f"  {line}")
                    if idx < len(self.items.keys())-1:
                        f.write(",\n")
                    else:
                        f.write("\n")
                f.write("]")
            shutil.move("tmp.json", "data.json")
            tmp_buffer.clear()
            self.saved = True
            return True
        except Exception as e:
            # Todo: Need to implement original data recovery logic
            print(e)
            tmp_buffer.clear()
            return False
