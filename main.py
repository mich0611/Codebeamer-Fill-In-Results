import sys
import json
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from codebeamer_client import CustomCodeBeamer

USERNAME = ""
PASSWORD = ""
HEADERS = {
    'Content-Type': 'application/json'
}

class SetTestCaseToNotTest:
    def __init__(self, test_set_id, input_data):
        self.cb_agent = CustomCodeBeamer(username=USERNAME, password=PASSWORD)
        self.input_data = input_data
        self.test_set_id = test_set_id
        self.illegal_test_case_ids = []

    def build_test_case_id_map(self, childs: list[dict]):
        # Map testcase id by name
        return {child['name'].split('-')[-1]: child['id'] for child in childs}

    def update_test_cases_results(self, res_map: dict, input_data: dict):
        # Update testcase status
        res_lst = []
        for item_id, status_note in input_data.items():
            test_case_id = res_map.get(item_id)
            if test_case_id is not None:
                updated_test_case_info = {
                    "id": item_id,
                    "result": status_note['status'],
                    "url": status_note['note']
                }
                res_lst.append(updated_test_case_info)
            else:
                self.illegal_test_case_ids.append(item_id)
        return res_lst

    def run(self):
        test_run_id = self.cb_agent.find_test_run_id_by_test_set(self.test_set_id)
        childs = self.cb_agent.get_item_info(test_run_id)['children']
        res_map = self.build_test_case_id_map(childs)
        self.cb_agent.test_run_status_to_progress(test_run_id)
        updated_test_cases_list = self.update_test_cases_results(res_map, self.input_data)
        print('updated_test_cases_list:', updated_test_cases_list)
        if updated_test_cases_list:
            self.cb_agent.update_test_runs(test_run_id, updated_test_cases_list)
            print("Update Successfully")
        if self.illegal_test_case_ids:
            print(f"Illegal Test Case IDs: {self.illegal_test_case_ids}")

