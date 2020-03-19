from sqlalchemy import Column, Integer, Boolean
from sqlalchemy.dialects.postgresql import TEXT, DATE, TIME, ARRAY

from ballot.routes import db

# quorum and passing percent not completed!!!!!


class Ballots(db.Model):
    __tablename__ = "ballots"
    ballot_id = Column(Integer, primary_key=True)
    name = Column(TEXT, nullable=False)
    vote_type = Column(Integer, nullable=False)
    group = Column(TEXT, nullable=False)
    description = Column(TEXT, nullable=False)
    start_date = Column(DATE, nullable=False)
    end_date = Column(DATE, nullable=False)
    start_time = Column(TIME, nullable=False)
    end_time = Column(TIME, nullable=False)
    quorum_percentage = Column(Integer, nullable=False)
    passing_percentage = Column(Integer, nullable=False)

    def __init__(self, name, vote_type, group, description, start_date, end_date, start_time, end_time):
        self.name = name
        self.vote_type = vote_type
        self.group = group
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time


class YNO(db.Model):
    __tablename__ = "yno"
    yno_id = Column(Integer, primary_key=True)
    ballot_id = Column(Integer, nullable=False)
    yes_count = Column(Integer, nullable=False)
    no_count = Column(Integer, nullable=False)
    obstain_count = Column(Integer, nullable=False)

    def __init__(self, ballot_id):
        self.ballot_id = ballot_id
        self.yes_count = 0
        self.no_count = 0
        self.obstain_count = 0

    def vote_yes(self):
        self.yes_count += 1

    def vote_no(self):
        self.no_count += 1

    def vote_obstain(self):
        self.obstain_count += 1


class Alternative(db.Model):
    __tablename__ = "alternative"
    alternative_id = Column(Integer, primary_key=True)
    ballot_id = Column(Integer, nullable=False)
    options = Column(ARRAY, nullable=False)
    counts = Column(ARRAY, nullable=False)

    def __init__(self, ballot_id, options):
        self.ballot_id = ballot_id
        self.options = options
        self.counts = []


class Alternative_Votes(db.Model):
    __tablename__ = "alternative_votes"
    av_id = Column(Integer, primary_key=True)
    ballot_id = Column(Integer, nullanle=False)
    ranks = Column(ARRAY, nullable=False)

    def __init__(self, ballot_id, ranks):
        self.ballot_id = ballot_id
        self.ranks = ranks


class Vote(db.Model):
    __tablename__ = "vote"
    vote_id = Column(Integer, primary_key=True)
    uid = Column(TEXT, nullable=False)
    ballot_id = Column(Integer, nullable=False)
    voted = Column(Boolean, nullable=False)

    def __init__(self, uid, ballot_id):
        self.uid = uid
        self.ballot_id = ballot_id
        self.voted = False

    def voted_true(self):
        self.voted = True
