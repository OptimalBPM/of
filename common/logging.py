from mbe.logging import Logging
from of.common.messaging.factory import log_process_state_message

__author__ = 'Nicklas Borjesson'


class BPMLogging(Logging):
    def log_process_state(self, _changed_by, _process_id, _state, _reason):
        _data = log_process_state_message(_changed_by=_changed_by, _process_id=_process_id, _state=_state,
                                          _reason=_reason)

        self.write_log(_data)
