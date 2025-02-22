################################################################################
# A simple job manager for running multiple jobs in parallel using ThreadPoolExecutor
################################################################################
import enum
import subprocess
import threading
import time
import signal
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.console import Console

console = Console()

class JobStatus(enum.Enum):
    WAITING = 0     # Job is waiting for dependencies to complete
    PENDING = 1     # Job is ready to run
    RUNNING = 2     # Job is currently running
    COMPLETED = 3   # Job has completed successfully
    FAILED = 4      # Job has failed

class Job:
    def __init__(self, name, command, log_file=None):
        self.name = name
        self.command = command
        self.status = JobStatus.PENDING
        self.stdout = None
        self.stderr = None
        self.process = None
        self.log_file = log_file
        self.dependencies = []

    def add_dependencies(self, dependencies):
        self.dependencies.extend(dependencies)

    def can_run(self):
        return all(dep.status == JobStatus.COMPLETED for dep in self.dependencies)

    def run(self):
        self.status = JobStatus.RUNNING
        try:
            self.process = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.stdout, self.stderr = self.process.communicate()
            self.status = JobStatus.COMPLETED if self.process.returncode == 0 else JobStatus.FAILED

            if self.log_file:
                with open(self.log_file, "w") as f:
                    f.write(f'Jobname: {self.name}')
                    f.write(f'Command: {self.command}')
                    f.write(f'Retcode: {self.process.returncode}\n')
                    f.write('-- StdOut ----------\n')
                    f.write(self.stdout)
                    f.write('-- StdErr ----------\n')
                    f.write(self.stderr)
                                    

        except Exception as e:
            self.stderr = str(e)
            self.status = JobStatus.FAILED

    def kill(self):
        if self.process and self.process.poll() is None:
            console.print(f"[red]Killing job: {self.name}[/red]")
            self.process.terminate()  # Send SIGTERM to the process
            try:
                self.process.wait(timeout=5)  # Wait for the process to terminate
            except subprocess.TimeoutExpired:
                self.process.kill()  # Force kill if the process does not terminate
            self.status = JobStatus.FAILED



class JobManager:
    def __init__(self, max_workers):
        self.max_workers = max_workers
        self.jobs = []
        self._stop_status_thread = threading.Event()
        self._executor = None
        self.start_time = 0
        self.end_time = 0

    def add_job(self, job):
        self.jobs.append(job)

    def _print_status(self):
        total_jobs = len(self.jobs)
        self.start_time = time.time()

        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn()
        ) as progress:
            task = progress.add_task("", total=total_jobs)

            while not self._stop_status_thread.is_set():
                n_running = sum(1 for job in self.jobs if job.status == JobStatus.RUNNING)
                n_pending = sum(1 for job in self.jobs if job.status == JobStatus.PENDING)
                n_completed = sum(1 for job in self.jobs if job.status == JobStatus.COMPLETED)
                n_failed = sum(1 for job in self.jobs if job.status == JobStatus.FAILED)

                # Progress Bar
                completed_jobs = n_completed + n_failed
                progress.update(task, completed=completed_jobs)
              
                # Print
                progress.update(task, description=f'Running jobs: {total_jobs}, P: {n_pending}  R: {n_running}  C: {n_completed}  F: {n_failed} ')
                progress.refresh()
                time.sleep(2)

            progress.update(task, completed=total_jobs)
            self.end_time = time.time()


    def run(self, max_workers=None, silent=False, dry_run=False):
        if max_workers:
            self.max_workers = max_workers

        console.print(f"[bold]Jobs submitted: {len(self.jobs)}[/bold]")
        console.print("[bold]Starting jobs...[/bold]")

        if dry_run:
            console.print("[bold]Dry run mode enabled. Exiting...[/bold]")
            return

        def signal_handler(sig, frame):
            console.print("\n[red]Ctrl+C pressed. Terminating all jobs...[/red]")
            for job in self.jobs:
                job.kill()
            self._stop_status_thread.set()
            if self._executor:
                self._executor.shutdown(wait=False)
            exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        if not silent:
            status_thread = threading.Thread(target=self._print_status)
            status_thread.start()

        self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
        futures = {self._executor.submit(job.run): job for job in self.jobs}
        try:
            for future in as_completed(futures):
                job = futures[future]
                try:
                    future.result()
                except Exception as e:
                    job.status = JobStatus.FAILED
                    job.stderr = str(e)
        finally:
            self._stop_status_thread.set()
            if not silent:
                status_thread.join()
            self._executor.shutdown(wait=True)
        
        self.finalize()
    

    def finalize(self):
        for job in self.jobs:
            if job.status == JobStatus.RUNNING:
                job.kill()
        
        # Generate a summary in jobman.log
        console.print("\n[bold]Generating jobman.log...[/bold]")
        with open("jobman.log", "w") as f:
            for job in self.jobs:
                f.write(f"=====[ {job.name}: {job.status} ]====================\n")
                f.write(f"Command: {job.command}\n")
                f.write(f"Retcode: {job.process.returncode}\n")
                f.write(f"-- StdOut --------------------\n")
                f.write(f"{job.stdout}\n")
                if job.status == JobStatus.FAILED:
                    f.write(f"-- StdErr --------------------\n")
                    f.write(f"{job.stderr}\n")
                f.write("\n")

        # Print summary
        n_completed = sum(1 for job in self.jobs if job.status == JobStatus.COMPLETED)
        n_failed = sum(1 for job in self.jobs if job.status == JobStatus.FAILED)
        console.print(f"[bold]Summary: Completed: {n_completed}, Failed: {n_failed}[/bold]")