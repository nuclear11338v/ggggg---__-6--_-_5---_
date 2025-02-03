import telebot
import subprocess
import os
import time
import shutil

API_TOKEN = '7889212498:AAGt1Dn2FKPyp1DB3usDDys-ALGmWN5NzQY'  # Replace with your bot's API token
bot = telebot.TeleBot(API_TOKEN)

# Define paths for your text files
USER_FILE = "users.txt"
USER_BUILD_FILE = "user_build.txt"
user_directories = {}
BASE_DIR = 'user_files'
os.makedirs(BASE_DIR, exist_ok=True)
running_processes = {}

# Helper function to read and write to text files
def write_to_file(filename, text):
    with open(filename, 'a') as f:
        f.write(text + '\n')

def read_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return f.readlines()
    return []

users_file = 'userss.txt'

# Function to add user details to file
def add_user(user_id, username):
    with open(users_file, 'a') as f:
        f.write(f"{user_id},{username}\n")

# Function to read users from file
def get_users():
    if os.path.exists(users_file):
        with open(users_file, 'r') as f:
            return [line.strip().split(',') for line in f.readlines()]
    return []
# Send processing animation (dots)
def send_processing_animation(chat_id):
    processing_message = bot.send_message(chat_id, "Processing... 🔄")
    return processing_message

# Helper function to execute commands
def execute_command(command, chat_id):
    # Send processing animation
    processing_message = send_processing_animation(chat_id)
    
    try:
        # Run the command
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        
        # Check if the command ran successfully
        if result.returncode == 0:
            bot.edit_message_text(f"Terminal Output: ✅\n{result.stdout}", chat_id, processing_message.message_id)
        else:
            bot.edit_message_text(f"Error: ❌\n{result.stderr}", chat_id, processing_message.message_id)
    except Exception as e:
        bot.edit_message_text(f"Error: ❌\n{str(e)}", chat_id, processing_message.message_id)

# Handler when a new user joins
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    username = message.from_user.username or "No Username"
    
    add_user(user_id, username)
    user_id = message.from_user.id
    username = message.from_user.username
    write_to_file(USER_FILE, f"User ID: {user_id} | Username: {username}")
    bot.reply_to(message, f"Welcome, {username}! 🎉")

    # Notify admins
    admin_ids = ['7858368373']  # List your admin user IDs here
    for admin_id in admin_ids:
        bot.send_message(admin_id, f"New user joined\nUsername: {username}\nUser ID: {user_id}")

@bot.message_handler(commands=['users'])
def users(message):
    admin_id = '7858368373'  # Apne admin user ID yahan daalein
    if str(message.from_user.id) == admin_id:
        users_list = get_users()
        if users_list:
            response = "User List:\n"
            for user in users_list:
                response += f"Username: {user[1]}, User ID: {user[0]}\n"
            bot.reply_to(message, response)
        else:
            bot.reply_to(message, "No users found.")
    else:
        bot.reply_to(message, "You are not an admin.")

# Command /broadcast
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    admin_id = '7858368373'  # Apne admin user ID yahan daalein
    if str(message.from_user.id) == admin_id:
        msg_content = message.text.replace('/broadcast ', '')
        users_list = get_users()
        for user in users_list:
            try:
                bot.send_message(user[0], msg_content)
            except Exception as e:
                print(f"Could not send message to {user[0]}: {e}")
        bot.reply_to(message, "Message broadcasted to all users.")
    else:
        bot.reply_to(message, "You are not an admin.")
        
@bot.message_handler(content_types=['document'])
def handle_document(message):
    user_id = message.from_user.id
    user_dir = os.path.join(BASE_DIR, str(user_id))
    
    # Create user-specific directory if it doesn't exist
    os.makedirs(user_dir, exist_ok=True)

    # Get the file info
    file_info = bot.get_file(message.document.file_id)
    file_name = message.document.file_name
    file_path = os.path.join(user_dir, file_name)

    # Download and save the file
    downloaded_file = bot.download_file(file_info.file_path)

    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    bot.reply_to(message, f"File '{file_name}' has been saved in your personal directory.")
    
