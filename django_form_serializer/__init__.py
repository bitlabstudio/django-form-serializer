class DjangoFormSerializer(object):

    def get_fieldsets(self, fieldsets):
        result = []
        for item in fieldsets:
            fieldset = {}
            title = item[0]
            fields = item[1]['fields'] if type(
                item[1]['fields']) == tuple else (item[1]['fields'],)
            fieldset['title'] = title
            fieldset['fields'] = fields
            result.append(fieldset)
        return result

    def get_choices(self, django_input_type, form, key):
        if django_input_type in [
                'RadioSelect', 'LazySelect', 'Select',
                'CheckboxSelectMultiple'
                ]:
            if type(form.fields[key].choices) == list:
                choices = form.fields[key].choices
                return [
                    (str(item[0]), str(item[1]))
                    for item in choices
                ]
            else:  # 'Select'
                queryset = form.fields[key].queryset
                return [
                    (str(instance.id), str(instance))
                    for instance in queryset.all()
                ]
        else:
            return None

    def get_initial_value(self, key, form):
        form_field = form.fields[key]
        field_type = form_field.__class__.__name__
        initial_value = None
        if field_type == 'ImageField':
            try:
                initial_value = form.initial[key].url
            except:
                initial_value = None
        elif field_type == 'LazyTypedChoiceField':
            initial_value = form.initial.get(key).code if form.initial.get(
                key) else None
        elif field_type == 'TagField':
            if form.initial[key]:
                initial_value = list(form.initial[key].values(
                    'tag__slug', 'tag__name'))
        elif field_type in ['TypedChoiceField', 'BooleanField']:
            initial_value = form.initial.get(key)
            return initial_value
        else:
            initial_value = str(
                form.initial.get(key)) if form.initial.get(key) else None
        return (initial_value if initial_value else '')

    def get_placeholder(self, key, form):
        if key == 'tags':
            return ''
        elif form.fields[key].widget.attrs.get('placeholder'):
            return form.fields[key].widget.attrs['placeholder']
        else:
            return form.fields[key].help_text

    def parse(self, form):
        result = {}
        result['fields'] = {}
        result['fieldsets'] = self.get_fieldsets(form.Meta.fieldsets)
        keys = form.fields.keys()

        for key in keys:
            input_element = {}
            choices = None
            value = None
            disabled = False

            disabled = form.fields[key].disabled
            django_input_type = form.fields[key].widget.__class__.__name__
            choices = self.get_choices(django_input_type, form, key)
            value = self.get_initial_value(key, form)
            label = form.fields[key].label
            placeholder = self.get_placeholder(key, form)

            if key == 'tags':
                label = "Tags"

            input_element['type'] = django_input_type
            input_element['choices'] = choices
            input_element['value'] = value
            input_element['label'] = label
            input_element['placeholder'] = placeholder
            input_element['disabled'] = disabled

            result['fields'][key] = input_element
        return result
