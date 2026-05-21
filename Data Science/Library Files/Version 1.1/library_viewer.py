
import json
import os
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, HTML

# VERSION 1.1 (5/20/2026)

FILE = "student_library.json"

CODE_STRUCTURES = [
    'Please Select',
    'Operation',
    'Function',
    'Method',
    'Index',
    'Other'
]

class LibraryViewer:

    def __init__(self):

        self.data = self.load_library()

        self.create_widgets()

        self.connect_events()

    # ---------------------------------------------
    # DATA
    # ---------------------------------------------

    def load_library(self):

        if not os.path.exists(FILE):
            return []

        try:

            with open(FILE, "r") as f:
                data = json.load(f)

            if isinstance(data, list):
                return data

            return []

        except Exception:
            return []

    # ---------------------------------------------
    # WIDGETS
    # ---------------------------------------------

    def create_widgets(self):

        self.w_search = widgets.Text(
            description='Search:',
            placeholder='Search structures, descriptions, libraries...',
            layout=widgets.Layout(width='500px'),
            style={'description_width': '90px'}
        )

        self.w_type = widgets.Dropdown(
            description='Type:',
            options=['All'] + sorted(list({
                e.get('Structure Type', 'Other')
                for e in self.data
            })),
            value='All',
            layout=widgets.Layout(width='300px'),
            style={'description_width': '90px'}
        )

        self.w_library = widgets.Dropdown(
            description='Library:',
            options=['All'] + sorted(list({
                e.get('Library', '') or 'Python Default'
                for e in self.data
            })),
            value='All',
            layout=widgets.Layout(width='300px'),
            style={'description_width': '90px'}
        )

        self.w_sort = widgets.Dropdown(
            description='Sort:',
            options=[
                'Alphabetical',
                'Number of Arguments',
                'Source'
            ],
            value='Alphabetical',
            layout=widgets.Layout(width='300px'),
            style={'description_width': '90px'}
        )

        self.w_edit_name = widgets.Text(
            description='Structure:',
            layout=widgets.Layout(width='500px')
        )
        
        self.w_edit_description = widgets.Textarea(
            description='Description:',
            layout=widgets.Layout(width='700px', height='120px')
        )

        self.w_edit_structure_type = widgets.Dropdown(
            description='Type:',
            options=CODE_STRUCTURES,
            layout=widgets.Layout(width='400px')
        )
        
        self.w_edit_library = widgets.Text(
            description='Library:',
            layout=widgets.Layout(width='400px')
        )
        
        self.w_edit_num_args = widgets.Text(
            description='Args:',
            layout=widgets.Layout(width='400px')
        )
        
        self.w_edit_additional = widgets.Textarea(
            description='Additional:',
            layout=widgets.Layout(width='600px', height='100px')
        )
        
        self.w_edit_source = widgets.Text(
            description='Source:',
            layout=widgets.Layout(width='400px')
        )
        
        self.btn_save_edit = widgets.Button(
            description='Save Changes',
            button_style='success',
            icon='check'
        )
        
        self.btn_cancel_edit = widgets.Button(
            description='Cancel',
            button_style='warning'
        )
        
        self.edit_out = widgets.Output()

        self.w_inputs_edit_index = None
        
        self.edit_box = widgets.VBox([
            self.w_edit_structure_type,
            self.w_edit_name,
            self.w_edit_library,
            self.w_edit_num_args,
            self.w_edit_description,
            self.w_edit_additional,
            self.w_edit_source,
            widgets.HBox([
                self.btn_save_edit,
                self.btn_cancel_edit
            ]),
            self.edit_out
        ])

        self.inputs_editor_box = widgets.VBox([])
        
        self.btn_save_inputs = widgets.Button(
            description='Save Inputs',
            button_style='success'
        )
        
        self.btn_cancel_inputs = widgets.Button(
            description='Cancel',
            button_style='warning'
        )
        
        self.btn_save_inputs.on_click(self.save_inputs)
        self.btn_cancel_inputs.on_click(self.cancel_inputs)
        
        self.inputs_editor = widgets.VBox([
            self.inputs_editor_box,
            widgets.HBox([self.btn_save_inputs, self.btn_cancel_inputs])
        ])
        self.inputs_editor.layout.display = "none"
        
        self.edit_box.layout.display = "none"

        self.out = widgets.Output()

    # ---------------------------------------------
    # EVENTS
    # ---------------------------------------------

    def connect_events(self):

        self.w_search.observe(self.on_change, names='value')
        self.w_type.observe(self.on_change, names='value')
        self.w_library.observe(self.on_change, names='value')

        self.btn_save_edit.on_click(
            self.save_edit
        )
        
        self.btn_cancel_edit.on_click(
            self.cancel_edit
        )

        self.w_sort.observe(
            self.on_change,
            names='value'
        )

    def on_change(self, change):

        self.refresh_results()

    # ---------------------------------------------
    # FILTERING
    # ---------------------------------------------

    def matches_search(self, entry, query):

        if not query:
            return True

        query = query.lower()

        searchable_text = " ".join([
            str(entry.get('General Structure', '')),
            str(entry.get('Brief Description', '')),
            str(entry.get('Additional Details', '')),
            str(entry.get('Library', '')),
            str(entry.get('Source', ''))
        ]).lower()

        return query in searchable_text

    def filter_entries(self):

        results = []

        for index, entry in enumerate(self.data):

            # SEARCH
            if not self.matches_search(
                entry,
                self.w_search.value.strip()
            ):
                continue

            # TYPE
            if (
                self.w_type.value != 'All'
                and
                entry.get('Structure Type') != self.w_type.value
            ):
                continue

            # LIBRARY
            library_value = (
                entry.get('Library')
                or
                'Python Default'
            )

            if (
                self.w_library.value != 'All'
                and
                library_value != self.w_library.value
            ):
                continue

            results.append((index, entry))

        # -----------------------------------------
        # SORTING
        # -----------------------------------------
        
        if self.w_sort.value == 'Alphabetical':
        
            results.sort(
                key=lambda x:
                x[1].get(
                    'General Structure',
                    ''
                ).lower()
            )
        
        elif self.w_sort.value == 'Number of Arguments':
        
            def parse_args(entry):
        
                raw = entry.get(
                    'Number of Arguments',
                    ''
                )
        
                try:
                    return int(raw)
        
                except:
                    return 999999
        
            results.sort(
                key=lambda x:
                parse_args(x[1])
            )
        
        elif self.w_sort.value == 'Source':
        
            results.sort(
                key=lambda x:
                x[1].get(
                    'Source',
                    ''
                ).lower()
            )

        return results

    # ---------------------------------------------
    # DISPLAY
    # ---------------------------------------------

    def display_entry(self, entry, index):
    
        # -----------------------------------------
        # HEADER
        # -----------------------------------------
    
        header_html = widgets.HTML(f"""
        <div style="
            font-size:20px;
            font-weight:700;
            color:#9E1B34;
            padding:8px;
        ">
            {entry.get('General Structure', '')}
        </div>
    
        <div style="
            padding-left:8px;
            color:#666;
            margin-bottom:8px;
        ">
            {entry.get('Structure Type', '')}
            |
            {entry.get('Library', '') or 'Python Default'}
        </div>
        """)
    
        # -----------------------------------------
        # FULL DETAILS
        # -----------------------------------------
    
        inputs_html = ""
    
        for inp in entry.get('Inputs', []):
    
            inputs_html += f"""
            <div style='margin-left:20px;margin-top:8px;'>
    
                <b>{inp.get('input', '')}</b>
                → {inp.get('represents', '')}
    
                <br>
    
                <span style='color:#666;'>
                    Type: {inp.get('type', '')}
                    |
                    Status: {inp.get('status', '')}
                </span>
    
            </div>
            """
    
        details = widgets.HTML(f"""
        <div style="
            border-top:1px solid #DDD;
            margin-top:10px;
            padding-top:12px;
        ">
    
            <div><b>Description:</b>
            {entry.get('Brief Description', '')}</div>
    
            <div style='margin-top:8px;'>
            <b>Additional Details:</b>
            {entry.get('Additional Details', '')}
            </div>
    
            <div style='margin-top:8px;'>
            <b>Source:</b>
            {entry.get('Source', '')}
            </div>
    
            <div style='margin-top:12px;'>
            <b>Inputs:</b>
            {inputs_html}
            </div>
    
        </div>
        """)
    
        # -----------------------------------------
        # COLLAPSIBLE AREA
        # -----------------------------------------
    
        detail_box = widgets.VBox([details])
        detail_box.layout.display = "none"
    
        # -----------------------------------------
        # TOGGLE BUTTON
        # -----------------------------------------
    
        btn_toggle = widgets.Button(
            description='Expand',
            button_style='info',
            icon='chevron-down',
            layout=widgets.Layout(width='120px')
        )
    
        def toggle(_):
    
            if detail_box.layout.display == "none":
    
                detail_box.layout.display = "block"
    
                btn_toggle.description = "Collapse"
                btn_toggle.icon = "chevron-up"
    
            else:
    
                detail_box.layout.display = "none"
    
                btn_toggle.description = "Expand"
                btn_toggle.icon = "chevron-down"
    
        btn_toggle.on_click(toggle)
    
        # -----------------------------------------
        # ACTION BUTTONS
        # -----------------------------------------
    
        btn_edit = widgets.Button(
            description='Edit',
            button_style='warning',
            icon='edit',
            layout=widgets.Layout(width='100px')
        )
    
        btn_edit_inputs = widgets.Button(
            description='Edit Inputs',
            button_style='info',
            icon='sliders',
            layout=widgets.Layout(width='120px')
        )
    
        btn_delete = widgets.Button(
            description='Delete',
            button_style='danger',
            icon='trash',
            layout=widgets.Layout(width='100px')
        )
    
        btn_edit.on_click(
            lambda b, i=index: self.edit_entry(i)
        )
    
        btn_edit_inputs.on_click(
            lambda b, i=index: self.edit_inputs(i)
        )
    
        btn_delete.on_click(
            lambda b, i=index: self.delete_entry(i)
        )
    
        buttons = widgets.HBox([
            btn_toggle,
            btn_edit,
            btn_edit_inputs,
            btn_delete
        ])
    
        # -----------------------------------------
        # FINAL CARD
        # -----------------------------------------
    
        card = widgets.VBox([
            header_html,
            buttons,
            detail_box
        ])
    
        card.layout = widgets.Layout(
            border='2px solid #9E1B34',
            padding='16px',
            margin='8px',
            border_radius='12px'
        )
    
        return card

    def refresh_results(self):

        with self.out:

            self.out.clear_output()

            results = self.filter_entries()

            display(HTML(f"""
            <div style='margin-top:10px;margin-bottom:10px;'>
                <b>{len(results)}</b> entries found.
            </div>
            """))

            if not results:

                display(HTML(
                    """
                    <div style='color:#999;'>
                        No matching entries found.
                    </div>
                    """
                ))

                return

            cards = []

            for index, entry in results:
            
                card = self.display_entry(
                    entry,
                    index
                )
            
                cards.append(card)
            
            grid = widgets.GridBox(
                cards,
                layout=widgets.Layout(
                    grid_template_columns='repeat(2, 1fr)',
                    grid_gap='20px',
                    width='100%'
                )
            )
            
            display(grid)

    # ---------------------------------------------
    # MAIN DISPLAY
    # ---------------------------------------------

    def display(self):
    
        title = widgets.HTML("""
        <div style='font-size:28px;font-weight:700;color:#9E1B34;margin-bottom:14px;'>
            Student Library Viewer
        </div>
        """)
    
        controls = widgets.HBox([
            self.w_search,
            self.w_type,
            self.w_library,
            self.w_sort
        ])
    
        app = widgets.VBox([
            title,
            controls,
            self.out,
            self.edit_box,
            self.inputs_editor
        ])
    
        display(app)
    
        self.refresh_results()

    def save_library(self):

        with open(FILE, "w") as f:
            json.dump(self.data, f, indent=2)
    
    
    def delete_entry(self, index):
    
        del self.data[index]
    
        self.save_library()
    
        self.refresh_results()

    def edit_entry(self, index):
    
        entry = self.data[index]
    
        self.w_edit_index = index
    
        self.w_edit_structure_type.value = entry.get("Structure Type", "Operation")
        self.w_edit_name.value = entry.get("General Structure", "")
        self.w_edit_library.value = entry.get("Library", "")
        self.w_edit_num_args.value = entry.get("Number of Arguments", "")
        self.w_edit_description.value = entry.get("Brief Description", "")
        self.w_edit_additional.value = entry.get("Additional Details", "")
        self.w_edit_source.value = entry.get("Source", "")
    
        self.edit_box.layout.display = "block"

    
    def edit_inputs(self, index):

        self.inputs_editor_box.children = ()
    
        entry = self.data[index]
    
        self.w_inputs_edit_index = index
    
        self.input_rows = []
    
        rows = []
    
        for inp in entry.get("Inputs", []):
    
            name = widgets.Text(
                value=inp.get("input", ""),
                description='Input:',
                layout=widgets.Layout(width='180px')
            )
    
            rep = widgets.Text(
                value=inp.get("represents", ""),
                description='Represents:',
                layout=widgets.Layout(width='500px')
            )
    
            typ = widgets.Dropdown(
                options=[
                    '---',
                    'integer',
                    'float',
                    'integer/float',
                    'string',
                    'list',
                    'array',
                    'list/array',
                    'table',
                    'boolean',
                    'anything'
                ],
                value=inp.get("type", "---"),
                description='Type:',
                layout=widgets.Layout(width='220px')
            )
            
            status = widgets.Dropdown(
                options=[
                    '---',
                    'Required',
                    'Optional'
                ],
                value=inp.get("status", "---"),
                description='Status:',
                layout=widgets.Layout(width='220px')
            )
    
            assumed = widgets.Text(
                value=inp.get("assumed", ""),
                description='Assumed:',
                layout=widgets.Layout(width='220px')
            )
    
            row = widgets.VBox([
                widgets.HBox([name, rep]),
                widgets.HBox([typ, status, assumed]),
                widgets.HTML("<hr>")
            ])
    
            rows.append(row)
    
            self.input_rows.append(
                (name, rep, typ, status, assumed)
            )
    
        self.inputs_editor_box.children = tuple(rows)
    
        self.inputs_editor.layout.display = "block"

    def save_edit(self, _):
    
        index = self.w_edit_index
    
        self.data[index] = {
            "Structure Type": self.w_edit_structure_type.value,
            "General Structure": self.w_edit_name.value,
            "Library": self.w_edit_library.value,
            "Number of Arguments": self.w_edit_num_args.value,
            "Brief Description": self.w_edit_description.value,
            "Additional Details": self.w_edit_additional.value,
            "Source": self.w_edit_source.value,
            "Inputs": self.data[index].get("Inputs", []),
            "Timestamp": self.data[index].get("Timestamp", "")
        }
    
        self.save_library()
    
        self.edit_box.layout.display = "none"
    
        self.refresh_results()

    def save_inputs(self, _):

        index = self.w_inputs_edit_index
    
        new_inputs = []
    
        for name, rep, typ, status, assumed in self.input_rows:
    
            if not name.value.strip():
                continue
    
            new_inputs.append({
                "input": name.value,
                "represents": rep.value,
                "type": typ.value,
                "status": status.value,
                "assumed": assumed.value
            })
    
        self.data[index]["Inputs"] = new_inputs
    
        self.save_library()
    
        self.inputs_editor.layout.display = "none"
    
        self.refresh_results()
    
    def cancel_edit(self, _):
    
        self.edit_box.layout.display = "none"

    def cancel_inputs(self, _):

        self.inputs_editor.layout.display = "none"