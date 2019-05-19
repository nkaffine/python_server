import json
import requests
import re
from itertools import ifilter

class MondayUser:
    def __init__(self, monday_user_json):
        if monday_user_json == None:
            self.name = None
            self.id = None
            self.title = None
            self.email = None
        else:
            self.name = monday_user_json["name"]
            self.id = monday_user_json["id"]
            self.title = monday_user_json["title"]
            self.email = monday_user_json.get("email", None)
    def __str__(self):
        return "{}: {}".format(self.name, self.title)

class MondayPulse:
    def __init__(self, monday_pulse_json, type_dictionary):
        board_meta_data = monday_pulse_json["board_meta"]
        column_values = monday_pulse_json["column_values"]
        pulse = monday_pulse_json["pulse"]
        self.id = pulse["id"]
        self.name = pulse["name"]
        self.created_on = pulse["created_at"]
        self.updated_on = pulse["updated_at"]
        self.board_id = pulse["board_id"]
        self.url = pulse["url"]
        self.group_id = board_meta_data["group_id"]
        self.column_values = {}
        for column_value in column_values:
            self.column_values[column_value["title"]] = column_value
    def __str__(self):
        return "{}({}): created on: {}, updated on: {}".format(self.name, self.id, self.created_on, self.updated_on)

class MondayBoard:
    def __init__(self, monday_board_json, monday_api):
        self.url = monday_board_json["url"]
        self.id = monday_board_json["id"]
        self.name = monday_board_json["name"]
        self.description = monday_board_json["description"]
        self.columns = parse_monday_column_types(monday_board_json["columns"])
        self.board_type = monday_board_json["board_kind"]
        self.groups = filter(lambda x: not (x.archived or x.deleted), map(lambda x: MondayBoardGroup(x, self.id), monday_board_json["groups"]))
        self.created_at = monday_board_json["created_at"]
        self.updated_at = monday_board_json["updated_at"]
        self.api = monday_api
    #Gets all of the pulses in the board
    def getPulses(self):
        raw_pulses = self.api.getBoardPulses(self.id)
        return map(lambda x: MondayPulse(x, self.columns), raw_pulses)
    def movePulsesToGroup(self, pulses, group_name):
        group = next(ifilter(lambda x: x.title == group_name, self.groups), None)
        if group == None:
            raise Exception("No group exists")
        self.api.movePulsesToGroup(self.id, map(lambda x: x.id, pulses), group.id)
    # #Gets all pulses in the board in the given group if the group exists.
    # def getPulsesFromColumn(self, column):
    def __str__(self):
        return "{}: {}".format(self.name, self.description)

#returns a dictionary of column id's to the type
def parse_monday_column_types(columns):
    dictionary = {}
    for column in columns:
        dictionary[column["title"]] = mondayColumnInitializerForType(column)
    return dictionary
    
def mondayColumnInitializerForType(column):
    if column["type"] == "name":
        return lambda x: MondayNameColumn(x)
    elif column["type"] == "person":
        return lambda x: MondayPersonColumn(x)
    elif column["type"] == "team":
        return lambda x: MondayTeamColumn(x)
    elif column["type"] == "color":
        return lambda x: MondayColorColumn(x, column["labels"])
    elif column["type"] == "timerange":
        return lambda x: MondayTimelineColumn(x)
    elif column["type"] == "tag":
        return lambda x: MondayTagColumn(x)
    elif column["type"] == "date":
        return lambda x: MondayDateColumn(x)
    elif column["type"] == "boolean":
        return lambda x: MondayBooleanColumn(x)
    elif column["type"] == "file":
        return lambda x: MondayFileColumn(x)
    elif column["type"] == "numeric":
        return lambda x: MondayNumericColumn(x)
    elif column["type"] == "text":
        return lambda x: MondayTextColumn(x)
    elif column["type"] == "multiple-person":
        return lambda x: MondayMultiplePersonColumn(x)
    elif column["type"] == "formula":
        return lambda x: MondayFormulaColumn(x)
    elif column["type"] == "link":
        return lambda x: MondayLinkColumn(x)
    elif column["type"] == "votes":
        return lambda x: MondayVotesColumn(x)
    else:
        raise Exception("Unknown column type {}".format(column["type"]))

