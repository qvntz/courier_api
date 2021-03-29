from flask import make_response


def response_200(info):
    return make_response(info, 200)


def response_201(info):
    return make_response(info, 201)


def response_400(info):
    return make_response({"validation_error": info}, 400)


def response_400_without_info():
    return make_response("", 400)


def response_404():
    return make_response("", 404)
