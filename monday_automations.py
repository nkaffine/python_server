import monday
from itertools import ifilter
import datetime
import sys

class MondayAutomator:
    def __init__(self):
        self.api = self.__setup_monday_api__()

    def __get_monday_credentials__(self):
        api_key_file = open("api_key.txt", "r")
        api_key = api_key_file.readline().rstrip("\n")
        api_key_file.close()
        user_id_file = open("user_id.txt", "r")
        user_id = user_id_file.readline().rstrip("\n")
        user_id_file.close()
        return api_key, user_id

    def __setup_monday_api__(self):
        api_key, user_id = self.__get_monday_credentials__()
        return monday.MondayAPI(api_key, user_id)

    def reset_week(self):
        relevant_boards = ["Operations Tasks", "Website Tasks", "Marketing Team Tasks"]
        monday_boards = filter(lambda x: x.name in relevant_boards, self.api.getBoards())
        for board in monday_boards:
            this_week = next(ifilter(lambda x: x.title == "This Week", board.groups), None)
            complete = next(ifilter(lambda x: x.title == "Completed", board.groups), None)
            future = next(ifilter(lambda x: x.title == "Future", board.groups), None)
            pulses = board.getPulses()
            this_week_pulses = filter(lambda x: x.group_id == this_week.id, pulses)
            future_pulses = filter(lambda x: x.group_id == future.id, pulses)
            this_week_finished = filter(lambda x: self.__is_pulse_done__(board.columns, x), this_week_pulses)
            future_coming_up = filter(lambda x: self.__is_pulse_coming_up(x), future_pulses)
            if len(this_week_finished) > 0:
                board.movePulsesToGroup(this_week_finished, "Completed")
            if len(future_coming_up) > 0:
                board.movePulsesToGroup(future_coming_up, "This Week")
    def __is_pulse_done__(self, columns, pulse):
        if pulse.column_values["Status"].get("value", None) != None:
            value = pulse.column_values["Status"]
            status = columns["Status"](value)
            return status.value == "Done"
        else:
            return False
    def __is_pulse_coming_up(self, pulse):
        if pulse.column_values["Timeline"]["value"] != None:
            start_date = datetime.datetime.strptime(pulse.column_values["Timeline"]["value"]["from"], '%Y-%m-%d')
            cutoff = datetime.datetime.now() + datetime.timedelta(days=7)
            return start_date < cutoff
        else:
            return False

class AutomationHandler:
    def __init__(self):
        self.automator = MondayAutomator()
    def handleCommand(self, arguments):
        if arguments[1] == "reset_week":
            self.automator.reset_week()

if (len(sys.argv) < 2):
    raise Exception("Invalid parameters passed")

handler = AutomationHandler()
handler.handleCommand(sys.argv)