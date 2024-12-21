import os
import tarfile
import configparser
import platform
import calendar
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext


class ShellEmulatorGUI:
    def __init__(self, config_path):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        self.username = self.config.get("user", "name", fallback="user")
        self.hostname = self.config.get("system", "hostname", fallback="emulator")
        self.fs_path = self.config.get("filesystem", "path", fallback="virtual_fs.tar")
        self.current_dir = "/"
        self.fs = {}  # Виртуальная файловая система

        self.load_virtual_fs()
        self.init_gui()

    def load_virtual_fs(self):
        if not os.path.exists(self.fs_path):
            self.print_output(f"Error: Virtual filesystem archive '{self.fs_path}' not found.")
            return

        with tarfile.open(self.fs_path, "r") as tar:
            for member in tar.getmembers():
                self.fs[member.name] = member

    def init_gui(self):
        self.root = tk.Tk()
        self.root.title("Shell Emulator GUI")

        # Вывод команд
        self.output_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=20, width=80)
        self.output_area.pack(padx=10, pady=5)
        self.output_area.config(state=tk.DISABLED)

        # Поле ввода команд
        self.command_entry = tk.Entry(self.root, width=80)
        self.command_entry.pack(padx=10, pady=5)
        self.command_entry.bind("<Return>", self.handle_command)

        self.print_output(f"Welcome to the shell emulator, {self.username}@{self.hostname}!")
        self.print_output("Type 'exit' to close the shell.")

    def print_output(self, text):
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.see(tk.END)
        self.output_area.config(state=tk.DISABLED)

    def handle_command(self, event):
        command = self.command_entry.get().strip()
        self.command_entry.delete(0, tk.END)

        if command:
            self.print_output(f"{self.username}@{self.hostname}:{self.current_dir} $ {command}")
            self.process_command(command)

    def process_command(self, command):
        parts = command.split()
        cmd = parts[0]
        args = parts[1:]

        if cmd == "ls":
            self.do_ls()
        elif cmd == "cd":
            self.do_cd(args[0] if args else "/")
        elif cmd == "exit":
            self.root.quit()
        elif cmd == "clear":
            self.output_area.config(state=tk.NORMAL)
            self.output_area.delete("1.0", tk.END)
            self.output_area.config(state=tk.DISABLED)
        elif cmd == "uname":
            self.do_uname()
        elif cmd == "tail":
            if args:
                self.do_tail(args[0])
            else:
                self.print_output("Usage: tail <file>")
        elif cmd == "cal":
            self.do_cal()
        elif cmd == "tac":
            if args:
                self.do_tac(args[0])
            else:
                self.print_output("Usage: tac <file>")
        elif cmd == "date":
            self.do_date()
        else:
            self.print_output(f"{cmd}: command not found")

    def do_ls(self):
        current_path = self.current_dir.lstrip("/")
        items = [name[len(current_path):].strip("/")
                 for name in self.fs.keys() if name.startswith(current_path) and name != current_path]
        if items:
            self.print_output("  ".join(sorted(set(item.split("/")[0] for item in items))))
        else:
            self.print_output("")

    def do_cd(self, path):
        if path == "/":
            self.current_dir = "/"
        elif path == "..":
            if self.current_dir != "/":
                self.current_dir = os.path.dirname(self.current_dir.rstrip("/"))
        else:
            new_dir = os.path.normpath(os.path.join(self.current_dir, path))
            if any(name.startswith(new_dir.lstrip("/")) for name in self.fs.keys()):
                self.current_dir = new_dir
            else:
                self.print_output(f"{path}: No such directory")

    def do_uname(self):
        self.print_output(platform.system())

    def do_tail(self, file_path):
        file_path = os.path.normpath(os.path.join(self.current_dir, file_path)).lstrip("/")
        if file_path in self.fs and self.fs[file_path].isfile():
            with tarfile.open(self.fs_path, "r") as tar:
                file_obj = tar.extractfile(file_path)
                if file_obj:
                    lines = file_obj.read().decode("utf-8").splitlines()[-10:]
                    self.print_output("\n".join(lines))
        else:
            self.print_output(f"{file_path}: No such file or directory")

    def do_cal(self):
        self.print_output(calendar.month(datetime.now().year, datetime.now().month))

    def do_tac(self, file_path):
        file_path = os.path.normpath(os.path.join(self.current_dir, file_path)).lstrip("/")
        if file_path in self.fs and self.fs[file_path].isfile():
            with tarfile.open(self.fs_path, "r") as tar:
                file_obj = tar.extractfile(file_path)
                if file_obj:
                    lines = file_obj.read().decode("utf-8").splitlines()
                    self.print_output("\n".join(reversed(lines)))
        else:
            self.print_output(f"{file_path}: No such file or directory")

    def do_date(self):
        self.print_output(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    emulator = ShellEmulatorGUI("config.ini")
    emulator.run()

