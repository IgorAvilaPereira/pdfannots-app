import subprocess
import os

from flet import Column, ElevatedButton, Icons, FilePicker, Page, Ref, FilePickerResultEvent, Row, \
    app, Container, padding, border_radius, \
    CrossAxisAlignment, ScrollMode, RadioGroup, Radio, Markdown, \
    MarkdownExtensionSet, AlertDialog, Text, TextButton, TextField, MainAxisAlignment

from pdfannots.cli import main_igor

import flet as ft


def main(page: Page):
    page.title = "PDFannots App"
    page.scroll = "adaptive"
    page.window_width = 190
    page.window_height = 210
    page.window_min_width = 190
    page.window_min_height = 210

    def request_preview(e):
        preview.current.value = main_igor(radio_group.value)
        markdown_pane.width = 600
        markdown_pane.visible = True
        page.window_width = 1100
        page.window_height = 600
        page.update()

    path_export = Ref[TextField]()

    def save_markdown(e, modal):
        with open(path_export.current.value, 'w') as markdown_file:
            markdown_file.write(preview.current.value)        
        page.close(modal)
        page.update()

    
    def export_markdown(e):
        print("oi")
        dlg_modal = AlertDialog(
                modal=True,
                title=Text("Exporting annotations"),
                content=Column([
                    Text("Do you want to save exported PDF annotations as markdown?"),
                    TextField(value=os.path.expanduser("~")+"/export.md", ref=path_export)]
                ),
                actions=[
                    TextButton("Save", on_click=lambda e: save_markdown(e, dlg_modal)),
                    TextButton("Close", on_click=lambda e: page.close(dlg_modal))
                ],
                on_dismiss=lambda e: print("Fechando PopUp!"),
                actions_alignment=MainAxisAlignment.END,
        )
        page.open(dlg_modal)

    export_button = Ref[ElevatedButton]()
    menu = Container(
        bgcolor="#E8EFF8",
        border_radius=border_radius.all(10),
        padding=padding.all(10),
        content=Column(
            spacing=10,
            controls=[
                ElevatedButton(
                    "Select files...",
                    icon=Icons.FOLDER_OPEN,
                    on_click=lambda _: file_picker.pick_files(allow_multiple=True, allowed_extensions=['pdf']),
                ),
                ElevatedButton(
                    "Export",
                    icon=Icons.IMPORT_EXPORT,
                    ref=export_button,
                    on_click=lambda e: export_markdown(e),
                    disabled=True,
                ),
            ]
        )
    )

    files = Ref[Column]()
    radio_group = RadioGroup(content=Column(ref=files), on_change=lambda e: request_preview(e))
    preview = Ref[Markdown]()

    pdf_list = Container(
        visible=True,
        width=None,
        content=Row(
            scroll=ScrollMode.ADAPTIVE,
            controls=[radio_group]
        )
    )

    markdown_pane = Container(
        visible=False,
        width=None,
        padding=15,
        content=Row(
            wrap=True,
            controls=[Markdown(
                ref=preview,
                selectable=True,
                extension_set=MarkdownExtensionSet.GITHUB_WEB,
                on_tap_link=lambda e: page.launch_url(e.data)
            )]
        )
    )

    def file_picker_result(e: FilePickerResultEvent):
        pdf_list.visible = False if e.files is None else True
        # preview_button.current.disabled = True if e.files is None else False
        export_button.current.disabled = True if e.files is None else False
        if e.files is not None:
            pdf_list.width = 300

            if page.window_width < 500:
                page.window_width = 500
            if page.window_height < 500:
                page.window_height = 500

            for f in e.files:
                files.current.controls.append(
                    Radio(value=f.path, label=f.name)
                )

        page.update()

    file_picker = FilePicker(on_result=file_picker_result)
    page.overlay.append(file_picker)

    page.add(
        Row(
            vertical_alignment=CrossAxisAlignment.START,
            scroll=ScrollMode.HIDDEN,
            controls=[
                menu,
                pdf_list,
                markdown_pane
            ]
        )
    )
ft.app(main)
