"Smarkets event request helper classes"
# Copyright (C) 2011 Smarkets Limited <support@smarkets.com>
#
# This module is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php
import smarkets.seto.piqi_pb2 as seto


class EventsRequest(object):
    "Base class for events requests"
    __slots__ = ('_payload',)
    _payload = seto.Payload()
    _payload.type = seto.PAYLOAD_EVENTS_REQUEST
    _payload.events_request.content_type = seto.CONTENT_TYPE_PROTOBUF

    def copy_to(self, dest_payload):
        "Copy the event request to the destination payload"
        dest_payload.MergeFrom(self._payload)

    def copy(self):
        "Copy the payload to a new one"
        payload = seto.Payload()
        self.copy_to(payload)
        return payload


class Politics(EventsRequest):
    "Request for politics events"
    _payload = seto.Payload()
    _payload.CopyFrom(EventsRequest._payload)
    _payload.events_request.type = seto.EVENTS_REQUEST_POLITICS


class CurrentAffairs(EventsRequest):
    "Request for current affairs events"
    _payload = seto.Payload()
    _payload.CopyFrom(EventsRequest._payload)
    _payload.events_request.type = seto.EVENTS_REQUEST_CURRENT_AFFAIRS


class TvAndEntertainment(EventsRequest):
    "Request for TV/entertainment events"
    _payload = seto.Payload()
    _payload.CopyFrom(EventsRequest._payload)
    _payload.events_request.type = seto.EVENTS_REQUEST_TV_AND_ENTERTAINMENT


class SportByDate(EventsRequest):
    "Request for sport by date"
    __slots__ = ('date', 'payload')
    _payload = seto.Payload()
    _payload.CopyFrom(EventsRequest._payload)
    _payload.events_request.type = seto.EVENTS_REQUEST_SPORT_BY_DATE

    def __init__(self, date):
        super(SportByDate, self).__init__()
        self.date = date
        self.payload = seto.Payload()
        self.payload.CopyFrom(self._payload)
        self.payload.events_request.sport_by_date.date.year = date.year
        self.payload.events_request.sport_by_date.date.month = date.month
        self.payload.events_request.sport_by_date.date.day = date.day

    def copy_to(self, dest_payload):
        "Copy the event request to the destination payload"
        dest_payload.MergeFrom(self.payload)


class FootballByDate(SportByDate):
    "Request for football by date"
    def __init__(self, date):
        super(FootballByDate, self).__init__(date)
        self.payload.events_request.sport_by_date.type = \
            seto.SPORT_BY_DATE_FOOTBALL


class HorseRacingByDate(SportByDate):
    "Request for horse racing by date"
    def __init__(self, date):
        super(HorseRacingByDate, self).__init__(date)
        self.payload.events_request.sport_by_date.type = \
            seto.SPORT_BY_DATE_HORSE_RACING


class TennisByDate(SportByDate):
    "Request for football by date"
    def __init__(self, date):
        super(TennisByDate, self).__init__(date)
        self.payload.events_request.sport_by_date.type = \
            seto.SPORT_BY_DATE_TENNIS


class SportOther(EventsRequest):
    "Request for other sport"
    _payload = seto.Payload()
    _payload.CopyFrom(EventsRequest._payload)
    _payload.events_request.type = seto.EVENTS_REQUEST_SPORT_OTHER
