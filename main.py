from PySimpleGUI import PySimpleGUI as sg
from webbrowser import open
import zipfile
import os
import shutil
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

iniServer = cfg.get('ssh_config', 'server')
iniUser = cfg.get('ssh_config', 'usuario')
iniPassword = cfg.get('ssh_config', 'senha')
iniDirectorySsh = cfg.get('ssh_config', 'diretorio_ssh')
iniProjectName = cfg.get('ssh_config', 'nome_do_projeto')
iniDiretorioDoProjeto = cfg.get('ssh_config', 'diretorio_do_projeto')

layout = [
    [sg.Text('Servidor', size=(15, 1)), sg.Input(key='servidor', default_text=iniServer, size=(20, 1))],
    [sg.Text('Usuario', size=(15, 1)), sg.Input(key='usuario',default_text=iniUser, size=(20, 1))],
    [sg.Text('Senha', size=(15, 1)), sg.Input(key='senha', password_char='*', default_text=iniPassword, size=(20, 1))],
    [sg.Text('Nome do Projeto', size=(15, 1)), sg.Input(key='nome_do_projeto', default_text=iniProjectName, size=(20, 1))],
    [sg.Text('Diretório', size=(15, 1)), sg.Input(key='diretoriossh', default_text=iniDirectorySsh, size=(20, 1))],
    [sg.In(iniDiretorioDoProjeto), sg.FolderBrowse(key="files", initial_folder=iniDiretorioDoProjeto)],
    [sg.Button("Enviar")],
    [sg.Text("", key="updateEvent")]
]



janela = sg.Window('Sender', layout)

while True:
    eventos, valores = janela.read()
    if eventos == sg.WINDOW_CLOSED:
        break
    if eventos == 'Entrar':
        directoryProject = valores["files"]
        if valores["files"] == "" and iniDiretorioDoProjeto is not None:
            directoryProject = iniDiretorioDoProjeto

        fileName = "project.zip"
        projectName = valores['nome_do_projeto']
        make_zipfile(fileName, directoryProject)
        address = valores["servidor"]
        username = valores["usuario"]
        password = valores["senha"]
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=address, username=username, password=password)
        directorySsh = valores["diretoriossh"]
        cwd = os.getcwd()
        stdin, stdout, stderr = ssh.exec_command('rm -r ' + directorySsh + '/*')
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(cwd + "/" + fileName, directorySsh)
            ssh.exec_command('unzip ' + directorySsh + '/' + fileName + ' -d ' + directorySsh)
            ssh.exec_command('mv ' + directorySsh + '/' + projectName + '/* ' + directorySsh)
            ssh.exec_command('rm ' + directorySsh + '/' + fileName)
            ssh.exec_command('rm -r ' + directorySsh + '/' + projectName)



