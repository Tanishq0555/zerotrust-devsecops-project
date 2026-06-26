import subprocess

def run_command(user_input):
    # This is an actual security vulnerability - command injection
    subprocess.call(user_input, shell=True)
