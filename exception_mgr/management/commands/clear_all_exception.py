'''
Created on 2014-3-11

@author: liuli12
'''
import logging
from django.core.management.base import BaseCommand
from exception_mgr.models import SeException

class Command(BaseCommand):
    help = 'clear all exception'
   
    def handle(self, *args, **options):
        try:
            SeException.objects.all().delete()
            logging.info("delete all exception success")
        except:
            pass
        
            
        