def parseMondayColumn(column):
    if column["type"] == "name":
        return MondayNameColumn(column)
    elif column["type"] == "person":
        return MondayPersonColumn(column)
    elif column["type"] == "team":
        return MondayTeamColumn(column)
    elif column["type"] == "color":
        return MondayColorColumn(column)
    elif column["type"] == "timerange":
        return MondayTimelineColumn(column)
    elif column["type"] == "tag":
        return MondayTagColumn(column)
    elif column["type"] == "date":
        return MondayDateColumn(column)
    elif column["type"] == "boolean":
        return MondayBooleanColumn(column)
    elif column["type"] == "file":
        return MondayFileColumn(column)
    elif column["type"] == "numeric":
        return MondayNumericColumn(column)
    elif column["type"] == "text":
        return MondayTextColumn(column)
    elif column["type"] == "multiple-person":
        return MondayMultiplePersonColumn(column)
    elif column["type"] == "formula":
        return MondayFormulaColumn(column)
    else:
        raise Exception("Unknown column type {}".format(column["type"]))

class MondayBoardGroup:
    def __init__(self, monday_board_json, board_id):
        self.color = monday_board_json["color"]
        self.board_id = monday_board_json["board_id"] if board_id is None else board_id
        self.id = monday_board_json["id"]
        self.title = monday_board_json["title"]
        self.archived = monday_board_json.get("archived", False)
        self.deleted = monday_board_json.get("deleted", False)
    def __str__(self):
        return "{}({})".format(self.title, self.id)

class MondayNameColumn:
    def __init__(self, monday_column_json):
        self.cid = monday_column_json["cid"]
        self.title = monday_column_json["title"]
        self.name = monday_column_json["name"]
    def __str__(self):
        return "{}({}): {}".format(self.title, self.cid, self.name)

class MondayPersonColumn:
    def __init__(self, monday_column_json):
        self.cid = monday_column_json["cid"]
        self.title = monday_column_json["title"]
        self.person = MondayUser(monday_column_json["value"])
    # def __str__(self):
    #     return "{}({}):{}".format(self.title, self.id, self.type)
    
class MondayTeamColumn:
    def __init__(self, monday_column_json):
        self.cid = monday_column_json["cid"]
        self.title = monday_column_json["title"]
        self.value = monday_column_json["value"]
    # def __str__(self):
    #     return "{}({}):{}".format(self.title, self.id, self.type)

class MondayColorColumn:
    def __init__(self, monday_column_json, column_index_values):
        self.cid = monday_column_json["cid"]
        self.title = monday_column_json["title"]
        self.value = monday_column_json["value"]
        if self.value != None:
            self.value = column_index_values[str(self.value["index"])] if self.value.get("index", None) != None else self.value
        else:
            self.value = "None"
    # def __str__(self):
    #     labels = "[" + reduce(lambda x, y: x + ", " + y, self.labels.values()) + "]"
    #     return "{}({}):{} {}".format(self.title, self.id, self.type, labels)

class MondayTimelineValue:
    def __init__(self, timeline_json):
        if timeline_json != None:
            self.start = timeline_json["from"]
            self.end = timeline_json["to"]
        else:
            self.start = None
            self.end = None
    def __str__(self):
        return "start: {}, end: {}".format(self.start, self.end)

class MondayTimelineColumn:
    def __init__(self, monday_column_json):
        self.cid = monday_column_json["cid"]
        self.title = monday_column_json["title"]
        self.value = MondayTimelineValue(monday_column_json["value"])
    # def __str__(self):
    #     return "{}({}):{}".format(self.title, self.id, self.type)

class MondayTagColumn:
    def __init__(self, monday_column_json):
        if monday_column_json["type"] != "tag":
            raise Exception("Incorrect json provided")
        self.type = "tag"
        self.title = monday_column_json["title"]
        self.id = monday_column_json['id']
    def __str__(self):
        return "{}({}):{}".format(self.title, self.id, self.type)
    
class MondayDateColumn:
    def __init__(self, monday_column_json):
        if monday_column_json["type"] != "date":
            raise Exception("Incorrect json provided")
        self.type = "date"
        self.title = monday_column_json["title"]
        self.id = monday_column_json['id']
    def __str__(self):
        return "{}({}):{}".format(self.title, self.id, self.type)

class MondayBooleanColumn:
    def __init__(self, monday_column_json):
        if monday_column_json["type"] != "boolean":
            raise Exception("Incorrect json provided")
        self.type = "boolean"
        self.title = monday_column_json["title"]
        self.id = monday_column_json['id']
    def __str__(self):
        return "{}({}):{}".format(self.title, self.id, self.type)