# Help command
@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = """
Here are the commands you can use:

    ❤️ *Install Packages*  
    - `pip install <package_name>`  
    - `npm install <package_name>`  
    - `pkg install <package_name>`  

    😂 *Git & Files*  
    - `git clone <repo_link>`  
    - `python3 <file.py>`  
    - `node <file.js>`  
    - `delete <file_name>` - Delete a file  
    - `edit <file_name>` - Edit a file  
    - `redo <file_name>` - Redo changes to a file  
    - `undo <file_name>` - Undo changes to a file  

    📂 *Terminal Commands*  
    - `ls` - List files and directories  
    - `pwd` - Show current directory  
    - `cat <file_name>` - Show file contents  
    - `echo <text>` - Print text to terminal  
    - `top` - Display system processes  
    - `cd <dir_name>` - Change directory  
    - `clear` - Clear terminal screen  
    - `touch <file_name>` - Create a new file  
    - `chmod <permissions> <file_name>` - Change file permissions  
    - `cp <source> <destination>` - Copy a file  
    - `mv <source> <destination>` - Move or rename a file  
    - `rm <file_name>` - Remove a file  
    - `mkdir <dir_name>` - Create a directory  
    - `rmdir <dir_name>` - Remove a directory  
    - `find <path> -name <file_name>` - Find a file  
    - `grep <pattern> <file_name>` - Search for a pattern in a file  
    - `wget <url>` - Download a file from the internet  
    - `curl <url>` - Transfer data to or from a server  
    - `df -h` - Disk space usage  
    - `du -sh <dir>` - Disk usage of a directory  
    - `ifconfig` - Network interfaces configuration  
    - `ping <host>` - Ping a host  
    - `shutdown` - Shut down the system  
    - `reboot` - Reboot the system  

    🖥️ *General Info*  
    - Use `/stop <file_name>` to stop running files (Python or Node.js).  
    """
    bot.reply_to(message, help_text, parse_mode="Markdown")

# Terminal Commands
@bot.message_handler(func=lambda message: message.text.startswith('pip install'))
def handle_pip_install(message):
    package_name = message.text[12:]
    if not package_name:
        bot.reply_to(message, "Please type `pip install <package_name>` 🤔")
        return
    execute_command(f"pip install {package_name}", message.chat.id)

@bot.message_handler(func=lambda message: message.text.startswith('npm install'))
def handle_npm_install(message):
    package_name = message.text[13:]
    if not package_name:
        bot.reply_to(message, "Please type `npm install <package_name>` 🤔")
        return
    execute_command(f"npm install {package_name}", message.chat.id)

@bot.message_handler(func=lambda message: message.text.startswith('pkg install'))
def handle_pkg_install(message):
    package_name = message.text[13:]
    if not package_name:
        bot.reply_to(message, "Please type `pkg install <package_name>` 🤔")
        return
    execute_command(f"pkg install {package_name}", message.chat.id)

@bot.message_handler(func=lambda message: message.text.startswith('git clone'))
def handle_git_clone(message):
    repo_link = message.text[10:]
    if not repo_link:
        bot.reply_to(message, "Please type `git clone <repo_link>` 🤔")
        return
    execute_command(f"git clone {repo_link}", message.chat.id)




@bot.message_handler(commands=['find'])
def cmd_find(message):
    try:
        _, path, file_name = message.text.split()
        result = subprocess.check_output(['find', path, '-name', file_name]).decode()
        bot.reply_to(message, result)
    except Exception as e:
        bot.reply_to(message, str(e))

@bot.message_handler(commands=['grep'])
def cmd_grep(message):
    try:
        _, pattern, file_name = message.text.split()
        result = subprocess.check_output(['grep', pattern, file_name]).decode()
        bot.reply_to(message, result)
    except Exception as e:
        bot.reply_to(message, str(e))

@bot.message_handler(commands=['wget'])
def cmd_wget(message):
    try:
        _, url = message.text.split()
        result = subprocess.check_output(['wget', url]).decode()
        bot.reply_to(message, result)
    except Exception as e:
        bot.reply_to(message, str(e))

@bot.message_handler(commands=['curl'])
def cmd_curl(message):
    try:
        _, url = message.text.split()
        result = subprocess.check_output(['curl', url]).decode()
        bot.reply_to(message, result)
    except Exception as e:
        bot.reply_to(message, str(e))

@bot.message_handler(commands=['df'])
def cmd_df(message):
    result = subprocess.check_output(['df', '-h']).decode()
    bot.reply_to(message, result)

