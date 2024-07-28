import os
import fire
import asyncio

from examples.di.requirements_prompt import (
    OPEN_ENDED_TASKS_REQUIREMENTS,
    ML_BENCHMARK_REQUIREMENTS,
)
from metagpt.const import DATA_PATH
from metagpt.roles.di.data_interpreter import DataInterpreter
from metagpt.tools.tool_recommend import TypeMatchToolRecommender
from metagpt.utils.agent_logger import agent_logger

import datetime
import json
from pathlib import Path


async def math_problems(data_dir):
    if data_dir != DATA_PATH and not os.path.exists(os.path.join(data_dir, "test_l5")):
        raise FileNotFoundError(f"MATH L5 dataset not found in {data_dir}.")

    data_dir = os.path.join(data_dir, "test_l5")

    start_from = ("number_theory", "232")
    started = False

    for category in [
        "counting_and_probability",
        "number_theory",
        "prealgebra",
        "precalculus",
    ]:
        category_file_path = Path(data_dir) / f"{category}.json"
        with open(category_file_path, "r") as file:
            category_problems = json.load(file)

            for problem in category_problems:

                if not started and category == start_from[0] and problem["id"] == start_from[1]:
                        started = True
                if not started:
                    continue

                di = DataInterpreter()
                agent_logger.log(
                    "USER",
                    -1,
                    f"Running task: math_problems/{category}/{problem['id']}",
                )
                agent_logger.allocate_request_id()
                await di.run(problem["problem"])
                await asyncio.sleep(20)


# Ensure Open-Ended Tasks dataset has been downloaded before using this example.
async def open_ended_tasks(data_dir=DATA_PATH, use_reflection=True):
    if data_dir != DATA_PATH and not os.path.exists(
        os.path.join(data_dir, "di_dataset/open_ended_tasks")
    ):
        raise FileNotFoundError(f"Open-ended task dataset not found in {data_dir}.")

    for task_name in OPEN_ENDED_TASKS_REQUIREMENTS:
        requirement = OPEN_ENDED_TASKS_REQUIREMENTS[task_name].format(data_dir=data_dir)
        di = DataInterpreter(
            use_reflection=use_reflection,
            tool_recommender=TypeMatchToolRecommender(tools=["<all>"]),
        )
        agent_logger.log("USER", -1, f"Running task: open_ended_tasks/{task_name}")
        agent_logger.allocate_request_id()
        await di.run(requirement)
        await asyncio.sleep(30)


# Ensure ML-Benchmark dataset has been downloaded before using these example.
async def ml_benchmark(data_dir=DATA_PATH, use_reflection=True):
    if data_dir != DATA_PATH and not os.path.exists(
        os.path.join(data_dir, "di_dataset/ml_benchmark")
    ):
        raise FileNotFoundError(f"ML-Benchmark dataset not found in {data_dir}.")

    for task_name in ML_BENCHMARK_REQUIREMENTS:
        requirement = ML_BENCHMARK_REQUIREMENTS[task_name].format(data_dir=data_dir)
        di = DataInterpreter(
            use_reflection=use_reflection,
            tool_recommender=TypeMatchToolRecommender(tools=["<all>"]),
        )
        agent_logger.log("USER", -1, f"Running task: ml_benchmark/{task_name}")
        agent_logger.allocate_request_id()
        await di.run(requirement)
        await asyncio.sleep(30)


async def main(data_dir=DATA_PATH, use_reflection=True):
    now = datetime.datetime.now().isoformat().replace(":", "")
    agent_logger.set_log_file(f"./{now}-all-tasks.log")

    await open_ended_tasks(data_dir, use_reflection)
    await ml_benchmark(data_dir, use_reflection)
    await math_problems(data_dir)


if __name__ == "__main__":
    fire.Fire(main)