class MondayFileColumn:
    def __init__(self, monday_column_json):
        if monday_column_json["type"] != "file":
            raise Exception("Incorrect json provided")
        self.type = "file"
        self.title = monday_column_json["title"]
        self.id = monday_column_json['id']
    def __str__(self):
        return "{}({}):{}".format(self.title, self.id, self.type)

class MondayNumericColumn:
    def __init__(self, monday_column_json):
        if monday_column_json["type"] != "numeric":
            raise Exception("Incorrect json provided")
        self.type = "numeric"
        self.title = monday_column_json["title"]
        self.id = monday_column_json["id"]
        self.unit_symbol = monday_column_json["unit"]["symbol"] if monday_column_json.get("unit", None) != None else ""
    def __str__(self):
        return "{}({}):{} (Unit: ".format(self.title, self.id, self.type) + self.unit_symbol + ")"

class MondayTextColumn:
    def __init__(self, monday_column_json):
        if monday_column_json["type"] != "text":
            raise Exception("Incorrect json provided")
        self.type = "text"
        self.title = monday_column_json["title"]
        self.id = monday_column_json['id']
    def __str__(self):
        return "{}({}):{}".format(self.title, self.id, self.type)

class MondayMultiplePersonColumn:
    def __init__(self, monday_column_json):
        if monday_column_json["type"] != "multiple-person":
            raise Exception("Incorrect json provided")
        self.type = "multiple-person"
        self.title = monday_column_json["title"]
        self.id = monday_column_json['id']
    def __str__(self):
        return "{}({}):{}".format(self.title, self.id, self.type)

class MondayFormulaColumn:
    def __init__(self, monday_column_json):
        if monday_column_json["type"] != "formula":
            raise Exception("Incorrect json provided")
        self.type = "formula"
        self.title = monday_column_json["title"]
        self.id = monday_column_json["id"]
        self.formula = monday_column_json["settings"]["formula"]
        self.unit_symbol = monday_column_json["unit"]["symbol"] if monday_column_json.get("unit") != None else ""
    def __str__(self):
        return "{}({}):{} (formula: {}, units: {})".format(self.title, self.id, self.type, self.formula, self.unit_symbol)

class MondayLinkColumn:
    def __init__(self, monday_column_json):
        if monday_column_json["type"] != "link":
            raise Exception("Incorrect json provided")
        self.type = "link"
        self.title = monday_column_json["title"]
        self.id = monday_column_json["id"]
    def __str__(self):
        return "{}({}):{}".format(self.title, self.id, self.type)

class MondayVotesColumn:
    def __init__(self, monday_column_json):
        if monday_column_json["type"] != "votes":
            raise Exception("Incorrect json provided")
        self.type = "votes"
        elf.title = monday_column_json["title"]
        self.id = monday_column_json["id"]
    def __str__(self):
        return "{}({}):{}".format(self.title, self.id, self.type)

#TODO: Create a class for columns and groups

