from typing import Dict


class DataItem:
    def __init__(self,item_id, input_text='', output_text='',
                 input_changed_text='', output_changed_text='', status='normal'):
        self.item_id = item_id
        self.input = input_text
        self.output = output_text
        self.input_changed = input_changed_text
        self.output_changed = output_changed_text
        self.status = status

    def get(self) -> Dict[str, str]:
        if not self.input_changed:
            self.input_changed = self.input
        if not self.output_changed:
            self.output_changed = self.output

        return {"input": self.input_changed, "output": self.output_changed}

    def update(self, input_text: str, out_text: str) -> bool:
        if self.input == input_text and self.output == out_text:
            return False

        self.input_changed = input_text
        self.output_changed = out_text
        if not self.input and not self.output:
            self.status = "added"
        else:
            self.status = "changed"
        return True

    def delete(self) -> bool:
        if self.status == "deleted":
            return False
        self.status = "deleted"
        return True

    def apply(self):
        self.input = self.input_changed
        self.output = self.output_changed
        self.input_changed = ""
        self.output_changed = ""
        self.status = "normal"

    def export(self) -> Dict[str, str]:
        return {"input": self.input, "output": self.output}
