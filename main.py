import tkinter as tk
from tkinter import ttk
from subprocess import Popen, PIPE, STDOUT
from tkinter import filedialog
import threading
import subprocess

is_listening = False  # 全局变量，用于跟踪是否正在监听

def execute_command(text_box, password, cmd):
    process = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT, text=True)
    while True:
        output = process.stdout.readline()
        if output:
            text_box.insert(tk.END, output)
            text_box.see(tk.END)
        elif process.poll() is not None:
            break

def start_or_stop_capture(text_box, password, selected_channel):
    global is_listening
    if is_listening:
        text_box.insert(tk.END, "停止监听...\n")
        kill_airport_processes(password)
    else:
        cmd = f"echo {password} | sudo -S /System/Library/PrivateFrameworks/Apple80211.framework/Versions/A/Resources/airport en0 sniff {selected_channel}"
        text_box.insert(tk.END, "开始监听...\n")
        threading.Thread(target=execute_command, args=(text_box, password, cmd)).start()

    is_listening = not is_listening
    button2.config(text="停止监听" if is_listening else "开始监听")

def kill_airport_processes(password):
    cmd = "ps aux | grep airport | grep -v grep | awk '{print $2}'"
    process_ids = subprocess.check_output(cmd, shell=True, text=True).strip().split('\n')
    if process_ids:
        joined_ids = ' '.join(process_ids)
        cmd = f"echo {password} | sudo -S kill -9 {joined_ids}"
        subprocess.run(cmd, shell=True)
        print(f"Killed airport processes with IDs: {joined_ids}")

def open_capture_folder():
    subprocess.run(["open", "/private/tmp"])

def parse_capture():
    text_box.insert(tk.END, "开始解析抓包文件...\n")
    cmd = f"echo {password_entry.get()} | sudo -S aircrack-ng {pack_path_entry.get()} "
    threading.Thread(target=execute_command, args=(text_box, password_entry.get(), cmd)).start()

def select_dictionary_file():
    file_path = filedialog.askopenfilename()
    dictionary_path_entry.delete(0, tk.END)
    dictionary_path_entry.insert(0, file_path)

def select_pack_file():
    file_path = filedialog.askopenfilename()
    pack_path_entry.delete(0, tk.END)
    pack_path_entry.insert(0, file_path)

def start_cracking():
    text_box.insert(tk.END, "开始破解...\n")
    command_to_run = f"echo {password_entry.get()} | sudo -S aircrack-ng -w {dictionary_path_entry.get()} -b {wifi_BSSID_entry.get()} {pack_path_entry.get()}"
    open_new_terminal_and_run_command(command_to_run)

def open_new_terminal_and_run_command(command):
    apple_script = f'tell app "Terminal" to do script "{command}"'
    subprocess.run(["osascript", "-e", apple_script])

root = tk.Tk()
root.title("WI-FI暴力破解-by柚子studio")

left_frame = tk.Frame(root)
left_frame.pack(side=tk.LEFT, padx=10, pady=10)

right_frame = tk.Frame(root)
right_frame.pack(side=tk.RIGHT, padx=10, pady=10)


password_label = ttk.Label(root, text="输入管理员密码")
password_label.pack(side=tk.TOP)
password_entry = ttk.Entry(root, show="*")
password_entry.pack(side=tk.TOP)

ch_label = ttk.Label(root, text="选择WiFi信道")
ch_label.pack(side=tk.TOP)
ch_entry = ttk.Combobox(root, values=[str(i) for i in range(1, 12)])
ch_entry.pack(side=tk.TOP)
ch_entry.set("1")

text_box = tk.Text(root, wrap='word', height=20, width=120)
text_box.pack(side=tk.BOTTOM)

install_button = tk.Button(root, text="安装aircrack-ng",
                           command=lambda: threading.Thread(target=execute_command,
                                                            args=(text_box, password_entry.get(),
                                                                  "brew install aircrack-ng")).start())
install_button.pack(side=tk.TOP)

scan_button = tk.Button(root, text="开始扫描",
                        command=lambda: threading.Thread(target=execute_command,
                                                         args=(text_box, password_entry.get(),
                                                               f"echo {password_entry.get()} | sudo -S /System/Library/PrivateFrameworks/Apple80211.framework/Versions/A/Resources/airport -s")).start())
scan_button.pack(side=tk.TOP)

button2 = tk.Button(root, text="开始监听",
                    command=lambda: start_or_stop_capture(text_box, password_entry.get(), ch_entry.get()))
button2.pack(side=tk.TOP)

open_folder_button = tk.Button(root, text="打开抓包路径", command=open_capture_folder)
open_folder_button.pack(side=tk.TOP)

parse_button = tk.Button(right_frame, text="抓包解析", command=parse_capture)
parse_button.pack(side=tk.TOP, pady=5)

pack_path_label = ttk.Label(right_frame, text="选择抓包文件路径")
pack_path_label.pack(side=tk.TOP, pady=5)

pack_path_entry = ttk.Entry(right_frame)
pack_path_entry.pack(side=tk.TOP, pady=5)

select_pack_button = tk.Button(right_frame, text="浏览", command=select_pack_file)
select_pack_button.pack(side=tk.TOP, pady=5)

dictionary_path_label = ttk.Label(right_frame, text="选择字典文件路径")
dictionary_path_label.pack(side=tk.TOP, pady=5)

dictionary_path_entry = ttk.Entry(right_frame)
dictionary_path_entry.pack(side=tk.TOP, pady=5)

select_dictionary_button = tk.Button(right_frame, text="浏览", command=select_dictionary_file)
select_dictionary_button.pack(side=tk.TOP, pady=5)

wifi_BSSID_label = ttk.Label(right_frame, text="输入BSSID")
wifi_BSSID_label.pack(side=tk.TOP, pady=5)

wifi_BSSID_entry = ttk.Entry(right_frame)
wifi_BSSID_entry.pack(side=tk.TOP, pady=5)


start_cracking_button = tk.Button(right_frame, text="开始破解", command=start_cracking)
start_cracking_button.pack(side=tk.TOP, pady=5)

root.mainloop()
