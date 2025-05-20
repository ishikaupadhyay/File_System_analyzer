import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import csv
import json
import datetime

# Get details of a single file or folder
def get_file_details(path):
    try:
        stats = os.stat(path)
        return {
            "Name": os.path.basename(path),
            "Type": "Folder" if os.path.isdir(path) else "File",
            "Size (KB)": round(stats.st_size / 1024, 2),
            "Created": datetime.datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
            "Modified": datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            "Accessed": datetime.datetime.fromtimestamp(stats.st_atime).strftime('%Y-%m-%d %H:%M:%S'),
            "Readable": os.access(path, os.R_OK),
            "Writable": os.access(path, os.W_OK),
            "Executable": os.access(path, os.X_OK),
            "Owner UID": stats.st_uid if hasattr(stats, 'st_uid') else "N/A",
            "Group GID": stats.st_gid if hasattr(stats, 'st_gid') else "N/A",
        }
    except Exception as e:
        return {"Name": path, "Error": str(e)}

# Scan all files and folders in a directory
def analyze_directory(directory):
    file_info = []
    for root, dirs, files in os.walk(directory):
        for name in files + dirs:
            path = os.path.join(root, name)
            file_info.append(get_file_details(path))
    return file_info

# GUI App
class FileSystemAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🗂️ File System Analyzer")
        self.root.geometry("1100x600")
        self.root.configure(bg='#f2f2f2')

        self.data = []

        self.setup_gui()

    def setup_gui(self):
        frame = tk.Frame(self.root, bg='#f2f2f2')
        frame.pack(pady=10)

        tk.Label(frame, text="📁 Directory:", bg='#f2f2f2', font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5)
        self.dir_entry = tk.Entry(frame, width=60, font=('Arial', 11))
        self.dir_entry.grid(row=0, column=1, padx=5)
        tk.Button(frame, text="Browse", command=self.browse_directory, bg='#4caf50', fg='white').grid(row=0, column=2, padx=5)
        tk.Button(frame, text="Analyze", command=self.analyze, bg='#2196f3', fg='white').grid(row=0, column=3, padx=5)

        # Table
        self.tree = ttk.Treeview(self.root, columns=list(range(12)), show='headings', height=20)
        headings = [
            "Name", "Type", "Size (KB)", "Created", "Modified", "Accessed",
            "Readable", "Writable", "Executable", "Owner UID", "Group GID"
        ]
        for i, head in enumerate(headings):
            self.tree.heading(i, text=head)
            self.tree.column(i, width=110, anchor='center')

        self.tree.pack(pady=10, fill='both', expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        # Export Buttons
        export_frame = tk.Frame(self.root, bg='#f2f2f2')
        export_frame.pack(pady=5)
        tk.Button(export_frame, text="Export to CSV", command=self.export_csv, bg='#ff9800', fg='white').pack(side='left', padx=10)
        tk.Button(export_frame, text="Export to JSON", command=self.export_json, bg='#9c27b0', fg='white').pack(side='left', padx=10)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)

    def analyze(self):
        directory = self.dir_entry.get()
        if not os.path.isdir(directory):
            messagebox.showerror("Error", "Please select a valid directory.")
            return

        self.data = analyze_directory(directory)
        self.tree.delete(*self.tree.get_children())
        for item in self.data:
            values = [item.get(key, '') for key in [
                "Name", "Type", "Size (KB)", "Created", "Modified", "Accessed",
                "Readable", "Writable", "Executable", "Owner UID", "Group GID"]]
            self.tree.insert('', tk.END, values=values)

    def export_csv(self):
        if not self.data:
            messagebox.showwarning("Warning", "No data to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
                writer.writeheader()
                writer.writerows(self.data)
            messagebox.showinfo("Success", "Data exported to CSV successfully.")

    def export_json(self):
        if not self.data:
            messagebox.showwarning("Warning", "No data to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4)
            messagebox.showinfo("Success", "Data exported to JSON successfully.")

if __name__ == '__main__':
    root = tk.Tk()
    app = FileSystemAnalyzerApp(root)
    root.mainloop()
