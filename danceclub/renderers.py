from bootstrap3.renderers import FieldRenderer, FormsetRenderer

class ConcordiaFormsetRenderer(FormsetRenderer):
    def render_form(self, form, **kwargs):
        html = super(ConcordiaFormsetRenderer, self).render_form(form, **kwargs)
        if self.layout == 'tabular':
            return '<tr>{html}</tr>'.format(html=html)
        return html

    def render_form_labels(self):
        form = self.formset.forms[0]
        labels = []
        for field in form:
            if field.is_hidden:
                continue
            labels.append('<td>{label}</td>'.format(label=field.label))
        html = '\n'.join(labels)
        return '<tr>{html}</tr>'.format(html=html)

    def render_forms(self):
        html = super(ConcordiaFormsetRenderer, self).render_forms()
        if self.layout == 'tabular':
            labels = self.render_form_labels()
            return '<table class="table table-bordered table-hover table-striped">{labels}{html}</table>'.format(labels=labels, html=html)
        return html

class ConcordiaFieldRenderer(FieldRenderer):
    def wrap_label_and_field(self, html):
        if self.layout == "tabular":
            field_class = self.get_field_class() or ''
            html = '<td class="{klass}">{html}</td>'.format(klass=field_class, html=html)
            return html

        return super(ConcordiaFieldRenderer, self).wrap_label_and_field(html)

    def get_label(self):
        if self.layout == 'tabular':
            return None
        return super(ConcordiaFieldRenderer, self).get_label()