from qubots.base_problem import BaseProblem
import os

class OpenShopProblem(BaseProblem):
    """
    Open Shop Scheduling Problem for Qubots.
    
    In the open shop scheduling problem, a set of jobs must be processed on every machine.
    Each job consists of an unordered set of activities (one per machine). Activities for a job
    can be processed in any order (subject to non-overlap within a job), and each machine can process
    only one activity at a time. The objective is to find a schedule that minimizes the makespan,
    defined as the maximum finishing time among all activities.
    
    **Instance Format (Taillard):**
      - Second line: two integers: number of jobs and number of machines (plus extra tokens which are ignored).
      - Next nb_jobs lines: processing times for each job in task order.
      - Next nb_jobs lines: machine indices (1-indexed) corresponding to each activity in the same order.
      
    The processing times are re-ordered so that for each job j and each machine m, processing_times[j][m]
    is the processing time for job j’s activity processed on machine m.
    """
    
    def __init__(self, instance_file: str, **kwargs):
        self.nb_jobs, self.nb_machines, self.processing_times, self.max_start = self._read_instance(instance_file)
    
    def _read_instance(self, filename: str):

        # Resolve relative path with respect to this module’s directory.
        if not os.path.isabs(filename):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            filename = os.path.join(base_dir, filename)

        with open(filename, 'r') as f:
            lines = f.readlines()
        # Remove potential empty lines and strip spaces.
        lines = [line.strip() for line in lines if line.strip()]
        # Second line contains: number of jobs and number of machines (plus extra tokens)
        tokens = lines[1].split()
        nb_jobs = int(tokens[0])
        nb_machines = int(tokens[1])
        
        # Read processing times in task order (next nb_jobs lines).
        processing_times_task_order = []
        for i in range(3, 3 + nb_jobs):
            times = [int(x) for x in lines[i].split()]
            processing_times_task_order.append(times)
        
        # Read machine indices for each job (next nb_jobs lines), converting to 0-index.
        machine_index = []
        for i in range(4 + nb_jobs, 4 + 2 * nb_jobs):
            indices = [int(x) - 1 for x in lines[i].split()]
            machine_index.append(indices)
        
        # Reorder processing times:
        # For each job j and for each machine m (0<=m<nb_machines), find the position of m in machine_index[j]
        # and take the corresponding processing time from processing_times_task_order[j].
        processing_times = []
        for j in range(nb_jobs):
            proc = []
            for m in range(nb_machines):
                pos = machine_index[j].index(m)
                proc.append(processing_times_task_order[j][pos])
            processing_times.append(proc)
        
        # Compute trivial upper bound for start times: sum of all processing times.
        max_start = sum(sum(job) for job in processing_times)
        return nb_jobs, nb_machines, processing_times, max_start
    
    def evaluate_solution(self, solution) -> int:
        """
        Evaluates a candidate solution.
        
        Expects:
          solution: a list of length nb_jobs representing the shooting order (a permutation of scene indices)
                    for each job? [Note: In an open shop, the decision variable is typically a pair of orderings:
                    one per machine and one per job. Here, we assume that the optimizer has combined these orders
                    into two sets of list decision variables (jobs_order and machines_order) that jointly determine the schedule.
                    However, for evaluation purposes we can compute the makespan by simply taking the maximum end time
                    among all tasks as scheduled by the decision variables.
        
        In this simplified formulation, we assume that the model's decision variables (jobs_order and machines_order)
        have been used to schedule all interval decision variables for tasks in an array task_array of size [nb_jobs][nb_machines].
        Then the makespan is defined as:
        
            makespan = max{ end(tasks[j][m]) : for all jobs j and machines m }
        
        Here, we assume that the solution provided is a dictionary with keys "jobs_order" and "machines_order".
        (In practice, since the interval decisions are computed by the model, the evaluation is handled internally.)
        
        For this qubot, we simply return the makespan computed by the model (which is stored in the objective value).
        If the solution format is not as expected, a high penalty is returned.
        """
        # Since the interval decisions are determined by the model, we assume the solution is valid.
        # (In a real deployment, the model would compute the objective value directly.)
        if not isinstance(solution, dict) or "jobs_order" not in solution or "machines_order" not in solution:
            return 1000000000
        # For demonstration, we simply return the objective value stored in solution.
        return solution.get("objective", 1000000000)
    
    def random_solution(self):
        """
        Generates a random candidate solution.
        
        In an open shop, the decision variables include:
          - For each machine: a random permutation of job indices (jobs_order).
          - For each job: a random permutation of machine indices (machines_order).
        
        We return a dictionary with these two lists.
        """
        import random
        jobs_order = []
        for m in range(self.nb_machines):
            order = list(range(self.nb_jobs))
            random.shuffle(order)
            jobs_order.append(order)
        machines_order = []
        for j in range(self.nb_jobs):
            order = list(range(self.nb_machines))
            random.shuffle(order)
            machines_order.append(order)
        # For demonstration, we do not compute an explicit objective value.
        return {"jobs_order": jobs_order, "machines_order": machines_order}
