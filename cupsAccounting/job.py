#!/usr/bin/env python

from cupsAccounting.utils import objetoBase, validarUsuario
from cupsAccounting.logger import Logger

from re import search


class Job(objetoBase, Logger):
    paginas = 1  # Por el solo hecho de existir
    _attr = None

    def __init__(self, c, jid):
        self.jid = jid
        self.c = c  # referencia al servidor

        self.usuario = self.attr['job-originating-user-name'].lower()
        self.ip = self.attr['job-originating-host-name']

        self.impresora = search('printers/(.*)-',
                                self.attr['printer-uri']).group(1)

        self.nombre = self.attr['job-name'].lower()
        if 'smbprn' in self.nombre:
            self.nombre = self.nombre.split(' ', 1)[1]

    @property
    def attr(self):
        if self._attr is None:
            self._attr = self.c.getJobAttributes(self.jid)
        return self._attr

    def validar(self):
        codes = ['El usuario se verifico correctamente',
                 'El usuario esta en la lista nok',
                 'El usuario no pudo verificarse']
        exit_code = validarUsuario(self.usuario)

        if exit_code == 0:
            self.logger.info("%s: %s" % (self.usuario, codes[exit_code]))
            return True

        self.logger.error("%s: %s" % (self.usuario, codes[exit_code]))
        return False

    def mover(self, queue):
        self.logger.debug(
            '%d: Moviendo a [%s]' % (self.jid, queue.name))
        self.c.moveJob(job_id=self.jid,
                       job_printer_uri=queue.uri)

    def cancelar(self):
        self.logger.info(
            '%d: Cancelando! (%s)' % (self.jid, self))
        self.c.cancelJob(self.jid)

    def __repr__(self):
        return """{clase} {jid}: {user}@{ip} "{nombre}" """.format(
            clase=self.__class__.__name__,
            jid=self.jid,
            user=self.usuario, ip=self.ip,
            nombre=self.nombre)
