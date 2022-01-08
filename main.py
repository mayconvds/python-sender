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
print("zipando arquivo")
make_zipfile(fileName, directoryProject)
print("arquivo zipado")
address = iniServer
username = iniUser
password = iniPassword
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cwd = os.getcwd()

if not os.path.isfile(cwd + "/" + fileName):
    sg.PopupError("Arquivo " + fileName + " não existe.")
    sys.exit(69)

print("conectando")
ssh.connect(hostname=address, username=username, password=password)
print("conectado")
directorySsh = iniDirectorySsh


with SCPClient(ssh.get_transport()) as scp:
    print("enviando arquivo " + fileName)
    scp.put(cwd + "/" + fileName, directorySsh + "/..")
    print("arquivo enviado")
    ssh.exec_command('rm -r ' + directorySsh + '/*')
    print("arquivos do diretório '" + directorySsh + "' excluído")
    ssh.exec_command('mv ' + directorySsh + "/../" + fileName + ' ' + directorySsh)
    print('aquivo ' + directorySsh + ' movido para ' + directorySsh)
    print("unzip no arquivo " + fileName)
    ssh.exec_command('unzip ' + directorySsh + '/' + fileName + ' -d ' + directorySsh)
    print("movendo arquivos do projeto '" + projectName + "' para '" + directorySsh + "'")
    ssh.exec_command('mv ' + directorySsh + '/' + projectName + '/* ' + directorySsh)
    print("removendo arquivo " + fileName)
    ssh.exec_command('rm ' + directorySsh + '/' + fileName)
    print("excluindo diretório " + projectName + " da pasta " + directorySsh)
    ssh.exec_command('rm -r ' + directorySsh + '/' + projectName)
    scp.close()


if os.path.isfile(cwd + "/" + fileName):
    os.remove(cwd + "/" + fileName)
    print("deletando arquivo " + fileName + " do diretório " + cwd)

ssh.close()
print("processo finalizado conexão encerrada")