from django.db import models


class BaseModel(models.Model):
    class Meta:
        abstract = True

    def __str__(self) -> str:
        if name := getattr(self, "name", None):
            return str(name)
        return super().__str__()
