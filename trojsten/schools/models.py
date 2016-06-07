# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class School(models.Model):
    abbreviation = models.CharField(max_length=100,
                                    blank=True,
                                    verbose_name='skratka',
                                    help_text='Sktatka názvu školy.')
    verbose_name = models.CharField(max_length=100,
                                    verbose_name='celý názov')
    addr_name = models.CharField(max_length=100, blank=True, verbose_name='názov v adrese')
    street = models.CharField(max_length=100, blank=True, verbose_name='ulica')
    city = models.CharField(max_length=100, blank=True, verbose_name='mesto')
    zip_code = models.CharField(max_length=10, blank=True, verbose_name='PSČ')

    class Meta:
        verbose_name = 'škola'
        verbose_name_plural = 'školy'
        ordering = ('city', 'street', 'verbose_name')

    def __str__(self):
        result = ''
        if self.abbreviation:
            result += self.abbreviation + ', '
        result += self.verbose_name
        if self.street:
            result += ', ' + self.street
        if self.city or self.zip_code:
            result += ', '
        if self.zip_code:
            result += self.zip_code
        if self.city:
            result += ' ' + self.city
        return result

    @property
    def has_abbreviation(self):
        return self.abbreviation.strip() != ''
