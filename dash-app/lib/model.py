from docplex.mp.model import Model


def get_distance(routes_df, p1, p2):
    return routes_df.loc[p1.geocode + '_' + p2.geocode]['distance']

def build_and_solve(places_df, routes_df, number_sites=3):
    print('Building and solving model')

    postal_codes = places_df['postal_code'].unique()
    
    places = list(places_df.itertuples(name='Place', index=False))
    
    routes_df.set_index(['geopoints'], inplace=True)

    mdl = Model(name='temporary medical sites')

    places_vars = mdl.binary_var_dict(places, name='is_place')
    link_vars = mdl.binary_var_matrix(places, postal_codes, 'link')

    # match places with their correct postal_code
    for place in places:
        for postal in postal_codes:
            if place.postal_code != postal:
                mdl.add_constraint(link_vars[place, postal] == 0, 'ct_forbid_{0!s}_{1!s}'.format(place, postal))

    # only want one place per postal_code
    mdl.add_constraints(
        mdl.sum(link_vars[place, postal] for place in places) == 1
            for postal in postal_codes
    )

    # each postal_code must be associated with a place
    mdl.add_constraints(
      link_vars[place, postal] <= places_vars[place] for place in places for postal in postal_codes
    )

    # solve for 'number_sites' places
    mdl.add_constraint(mdl.sum(places_vars[place] for place in places) == number_sites)

    # minimize distance between places
    places_link_vars = mdl.binary_var_matrix(places, places, 'link')
    total_distance = mdl.sum(places_link_vars[c_loc, b] * get_distance(routes_df, c_loc, b) for c_loc in places for b in places)
    mdl.minimize(total_distance)

    mdl.print_information()

    mdl.solve()

    possible_sites = [p for p in places if places_vars[p].solution_value == 1]

    return possible_sites
