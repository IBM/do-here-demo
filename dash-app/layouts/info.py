
import dash_core_components as dcc
import dash_html_components as html

from config import demo_title, demo_subtitle, demo_description

info_panel_content = '''
# {title} {subtitle}

{description}

[Demo GitHub repository](https://github.com/IBM/do-here-demo)

&nbsp;

**IBM Technologies**

- [IBM Decision Optimization](https://www.ibm.com/analytics/decision-optimization)
- [Watson Studio](https://www.ibm.com/cloud/watson-studio)
- [Watson Machine Learning](https://www.ibm.com/cloud/machine-learning)
- [DOcplex examples](https://github.com/IBMDecisionOptimization/docplex-examples)

&nbsp;

**HERE Technologies**

- [HERE.com API Key](https://developer.here.com/sign-up)
- [HERE Maps](https://developer.here.com/products/maps)
- [HERE Geocoding and Search](https://developer.here.com/products/geocoding-and-search)
- [Integrate interactive maps and location features into your application](https://developer.here.com/documentation/)

'''.format(
  title=demo_title,
  subtitle=demo_subtitle,
  description=demo_description
)

info_panel = html.Aside(
  id='max-info-panel',
  className='max-panel',
  children=[
    dcc.Markdown(info_panel_content)
  ]
)
