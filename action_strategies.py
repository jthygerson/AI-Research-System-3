from experiment_execution import ActionStrategy

class InitializeOpenAIStrategy(ActionStrategy):
    def execute(self, step, executor):
        return executor.initialize_openai()

class RunPythonCodeStrategy(ActionStrategy):
    def execute(self, step, executor):
        code = step.get('code', 'print("No code provided")')
        return executor.run_python_code(code)

class UseLLMAPIStrategy(ActionStrategy):
    def execute(self, step, executor):
        prompt = step.get('prompt')
        if prompt is None and 'parameters' in step:
            prompt = step['parameters'].get('prompt')
            if prompt is None and 'args' in step['parameters']:
                prompt = step['parameters']['args'].get('prompt')
        
        if prompt is None:
            raise ValueError(f"No prompt provided for LLM API action. Step details: {step}")
        return executor.use_llm_api(prompt)

class WebRequestStrategy(ActionStrategy):
    def execute(self, step, executor):
        url = step.get('url')
        method = step.get('method', 'GET')
        if url is None:
            raise ValueError("No URL provided for web request action")
        return executor.make_web_request(url, method, retry_without_ssl=True)

class UseGPUStrategy(ActionStrategy):
    def execute(self, step, executor):
        task = step.get('task')
        if task is None:
            raise ValueError("No task provided for GPU action")
        return executor.use_gpu(task)

class RunStrategy(ActionStrategy):
    def execute(self, step, executor):
        if 'parameters' in step and 'iterations' in step['parameters']:
            iterations = step['parameters']['iterations']
            return executor.run_experiment_designer(iterations)
        else:
            return {"error": "Missing 'iterations' parameter for 'run' action"}

class ExecuteStrategy(ActionStrategy):
    def execute(self, step, executor):
        return executor.run_python_code(step.get('code', 'print("No code provided")'))