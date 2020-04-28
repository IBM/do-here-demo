import dash_html_components as html

from config import demo_title, demo_subtitle, demo_description

page_header = html.Header(
  className='max-header',
  children=[
    html.A(
      className='max-header-name',
      href='/',
      title=demo_description,
      children=[
        html.Span(
          className='max-header-name-prefix',
          children=[demo_title]
        ),
        demo_subtitle
      ]
    ),
    html.Div(
      className='max-header-sub',
      children=[
        html.Span(
          className='max-header-sub-text',
          children=[demo_description]
        )
      ]
    ),
    html.Div(
      className='max-header-filler',
      children=[
        html.Button(
          title='Toggle info',
          **{ 'data-max-panel': 'max-info-panel' },
          children=[
            html.Img(
              src='./assets/icon-info.svg',
              className='max-panel-expand-icon'
            ),
            html.Img(
              src='./assets/icon-cross.svg',
              className='max-panel-collapse-icon'
            )
          ]
        )
      ]
    )
  ]
)
