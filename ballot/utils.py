from flask import jsonify
import json


def jsonify_ballots(ballots):
    ballot_list = []
    for ballot in ballots:
        json = jsonify({
            "id": str(ballot.ballot_id),
            "name": str(ballot.name),
            "vote_type": str(ballot.vote_type),
            "description": str(ballot.description),
            "start_date": str(ballot.start_date),
            "end_date": str(ballot.end_date),
            "start_time": str(ballot.start_time),
            "end_time": str(ballot.end_time)
        })
        ballot_list.append(json)

    return ballot_list
