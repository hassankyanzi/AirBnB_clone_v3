#!/usr/bin/python3
"""
route for handling Place objects and operations
"""
from flask import jsonify, abort, request
from api.v1.views import app_views, storage
from models.place import Place


@app_views.route("/cities/<city_id>/places", methods=["GET"],
                 strict_slashes=False)
def places_by_city(city_id):
    """
    retrieves all Place objects by city
    :return: json of all Places
    """
    place_list = []
    city_obj = storage.get("City", str(city_id))
    if city_obj is None:
        abort(404)
    for obj in city_obj.places:
        place_list.append(obj.to_json())

    return jsonify(place_list)


@app_views.route("/cities/<city_id>/places", methods=["POST"],
                 strict_slashes=False)
def place_create(city_id):
    """
    create place route
    :return: newly created Place obj
    """
    place_json = request.get_json(silent=True)
    if place_json is None:
        abort(400, 'Not a JSON')
    if "user_id" not in place_json:
        abort(400, 'Missing user_id')
    if "name" not in place_json:
        abort(400, 'Missing name')
    if not storage.get("User", place_json["user_id"]):
        abort(404)
    if not storage.get("City", str(city_id)):
        abort(404)

    place_json["city_id"] = city_id

    new_place = Place(**place_json)
    new_place.save()
    resp = jsonify(new_place.to_json())
    resp.status_code = 201

    return resp


@app_views.route("/places/<place_id>",  methods=["GET"],
                 strict_slashes=False)
def place_by_id(place_id):
    """
    gets a specific Place object by ID
    :param place_id: place object id
    :return: place obj with the specified id or error
    """

    fetched_obj = storage.get("Place", str(place_id))

    if fetched_obj is None:
        abort(404)

    return jsonify(fetched_obj.to_json())


@app_views.route("/places/<place_id>",  methods=["PUT"],
                 strict_slashes=False)
def place_put(place_id):
    """
    updates specific Place object by ID
    :param place_id: Place object ID
    :return: Place object and 200 on success, or 400 or 404 on failure
    """
    place_json = request.get_json(silent=True)

    if place_json is None:
        abort(400, 'Not a JSON')

    fetched_obj = storage.get("Place", str(place_id))

    if fetched_obj is None:
        abort(404)

    for key, val in place_json.items():
        if key not in ["id", "created_at", "updated_at", "user_id", "city_id"]:
            setattr(fetched_obj, key, val)

    fetched_obj.save()

    return jsonify(fetched_obj.to_json()), 200


@app_views.route("/places/<place_id>",  methods=["DELETE"],
                 strict_slashes=False)
def place_delete_by_id(place_id):
    """
    deletes Place by id
    :param place_id: Place object id
    :return: empty dict with 200 or 404 if not found
    """

    fetched_obj = storage.get("Place", str(place_id))

    if fetched_obj is None:
        abort(404)

    storage.delete(fetched_obj)
    storage.save()

    return jsonify({}), 200


@app_views.route("/places_search", methods=["POST"],
                 strict_slashes=False)
def get_places_with_filter(states, cities, amenities):
    """
    retrieves all Place objects filtering by states, cities,
    or amenities
    :return: json of all Places
    """
    data_json = request.get_json(silent=True)

    if data_json is None:
        abort(400, 'Not a JSON')

    places_list = []
    places = storage.get("Place")
    if places is not None:
        states_filter_list = data_json["states"]
        cities_obj = storage.get("City")
        if states_filter_list is not None:
            for place in places:
                for city_obj in cities_obj:
                    if city_obj.id == place.city_id and city_obj.state_id in states_filter_list:
                        places_list.append(place.to_json())

        cities_filter_list = data_json["cities"]
        if cities_filter_list is not None:
            for place in places:
                if place.city_id in cities_filter_list:
                    places_list.append(place.to_json())

        amenities_filter_list = data_json["amenities"]
        if amenities_filter_list is not None:
            for place in places:
                amenities_list = place.amenities
                if amenities_list is not None:
                    for amenity_obj in amenities_list:
                        if amenity_obj.id in amenities_filter_list:
                            places_list.append(place.to_json())

    return jsonify(places_list)
