import logging
import time
from collections import defaultdict
from typing import Dict, AnyStr, Any, Tuple, Union
from metagpt.logs import logger

LLM_CALL = "LLM Call"
LLM_RETURN = "LLM Return"
LLM_DECODING = "LLM Decoding"
TOOL_CALL = "Tool Call"
TOOL_RETURN = "Tool Return"


class AgentLogger:
    def __init__(self):
        self._request_counters = int(time.time()) % 100000000
        self._log_counters = defaultdict(int)
        self._file_path = None
        self._logger = logging.getLogger("AgentLogger")
        self._logger.setLevel(logging.INFO)
        self._setup_stream_handler()

    def _setup_stream_handler(self):
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        self._logger.handlers = [handler]

    def _setup_file_handler(self, file_path):
        handler = logging.FileHandler(file_path)
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        self._logger.handlers = [handler]

    def allocate_call_id(self, call_type: AnyStr) -> int:
        current_id = self._log_counters[call_type]
        self._log_counters[call_type] += 1
        return current_id

    def allocate_request_id(self) -> int:
        current_id = self._request_counters
        self._request_counters += 1
        return current_id

    def current_request_id(self) -> int:
        return self._request_counters - 1

    def set_log_file(self, file_path: AnyStr):
        self._file_path = file_path
        self._setup_file_handler(file_path)

    def log(self, action: AnyStr, request_id: int, content: Union[Dict[AnyStr, Any], Tuple, AnyStr, Any]):
        timestamp = time.time() # Unit: seconds
        log_record = f"{timestamp:.6f}, {request_id}, {action}, {content}"
        self._logger.info(log_record)


# Registry instance
agent_logger = AgentLogger()


def stringify_input_messages(messages, model="gpt-3.5-turbo-0125"):
    """Return the number of tokens used by a list of messages."""
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-35-turbo",
        "gpt-35-turbo-16k",
        "gpt-3.5-turbo-16k",
        "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo-0125",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        "gpt-4-turbo",
        "gpt-4-turbo-preview",
        "gpt-4-0125-preview",
        "gpt-4-turbo",
        "gpt-4-vision-preview",
        "gpt-4-1106-vision-preview",
        "gpt-4-1106-preview",
        "gpt-4o-2024-05-13",
        "gpt-4o",
    }:
        role_prefix = "<|im_start|>"
        sep = "<|im_sep|>"
        content_suffix = "<|im_end|>"
    elif model == "gpt-3.5-turbo-0301":
        role_prefix = "<|im_start|>"
        sep = "\n"
        content_suffix = "<|im_end|>\n"
    elif "gpt-3.5-turbo" == model:
        logger.info(
            "Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0125."
        )
        return stringify_input_messages(messages, model="gpt-3.5-turbo-0125")
    elif "gpt-4" == model:
        logger.info(
            "Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613."
        )
        return stringify_input_messages(messages, model="gpt-4-0613")
    elif "open-llm-model" == model:
        """
        For self-hosted open_llm api, they include lots of different models. We just join the messages.
        """
        role_prefix = ""
        sep = ":"
        content_suffix = "\n"
    else:
        raise NotImplementedError(
            f"stringify_messages() is not implemented for model {model}. "
        )
    stringified_messages = []
    for message in messages:
        stringified_messages.append(
            role_prefix
            + message["role"]
            + ((":" + message["name"]) if "name" in message else "")
            + sep
            + str(message["content"])
            + content_suffix
        )
    stringified_messages.append(role_prefix + "assistant" + sep)
    return "".join(stringified_messages)


# # Example usage
# if "__main__" == __name__:
#     logger = AGENT_LOGGER

#     # Allocate IDs
#     rid = logger.allocate_request_id()
#     type1 = "LLM"
#     type2 = "Tool"
#     id1_1 = logger.allocate_call_id(type1)
#     id2_1 = logger.allocate_call_id(type2)

#     # Set log file (optional)
#     # logger.set_log_file("logfile.log")

#     # Log messages
#     logger.log(
#         LLM_CALL,
#         rid,
#         {
#             "call_id": id1_1,
#             "input": "Input for LLM Call",
#             "input_ntokens": 4,
#         },
#     )
#     logger.log(
#         LLM_DECODING,
#         rid,
#         {
#             "call_id": id1_1,
#             "output": "Output from LLM Decoding",
#         },
#     )
#     logger.log(
#         LLM_RETURN,
#         rid,
#         {
#             "call_id": id1_1,
#             "output": "Output from LLM Return",
#             "output_ntokens": 4,
#             "total_ntokens": 8,
#         },
#     )
#     logger.log(
#         TOOL_CALL,
#         rid,
#         {
#             "call_id": id2_1,
#             "tool_name": "SomeTool",
#             "tool_param": {
#                 "arg1": "Arg1",
#                 "arg2": "Arg2",
#             },
#         },
#     )
#     logger.log(
#         TOOL_RETURN,
#         rid,
#         {
#             "call_id": id2_1,
#             "output": "Output from Tool Return",
#         },
#     )