@bot.message_handler(commands=['du'])
def cmd_du(message):
    try:
        _, dir_name = message.text.split()
        result = subprocess.check_output(['du', '-sh', dir_name]).decode()
        bot.reply_to(message, result)
    except Exception as e:
        bot.reply_to(message, str(e))

@bot.message_handler(commands=['ifconfig'])
def cmd_ifconfig(message):
    result = subprocess.check_output(['ifconfig']).decode()
    bot.reply_to(message, result)

@bot.message_handler(commands=['ping'])
def cmd_ping(message):
    try:
        _, host = message.text.split()
        result = subprocess.check_output(['ping', '-c', '4', host]).decode()
        bot.reply_to(message, result)
    except Exception as e:
        bot.reply_to(message, str(e))

@bot.message_handler(commands=['shutdown'])
def cmd_shutdown(message):
    bot.reply_to(message, "Shutting down. This command requires admin privileges.")
    # Uncomment the next line if you want to enable this command.
    # subprocess.call(['shutdown', '-h', 'now'])

@bot.message_handler(commands=['reboot'])
def cmd_reboot(message):
    bot.reply_to(message, "Rebooting. This command requires admin privileges.")
    
@bot.message_handler(func=lambda message: message.text.startswith('delete'))
def handle_delete(message):
    file_name = message.text[7:]
    if not file_name:
        bot.reply_to(message, "Please type `delete <file_name>` 🤔")
        return
    try:
        os.remove(file_name)
        bot.reply_to(message, f"File {file_name} deleted successfully. 🗑️")
    except Exception as e:
        bot.reply_to(message, f"Error deleting file: {str(e)} ❌")

@bot.message_handler(func=lambda message: message.text.startswith('edit'))
def handle_edit(message):
    file_name = message.text[5:]
    if not file_name:
        bot.reply_to(message, "Please type `edit <file_name>` 🤔")
        return
    execute_command(f"nano {file_name}", message.chat.id)

@bot.message_handler(func=lambda message: message.text.startswith('redo'))
def handle_redo(message):
    file_name = message.text[5:]
    if not file_name:
        bot.reply_to(message, "Please type `redo <file_name>` 🤔")
        return
    # Placeholder for redo functionality
    bot.reply_to(message, f"Redoing changes for {file_name} 🧑‍💻")

@bot.message_handler(func=lambda message: message.text.startswith('undo'))
def handle_undo(message):
    file_name = message.text[5:]
    if not file_name:
        bot.reply_to(message, "Please type `undo <file_name>` 🤔")
        return
    # Placeholder for undo functionality
    bot.reply_to(message, f"Undoing changes for {file_name} 🔙")

# Additional Terminal Commands
@bot.message_handler(commands=['ls'])
def list_files(message):
    user_id = message.from_user.id
    user_dir = os.path.join(BASE_DIR, str(user_id))
    
    # Check if user directory exists
    if os.path.exists(user_dir):
        files = os.listdir(user_dir)
        if files:
            response = "Here are your files:\n" + "\n".join(files)
        else:
            response = "Your directory is empty."
    else:
        response = "You have not uploaded any files yet."

    bot.reply_to(message, response)

@bot.message_handler(func=lambda message: message.text.startswith('pwd'))
def handle_pwd(message):
    execute_command("pwd", message.chat.id)

@bot.message_handler(func=lambda message: message.text.startswith('cat'))
def handle_cat(message):
    file_name = message.text[5:]
    if not file_name:
        bot.reply_to(message, "Please type `cat <file_name>` 🤔")
        return
    execute_command(f"cat {file_name}", message.chat.id)

@bot.message_handler(func=lambda message: message.text.startswith('echo'))
def handle_echo(message):
    text_to_echo = message.text[5:]
    if not text_to_echo:
        bot.reply_to(message, "Please type `echo <text>` 🤔")
        return
    execute_command(f"echo {text_to_echo}", message.chat.id)

@bot.message_handler(func=lambda message: message.text.startswith('top'))
def handle_top(message):
    execute_command("top", message.chat.id)

@bot.message_handler(func=lambda message: message.text.startswith('cd'))
def handle_cd(message):
    dir_name = message.text[3:]
    if not dir_name:
        bot.reply_to(message, "Please type `cd <dir_name>` 🤔")
        return
    execute_command(f"cd {dir_name}", message.chat.id)

@bot.message_handler(func=lambda message: message.text.startswith('clear'))
def handle_clear(message):
    execute_command("clear", message.chat.id)

