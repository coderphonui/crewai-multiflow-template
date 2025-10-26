---
mode: agent
description: Create a new flow based on the requirement
---
# Create New CrewAI Flow

Implement a new flow following the project's multi-flow architecture conventions.

## Flow Requirement

```
${input:requirement:the requirement to implement the flow}
```


## Implementation Instructions

### 1. Create Flow Directory Structure
Create the following structure under `src/flows/`:
```
src/flows/<flow_name>/
├── __init__.py
├── main.py                          # Flow definition
└── crews/
    ├── __init__.py
    └── <crew_name>/
        ├── __init__.py
        ├── <crew_name>.py           # Crew implementation
        └── config/
            ├── agents.yaml          # Agent configurations
            └── tasks.yaml           # Task definitions
```

### 2. Implement the Flow (`main.py`)
- Create a Flow class that inherits from `crewai.flow.Flow`
- Use `@start` decorator for entry point methods
- Use `@listen` decorator for state-dependent methods
- Store results in the flow's state
- Implement a `kickoff()` function that instantiates and runs the flow
- Example pattern:
```python
from crewai.flow import Flow, listen, start
from .crews.<crew_name>.<crew_name> import <CrewClass>

class <FlowName>Flow(Flow):
    @start()
    def entry_method(self):
        # Initial flow logic
        result = <CrewClass>().crew().kickoff(inputs={...})
        self.state.<attribute> = result.raw
        return self.state.<attribute>
    
    @listen(entry_method)
    def process_result(self):
        # Process and save results
        pass

def kickoff():
    flow = <FlowName>Flow()
    flow.kickoff()

def plot():
    flow = <FlowName>Flow()
    flow.plot()
```

### 3. Implement the Crew (`crews/<crew_name>/<crew_name>.py`)
- Use `@CrewBase` decorator on the crew class
- Set `agents_config` and `tasks_config` paths to YAML files
- Define agent factory methods with `@agent` decorator
- Define task factory methods with `@task` decorator
- Define crew method with `@crew` decorator that returns a Crew instance
- Import and use tools from `src/shared/tools/` if needed
- Example pattern:
```python
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class <CrewName>Crew():
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def <agent_name>(self) -> Agent:
        return Agent(
            config=self.agents_config["<agent_name>"],
            # tools=[...] if needed
        )

    @task
    def <task_name>(self) -> Task:
        return Task(
            config=self.tasks_config["<task_name>"],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
```

### 4. Configure Agents (`config/agents.yaml`)

Ensure we follow the best practices defined under `crewai_practices` folder and setup agents, tasks to fit the requirement.

Define agents with the following structure:
```yaml
<agent_name>:
  role: >
    [Agent's role]
  goal: >
    [Agent's goal]
  backstory: >
    [Agent's backstory]
  llm: gemini/gemini-2.5-flash  # Or other configured LLM
```

### 5. Configure Tasks (`config/tasks.yaml`)
Define tasks with the following structure:
```yaml
<task_name>:
  description: >
    [Task description with any {input_variables}]
  expected_output: >
    [Description of expected output]
  agent: <agent_name>  # Reference to agent from agents.yaml
```