class MondayAPIOLD:
    #Creates the instance of the monday api with the given api key and the user id that things will be used with
    def __init__(self, key, user_id):
        self.key = key
        self.user_id = user_id
        self.base_url = "https://api.monday.com"
    #Returns a list of all of the users on the Monday
    def getUsers(self):
        extension = "/v1/users.json"
        result = self.__perform_request__(extension, {}, "get")
        return map(lambda x: MondayUser(x), result)
    #Returns a specific user
    def getUser(self, id):
        extension = "/v1/users/{}.json".format(id)
        result = self.__perform_request__(extension, {}, "get")
        return MondayUser(result)
    #Returns all the pulses from the account
    def getPulses(self):
        extension = "/v1/pulses.json"
        result = self.__perform_request__(extension, {}, "get")
        return map(lambda x: MondayPulse(x), result)
    #Returns all f the boards on the accunt
    def getBoards(self):
        extension = "/v1/boards.json"
        result = self.__perform_request__(extension, {}, "get")
        return map(lambda x: MondayBoard(x), result)
    def getBoard(self, board_id):
        extension = "/v1/boards/{}.json".format(board_id)
        result = self.__perform_request__(extension, {}, "get")
        return MondayBoard(result)
    def getBoardGroups(self, board_id):
        extension = "/v1/boards/{}/groups.json".format(board_id)
        result = self.__perform_request__(extension, {"show_archived":False, "show_deleted":False}, "get")
        return map(lambda x: MondayBoardGroup(x, board_id), result)
    def getBoardColumns(self, board_id):
        extension = "/v1/boards/{}/columns.json".format(board_id)
        result = self.__perform_request__(extension, {"all_columns":False}, "get")
        return map(lambda x: parseMondayColumn(x), result)
    #TODO: Need to test this still
    def getColumnValueForPulse(self, board_id, column_id, pulse_id):
        extension = "/v1/boards/{}/columns/{}/value.json".format(board_id, column_id)
        result = self.__perform_request__(extension, {"pulse_id":pulse_id}, "get")
    def getBoardPulses(self, board_id):
        extension = "/v1/boards/{}/pulses.json".format(board_id)
        result = self.__perform_request__(extension, {}, "get")
        return result
    def __perform_request__(self, extension, parameters, request_type):
        parameters["api_key"] = self.key
        parameters["user_id"] = self.user_id
        if request_type == "get":
            response = requests.get(url = self.base_url + extension, params = parameters)
            return self.__handle_monday_response(response)
        elif request_type == "post":
            response = requests.post(url = self.base_url + extension, params = parameters)
            return self.__handle_monday_response(response)
        elif request_type == "put":
            response = requests.put(url = self.base_url + extension, params = parameters)
            return self.__handle_monday_response(response)
        elif request_type == "delete":
            response = requests.delete(url = self.base_url + extension, params = parameters)
            return self.__handle_monday_response(response)
        else:
            raise Exception("Invalid request type")
    def __handle_monday_response(self, response):
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            raise Exception("invalid API key")
        elif response.status_code == 402:
            raise Exception("Monday payment required")
        elif response.status_code == 404:
            raise Exception("Resource not found")
        else:
            raise Exception("Unexpected status code {}".format(response.status_code))

class MondayAPI:
    #Creates the instance of the monday api with the given api key and the user id that things will be used with
    def __init__(self, key, user_id):
        self.key = key
        self.user_id = user_id
        self.base_url = "https://api.monday.com"
    #Gets all of the boards that are not archived or deleted
    def getBoards(self):
        extension = "/v1/boards.json"
        result = self.__perform_request__(extension, {}, "get")
        return map(lambda x: MondayBoard(x, self), result)
    def getBoardNamed(self, board_name):
        boards_matching = filter(lambda x: x.name == board_name, self.getBoards())
        if len(boards_matching) == 0:
            raise Exception("No board with that name")
        return boards_matching[0]
    #Gets the pulses for the board with the given id
    def getBoardPulses(self, board_id):
        extension = "/v1/boards/{}/pulses.json".format(board_id)
        result = self.__perform_request__(extension, {"per_page": 25, "page": 1}, "get")
        current_page = 2
        tmp = result
        while(len(tmp) == 25):
            tmp = self.__perform_request__(extension, {"per_page": 25, "page": current_page}, "get")
            current_page += 1
            result += tmp
        return result
    def movePulsesToGroup(self, board_id, pulse_ids, group_id):
        extension = "/v1/boards/{}/pulses/move.json".format(board_id)
        ids = reduce(lambda x,y: "{},{}".format(x,y), pulse_ids)
        result = self.__perform_request__(extension, {"group_id":group_id, "pulse_ids":ids}, "post")
    def __perform_request__(self, extension, parameters, request_type):
        parameters["api_key"] = self.key
        parameters["user_id"] = self.user_id
        if request_type == "get":
            response = requests.get(url = self.base_url + extension, params = parameters)
            return self.__handle_monday_response(response)
        elif request_type == "post":
            response = requests.post(url = self.base_url + extension, params = parameters)
            return self.__handle_monday_response(response)
        elif request_type == "put":
            response = requests.put(url = self.base_url + extension, params = parameters)
            return self.__handle_monday_response(response)
        elif request_type == "delete":
            response = requests.delete(url = self.base_url + extension, params = parameters)
            return self.__handle_monday_response(response)
        else:
            raise Exception("Invalid request type")
    def __handle_monday_response(self, response):
        if response.status_code == 200:
            return response.json()
        if response.status_code == 201:
            return response.json()
        elif response.status_code == 401:
            raise Exception("invalid API key")
        elif response.status_code == 402:
            raise Exception("Monday payment required")
        elif response.status_code == 404:
            raise Exception("Resource not found")
        else:
            raise Exception("Unexpected status code {}".format(response.status_code))