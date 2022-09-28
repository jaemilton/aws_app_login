#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import sys, os
from subprocess import Popen
import psutil
from subprocess import DEVNULL
from typing import List
if sys.platform == "win32":
    from subprocess import DETACHED_PROCESS, CREATE_NEW_PROCESS_GROUP, CREATE_BREAKAWAY_FROM_JOB, CREATE_NO_WINDOW

class OsProcessHelper(object):
    """
    Call in a loop to create terminal progress bar
    @params:
        command       - Required  : command
        args       - Optional  : with interation number is the start interation
    """
    creationflags=0
    if sys.platform == "win32":
        creationflags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_BREAKAWAY_FROM_JOB | CREATE_NO_WINDOW

    def __init__(self, 
                    command:str,
                    args:List[str]) -> None:
        self.command = command
        self.args = args

    def start(self):
        command_params = [self.command]
        command_params.extend(self.args)
        self.process_info =  Popen(command_params, creationflags=self.creationflags, stdin=DEVNULL)
        # self._pid = os.spawnl(os.P_DETACH, self.command, " ".join(str(x) for x in  self.args))
        if self.process_info == None:
            raise Exception(f"Error: Process {self.command} not started.")
            
        
    # def wait(self) -> None:
    #     return self.process_info.wait()

    def get_pid(self)-> int:
        return self._pid

    def finish(self) -> None:
        self.kill(self.get_pid())
        
    def kill(pid: int) -> None:
        if sys.platform == "win32":
            Popen(["taskkill", "/PID", str(pid), "/F"])
        else:
            Popen(["kill", str(pid), "-9"])
        # try:
        #     process = psutil.Process(pid)
        #     process.kill()
        # except psutil.NoSuchProcess:
        #     pass
        