# ---------- Tkinter UI ----------
class TestCaseUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Test Case Updater")
        self.root.geometry("800x600")

        self.input_data = {}
        self.input_mode = None

        label_width = 12

        # Test Set ID
        tk.Label(root, text="Test Set ID:", width=label_width, anchor="e").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        self.test_set_id_entry = tk.Entry(root, width=40)
        self.test_set_id_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="w")

        # Input Mode
        tk.Label(root, text="Input Mode:", width=label_width, anchor="e").grid(
            row=1, column=0, padx=0, pady=5, sticky="e"
        )
        mode_frame = tk.Frame(root)
        mode_frame.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="w")
        tk.Button(mode_frame, text="Import JSON Mode", command=self.enable_json_mode).pack(side="left", padx=0)
        tk.Button(mode_frame, text="Manual Add Mode", command=self.enable_manual_mode).pack(side="left", padx=5)

        self.dynamic_frame = tk.Frame(root)
        self.dynamic_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        # Run / Reset
        action_frame = tk.Frame(root)
        action_frame.grid(row=3, column=0, columnspan=3, pady=10)
        tk.Button(action_frame, text="Run", command=self.run_script,
                  bg="green", fg="white", width=12, height=2).pack(side="left", padx=10)
        tk.Button(action_frame, text="Reset", command=self.reset,
                  bg="red", fg="white", width=12, height=2).pack(side="left", padx=10)

        # Table
        self.tree = ttk.Treeview(root, columns=("ID", "Status", "Comment"), show="headings")
        self.tree.heading("ID", text="TestCase ID")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Comment", text="Comment")
        self.tree.column("ID", width=120, anchor="center")
        self.tree.column("Status", width=120, anchor="center")
        self.tree.column("Comment", width=500, anchor="w")
        self.tree.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        root.grid_rowconfigure(4, weight=1)
        root.grid_columnconfigure(1, weight=1)

    def clear_dynamic_frame(self):
        # Remove dynamic widgets
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()

    def enable_json_mode(self):
        self.clear_dynamic_frame()
        self.input_mode = "json"

        tk.Button(self.dynamic_frame, text="Import JSON", command=self.import_json).grid(
            row=0, column=0, padx=100, pady=5, sticky="w"
        )

        self.json_file_label = tk.Label(self.dynamic_frame, text="No file selected", anchor="w", fg="gray")
        self.json_file_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=100, pady=5)

    def enable_manual_mode(self):
        self.clear_dynamic_frame()
        self.input_mode = "manual"

        tk.Label(self.dynamic_frame, text="Test Case ID:", width=12, anchor="e").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.tc_id_entry = tk.Entry(self.dynamic_frame, width=20)
        self.tc_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(self.dynamic_frame, text="Status:", width=12, anchor="e").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.status_cb = ttk.Combobox(self.dynamic_frame, values=["PASSED", "FAILED", "NOT_APPLICABLE", "BLOCKED"], width=18)
        self.status_cb.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.status_cb.current(0)

        tk.Label(self.dynamic_frame, text="Comment:", width=12, anchor="e").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.note_entry = tk.Entry(self.dynamic_frame, width=60)
        self.note_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="w")

        tk.Button(self.dynamic_frame, text="Add", command=self.add_case).grid(row=3, column=1, pady=5, sticky="w")

    def reset(self):
        # Clear all input and table
        self.input_data.clear()
        self.input_mode = None
        self.clear_dynamic_frame()
        self.refresh_table()

    def activate_json_mode(self):
        self.input_mode = "json"
        self.json_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="w")
        self.manual_frame.grid_forget()
        self.json_mode_btn.config(state="disabled")
        self.manual_mode_btn.config(state="disabled")

    def activate_manual_mode(self):
        self.input_mode = "manual"
        self.manual_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="w")
        self.json_frame.grid_forget()
        self.json_mode_btn.config(state="disabled")
        self.manual_mode_btn.config(state="disabled")

    def import_json(self):
        filename = filedialog.askopenfilename(
            title="Select JSON File",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if not filename:
            return
        try:
            with open(filename, encoding="utf-8") as f:
                data = json.load(f)
            self.input_data.update(data)
            self.refresh_table()
            self.input_mode = "json"
            # Update file name label
            self.json_file_label.config(text=f"Selected: {filename}", fg="black")
            messagebox.showinfo("Success", f"Imported {len(data)} test cases from {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load JSON:\n{str(e)}")

    def add_case(self):
        if self.input_mode != "manual":
            messagebox.showerror("Error", "Please select Manual Add Mode first.")
            return

        tc_id = self.tc_id_entry.get().strip()
        status = self.status_cb.get().strip()
        note = self.note_entry.get().strip()
        if not tc_id:
            messagebox.showerror("Error", "Please enter Test Case ID.")
            return
        if not tc_id.isdigit():
            messagebox.showerror("Error", "Test Case ID must be a digit string.")
            return
        self.input_data[tc_id] = {"status": status, "con": note}
        self.refresh_table()
        self.tc_id_entry.delete(0, tk.END)
        self.note_entry.delete(0, tk.END)

    def reset_data(self):
        # Reset all data and UI widgets
        self.input_data.clear()
        self.refresh_table()
        self.input_mode = None
        self.json_entry.delete(0, tk.END)
        if hasattr(self, "tc_id_entry"):
            self.tc_id_entry.delete(0, tk.END)
        if hasattr(self, "note_entry"):
            self.note_entry.delete(0, tk.END)
        # Hide mode frame and enable mode buttons
        self.json_frame.grid_forget()
        self.manual_frame.grid_forget()
        self.json_mode_btn.config(state="normal")
        self.manual_mode_btn.config(state="normal")
        messagebox.showinfo("Reset", "All data cleared. Please select input mode.")

    def refresh_table(self):
        # Refresh case table in UI
        for row in self.tree.get_children():
            self.tree.delete(row)
        for tc_id, info in self.input_data.items():
            status = info.get("status") if isinstance(info, dict) else str(info)
            note = info.get("con") if isinstance(info, dict) else ""
            self.tree.insert("", "end", values=(tc_id, status, note))

    def run_script(self):
        # Validate input mode
        if not self.input_mode:
            messagebox.showerror("Error", "Please select input mode (Import JSON or Manual Add).")
            return
        # Validate test set id
        test_set_id = self.test_set_id_entry.get().strip()
        if not test_set_id:
            messagebox.showerror("Error", "Please input Test Set ID.")
            return
        if not test_set_id.isdigit():
            messagebox.showerror("Error", "Test Set ID must be an integer.")
            return
        if not self.input_data:
            messagebox.showerror("Error", "No test cases to update. Please import JSON or add at least one Test Case.")
            return

        try:
            tc_agent = SetTestCaseToNotTest(int(test_set_id), self.input_data)
            tc_agent.run()
            messagebox.showinfo("Success", "Update Completed")
        except Exception as e:
            messagebox.showerror("Error", f"Error during execution:\n{str(e)}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        root = tk.Tk()
        app = TestCaseUI(root)
        root.mainloop()
    else:
        print("UI only: just run python main.py")