@bot.message_handler(func=lambda message: message.text.startswith('touch'))
def handle_touch(message):
    file_name = message.text[6:]
    if not file_name:
        bot.reply_to(message, "Please type `touch <file_name>` 🤔")
        return
    execute_command(f"touch {file_name}", message.chat.id)

@bot.message_handler(func=lambda message: message.text.startswith('chmod'))
def handle_chmod(message):
    command_parts = message.text.split()
    if len(command_parts) < 3:
        bot.reply_to(message, "Please type `chmod <permissions> <file_name>` 🤔")
        return
    execute_command(f"chmod {command_parts[1]} {command_parts[2]}", message.chat.id)

@bot.message_handler(func=lambda message: message.text.startswith('cp'))
def handle_cp(message):
    command_parts = message.text.split()
    if len(command_parts) < 3:
        bot.reply_to(message, "Please type `cp <source> <destination>` 🤔")
        return
    execute_command(f"cp {command_parts[1]} {command_parts[2]}", message.chat.id)

@bot.message_handler(func=lambda message: message.text.startswith('mv'))
def handle_mv(message):
    command_parts = message.text.split()
    if len(command_parts) < 3:
        bot.reply_to(message, "Please type `mv <source> <destination>` 🤔")
        return
    execute_command(f"mv {command_parts[1]} {command_parts[2]}", message.chat.id)

@bot.message_handler(func=lambda message: message.text.startswith('rm'))
def handle_rm(message):
    file_name = message.text[3:]
    if not file_name:
        bot.reply_to(message, "Please type `rm <file_name>` 🤔")
        return
    execute_command(f"rm {file_name}", message.chat.id)
    
def send_processing_animation(chat_id):
    # Send a "Processing..." message with an emoji, indicating the file is running.
    processing_message = bot.send_message(chat_id, "🔄")
    return processing_message

# Handle python3 command
@bot.message_handler(func=lambda message: message.text.startswith("python3"))
def handle_python3(message):
    user_id = message.from_user.id
    command = message.text.split()
    if len(command) != 2:
        bot.send_message(user_id, "❌ Usage: `python3 <file.py>`")
        return
    file_name = command[1]
    user_dir = os.path.join("users", str(user_id))
    file_path = os.path.join(user_dir, file_name)
    if not os.path.exists(file_path):
        bot.send_message(user_id, f"❌ File '{file_name}' not found. Please upload the file first.")
        return
    bot.send_message(user_id, f"The file `{file_name}` is running 🎽\n\nWARNING DO NOT RUN DDOS BOT ✅")
    process = subprocess.Popen(f"cd {user_dir} && python3 {file_name}", shell=True)

    # Optionally, you can track the running processes
    if user_id not in running_processes:
        running_processes[user_id] = {}
    running_processes[user_id][file_name] = process.pid


# Handle node command
@bot.message_handler(func=lambda message: message.text.startswith("node"))
def handle_node(message):
    user_id = message.from_user.id
    command = message.text.split()
    if len(command) != 2:
        bot.send_message(user_id, "❌ Usage: `node <file.js>`")
        return
    file_name = command[1]
    user_dir = os.path.join("users", str(user_id))
    file_path = os.path.join(user_dir, file_name)
    if not os.path.exists(file_path):
        bot.send_message(user_id, f"❌ File '{file_name}' not found. Please upload the file first.")
        return
    bot.send_message(user_id, f"The file `{file_name}` is running 🎽")
    process = subprocess.Popen(f"cd {user_dir} && node {file_name}", shell=True)

    # Track the running process
    if user_id not in running_processes:
        running_processes[user_id] = {}
    running_processes[user_id][file_name] = process.pid

@bot.message_handler(commands=['stop'])
def stop_file(message):
    user_id = message.from_user.id
    command = message.text.split()
    if len(command) != 2:
        bot.send_message(user_id, "❌ Usage: `/stop <file_name>`")
        return
    file_name = command[1]
    if user_id not in running_processes or file_name not in running_processes[user_id]:
        bot.send_message(user_id, f"❌ No running process found for `{file_name}`.")
        return

    # Stop the process
    pid = running_processes[user_id][file_name]
    os.kill(pid, 9)  # Kill the process
    del running_processes[user_id][file_name]
    bot.send_message(user_id, f"⏹️ The file `{file_name}` has been stopped.")
    

# Start the bot
bot.infinity_polling()
