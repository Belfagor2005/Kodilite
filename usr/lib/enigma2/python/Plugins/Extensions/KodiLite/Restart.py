#!/usr/bin/python
# -*- coding: utf-8 -*-

from Screens.Standby import TryQuitMainloop


def Restart(session):
    session.open(TryQuitMainloop, 3)
