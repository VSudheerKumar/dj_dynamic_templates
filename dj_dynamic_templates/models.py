
from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.contrib import messages

import os
from .validators import *
from .utils import file_or_dir_remove_signal


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    remarks = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    parent_obj = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    code = models.PositiveBigIntegerField()

    code_filter = {}
    
    @classmethod
    def get_code(cls):
        return cls.objects.filter(**cls.code_filter).count() + 1
    
    def pre_save(self):
        pass
    
    def post_save(self):
        pass

    def soft_save(self):
        if self.pk:
            self.__class__.objects.filter(id=self.id).update(is_active=False)
            self.parent_obj_id = self.id
            self.pk = None


    class Meta:
        abstract = True


class Category(BaseModel):
    
    parent_obj = is_active = None

    app_name = models.CharField(max_length=50, validators=[validate_app], help_text="In this App, Directory will be created within templates folder")
    name = models.CharField(max_length=50, help_text="Will use this name as an Directory name")

    def _get_directory_path(self):
        return f'{self.app_name}/templates/{self.name}/'

    def get_directory_path(self):
        return f'{settings.BASE_DIR}/{self._get_directory_path()}'
            
    def get_files_in_dir(self):
        try:
            return os.listdir(self.get_directory_path())
        except FileNotFoundError:
            return list()

    def clean(self):
        base_filter = self.__class__.objects.filter(app_name=self.app_name, name=self.name)
        if self.pk:
            base_filter = base_filter.exclude(id=self.id)
        else:
            if self.__class__.objects.filter(code=self.code).exists():
                raise ValidationError({'code': 'This code is already in use, Please choose another one'})
        if base_filter.exists():
            raise ValidationError({'name': 'Folder Already Exist'})

    def __str__(self):
        return f'{self.app_name} - {self.name}'


    class Meta:
        managed = apps.is_installed('dj_dynamic_templates')
        db_table = 'dj_dynamic_templates__category'
        verbose_name = ' DJ Dynamic Template Category'
        verbose_name_plural = verbose_name.replace('Category', 'Categories')


class MailTemplate(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, help_text='Select the category where you want to save the template', related_name='mail_template_category')

    try:
        from markdownx.models import MarkdownxField
        body_content = MarkdownxField()
    except ModuleNotFoundError:
        body_content = models.TextField()

    style_content = models.TextField(blank=True)
    script_content = models.TextField(blank=True)

    name = models.CharField(max_length=50, help_text='Entered name will treated as template file name, A template file is created with this file name')

    code_filter = {'parent_obj': None}
    base_template = "'dj_dynamic_templates/base.html'"

    def get_template_path(self):
        return f'{self.category._get_directory_path()}{self.name}.html'

    def get_template_render_path(self):
        return f'{self.category.name}/{self.name}.html'

    def get_template_content(self):
        return """\n{% extends """ + self.base_template + """ %}\n""" + """\n{% block style %}\n""" + self.style_content + \
                   """\n{% endblock %}\n""" + """\n{% block script %}\n""" + self.script_content + """\n{% endblock %}\n""" + \
                   """\n{% block content %}\n""" + self.body_content + """\n{% endblock %}\n"""

    def set_template(self, new_obj=False, re_sync=False):
        content = self.get_template_content()
        if not self.parent_obj and not re_sync:
            file = open(self.get_template_path(), "x")
        else:
            try:
                if not re_sync:
                    os.rename(self.parent_obj.get_template_path(), self.get_template_path())
                if self.parent_obj:
                    file_or_dir_remove_signal.send(sender=None, path=self.parent_obj.get_template_path(), name=self.parent_obj.name, id=self.parent_obj.id, re_sync=re_sync)
                else:
                    file_or_dir_remove_signal.send(sender=None, path=self.get_template_path(), name=self.name, id=self.id)
                file = open(self.get_template_path(), "w")
            except FileNotFoundError:
                file = open(self.get_template_path(), "x")
        file.write(content)
        file.close()

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.soft_save()
        super(MailTemplate, self).save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
        self.set_template()
        
    def clean(self):
        if hasattr(self, 'category'):
            if self.pk:
                if self.__class__.objects.get(pk=self.pk).name != self.name:
                    if self.__class__.objects.filter(name=self.name, category=self.category, is_active=True).exclude(id=self.id).exists():
                        raise ValidationError({'name': 'Already an Record is exists with this name '})
            else:
                if self.__class__.objects.filter(name=self.name, category=self.category, is_active=True).exists():
                    raise ValidationError({'name': 'Already an Record is exists with this name '})

    def __str__(self):
        return self.name


    class Meta:
        managed = apps.is_installed('dj_dynamic_templates')
        db_table = 'dj_dynamic_templates__mail_template'
        verbose_name = 'DJ Dynamic Template - Mail Template'
        verbose_name_plural = verbose_name + "'s"
        permissions = (
            ('can_view_inactive_objects', 'Can view Inactive Objects'),
            ('can_sync_templates', 'Can Sync Templates'),
            ('can_view_created_by', 'Can View Created By'),
            ('can_view_history', 'Can View History')
        )

