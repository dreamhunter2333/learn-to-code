import paramiko
import interactive

ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect(
    "ubuntu-ssh",
    port=22,
    username='root',
    key_filename='id_rsa',
    compress=True
)

channel = ssh.invoke_shell()
interactive.interactive_shell(channel)
channel.close()
ssh.close()
