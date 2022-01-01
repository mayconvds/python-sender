import sys

from PySimpleGUI import PySimpleGUI as sg
import zipfile
import os
import paramiko
from scp import SCPClient
import configparser


def make_zipfile(output_filename, source_dir):
    try:
        relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
        sl = zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED)
        with sl as zip:
            for root, dirs, files in os.walk(source_dir):
                zip.write(root, os.path.relpath(root, relroot))
                for file in files:
                    filename = os.path.join(root, file)
                    if os.path.isfile(filename):
                        arcname = os.path.join(os.path.relpath(root, relroot), file)
                        zip.write(filename, arcname)

        sl.close()

    except OSError:
        pass


sg.theme("DarkAmber")
cfg = configparser.ConfigParser()
can = cfg.read('config/config.ini')
iniServer = ""
iniUser = ""
iniPassword = ""
iniDirectorySsh = ""
iniProjectName = ""
iniDiretorioDoProjeto = ""
if can:
    iniServer = cfg.get('ssh_config', 'server')
    iniUser = cfg.get('ssh_config', 'usuario')
    iniPassword = cfg.get('ssh_config', 'senha')
    iniDirectorySsh = cfg.get('ssh_config', 'diretorio_ssh')
    iniProjectName = cfg.get('ssh_config', 'nome_do_projeto')
    iniDiretorioDoProjeto = cfg.get('ssh_config', 'diretorio_do_projeto')
else:
    sg.PopupError("Atenção! Criar o diretório config/config.ini.")
    sys.exit(69)

directoryProject = iniDiretorioDoProjeto

fileName = "project.zip"
projectName = iniProjectName
make_zipfile(fileName, directoryProject)
address = iniServer
username = iniUser
password = iniPassword
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=address, username=username, password=password)
directorySsh = iniDirectorySsh
cwd = os.getcwd()
stdin, stdout, stderr = ssh.exec_command('rm -r ' + directorySsh + '/*')
with SCPClient(ssh.get_transport()) as scp:
    scp.put(cwd + "/" + fileName, directorySsh)
    ssh.exec_command('unzip ' + directorySsh + '/' + fileName + ' -d ' + directorySsh)
    ssh.exec_command('mv ' + directorySsh + '/' + projectName + '/* ' + directorySsh)
    ssh.exec_command('rm ' + directorySsh + '/' + fileName)
    ssh.exec_command('rm -r ' + directorySsh + '/' + projectName)
