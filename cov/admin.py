from django.contrib import admin

# Register your models here.
from .models import ReposType
from .models import Module
from .models import CovTask
from .models import CovData
from .models import CovReport


admin.site.register(ReposType)
admin.site.register(Module)
admin.site.register(CovTask)
admin.site.register(CovData)
admin.site.register(CovReport)