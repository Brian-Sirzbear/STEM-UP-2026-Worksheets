import ipywidgets as widgets
from IPython.display import display, HTML
import numpy as np


class LibraryUI:

    def __init__(self):

        self.style_lbl = {
            'description_width': '160px'
        }

        self.CODE_STRUCTURES = [
            'Please Select',
            'Operation',
            'Function',
            'Method',
            'Index',
            'Other'
        ]

        self.MAX_INPUTS = 6

        self.DATA_TYPES = [
            'integer',
            'float',
            'integer/float',
            'string',
            'list',
            'array',
            'list/array',
            'table',
            'anything'
        ]

        self.ALPHABET = [
            'a', 'b', 'c', 'd', 'e', 'f'
        ]

        self.SAMPLE_ROLES = [
            'a column header',
            'a string containing (another input)',
            'a function name',
            'a math expression'
        ]

        self.STATUS = [
            'Required',
            'Optional'
        ]

        self.create_identity_widgets()
        self.create_input_widgets()
        self.create_buttons()

    # ---------------------------------------------
    # IDENTITY WIDGETS
    # ---------------------------------------------

    def create_identity_widgets(self):

        self.w_struc = widgets.Dropdown(
            description='Structure Type:',
            options=self.CODE_STRUCTURES,
            style=self.style_lbl,
            layout=widgets.Layout(width='600px')
        )

        self.w_name = widgets.Text(
            description='General Structure:',
            placeholder='e.g. print(a, b)',
            style=self.style_lbl,
            layout=widgets.Layout(width='600px')
        )

        self.w_library = widgets.Text(
            description='Library:',
            placeholder='e.g. numpy, datascience, etc.',
            style=self.style_lbl,
            layout=widgets.Layout(width='600px')
        )

        self.w_num_inputs = widgets.Text(
            description='Number of Arguments:',
            placeholder='e.g. 4 (if unlimited, enter -1)',
            style=self.style_lbl,
            layout=widgets.Layout(width='600px')
        )

        self.w_description = widgets.Textarea(
            description='Brief Description:',
            placeholder='e.g. puts arguments to output',
            style=self.style_lbl,
            layout=widgets.Layout(
                width='600px',
                height='90px'
            )
        )

        self.w_additional = widgets.Textarea(
            description='Any additional details:',
            placeholder='Optional notes...',
            style=self.style_lbl,
            layout=widgets.Layout(
                width='600px',
                height='110px'
            )
        )

        self.w_source = widgets.Text(
            description='Where did you learn this:',
            placeholder='e.g. Lab 2, Question 4',
            style=self.style_lbl,
            layout=widgets.Layout(width='600px')
        )

    # ---------------------------------------------
    # INPUT WIDGETS
    # ---------------------------------------------

    def create_input_widgets(self):

        self.inputs_widgets = []

        for i in range(self.MAX_INPUTS):

            identifier_w = widgets.Text(
                description="The Input",
                placeholder=f"e.g. {self.ALPHABET[i]}",
                style={'description_width': '70px'},
                layout=widgets.Layout(width='150px')
            )

            role_w = widgets.Text(
                description="represents:",
                placeholder='e.g. ' + np.random.choice(self.SAMPLE_ROLES),
                style={'description_width': '70px'},
                layout=widgets.Layout(width='320px')
            )

            type_w = widgets.Dropdown(
                description='of Type:',
                options=['---'] + self.DATA_TYPES,
                style={'description_width': '50px'},
                layout=widgets.Layout(width='150px')
            )

            status_w = widgets.Dropdown(
                description='and Status:',
                options=['---'] + self.STATUS,
                style={'description_width': '65px'},
                layout=widgets.Layout(width='150px')
            )

            assume_w = widgets.Text(
                description=". If omitted, is assumed to be:",
                placeholder="e.g. 0",
                style={'description_width': '170px'},
                layout=widgets.Layout(width='250px')
            )

            self.inputs_widgets.append((
                identifier_w,
                role_w,
                type_w,
                status_w,
                assume_w
            ))

    # ---------------------------------------------
    # BUTTONS / OUTPUTS
    # ---------------------------------------------

    def create_buttons(self):

        self.btn_submit = widgets.Button(
            description="Add Entry",
            button_style='danger',
            icon='plus'
        )

        self.out_submit = widgets.Output()

    # ---------------------------------------------
    # DISPLAY
    # ---------------------------------------------

    def display_interface(self):

        display(
            widgets.HTML(
                '''
                <div style="
                    font-size:20px;
                    font-weight:600;
                    color:#9E1B34;
                    margin-bottom:6px;
                ">
                    Add a new entry to your library:
                </div>
                '''
            )
        )

        display(
            self.w_struc,
            self.w_name,
            self.w_library,
            self.w_num_inputs,
            self.w_description,
            self.w_additional,
            self.w_source
        )

        display(
            widgets.HTML(
                '''
                <div style="
                    font-size:20px;
                    font-weight:600;
                    color:#9E1B34;
                    margin-bottom:6px;
                    margin-top:15px;
                ">
                    What does each input represent?
                </div>
                '''
            )
        )

        for row in self.inputs_widgets:

            display(
                widgets.HBox(
                    list(row),
                    layout=widgets.Layout(gap='50px')
                )
            )

        display(
            widgets.HTML(
                '''
                <div style="
                    color:#888;
                    font-size:15px;
                    margin-top:10px;
                ">
                    Leave unused rows blank.
                </div>
                '''
            )
        )

        display(
            self.btn_submit,
            self.out_submit
        )

    # ---------------------------------------------
    # MESSAGES
    # ---------------------------------------------

    def show_errors(self, errors):

        with self.out_submit:

            self.out_submit.clear_output()

            display(HTML(
                "<br>".join(
                    f'<div style="color:#9E1B34;font-weight:bold;">⚠️ {e}</div>'
                    for e in errors
                )
            ))

    def show_success(self, entry):

        with self.out_submit:

            self.out_submit.clear_output()

            display(HTML(f"""
            <div style="
                background:#F5F2EC;
                border:2px solid #9E1B34;
                border-radius:12px;
                padding:20px;
                max-width:650px;
                font-family:system-ui;
            ">

                <div style="
                    font-size:22px;
                    font-weight:700;
                    color:#9E1B34;
                    margin-bottom:10px;
                ">
                    ✅ Entry Added
                </div>

                <div>
                    <b>General Structure:</b>
                    {entry["General Structure"]}
                </div>

                <div>
                    <b>Structure Type:</b>
                    {entry["Structure Type"]}
                </div>

                <div>
                    <b>Description:</b>
                    {entry["Brief Description"]}
                </div>

            </div>
            """))