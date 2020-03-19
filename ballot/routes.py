from ballot.models import *
import os
import json
from datetime import date, time, datetime
import requests

from flask import request, jsonify, session
import flask_migrate
from flask_sqlalchemy import SQLAlchemy
from flask_pyoidc.provider_configuration import *

from csh_ldap import CSHLDAP
from ballot import auth
from ballot.ldap import get_groups, get_member, is_member_of_group
from ballot.utils import jsonify_ballots

from ballot import app

db = SQLAlchemy(app)
migrate = flask_migrate.Migrate(app, db)


ldap = CSHLDAP(app.config["LDAP_BIND_DN"], app.config["LDAP_BIND_PS"])


# enter UTC for time and date
@app.route("/ballot", methods=["POST"])
@auth.oidc_auth
def ballot():
    body = request.json
    name = body['name']
    vote_type = body['vote_type']
    group = body['group']
    description = body['description']
    start_date = body['start_date']
    end_date = body['end_date']
    start_time = body['start_time']
    end_time = body['end_time']

    start_date = datetime.strptime(start_date, '%m/%d/%Y')
    end_date = datetime.strptime(end_date, '%m/%d/%Y')
    start_time = datetime.strptime(start_time, '%H:%M')
    end_time = datetime.strptime(end_time, '%H:%M')

    new_ballot = Ballots(name, vote_type, group, description,
                         start_date, end_date, start_time, end_time)
    db.session.add(new_ballot)
    if vote_type == 0:
        new_yno = YNO(Ballots.query.order_by(
            Ballots.ballot_id.desc()).first().ballot_id + 1)
        db.add(new_yno)
        db.session.flush()
        db.session.commit()
        db.session.expire(new_yno)

    if vote_type == 1:
        options_string = body['options']
        options_string = options_string.split(',')
        options = []
        for option in options_string:
            options.append(int(option))

        new_alternative = Alternative(Ballots.query.order_by(
            Ballots.ballot_id.desc()).first().ballot_id + 1, options)
        db.session.add(new_alternative)
        db.session.flush()
        db.session.commit()
        db.session.expire(new_alternative)

    db.session.expire(new_ballot)

    return 200, "new ballot created"


@app.route("/ballot/future", methods=["GET"])
@auth.oidc_auth
def get_current_ballots():
    now = datetime.now()
    today = now.date()
    time = now.time()

    uid = session['userinfo'].get('preferred_username')
    uid_group = get_groups(uid)
    ballots = Ballots.query \
        .filter(Ballots.start_date > today) \
        .filter(Ballots.start_time > time) \
        .filter(Ballots.group in uid_group) \
        .all()

    if ballots.len() > 0:
        return jsonify_ballots(ballots)

    return 500, "No ballots"


@app.route("/ballot/active", methods=["GET"])
@auth.oidc_auth
def get_active_ballots():
    now = datetime.now()
    time = now.time()
    date = now.date()
    uid = session['userinfo'].get('preferred_username')
    groups = get_groups(uid)
    active_ballots = Ballots.query \
        .filter(Ballots.start_date < date) \
        .filter(Ballots.start_time < time) \
        .filter(Ballots.end_date > date) \
        .filter(Ballots.end_time > time) \
        .filter(Ballots.group in groups) \
        .all()

    if active_ballots > 0:
        return jsonify_ballots(active_ballots)

    return 500, "No active ballots"


@app.route("/ballot/expired", methods=["GET"])
@auth.oidc_auth
def get_expired_ballots():
    now = datetime.now()
    time = now.time()
    date = now.date()
    uid = session['userinfo'].get('preferred_username')
    groups = get_groups(uid)
    expired_ballots = Ballots.query \
        .filter(Ballots.end_date < date) \
        .filter(Ballots.end_time < time) \
        .filter(Ballots.group in groups) \
        .all()

    return jsonify_ballots(expired_ballots)


# for alternative votes rank in the order that the options are in in the array
@app.route("/vote/<int:ballot_id>", methods=["POST"])
@auth.oidc_auth
def vote(ballot_id):
    body = request.json()
    uid = session['userinfo'].get('preferred_username')
    passed_vote = Vote.query \
        .filter(Vote.ballot_id == ballot_id) \
        .filter(Vote.uid == uid) \
        .first()
    if not passed_vote:
        return 403, "already voted"

    ballot = Ballots.query.filter(Ballots.ballot_id == ballot_id).first()
    if ballot.vote_type == 0:
        vote = body["vote"]
        yno = YNO.query.filter(YNO.ballot_id == ballot_id).first()
        if vote == "yes":
            yno.vote_yes()

        if vote == "no":
            yno.vote_no()

        if vote == "obstain":
            yno.vote_obstain()

    if ballot.vote_type == 1:
        ranks = body["rank"]
        ranks = ranks.split(',')
        ranks_number = []
        for rank in ranks:
            rank = int(rank)
            ranks_number.append(rank)

        alternative_votes = Alternative_Votes(ballot_id, ranks_number)
        db.session.add(alternative_votes)
        db.session.flush()
        db.session.commit()
        db.session.expire(alternative_votes)

    new_vote = Vote(uid, ballot_id)

    db.session.add(new_vote)
    db.sessin.flush()
    db.session.commit()
    db.session.expire(vote)

    last_vote = Vote.query.order_by(Vote.vote_id.desc()).first()
    last_vote.voted_true()

    return 200


@app.route("/vote/<int:ballot_id>", methods=["GET"])
@auth.oidc_auth
def get_vote_count(ballot_id):
    uid = session['userinfo'].get('preferred_username')

    if not is_member_of_group(uid, 'rtp') or not is_member_of_group(uid, 'eboard'):
        return 404, "not authorized"

    ballot = Ballots.query.filter(Ballots.ballot_id == ballot_id).first()

    # if ballot.vote_type == 0:
