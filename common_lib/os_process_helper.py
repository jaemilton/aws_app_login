#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from random import triangular
import sys
from subprocess import Popen
import psutil
from subprocess import DEVNULL
from typing import List
if sys.platform == "win32":
    from subprocess import DETACHED_PROCESS, CREATE_NEW_PROCESS_GROUP, CREATE_BREAKAWAY_FROM_JOB

class OsProcessHelper(object):
    """
    Call in a loop to create terminal progress bar
    @params:
        command       - Required  : command
        args       - Optional  : with interation number is the start interation
    """
    creationflags=0
    if sys.platform == "win32":
        creationflags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_BREAKAWAY_FROM_JOB

    def __init__(self, 
                    command:str,
                    args:List[str]) -> None:
        self.command = command
        self.args = args

    def start(self):
        command_params = [self.command]
        command_params.extend(self.args)
        self.process_info =  Popen(command_params, creationflags=self.creationflags, stdin=DEVNULL)
        if self.process_info == None:
            raise Exception(f"Error: Process {command_params} not started.")
            
        
    def wait(self) -> None:
        return self.process_info.wait()

    def get_pid(self)-> int:
        return self.process_info.pid

    def finish(self) -> None:
        self.kill(self.get_pid())
        
    def kill(pid: int) -> None:
        try:
            process = psutil.Process(pid)
            process.kill()
        except psutil.NoSuchProcess:
            pass
        