from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Branch(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Shift(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["start_time", "name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.start_time}-{self.end_time})"


class AcademicSession(TimeStampedModel):
    year = models.PositiveIntegerField(unique=True)
    is_active = models.BooleanField(default=True)
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ["-year"]

    def __str__(self) -> str:
        return str(self.year)


class SchoolClass(TimeStampedModel):
    name = models.CharField(max_length=100)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='classes')
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("name", "branch")
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} - {self.branch.name}"


class Section(TimeStampedModel):
    name = models.CharField(max_length=50)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='sections')
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("name", "school_class")
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.school_class.name} - {self.name}"


class Subject(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
