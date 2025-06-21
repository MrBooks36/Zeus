import os
import time
import subprocess
import platform

def get_user():
    home_users = [d for d in os.listdir("/home") if os.path.isdir(os.path.join("/home", d))]
    return home_users[0] if home_users else "pi"  # fallback default

def get_bootloader_path():
    system = platform.system().lower()
    if system == 'linux':
        user = get_user()
        return f'/media/{user}/bootloader/'
    elif system == 'windows':
        return 'D:/'
    return ''

def delete_log_files():
    if platform.system() == 'Windows': folder_path = 'c:'
    elif platform.system() == 'Linux': folder_path = '/'
    bootloader = get_bootloader_path()
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                if filename.endswith('.log'):
                    file_path = os.path.join(dirpath, filename)
                    try:
                     os.remove(file_path)
                     print(f"Deleted: {file_path}")
                    except: pass 
    except Exception as e:
        print(f"Error: {e}")
    if os.path.exists(os.path.join(bootloader, 'clean')):
        os.remove(os.path.join(bootloader, 'clean'))

def install_packages(pip_path):
    with open(pip_path, 'r') as file:
        for line in file:
            subprocess.run(['pip', 'install', line.strip()])
    os.remove(pip_path)

def run_shell(shell_path):
    with open(shell_path, 'r') as file:
        for line in file:
            subprocess.run(line.strip())
    os.remove(shell_path)


def main():
    bootloader = get_bootloader_path()
    file_path = os.path.join(bootloader, 'main.py')

    try:
        while True:
            pip_path = os.path.join(bootloader, 'pip')
            if os.path.exists(pip_path):
                install_packages(pip_path)
                print('pip updated')

            shell_path = os.path.join(bootloader, 'shell')
            if os.path.exists(shell_path):
                run_shell(shell_path)
                print('Shell executed')

            clean_path = os.path.join(bootloader, 'clean')
            if os.path.exists(clean_path):
                delete_log_files()

            if os.path.exists(bootloader):
                os.chdir(bootloader)    

            process = subprocess.Popen(['python', file_path])

            while True:
                if not os.path.exists(file_path):
                    process.terminate()
                    process.wait()  # Ensure process termination
                    print("File removed. Process terminated.")
                    break

                kill_path = os.path.join(bootloader, 'kill')
                if os.path.exists(kill_path):
                    process.terminate()
                    process.wait()  # Ensure process termination
                    print('Exit order received. Quitting...')
                    os.remove(kill_path)
                    return
                if process.poll() is not None:
                    print("Process terminated unexpectedly.")
                    input("Press Enter to restart...")
                    process = subprocess.Popen(['python', file_path])

                time.sleep(1)

            while not os.path.exists(file_path):
                time.sleep(1)

            print('File back. Restarting...')

    except Exception as e:
        process.terminate()
        process.wait()  # Ensure process termination
        print("An error occurred:", e)

if __name__ == "__main__":
    main()