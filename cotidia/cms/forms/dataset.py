import json

from django import forms

from codemirror import CodeMirrorTextarea

from cotidia.cms.models import PageDataSet

class PageDataSetAddForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'errorfield'
    initial = """[
  {
    "fieldset":"Page content",
    "fields":[
        {
            "name":"description",
            "type":"textfield",
            "required":false
        }
    ]
  },
  {
    "fieldset":"Meta data",
    "fields":[
        {
            "name":"meta_title",
            "type":"charfield",
            "required":false
        },
        {
            "name":"meta_description",
            "type":"textfield",
            "required":false
        }
    ]
  }
]
"""
    name = forms.CharField(
        label='',
        max_length=255,
        widget=forms.TextInput(attrs={'class':'form__text'})
        )

    config = forms.CharField(
        widget=CodeMirrorTextarea(
            mode="javascript",
            theme="cobalt",
            config={ 'fixedGutter': True, 'lineNumbers': True }),
        initial=initial)
    class Meta:
        model=PageDataSet
        exclude = ()

    def clean_config(self):

        config = self.cleaned_data['config']
        try:
            json.loads(config)
        except:
            raise forms.ValidationError(('The JSON string is invalid'))


        ############################
        # TO-DO                    #
        # Validate all fields data #
        ############################


        return config

class PageDataSetUpdateForm(PageDataSetAddForm):
    pass
