import subprocess
from tkinter import Tk, Label, Button, Radiobutton, IntVar, messagebox

# Function to start the selected script
def start_script(site_choice):
    try:
        if site_choice == 1:
            subprocess.run(["python", "./qvc/main.py"], check=True)
        elif site_choice == 2:
            subprocess.run(["python", "./bestbuy/main.py"], check=True)
        else:
            messagebox.showerror("Error", "Please select a valid site.")
            return
        messagebox.showinfo("Completed", "Process completed successfully!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# GUI setup
def main():
    root = Tk()
    root.title("Image Downloader")

    Label(root, text="Select a site to download images from:").pack(pady=10)

    site_choice = IntVar()
    Radiobutton(root, text="QVC", variable=site_choice, value=1).pack(anchor="w")
    Radiobutton(root, text="Best Buy", variable=site_choice, value=2).pack(anchor="w")

    Button(root, text="Start Download", command=lambda: start_script(site_choice.get())).pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
