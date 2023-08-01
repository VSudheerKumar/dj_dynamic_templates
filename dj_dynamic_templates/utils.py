from django.utils.html import format_html
from django.contrib import admin
from django.contrib import messages

from django.conf import settings

import os


class CategoryModelAdminUtils:

    # -----------------------utils------------------------------
    def make_dir(self, request, obj, change=False):
        if change:
            return os.rename(self.model.objects.get(code=obj.code).get_directory_path(), obj.get_directory_path())
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
            if obj.is_active and self.make_dir(request, obj):
                messages.info(request, f"Successfully Created the folder with {obj.name} in {obj.app_name} Directory")

    # -------------------------CRUD----------------------------
    def _pre_delete_model(self, request, obj):
        try:
            os.rmdir(obj.get_directory_path())
            return True
        except FileNotFoundError:
            messages.warning(request, 'Directory Does not Exists')
        except OSError:
            messages.error(request, f'Directory named "{obj.name}" contains some templates')
            return False

    def _post_save_model(self, request, obj, form, change):
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
            
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            kwargs['queryset'] = Category.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # ----------------------actions----------------------------------
    @admin.action(description='Sync the templates')
    def sync_templates(self, request, queryset):
        for obj in queryset:
            obj.set_template(re_sync=True)

    @admin.action(description='Hard delete the templates', permissions=['delete'])
    def hard_delete(self, request, queryset):
        deleted = 0
        for obj in queryset:
            obj.delete()
            deleted += 1
        messages.info(request, f"Successfully Hard deleted the {deleted} object{'s' if deleted > 1 else ''}")

    # -----------------------CRUD------------------------------------
