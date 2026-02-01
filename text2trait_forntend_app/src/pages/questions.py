"""
Questions Page – Text2Trait
----------------------------

This page contains an FAQ section for common user questions
about the Text2Trait application.
"""

import dash
from dash import html
import dash_bootstrap_components as dbc

# ───────────────────────────────
# Page Registration
# ───────────────────────────────
dash.register_page(
    __name__,
    path="/questions",
    name="Questions",
    title="Questions",
)


# ───────────────────────────────
# Page Layout
# ───────────────────────────────
layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H2(
                "Below you can find the most commonly asked questions:",
                className="pb-3"
            ),

            # FAQ Accordion
            dbc.Accordion([
                dbc.AccordionItem(
                    children=[
                        html.P(
                            "The tool is designed to assist researchers in identifying "
                            "single nucleotide polymorphisms (SNPs) that may influence "
                            "the appearance of specific traits. Since this is a lengthy "
                            "and costly process, we aim to provide an easy-to-use tool "
                            "that will help accelerate decision-making."
                        ),
                    ],
                    title="What is the purpose of the application?",
                ),

                dbc.AccordionItem(
                    children=[
                        html.P(
                            "The application provides two main functionalities. "
                            "The first is accessible directly from the homepage, "
                            "allowing users to search for a specific trait "
                            "(optionally a gene) in the database. "
                            "The second functionality enables users to browse "
                            "all knowledge gathered so far. Both features aim "
                            "to simplify knowledge representation, making it "
                            "easier for users to obtain meaningful information."
                        ),
                    ],
                    title="How to use the application?",
                ),

                dbc.AccordionItem(
                    children=[
                        html.P(
                            "The application is developed by the Faculty of Science "
                            "and Engineering of the University."
                        ),
                    ],
                    title="Who are the authors?",
                ),
            ], start_collapsed=True),

            # Contact Section
            html.H4(
                "If you would like more answers, please contact us at: "
                "kumarsaurabh.singh@maastrichtuniversity.nl",
                className="p-3 mt-4"
            )
        ])
    ])
])