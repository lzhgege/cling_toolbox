# -*- coding: utf-8 -*-
import logging
import maya.cmds as cmds
import os

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')


def setLoggingConsole(logger):

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)

    logger.addHandler(console)


def setLoggingFileName(logger):
    fileName = getFileLog()

    # print logger.handlers
    if isinstance(logger.handlers[-1], logging.FileHandler):
        handler = logger.handlers[-1]
        if fileName != handler.baseFilename:
            logger.removeHandler(logger.handlers[-1])
            setLoggingHandler(logger, fileName)
            # print logger.handlers

    else:
        setLoggingHandler(logger, fileName)


def setLoggingHandler(logger, fileName):
    handler = logging.FileHandler(fileName)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)

    logger.addHandler(handler)


def getFileLog():
    fileName = cmds.file(q=True, sn=True)
    if fileName:
        path, _ = os.path.splitext(fileName)
        fileLog = path + ".log"
    else:
        fileLog = os.path.join(os.getenv("TMP"), "untitled.log")
    return fileLog

