from docplex.mp.model import Model
from statistics import mean


def get_distance(routes_df, start, destination):
    s = getattr(start, 'geocode', start)
    d = getattr(destination, 'geocode', destination)
    row = routes_df.loc[
        (routes_df['start'] == s) &
        (routes_df['destination'] == d)
    ]
    return row['distance'].values[0]


def build_and_solve(places_df, routes_df, number_sites=3):
    print('Building and solving model')
    
    mean_dist = mean(routes_df['distance'].unique())
    p_only = places_df.loc[places_df['is_medical'] == False]
    h_only = places_df.loc[places_df['is_medical'] == True]
    
    places = list(p_only.itertuples(name='Place', index=False))

    postal_codes = p_only['postal_code'].unique()
    hospital_geocodes = h_only['geocode'].unique()

    mdl = Model(name='temporary emergency sites')
    
    ## decision variables
    places_vars = mdl.binary_var_dict(places, name='is_place')
    postal_link_vars = mdl.binary_var_matrix(postal_codes, places, 'link')
    hosp_link_vars = mdl.binary_var_matrix(hospital_geocodes, places, 'link')

    ## objective function
    # minimize hospital distances
    h_total_distance = mdl.sum(hosp_link_vars[h, p] * abs(mean_dist - get_distance(routes_df, h, p)) for h in hospital_geocodes for p in places)
    mdl.minimize(h_total_distance)

    ## constraints
    # match places with their correct postal_code
    for p in places:
        for c in postal_codes:
            if p.postal_code != c:
                mdl.add_constraint(postal_link_vars[c, p] == 0, 'ct_forbid_{0!s}_{1!s}'.format(c, p))

    # # each postal_code should have one only place
    # mdl.add_constraints(
    #     mdl.sum(postal_link_vars[c, p] for p in places) == 1 for c in postal_codes
    # )

    # # each postal_code must be associated with a place
    # mdl.add_constraints(
    #     postal_link_vars[c, p] <= places_vars[p] for p in places for c in postal_codes
    # )

    # solve for 'number_sites' places
    mdl.add_constraint(mdl.sum(places_vars[p] for p in places) == number_sites)

    ## model info
    mdl.print_information()
    stats = mdl.get_statistics()

    ## model solve
    mdl.solve(log_output=True)
    details = mdl.solve_details

    status = '''
    Model stats
      number of variables: {}
      number of constraints: {}

    Model solve
      time (s): {}
      status: {}
    '''.format(
        stats.number_of_variables,
        stats.number_of_constraints,
        details.time,
        details.status
    )

    possible_sites = [p for p in places if places_vars[p].solution_value == 1]

    return possible_sites, status
