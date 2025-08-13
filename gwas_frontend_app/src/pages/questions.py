import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__,
                   path='/questions',
                   name='Questions',
                   title='Questions',
)

layout = html.Div(
    [
        dbc.Row([
            dbc.Col([
                html.H2("Underneath you can find the most commonly asked questions:", className="pb-3"),
                dbc.Accordion([
                    dbc.AccordionItem([
                        html.P("The tool is designed to assist researchers in identifying single nucleotide polymorphisms (SNPs)" \
                        " that may influence the appearance of specific traits. Since this is a lengthy and costly process," \
                        " we aim to provide an easy-to-use tool that will help accelerate decision-making."),
                    ],
                    title="What is the purpose of the application?",
                    ),
                    dbc.AccordionItem([
                        html.P("The application provides two main functionalities. The first is accessible directly from the homepage," \
                        " allowing users to search for a specific trait (optionally a genome) in the database." \
                        " The second functionality enables users to search through all the knowledge we have gathered so far." \
                        " Both features aim to simplify knowledge representation, making it easier for users to obtain the meaningful information they need."),
                        ],
                        title="How to use the appliction?",
                    ),
                    dbc.AccordionItem([
                        html.P("Application is developed by Faculty of Science and Engineering of University in collaboration with XYZ."),
                    ],
                        title="Who are the authors?",
                    ),
                ], start_collapsed=True
                ),
                html.H4("If you would like to more answers please contact us at this e-mail adress: e-mail.adress@gmail.com", className="p-3 mt-20")
            ])
        ])
    ]
)