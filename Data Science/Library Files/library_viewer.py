
import json
import os
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, HTML


FILE = "student_library.json"


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

        self.w_edit_name = widgets.Text(
            description='Structure:',
            layout=widgets.Layout(width='500px')
        )
        
        self.w_edit_description = widgets.Textarea(
            description='Description:',
            layout=widgets.Layout(width='700px', height='120px')
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
        
        self.edit_box = widgets.VBox([
            self.w_edit_name,
            self.w_edit_description,
            widgets.HBox([
                self.btn_save_edit,
                self.btn_cancel_edit
            ]),
            self.edit_out
        ])
        
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

        return results

    # ---------------------------------------------
    # DISPLAY
    # ---------------------------------------------

    def display_entry(self, entry, index):

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

        display(HTML(f"""
        <div style="
            border:2px solid #9E1B34;
            border-radius:14px;
            padding:20px;
            margin-top:18px;
            background:#F8F6F2;
            max-width:900px;
            font-family:system-ui;
        ">

            <div style="
                font-size:24px;
                font-weight:700;
                color:#9E1B34;
                margin-bottom:12px;
            ">
                {entry.get('General Structure', '')}
            </div>

            <div style='margin-bottom:8px;'>
                <b>Structure Type:</b>
                {entry.get('Structure Type', '')}
            </div>

            <div style='margin-bottom:8px;'>
                <b>Library:</b>
                {entry.get('Library', '') or 'Python Default'}
            </div>

            <div style='margin-bottom:8px;'>
                <b>Number of Arguments:</b>
                {entry.get('Number of Arguments', '')}
            </div>

            <div style='margin-bottom:8px;'>
                <b>Description:</b>
                {entry.get('Brief Description', '')}
            </div>

            <div style='margin-bottom:8px;'>
                <b>Additional Details:</b>
                {entry.get('Additional Details', '')}
            </div>

            <div style='margin-bottom:8px;'>
                <b>Source:</b>
                {entry.get('Source', '')}
            </div>

            <div style='margin-top:14px;'>
                <b>Inputs:</b>
                {inputs_html}
            </div>

            <div style='margin-top:18px;color:#777;font-size:13px;'>
                Saved at {entry.get('Timestamp', '')}
            </div>

        </div>
        """))

        btn_edit = widgets.Button(
            description='Edit',
            button_style='warning',
            icon='edit',
            layout=widgets.Layout(width='100px')
        )
        
        btn_delete = widgets.Button(
            description='Delete',
            button_style='danger',
            icon='trash',
            layout=widgets.Layout(width='100px')
        )
        
        btn_edit.on_click(lambda b, i=index: self.edit_entry(i))
        btn_delete.on_click(lambda b, i=index: self.delete_entry(i))

        display(
            widgets.HBox([
                btn_edit,
                btn_delete
            ])
        )

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

            for index, entry in results:

                self.display_entry(
                    entry,
                    index
                )

    # ---------------------------------------------
    # MAIN DISPLAY
    # ---------------------------------------------

    def display(self):

        display(HTML(
            """
            <div style='font-size:28px;font-weight:700;color:#9E1B34;margin-bottom:14px;'>
                Student Library Viewer
            </div>
            """
        ))

        display(
            widgets.HBox([
                self.w_search,
                self.w_type,
                self.w_library
            ])
        )

        display(self.out)

        display(self.edit_box)

        self.refresh_results()

    def save_library(self):

        with open(FILE, "w") as f:
            json.dump(self.data, f, indent=2)

        print("saving:", self.data)
    
    
    def delete_entry(self, index):
    
        del self.data[index]
    
        self.save_library()
    
        self.refresh_results()

    def edit_entry(self, index):

        entry = self.data[index]
    
        self.w_edit_name.value = entry.get(
            "General Structure",
            ""
        )
    
        self.w_edit_description.value = entry.get(
            "Brief Description",
            ""
        )
    
        self.w_edit_index = index
    
        self.edit_box.layout.display = "block"

    def save_edit(self, _):
    
        index = self.w_edit_index
    
        self.data[index][
            "General Structure"
        ] = self.w_edit_name.value
    
        self.data[index][
            "Brief Description"
        ] = self.w_edit_description.value
    
        self.save_library()
    
        self.edit_box.layout.display = "none"
    
        self.refresh_results()
    
    
    def cancel_edit(self, _):
    
        self.edit_box.layout.display = "none"