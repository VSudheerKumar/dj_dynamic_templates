import datetime

from django.utils.html import format_html
from django.contrib import admin
from django.contrib import messages
from django.dispatch import Signal
from django.conf import settings

import os


file_or_dir_remove_signal = Signal()

class CategoryModelAdminUtils:

    # -----------------------utils------------------------------
    def make_dir(self, request, obj, change=False):
        if change:
            old_obj = self.model.objects.get(code=obj.code)
            if old_obj.get_directory_path() != obj.get_directory_path():
                file_or_dir_remove_signal.send(sender=None, path=old_obj.get_directory_path(), name=old_obj.name)
                messages.info(request, f'Successfully changed Directory name "{old_obj.name}" to "{obj.name}"')
                return os.rename(old_obj.get_directory_path(), obj.get_directory_path())
        if not os.path.exists(f'{settings.BASE_DIR}/{obj.app_name}/templates/'):
            os.mkdir(f'{settings.BASE_DIR}/{obj.app_name}/templates/')
        try:
            os.mkdir(obj.get_directory_path())
            return True
        except FileExistsError:
            messages.warning(request, f'folder named "{obj.name}" already exists in "{obj.app_name}" Directory')
            return False

    # -------------------------fields----------------------------
    @classmethod
    def is_directory_exist(cls, obj):
        if os.path.exists(obj._get_directory_path()):
            return True
        return False

    @staticmethod
    def files_in_directory(obj):
        return format_html("<ol>" + "".join(['<li>{file_name}</li>'.format(file_name=file) for file in obj.get_files_in_dir()]) + "</ol>")

    # -------------------------actions----------------------------
    @admin.action(description='Make Directory')
    def create_directory(self, request, queryset):
        for obj in queryset:
            if self.make_dir(request, obj):
                messages.info(request, f"Successfully Created the folder with {obj.name} in {obj.app_name} Directory")

    # -------------------------CRUD----------------------------
    def _pre_delete_model(self, request, obj):
        try:
            if os.path.exists(obj.get_directory_path()):
                os.rmdir(obj.get_directory_path())
                return True
            else:
                messages.warning(request, 'Directory Does not Exists')
        except OSError:
            messages.error(request, f'Directory named "{obj.name}" contains some templates')
            return False

    def _pre_save_model(self, request, obj, form, change):
        if any(button in request.POST for button in ['_addanother', '_save', '_continue']):
            self.make_dir(request, obj, change=change)


class MailTemplateModelAdminUtils:

    # -------------------------fields----------------------------
    @staticmethod
    def template(obj):
        return format_html(f"<a href='/admin/dj_dynamic_templates/mailtemplate/template-view/{obj.code}/' data-popup='yes' class='related-widget-wrapper-link'>Click Here to View Template</a>")

    def template_status(self, obj):
        if not obj.is_active:
            return "InActive"
        elif not CategoryModelAdminUtils.is_directory_exist(obj.category):
            return "Directory Does Not Exist"
        else:
            try:
                file = open(obj.get_template_path(), "r")
                file_data = file.read()
                for block, props in zip(self.template_blocks, self.template_check_props.keys()):
                    self.template_check_props[props].start_index = file_data.find(block) + self.template_check_props[props].length_of_start_key
                    self.template_check_props[props].end_index = file_data.find('{% endblock %}', self.template_check_props[props].start_index)
                value = []
                for props in self.template_check_props.keys():
                    if file_data[self.template_check_props[props].start_index: self.template_check_props[
                        props].end_index].strip() != getattr(obj, props.replace('props', 'content')).replace('\r', '').strip():
                        value.append(f'{props.split("_")[0].title()} not Synced')
                return ", ".join(value) or "Synced"
            except FileNotFoundError:
                return "File Does Not Exist"

    # ----------------------actions----------------------------------
    @admin.action(description='Sync the templates')
    def sync_templates(self, request, queryset):
        for obj in queryset.filter(is_active=True):
            obj.set_template(re_sync=True)

    # -----------------------CRUD------------------------------------
