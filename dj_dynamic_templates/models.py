
from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.contrib import messages

from markdownx.models import MarkdownxField

import os
from .validators import *


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    remarks = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    parent_obj = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    code = models.PositiveBigIntegerField(editable=False)

    code_filter = {}

    def get_code(self):
        return self.__class__.objects.filter(**self.code_filter).count() + 1
    
    def pre_save(self):
        pass
    
    def post_save(self):
        pass

    def soft_save(self):
        if not self.pk:
            self.code = self.get_code()
        else:
            self.__class__.objects.filter(id=self.id).update(is_active=False)
            self.parent_obj_id = self.id
            self.pk = None


    class Meta:
        abstract = True


class Category(BaseModel):
    
    parent_obj = is_active = None

    app_name = models.CharField(max_length=50, validators=[validate_app], help_text="Enter the App name to save template in that folder")
    name = models.CharField(max_length=50, help_text="With this name an folder will be created in this App")

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
        if base_filter.exists():
            raise ValidationError({'name': 'Folder Already Exist'})

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.pk:
            self.code = self.get_code()
        return super(Category, self).save(force_insert=force_insert, force_update=force_update, update_fields=update_fields, using=using)

    def __str__(self):
        return f'{self.app_name} - {self.name}'


    class Meta:
        managed = apps.is_installed('dj_dynamic_templates')
        db_table = 'dj_dynamic_templates__category'
        verbose_name = db_table.replace('_', ' ').title()
        verbose_name_plural = verbose_name.replace('category', 'categories')


class MailTemplate(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, help_text='Select the category where you want to save the template', related_name='mail_template_category')

    body_content = MarkdownxField()
    style_content = models.TextField(blank=True)
    script_content = models.TextField(blank=True)

    name = models.CharField(max_length=50, help_text='Entered name will treated as template file name, A template file is created with this file name')

    deleted_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, related_name='ddt_mail_template_deleted_by')
    deleted_at = models.DateTimeField(null=True, blank=True)

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
        if not self.parent_obj:
            file = open(self.get_template_path(), "x")
        else:
            try:
                if not re_sync:
                    os.rename(self.parent_obj.get_template_path(), self.get_template_path())
                file = open(self.get_template_path(), "w")
            except FileNotFoundError:
                file = open(self.get_template_path(), "x")
        file.write(content)
        file.close()

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.deleted_by or self.deleted_at:
            return super(MailTemplate, self).save(force_insert=force_insert, force_update=force_update, update_fields=update_fields, using=using)
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
        verbose_name = db_table.replace('_', ' ').title()
        verbose_name_plural = verbose_name + "'s"