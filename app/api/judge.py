import os
import subprocess
import uuid
import shutil
from typing import List

from fastapi import HTTPException

from app.models import TestCase, SubmissionCreate

DIR_NAME = "executions"
FILE_PATH_TEMPLATE = f"{DIR_NAME}/{{}}.{{}}"
OUTPUT_EXE_TEMPLATE = f"{DIR_NAME}/{{}}.exe"
CLASS_FILE_TEMPLATE = f"{DIR_NAME}/{{}}/Main.class"


def create_folder(dir_name):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)


def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def delete_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)


class Judge:
    def __init__(self, submission_in: SubmissionCreate, testcases: List["TestCase"]):
        self.source_code = submission_in.source
        self.language = submission_in.language
        self.testcases = testcases
        self.score = 100.0
        self.random_str = str(uuid.uuid4())
        self.file_path = self.get_file_path()

    def get_file_extension(self):
        extensions = {
            'c': 'c',
            'cpp': 'cpp',
            'python': 'py',
            'java': 'java'
        }
        return extensions.get(self.language, '')

    def get_file_path(self):
        if self.language == 'java':
            return f"{DIR_NAME}/{self.random_str}/Main.java"
        return FILE_PATH_TEMPLATE.format(self.random_str, self.get_file_extension())

    def run_code(self):
        create_folder(DIR_NAME)
        if self.language == 'java':
            create_folder(f"{DIR_NAME}/{self.random_str}")

        with open(self.file_path, "w") as f:
            f.write(self.source_code)

        print("Source file path:", self.file_path)
        print("Directory content before compilation:", os.listdir(DIR_NAME))

        try:
            if self.language == "c":
                self.run_c_code()
            elif self.language == "cpp":
                self.run_cpp_code()
            elif self.language == "python":
                self.run_python_code()
            elif self.language == "java":
                self.run_java_code()
            else:
                raise HTTPException(status_code=400, detail="Unsupported language")
        except Exception as e:
            self.score = 0.0
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            delete_file(self.file_path)
            if self.language in ["c", "cpp"]:
                delete_file(self.output_exe)
            elif self.language == "java":
                delete_folder(f"{DIR_NAME}/{self.random_str}")
            print("Directory content after cleanup:", os.listdir(DIR_NAME))

    def run_c_code(self):
        self.output_exe = OUTPUT_EXE_TEMPLATE.format(self.random_str)
        print("C output executable path:", self.output_exe)
        result = subprocess.run(["gcc", self.file_path, "-o", self.output_exe, "-mconsole"], capture_output=True,
                                text=True)
        print("GCC output:", result.stdout)
        print("GCC errors:", result.stderr)
        if result.returncode == 0:
            self.run_executable(self.output_exe)
        else:
            print("GCC failed to compile the C code.")
            self.score = 0.0

    def run_cpp_code(self):
        self.output_exe = OUTPUT_EXE_TEMPLATE.format(self.random_str)
        print("C++ output executable path:", self.output_exe)
        result = subprocess.run(["g++", self.file_path, "-o", self.output_exe, "-mconsole"], capture_output=True,
                                text=True)
        print("G++ output:", result.stdout)
        print("G++ errors:", result.stderr)
        if result.returncode == 0:
            self.run_executable(self.output_exe)
        else:
            print("G++ failed to compile the C++ code.")
            self.score = 0.0

    def run_java_code(self):
        result = subprocess.run(["javac", self.file_path], capture_output=True, text=True)
        self.class_file = CLASS_FILE_TEMPLATE.format(self.random_str)
        print("Javac output:", result.stdout)
        print("Javac errors:", result.stderr)
        if result.returncode == 0:
            self.run_interpreter(["java", "-cp", f"{DIR_NAME}/{self.random_str}", "Main"])
        else:
            print("Javac failed to compile the Java code.")
            self.score = 0.0

    def run_python_code(self):
        print("Python script path:", self.file_path)
        self.run_interpreter(["python", self.file_path])

    def run_executable(self, exec_path):
        for i, testcase in enumerate(self.testcases):
            print(f"Running executable for input {i + 1}/{len(self.testcases)}")
            process = subprocess.Popen([exec_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, text=True)
            output, error = process.communicate(testcase.input_text)
            print(f"Expected output: {testcase.output_texts.strip()}")
            print(f"Actual output: {output.strip()}")
            print(f"Error: {error}")
            if process.returncode != 0 or error:
                self.score = 0.0
                break
            if output.strip() != testcase.output_texts.strip():
                self.score -= 100.0 / len(self.testcases)

    def run_interpreter(self, command):
        for i, testcase in enumerate(self.testcases):
            print(f"Running interpreter for input {i + 1}/{len(self.testcases)}")
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       text=True)
            output, error = process.communicate(testcase.input_text)
            print(f"Expected output: {testcase.output_text.strip()}")
            print(f"Actual output: {output.strip()}")
            print(f"Error: {error}")
            if process.returncode != 0 or error:
                self.score = 0.0
                break
            if output.strip() != testcase.output_text.strip():
                self.score -= 100.0 / len(self.testcases)

    def get_score(self):
        return self.score
